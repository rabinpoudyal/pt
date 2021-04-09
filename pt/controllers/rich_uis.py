from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box


def rich_table(title, headers, data):
    console = Console()
    table = Table(show_header=True, header_style="bold green")
    for header in headers:
        table.add_column(header["disp_name"], width=int(header["width"]))
    for row in data:
        row = [str(item) for item in row]
        table.add_row(*row)

    table.title = f"[b magenta not dim]{title}[/]"
    table.caption = "Made with 💖 by [b red not dim]Rabin[/]"
    table.title_justify = "center"
    table.border_style = "bright_yellow"
    try:
        table.columns[1].justify = "left"
        table.columns[2].justify = "center"
        table.columns[3].justify = "center"
    except:
        pass
    table.row_styles = ["none", "dim"]
    table.box = box.ASCII2
    console.print(table, justify="center")


def rich_show_table(title, headers, stories, comments, blockers):
    console = Console()
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Story Details", width=100)
    for story in stories:
        for row in headers:
            table.add_row(*[ '[green underline]' + str(row["disp_name"]) + ':[/]\n' + str(story.get(row["name"], "")) + '\n'])

        table.add_row(*["\n[green underline]Labels:[/] \n"])
        labels = story.get("labels", [])
        labels = " ".join([f"[b magenta not dim]{item['name']}[/]" for item in labels])
        table.add_row(*[labels])

    table.add_row(*["\n[green underline]Blockers:[/] \n"])
    for blocker in blockers:
        blkr = blocker.get("description", "")
        person_id = blocker.get("person_id", "")
        table.add_row(
            *[f"[blue underline italics]{person_id} Says[/]:\n{blkr} \n"]
        )

    table.add_row(*["\n[green underline]Comments:[/] \n"])
    for comment in comments:
        comment_text = comment.get("text", "")
        person_id = comment.get("person_id", "")
        table.add_row(
            *[f"👨 [blue underline italic]{person_id} Says[/]:\n{comment_text} \n"]
        )

    table.title = f"[b magenta not dim]{title}[/]"
    table.caption = "Made with 💖 by [b red not dim]Rabin[/]"
    table.title_justify = "center"
    table.border_style = "bright_yellow"
    table.box = box.HEAVY
    console.print(table, justify="center")
