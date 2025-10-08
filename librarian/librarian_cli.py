import click


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
    files = lib.find_latest(limit)

    if not files:
        click.echo("No documents found in library.")
        return

    click.echo(f"{'Hash ID':<16} {'File Name':<30} {'Created At'}")
    click.echo("-" * 70)

    for file in files:
        created_str = file.created_at.strftime('%Y-%m-%d %H:%M:%S')
        click.echo(f"{file.hash_id[:14]:<16} {file.file_name[:28]:<30} {created_str}")


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
@click.argument('hash_id')
def librarian_rm(hash_id):
    """Remove document by hash key"""
    from librarian.librarian import Librarian

    lib = Librarian()
    success = lib.remove_by_hash(hash_id)

    if success:
        click.echo(f"Document with hash {hash_id} has been removed.")
    else:
        click.echo(f"Document with hash {hash_id} not found.")


if __name__ == '__main__':
    librarian()
