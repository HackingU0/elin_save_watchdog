# Elin Save Watchdog

This is a simple Python script to resolve the issue where the game **Elin** cannot save progress on macOS (when running through Wine).

## Features

- Monitors specific directories to automatically delete temporary files that may block the saving process in **Elin**.

## Requirements

- Python 3.9 or higher
- Watchdog Module

### Install Python 3.9+

To install Python 3.9 via **Homebrew**, run the following command in your terminal:

```bash
brew install python@3.9
```

### Install Watchdog Module

Next, install the **Watchdog** module, which is used for directory monitoring:

```bash
pip install watchdog
```

## Usage

1. **Modify the `watch_directory`** in the `elin_watchdog.py` script to the appropriate directory path where your game saves are located. 

2. Run the script using Python:

```bash
python elin_watchdog.py
```

This will start monitoring the specified folder and will automatically delete the `Temp` folder if conditions are met, allowing the game to save without issues.

---

### Notes

- The script continuously monitors the game's save folder for any newly created directories (like `world_01` folders) and deletes temporary files when necessary.
- If you encounter any issues, make sure that the directory paths are correct and that you have the required permissions to modify the folders.

---
