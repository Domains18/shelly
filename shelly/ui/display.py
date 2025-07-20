"""Display formatting functionality."""

from rich.console import Console
from rich.table import Table

console = Console()

def format_table(headers, rows):
    """Format data as a table."""
    table = Table()
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*row)
    return table

def format_error(message):
    """Format error message."""
    console.print(f"[red]Error:[/red] {message}")
