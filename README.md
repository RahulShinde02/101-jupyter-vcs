# 101-jupyter-vcs

A personal workspace archivist and lightweight local Version Control System (VCS) built to snapshot, catalog, and restore my Jupyter Notebooks and scratchpad scripts using an embedded **SQLite** database.

---

* The project is AI assisted; I used Gemini for checking bugs, designing the view functionality for ipynb files, decorating the final script, and generating the logo.

## 📌 Why I Built This (The Problem)

When I am working on an analysis, my project directories get incredibly messy, incredibly fast. I constantly end up with a mountain of clutter:

* Half-baked experimental scripts (`test_code.py`)
* Discarded notebook templates (`untitled1.ipynb`, `draft_analysis_v2.ipynb`)
* Temporary scratchpad SQL queries and text drafts

Leaving all these files in my active directory creates a lot of mental clutter and makes my workspace completely unmanageable. But whenever I try to clean up and ruthlessly purge these files, I get hit with **"deletion anxiety."** I worry that a week from now, I’ll realize that an old, abandoned script contained a brilliant custom helper function, or a specific data-cleaning snippet that I actually need.

I didn't want to choose between a cluttered folder or losing my hard work. So, I built `101-jupyter-vcs`.

This tool acts as an **intelligent, localized code archive**. Before I wipe out the messy files in my folder, I run this utility to snapshot my entire workspace into a single, compact **SQLite file**. My directory stays completely pristine and manageable, but I never have to worry about losing an important piece of code.

---

## 🛠️ Tech Stack & Architecture Choices

* **Python 3:** I used native modules (`pathlib`, `argparse`, `textwrap`, `hashlib`,`sqlite3`) to keep the CLI fast, lightweight, and zero-boilerplate.
* **SQLite:** I chose SQLite for its rock-solid reliability and seamless integration with Python. It provides an efficient, lightweight storage solution that perfectly handles the tracking of text data and notebook structures without needing external dependencies.

---

## 🚀 How It Solves My Workflow Pain

1. **Incremental Snapshotting:** It scans my workspace for extensions (`*.ipynb`, `*.py`, `*.md`, `*.txt`, `*.sql`) and updates the archive **only** if the file content has actually changed since the last backup by comparing the MD5 hash of the last backed-up file with the current file.
2. **Terminal Notebook Inspection:** If I am hunting for a function inside an old notebook I already deleted from my directory, the built-in `view` command parses the raw JSON structure of the `.ipynb` file and renders the code and markdown cells cleanly in my terminal.
3. **Safe, Clutter-Free Restores:** When I need to pull something back, it generates a time-stamped copy (e.g., `data_cleaning_20260613_223000.ipynb`) so it never accidentally overwrites active files I am working on.

---

## 📂 Project Structure

```text
101-jupyter-vcs/
│
├── README.md                # My project documentation and architecture log
└── 101-jupyter-vcs v2 sqlite/
    ├── 101.exe              # Compiled executable for Windows (fast, Nuitka-built)
    └── 101.py               # Core CLI engine and backup logic
```

---

##### Here is the direct, step-by-step breakdown to set up both methods on Windows so you can use the `101` command anywhere.

---

### Option A: Setting up `101.py` with a `.bat` file

This method keeps your script editable. When you type `101` in the terminal, Windows runs the batch file, which instantly forwards your command to Python.

#### Step 1: Create a dedicated utilities folder

1. Open File Explorer and create a folder where you will store your custom tools, for example: `C:\utils`
2. Move your `101.py` file into this folder (`C:\utils\101.py`).

#### Step 2: Create the `.bat` file

1. Inside `C:\utils`, right-click -> **New** -> **Text Document**.
2. Name it `101.bat` (make sure to change the extension from `.txt` to `.bat`).
3. Right-click `101.bat`, select **Edit** (or open it in Notepad), and paste the following line:

```batch
@echo off
python "C:\utils\101.py" %*
```

*(The `%*` is crucial—it ensures that arguments like `backup` or `list` get passed from the batch file straight to your Python script).*

#### Step 3: Add the folder to your System PATH

1. Press the **Windows Key**, type `env`, and select **Edit the system environment variables**.
2. Click the **Environment Variables...** button at the bottom right.
3. In the *User variables* (or *System variables*) box, look for the variable named **Path** and double-click it.
4. Click **New** on the right side and type your folder path: `C:\utils`
5. Click **OK** on all open windows to save.

---

### Option B: Setting up the precompiled `101.exe`

If you prefer a standalone executable (`101.exe`), you don't need a batch file or a dedicated Python setup for it to run globally.

#### Approach 1: Drop it into an existing PATH folder (Fastest)

Windows already tracks several system folders by default.

1. Copy the `101.exe` binary.
2. Paste it directly into `C:\Windows\System32\` (or `C:\Windows\`).
3. Because these directories are already hardcoded into every computer's environment path, it is instantly available globally.

#### Approach 2: Drop it into your custom PATH folder

1. If you already have a custom folder like `C:\utils` and added it to your Environment Variables, simply drop your `101.exe` file into that folder.
2. Windows will automatically find the executable whenever you type `101`.

---

### 🧪 Verification

To verify it works, close any active terminal windows (to refresh the environment variables), open a brand new **Command Prompt**  navigate to any random folder, and type:

```bash
101 list
```

A table layout or a "No backups found" message appears, your system path routing is configured perfectly.

> 💡 **PowerShell Execution Note:** > If you plan to use this tool in **PowerShell**, it is highly recommended to rename the executable or `.bat` to something starting with an alphabet (e.g., `jvcs.exe` or `jvcs.bat`).
>
> Because PowerShell treats purely numeric names (like `101`) differently, trying to run `101` directly will fail. To run a numeric binary without renaming it, you must explicitly use the call operator:
>
> ```powershell
> &101 backup
> ```

## 🛠️ 101-jupyter-vcs (`101`) CLI User Guide

`101` is a lightweight, local version control system powered by **SQLite**. It specifically targets data science workflows, backing up flat files and Jupyter Notebooks without the bloat and diff-clutter of standard Git repositories.

**Tracked Extensions:** `.ipynb`, `.py`, `.md`, `.txt`, `.sql`
**Storage:** Automatically creates a lightweight SQLite database (`<current_folder_name>_backup.sqlite`) in your active directory.

---

## ⚙️ Core Commands

### 1. Save Your Work: `backup`

Scans your current directory and saves a snapshot of all tracked files.

* **Smart Saving:** It checks the database first. If a file hasn't changed since your last backup, it skips it to prevent database bloat.
* **Command:**

```bash
101 backup
```

* **Output:** Tells you exactly what was backed up and what was skipped due to no changes.

> **⚠️ Global Command Context:** Always ensure your terminal is navigated to your actual project folder before running commands. Running `101 backup` inside system directories or your custom `C:\utils` folder will create accidental tracking databases in those locations.

### 2. Check Your History: `list`

Displays a summary of everything stored in your local database.

* **View Global Summary:**
  Shows all tracked files, how many versions exist, and the most recent backup time.

```bash
101 list
```

* **View Specific File History:**
  Provides a chronological list of every exact timestamp available for a single file.

```bash
101 list -f "tableaudataclean.ipynb"
```

### 3. Inspect Without Restoring: `view`

Prints the contents of a backed-up file directly into your terminal. This is highly optimized for Jupyter Notebooks. Instead of printing a massive, unreadable JSON string, it parses the `.ipynb` file and cleanly renders the code cells, stream outputs, and errors.

* **View Latest Version:**

```bash
101 view "tableaudataclean.ipynb"
```

* **View Specific Version (Time Travel):**
  You can use a partial or exact timestamp to view older versions.

```bash
101 view "tableaudataclean.ipynb" -t "2026-06-13"
```

### 4. Safe Recovery: `restore`

Pulls a file out of the database and saves it to your directory. **It never overwrites your active file.** Instead, it creates a new file appended with the backup's clean timestamp (e.g., `script_20260613_162500.py`).

* **Restore the Latest Good Copy:**

```bash
101 restore "tableaudataclean.ipynb"
```

* **Restore a Specific Snapshot:**
  Use the timestamp found via the `list` command to recover an exact moment in time. Thanks to partial string matching, you don't even need to type the full timestamp.

- Tip: Just copy-paste from list comand (works best..)

```bash
101 restore "tableaudataclean.ipynb" -t "2026-06-13 16:24"
```

---

## 🧠 Best Practices

> [!WARNING]
> **Directory Renaming:** If you rename your project directory, you must manually rename the local `<old_name>_backup.sqlite` file to match your new directory name. Otherwise, the tool will create a brand new database and lose track of your existing history.

> **🔤 Case-Sensitivity:** If you modify only the *casing* of a filename (e.g., `Analysis.ipynb` to `analysis.ipynb`), the tool will treat it as a completely new file and split your historical timeline. Try to keep filename casing consistent.

* **Add it to `.gitignore`:** Ensure you add `*.sqlite` to your `.gitignore` file so you don't accidentally push your local sqlite tracking file to a remote repository.
* **Use Quotes:** If your filenames have spaces or special characters (like `&`), always wrap the filename in double quotes (e.g., `101 restore "data cleaning & transformation.ipynb"`).
