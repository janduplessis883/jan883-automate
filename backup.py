import os
import shutil
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

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

# Initialize Rich console
console = Console()

# Create a single timestamp for all backups
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Display startup information with Rich
console.print(Panel.fit(
    f"[bold cyan]🔄 Email Automation Toolkit - Backup System[/bold cyan]\n"
    f"[yellow]Started at: {timestamp}[/yellow]",
    title="Backup Process",
    border_style="blue"
))

# Display skip items in a table
skip_table = Table(title="Files/Folders to Skip", show_header=False)
skip_table.add_column("Item", style="red")
for item in sorted(skip_items):
    skip_table.add_row(f"🚫 {item}")
console.print(skip_table)
console.print()

# Create backup summary table
summary_table = Table(title="Backup Summary")
summary_table.add_column("#", style="cyan", width=3)
summary_table.add_column("Source", style="magenta")
summary_table.add_column("Status", justify="center")
summary_table.add_column("Details", style="dim")

# Validate backup configurations before starting
console.print("[bold yellow]🔍 Validating backup configurations...[/bold yellow]")
for i, config in enumerate(backup_configs, 1):
    source = config["source"]
    if not os.path.exists(source):
        console.print(f"[bold red]❌ Warning:[/bold red] Source folder {source} does not exist")
    elif not os.access(source, os.R_OK):
        console.print(f"[bold red]❌ Warning:[/bold red] No read permission for {source}")
    else:
        console.print(f"[green]✅[/green] Source {i}: {source}")

console.print()

# Process each backup configuration
for i, config in enumerate(track(backup_configs, description="Processing backups..."), 1):
    source_folder = config["source"]
    backup_folder = config["destination"]

    # Create timestamped backup path with source folder name for uniqueness
    source_name = os.path.basename(source_folder.rstrip('/'))
    backup_path = os.path.join(backup_folder, f"{source_name}_backup_{timestamp}")

    try:
        console.print(f"\n[bold blue]Backup {i}/{len(backup_configs)}:[/bold blue] [cyan]{source_folder}[/cyan]")
        console.print(f"[dim]→ Destination: {backup_path}[/dim]")
        
        # Ensure the parent backup folder exists
        os.makedirs(backup_folder, exist_ok=True)

        # Copy entire directory tree recursively, skipping specified items
        # symlinks=False prevents copying broken symlinks that cause errors
        with console.status(f"[bold green]Copying files from {os.path.basename(source_folder)}..."):
            shutil.copytree(source_folder, backup_path, ignore=should_skip, symlinks=False)

        console.print(f"[bold green]✅ Backup completed successfully![/bold green]")
        summary_table.add_row(str(i), source_name, "[green]✅ Success[/green]", backup_path)

    except FileExistsError:
        error_msg = "Backup destination already exists"
        console.print(f"[bold red]❌ Error:[/bold red] {error_msg}")
        summary_table.add_row(str(i), source_name, "[red]❌ Failed[/red]", error_msg)
    except PermissionError:
        error_msg = "Permission denied - check folder access"
        console.print(f"[bold red]❌ Error:[/bold red] {error_msg}")
        summary_table.add_row(str(i), source_name, "[red]❌ Failed[/red]", error_msg)
    except FileNotFoundError:
        error_msg = "Source folder not found"
        console.print(f"[bold red]❌ Error:[/bold red] {error_msg}")
        summary_table.add_row(str(i), source_name, "[red]❌ Failed[/red]", error_msg)
    except Exception as e:
        error_msg = str(e)
        console.print(f"[bold red]❌ Backup failed:[/bold red] {error_msg}")
        summary_table.add_row(str(i), source_name, "[red]❌ Failed[/red]", error_msg)

# Display final summary
console.print("\n")
console.print(summary_table)
console.print(Panel.fit(
    "[bold green]🎉 All backup operations completed![/bold green]",
    title="Process Complete",
    border_style="green"
))
