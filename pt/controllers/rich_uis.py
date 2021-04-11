from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box
from rich.columns import Columns
from rich.panel import Panel

def show_columns(data, headers):
    user_renderables = [
        Panel("\n".join([str(i) for i in d[1:]]), width=30, highlight=True, title=d[0], title_align='left', height=13)
        for d in data
    ]
    console = Console()
    console.print(Columns(user_renderables))

def rich_table(title, headers, data):
    show_columns(data, headers)

def rich_show_table(title, stories, comments, blockers):
    blockers_text = "\n[b blue] Blockers:[/]\n"
    for blocker in blockers:
        blkr = blocker.get("description", "")
        person_id = blocker.get("person_id", "")
        blockers_text += f"\n[blue underline italics]{person_id} Says[/]:\n{blkr} \n"

    comment_text = "\n[b blue] Comments:[/]\n"
    for comment in comments:
        comment_message = comment.get("text", "")
        person_id = comment.get("person_id", "")
        comment_text += f"\n [b dim underline italic]{person_id} Says[/]:\n{comment_message} \n"

    story_details = "\n".join([str(i) for i in stories[0][1:]]) + '\n'
    story_details += blockers_text
    story_details += comment_text

    user_renderables = [
        Panel(story_details, highlight=True, title=stories[0][0], title_align='left')
    ]
    console = Console()
    console.print(Columns(user_renderables))

def notifications_table(headers, data):
    table = Table(title="[b blue]Notifications[/]", box=box.SIMPLE)
    for h in headers:
        table.add_column(f'[b blue]{h.capitalize()}[/]')
    for d in data:
        table.add_row(*d)
    console = Console()
    console.print(table, justify="center")