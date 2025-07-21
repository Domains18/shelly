"""Display formatting functionality."""

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()


def print_success(message: str) -> None:
    """Print a success message in green"""
    console.print(f"✅ {message}", style="green")


def print_error(message: str) -> None:
    """Print an error message in red"""
    console.print(f"❌ {message}", style="red")


def print_warning(message: str) -> None:
    """Print a warning message in yellow"""
    console.print(f"⚠️  {message}", style="yellow")


def print_info(message: str) -> None:
    """Print an info message in blue"""
    console.print(f"ℹ️  {message}", style="blue")


def print_header(message: str) -> None:
    """Print a header message"""
    console.print(f"\n🐚 {message}", style="cyan bold")
    console.print("=" * (len(message) + 3), style="cyan")


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


def format_repository_info(repo_info: dict) -> str:
    """Format repository information for display"""
    name = repo_info.get('name', 'Unknown')
    owner = repo_info.get('owner', '')
    platform = repo_info.get('platform', 'unknown')
    
    platform_emoji = {
        'github': '🐙',
        'gitlab': '🦊',
        'bitbucket': '📘'
    }.get(platform, '📦')
    
    if owner:
        return f"{platform_emoji} {owner}/{name}"
    else:
        return f"{platform_emoji} {name}"
