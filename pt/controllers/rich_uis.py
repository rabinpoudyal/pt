from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

def rich_table(title, headers, data):
    console = Console()
    table = Table(show_header=True ,header_style="bold green")
    for header in headers:
        table.add_column(header['disp_name'], width=int(header['width']), )
    for row in data:
        row = [str(item) for item in row]
        table.add_row(*row)

    table.title = f"[b magenta not dim]{title}[/]"
    table.caption = "Made with 💖 by [b red not dim]Rabin[/]"
    table.title_justify = "center"
    table.border_style = "bright_yellow"
    table.columns[1].justify = "left"
    table.columns[2].justify = "center"
    table.columns[3].justify = "center"
    table.row_styles = ["none", "dim"]
    table.box = box.ASCII2
    console.print(table, justify='center')