import click
from rich.console import Console
from rich.table import Table
from tqdm import tqdm


@click.group()
def librarian():
    """Manage documents in the library"""
    pass


@librarian.command('ls')
@click.option('--limit', '-n', default=10, help='Number of latest documents to show')
def librarian_ls(limit):
    """Show latest n documents added to the library"""
    from librarian.librarian import Librarian

    lib = Librarian()
    total_count = lib.count()

    if total_count == 0:
        click.echo("No documents found in library.")
        return

    files = lib.find_latest(limit)

    console = Console()

    table = Table(title=f"Showing latest {len(files)} documents (out of {total_count} total)")
    table.add_column("Hash ID", style="cyan", no_wrap=True)
    table.add_column("File Name", style="magenta")
    table.add_column("Created At", style="green")

    for file in files:
        created_str = file.created_at.strftime('%Y-%m-%d %H:%M:%S')
        table.add_row(file.hash_id[:14], file.file_name, created_str)

    console.print(table)


@librarian.command('drop')
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
def librarian_drop(force):
    """Remove entire vector store directory and database records"""
    from librarian.librarian import Librarian

    if not force:
        if not click.confirm('This will delete ALL documents from the library. Continue?'):
            click.echo("Operation cancelled.")
            return

    lib = Librarian()
    lib.drop_vector_store()
    click.echo("Vector store and library records have been cleared.")


@librarian.command('rm')
@click.option('--hash-prefix', '-h', default=None, help='Hash prefix to match')
@click.option('--filename', '-f', default=None, help='Filename to match (partial)')
def librarian_rm(hash_prefix, filename):
    """Remove document by hash prefix or filename"""
    from librarian.librarian import Librarian

    if not hash_prefix and not filename:
        click.echo("Error: Must provide either --hash-prefix or --filename")
        return

    lib = Librarian()

    try:
        success = lib.remove(hash_prefix=hash_prefix, filename=filename)

        if success:
            click.echo("Document has been removed.")
        else:
            click.echo("No matching document found.")
    except ValueError as e:
        click.echo(f"Error: {e}")


@librarian.command('add')
@click.argument('path', type=click.Path(exists=True))
@click.argument('device', type=str, default='cpu')
def librarian_add(path, device):
    """Add document(s) to the library"""
    from pathlib import Path
    from librarian.librarian import Librarian

    from librarian import components
    vector_store = components.get_vector_store(device=device)
    lib = Librarian(vector_store=vector_store)
    path_obj = Path(path)

    if path_obj.is_file():
        files_to_add = [path_obj]
    else:
        files_to_add = [f for f in path_obj.rglob('*') if f.is_file()]

    if not files_to_add:
        click.echo("No files found to add.")
        return

    added_count = 0
    skipped_count = 0

    for file_path in tqdm(files_to_add, desc="Adding files", unit="file"):
        try:
            lib.add_file(file_path)
            click.echo(f"Added: {file_path}")
            added_count += 1
        except ValueError as e:
            click.echo(f"Skipped: {file_path} - {e}")
            skipped_count += 1
        except FileNotFoundError as e:
            click.echo(f"Error: {e}")
            skipped_count += 1

    click.echo(f"\nSummary: {added_count} added, {skipped_count} skipped")


if __name__ == '__main__':
    librarian()
