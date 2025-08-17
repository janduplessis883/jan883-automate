import os
import shutil
from datetime import datetime

# Define multiple source folders and their corresponding backup destinations
backup_configs = [
    {
        "source": "/Users/janduplessis/code/janduplessis883",
        "destination": "/Volumes/JanBackupHD/AUTO-BACKUPS"
    },
    # Add more backup configurations here
    {
        "source": "/Users/janduplessis/Documents",
        "destination": "/Volumes/JanBackupHD/AUTO-BACKUPS"
    },
    # {
    #     "source": "/Users/janduplessis/Desktop",
    #     "destination": "/Volumes/JanBackupHD/Desktop-BACKUP"
    # }
]

# Files and folders to skip during backup
skip_items = {
    '.git',
    '.DS_Store',
    '__pycache__',
    'node_modules',
    '.env',
    '.vscode',
    'Thumbs.db',
    '.gitignore',
    'wandb',
    ".ipynb_checkpoints",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".cache.sqlite",
    ".python-version",
    }

def should_skip(path, names):
    """Function to determine which files/folders to skip"""
    return [name for name in names if name in skip_items]

# Create a single timestamp for all backups
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

print(f"Starting backup process at {timestamp}")
print(f"Skipping: {', '.join(sorted(skip_items))}")
print("-" * 50)

# Process each backup configuration
for i, config in enumerate(backup_configs, 1):
    source_folder = config["source"]
    backup_folder = config["destination"]

    # Create timestamped backup path with source folder name for uniqueness
    source_name = os.path.basename(source_folder.rstrip('/'))
    backup_path = os.path.join(backup_folder, f"{source_name}_backup_{timestamp}")

    try:
        print(f"[{i}/{len(backup_configs)}] Starting backup from {source_folder}")
        print(f"[{i}/{len(backup_configs)}] Backup destination: {backup_path}")

        # Ensure the parent backup folder exists
        os.makedirs(backup_folder, exist_ok=True)

        # Copy entire directory tree recursively, skipping specified items
        # symlinks=False prevents copying broken symlinks that cause errors
        shutil.copytree(source_folder, backup_path, ignore=should_skip, symlinks=False)

        print(f"[{i}/{len(backup_configs)}] ✅ Backup completed successfully at {backup_path}")

    except FileExistsError:
        print(f"[{i}/{len(backup_configs)}] ❌ Error: Backup destination {backup_path} already exists")
    except PermissionError:
        print(f"[{i}/{len(backup_configs)}] ❌ Error: Permission denied. Check access to source or destination folders")
    except FileNotFoundError:
        print(f"[{i}/{len(backup_configs)}] ❌ Error: Source folder {source_folder} not found")
    except Exception as e:
        print(f"[{i}/{len(backup_configs)}] ❌ Backup failed: {e}")

    print("-" * 50)

print("All backup operations completed!")
