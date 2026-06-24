import argparse
import json
import textwrap
from datetime import datetime
from pathlib import Path
import sqlite3
import hashlib

class JupyterBackup:

    def __init__(self, db_name=None, extensions=None):
        self.current_dir = Path.cwd()
        dir_name = self.current_dir.name
        self.db_filename = db_name or f"{dir_name}_backup.sqlite"
        self.extensions = extensions or [
            "*.ipynb",
            "*.txt",
            "*.py",
            "*.md",
            "*.sql",
        ]
        self._init_db()

    def _init_db(self):
        """Ensures the database and required table exist with raw text tracking columns."""
        with sqlite3.connect(self.db_filename) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS backup1 (
                    filename VARCHAR, 
                    inserted VARCHAR,  
                    file VARCHAR,
                    hash VARCHAR
                );
            """)
            con.commit()

    def backup(self):
        """Scans the directory and backs up matching files only if they have changed using md5 hashing."""
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        files_to_backup = [
            f
            for ext in self.extensions
            for f in self.current_dir.glob(ext)
            if f.name != self.db_filename and f.suffix not in ['.database', '.wal', '.tmp', '.db','.db-wal','.db-shm','.db-journal',]
        ]



        if not files_to_backup:
            print("No files found to backup.")
            return

        with sqlite3.connect(self.db_filename) as con:
            for f_path in files_to_backup:
                try:
                    with open(f_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        md5_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

                    # Fetch the most recent backup of this specific file
                    last = con.execute(
                        "SELECT hash FROM backup1 WHERE filename=? ORDER BY inserted DESC LIMIT 1",
                        [f_path.name],
                    ).fetchone()

                    # Only insert if it is the first time backing up OR the content has changed
                    if not last or last[0] != md5_hash:
                        con.execute(
                            "INSERT INTO backup1 VALUES (?, ?, ?, ?)",
                            [f_path.name, created_at, content, md5_hash],
                        )
                        con.commit()
                        print(f"✅ Backed up new version: {f_path.name}")
                    else:
                        print(f"⏩ Skipped (No changes): {f_path.name}")

                except Exception as e:
                    print(f"❌ Failed to backup {f_path.name}: {e}")

    def restore(self, target_filename, target_timestamp=None):
        """Fetches a backup of a file (latest or specific timestamp) and saves it safely."""
        with sqlite3.connect(self.db_filename) as con:
            if target_timestamp:
                target_timestamp = target_timestamp.strip()
                query = "SELECT file, inserted FROM backup1 WHERE filename = ? AND inserted LIKE ?"
                result = con.execute(
                    query, [target_filename, f"{target_timestamp}%"]
                ).fetchone()
            else:
                query = "SELECT file, inserted FROM backup1 WHERE filename = ? ORDER BY inserted DESC LIMIT 1"
                result = con.execute(query, [target_filename]).fetchone()

            if result:
                content, timestamp = result
                # Clean parse independent of operational type bindings
                dt_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") if isinstance(timestamp, str) else timestamp
                clean_ts = dt_obj.strftime("%Y%m%d_%H%M%S")
                path = Path(target_filename)
                restore_name = f"{path.stem}_{clean_ts}{path.suffix}"

                with open(restore_name, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Restored version from {timestamp} to -> {restore_name}")
            else:
                if target_timestamp:
                    print(f"⚠️ No backup found for '{target_filename}' matching timestamp '{target_timestamp}'.")
                else:
                    print(f"⚠️ No backups found for '{target_filename}'. Check the spelling.")

    def list_backups(self, specific_file=None):
        """Displays a summary of files, or detailed timestamps for a specific file."""
        with sqlite3.connect(self.db_filename) as con:
            if specific_file:

                results = con.execute(
                    "SELECT inserted FROM backup1 WHERE filename = ? ORDER BY inserted DESC",
                    [specific_file],
                ).fetchall()

                if not results:
                    print(f"No backups found for {specific_file}.")
                    return

                print(f"\nVersions available for {specific_file}:")
                print("-" * 35)
                for row in results:
                    print(f" • {row[0]}")
            else:
                results = con.execute("""
                    SELECT filename, COUNT(*) as versions, MAX(inserted) as last_backup 
                    FROM backup1 
                    GROUP BY filename
                    ORDER BY last_backup DESC
                """).fetchall()

                if not results:
                    print("No backups found in the database.")
                    return

                print(f"\n{'Filename':<30} | {'Versions':<10} | {'Last Backup'}")
                print("-" * 65)
                for row in results:
                    fname = row[0] if len(row[0]) <= 29 else row[0][:26] + "..."
                    print(f"{fname:<30} | {row[1]:<10} | {row[2]}")

    def _render_ipynb(self, raw_json_str):
        """Parses and formats JSON string representing an ipynb notebook file."""
        try:
            notebook = json.loads(raw_json_str)
            cells = notebook.get("cells", [])

            for i, cell in enumerate(cells):
                cell_type = cell.get("cell_type", "unknown").upper()
                source = "".join(cell.get("source", []))

                if not source.strip():
                    continue

                print(f"\n{'='*20} CELL {i+1} ({cell_type}) {'='*20}")
                print(source)

                if cell_type == "CODE" and "outputs" in cell:
                    for output in cell.get("outputs", []):
                        out_type = output.get("output_type")
                        if out_type == "stream":
                            print("\n[Output - Stream]:")
                            print("".join(output.get("text", [])))
                        elif out_type in ["execute_result", "display_data"]:
                            data = output.get("data", {})
                            if "text/plain" in data:
                                print("\n[Output - Result]:")
                                print("".join(data["text/plain"]))
                        elif out_type == "error":
                            print("\n[Output - ERROR]:")
                            print("\n".join(output.get("traceback", [])))
        except json.JSONDecodeError:
            print("❌ Error parsing notebook file: Stored file contents are not valid JSON.")

    def view(self, target_filename, target_timestamp=None):
        """Displays the contents of a backed-up file directly in the terminal."""
        with sqlite3.connect(self.db_filename) as con:
            if target_timestamp:
                query = "SELECT file, inserted FROM backup1 WHERE filename = ? AND inserted LIKE ?"
                result = con.execute(
                    query, [target_filename, f"{target_timestamp}%"]
                ).fetchone()
            else:
                query = "SELECT file, inserted FROM backup1 WHERE filename = ? ORDER BY inserted DESC LIMIT 1"
                result = con.execute(query, [target_filename]).fetchone()

            if result:
                content, timestamp = result
                print(f"\n--- Viewing: {target_filename} (Backup Timestamp: {timestamp}) ---")

                if target_filename.lower().endswith(".ipynb"):
                    self._render_ipynb(content)
                else:
                    print("~" * 80)
                    for line in content.splitlines():
                        if not line.strip():
                            print()
                        else:
                            wrapped = textwrap.wrap(
                                line, width=80, drop_whitespace=False, replace_whitespace=False
                            )
                            print("\n".join(wrapped))
                    print("~" * 80)
            else:
                if target_timestamp:
                    print(f"⚠️ No backup found for '{target_filename}' matching timestamp '{target_timestamp}'.")
                else:
                    print(f"⚠️ No backups found for '{target_filename}'. Check the spelling.")


def main():
    parser = argparse.ArgumentParser(description="Jupyter Notebook Local Version Control")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("backup", help="Backup all tracked files in the current directory")

    restore_parser = subparsers.add_parser("restore", help="Restore the latest or a specific version of a file safely")
    restore_parser.add_argument("filename", help="Exact name of the file to restore")
    restore_parser.add_argument("-t", "--timestamp", help="Timestamp to restore", default=None)

    list_parser = subparsers.add_parser("list", help="List all backed up files and their metadata")
    list_parser.add_argument("-f", "--filename", help="List all available timestamps for a specific file", default=None)

    view_parser = subparsers.add_parser("view", help="Print the contents of a backed up file to the terminal")
    view_parser.add_argument("filename", help="Exact name of the file to view")
    view_parser.add_argument("-t", "--timestamp", help="Timestamp to view", default=None)

    args = parser.parse_args()


    if args.command in ["backup", "restore", "list", "view"]:
        app = JupyterBackup()
        if args.command == "backup":
            app.backup()
        elif args.command == "restore":
            app.restore(args.filename, args.timestamp)
        elif args.command == "list":
            app.list_backups(args.filename)
        elif args.command == "view":
            app.view(args.filename, args.timestamp)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
