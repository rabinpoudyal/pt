import requests
import json
from time import strftime
from cement import Controller, ex

from .utils import preety_print
from .rich_uis import rich_table, rich_show_table, notifications_table
from rich.prompt import Prompt, Confirm

from .constants import TRACKER_CONSTANTS
class Pivotal(Controller):
    class Meta:
        label = "pivotal"

    def api_header(self):
        """
        Generates the API header.
        Returns the dict with token.
        """
        self.app.log.info("Setting the tracker token")
        api_token = self.app.config.get("pt", "PIVOTAL_TRACKER_API_TOKEN")
        return {"X-TrackerToken": api_token}

    @ex(help="me in tracker")
    def me(self):
        """
        Gets details about your account from tracker and prints it in nice format.
        """
        url = TRACKER_CONSTANTS["endpoints"].get("my_details")
        result = requests.get(url, headers=self.api_header())
        self.app.log.info("Your details as JSON:")
        preety_print(result.json())

    @ex(help="notifications")
    def notifications(self):
        """
        Shows notifications
        """
        url = TRACKER_CONSTANTS["endpoints"].get("notifications")
        result = requests.get(url, headers=self.api_header())
        results = result.json()
        headers = ["id", "performer", "message", "notification_type", "action", "story"]
        data = []
        for item in results["data"]:
            record = []
            for k, v in item.items():
                if k in headers:
                    if k in ["performer", "story"]:
                        record.append(str(v["id"]))
                    else:
                        record.append(str(v))
            data.append(record)
        notifications_table(headers, data)

    def arrange_tasks_bsed_on_state(self, stories):
        """
        Sorts the task bsed on order
        """
        stories_order = [
            "unscheduled",
            "unstarted",
            "planned",
            "started",
            "finished",
            "delivered",
        ]
        new_story_order = []
        for item in stories_order:
            result = filter(lambda x: x["current_state"] == item, stories)
            new_story_order += result

        return reversed(new_story_order)

    def generate_headers_and_data(self, story_type, results):
        """
        This method generates keys and data depending upon the story type.
        So that it can be rendered in UI.
        It also filter stories based on bug / feature / chore.
        And sorts the data
        """
        base_headers = [
            {"name": "id", "disp_name": "ID", "width": "10"},
            {"name": "name", "disp_name": "Name", "width": "85"},
            {"name": "description", "disp_name": "Description", "width": "85"},
            {"name": "url", "disp_name": "Link", "width": "85"},
        ]

        if story_type in ["f", "feature", "features"]:
            selected_story_type = "feature"
            headers = base_headers + [
                {"name": "current_state", "disp_name": "State", "width": "10"},
                {"name": "estimate", "disp_name": "Estimate", "width": "5"},
            ]
            stories = [item for item in results if item.get("story_type") == "feature"]
        elif story_type in ["c", "chore", "chores"]:
            selected_story_type = "chore"
            headers = base_headers + [
                {"name": "requested_by_id", "disp_name": "Requester.", "width": "5"},
                {"name": "current_state", "disp_name": "State", "width": "10"},
            ]
            stories = [item for item in results if item.get("story_type") == "chore"]
        elif story_type in ["b", "bug", "bugs"]:
            selected_story_type = "bug"
            headers = base_headers + [
                {"name": "current_state", "disp_name": "State", "width": "10"},
            ]
            stories = [item for item in results if item.get("story_type") == "bug"]
        else:
            print("Only: f/c/b")
            selected_story_type = ""
            stories, headers = [], []

        stories = self.arrange_tasks_bsed_on_state(stories)
        return stories, headers, selected_story_type

    def transform_values(self, story_type, results):
        """
        This method transforms the values.
        It adds appropriate emojis depending on the task state.
        """
        color_codes = {
            "started": {"color_tag": "[b orchid not dim]", "emoji": " "},
            "finished": {"color_tag": "[b yellow not dim]", "emoji": " "},
            "delivered": {"color_tag": "[b green not dim]", "emoji": "ﮒ "},
            "planned": {"color_tag": "[b tan not dim]", "emoji": " "},
            "unscheduled": {"color_tag": "[b black not dim]", "emoji": " "},
            "unstarted": {"color_tag": "[b dim]", "emoji": "ﲅ "},
        }
        stories, headers, selected_story_type = self.generate_headers_and_data(
            story_type, results
        )
        for table in [stories]:
            data = []
            for item in table:
                record = []
                for key in headers:
                    title_text = "\n[b blue]" + key["disp_name"] + ": [/]\n  "
                    if key["name"] == "id":
                        s = f"[b blue][link={item['url']}] {item[key['name']]}[/link][/]\n"
                    elif key["name"] == "current_state":
                        state = item[key["name"]]
                        s = (
                            title_text
                            + color_codes[state]["color_tag"]
                            + color_codes[state]["emoji"]
                            + state
                            + "[/]"
                        )
                    else:
                        s = title_text + str(item.get(key["name"], "ﲅ"))
                    record.append(s)
                data.append(record)
        return selected_story_type, headers, data

    def generate_panel_lists(self, story_type, results):
        """
        This method generates the panel lists.
        It also removes details and urls from index view.
        """
        selected_story_type, headers, data = self.transform_values(story_type, results)
        # Delete link and description
        for d in data:
            del d[2:4]
        rich_table(
            selected_story_type.capitalize() + " Tickets",
            headers,
            reversed(data),
        )

    @ex(
        help="list stories",
        arguments=[
            (["story_type"], {"help": "story type", "action": "store"}),
        ],
    )
    def list(self):
        """
        Lists items from tracker and builds panels for UI.
        """
        story_type = self.app.pargs.story_type
        url = TRACKER_CONSTANTS["endpoints"].get("stories_search")
        PROJECT_ID = self.app.config.get("pt", "PROJECT_ID")
        result = requests.get(
            f"{url}".format(PROJECT_ID=PROJECT_ID), headers=self.api_header()
        )
        results = result.json()["stories"]["stories"]
        self.generate_panel_lists(story_type, results)

    @ex(
        help="list labels",
    )
    def labels(self):
        """
        Displays labels present in the project
        """
        url = TRACKER_CONSTANTS["endpoints"].get("labels")
        PROJECT_ID = self.app.config.get("pt", "PROJECT_ID")
        result = requests.get(
            f"{url}".format(PROJECT_ID=PROJECT_ID), headers=self.api_header()
        )
        results = result.json()
        data = []
        for item in results:
            data.append(
                [
                    str(item["id"]),
                    "[b blue]Label Name:[/]\n  " + item["name"],
                    "[b blue]Created At:[/]\n  " + item["created_at"],
                ]
            )
        rich_table("", [], data)

    @ex(
        help="list releases",
    )
    def releases(self):
        """
        Lists the releases in nice format
        """
        url = TRACKER_CONSTANTS["endpoints"].get("releases")
        PROJECT_ID = self.app.config.get("pt", "PROJECT_ID")
        result = requests.get(
            f"{url}".format(PROJECT_ID=PROJECT_ID), headers=self.api_header()
        )
        results = result.json()
        data = []
        for item in results:
            data.append(
                [
                    str(item["id"]),
                    "[b blue]Release Name:[/]\n  " + item["name"],
                    "[b blue]Description:[/]\n  " + item["description"],
                    "[b blue]Deadline:[/]\n  " + item["deadline"],
                ]
            )
        rich_table("", [], data)

    @ex(
        help="list epics",
    )
    def epics(self):
        """
        Lists the epics of the project
        """
        url = TRACKER_CONSTANTS["endpoints"].get("epics")
        PROJECT_ID = self.app.config.get("pt", "PROJECT_ID")
        result = requests.get(
            f"{url}".format(PROJECT_ID=PROJECT_ID), headers=self.api_header()
        )
        results = result.json()
        data = []
        for item in results:
            row = ["", "[b blue]Name: [/]\n  " + item["name"]]
            data.append(row)
        rich_table(
            "Epics",
            [],
            data,
        )

    @ex(help="create ticket", arguments=[])
    def create(self):
        """
        Creates the task interactively
        """
        text = Prompt.ask("Task title: ")
        description = Prompt.ask("Task description: ")
        options = ["feature", "bug", "chore", "release"]
        story_type = Prompt.ask("Story Type:", choices=options, default="feature")

        options = ["unstarted", "unscheduled", "started", "planned"]
        current_state = Prompt.ask("Task state: ", choices=options, default="unstarted")
        options = ["1", "2", "3", "5", "7"]
        estimate = Prompt.ask(
            "Task estimation points(1/5): ", choices=options, default="2"
        )
        labels = Prompt.ask("Add labels separated by comma: ").split(",")
        tasks = Prompt.ask("Add tasks separated by comma: ").split(",")
        labels_list = [{"name": item} for item in labels if item != '']
        tasks_list = [{"description": item} for item in tasks if item != '']
        my_id = self.app.config.get("pt", "PERSON_ID")
        data = {
            "name": text,
            "story_type": story_type,
            "description": description,
            "current_state": current_state,
            "estimate": int(estimate),
            "owned_by_id": my_id,
            "tasks": tasks_list,
            "labels": labels_list,
        }
        if story_type == "bug" or story_type == "chore":
            data.pop("estimate")
        url = TRACKER_CONSTANTS["endpoints"].get("stories")
        PROJECT_ID = self.app.config.get("pt", "PROJECT_ID")
        url = f"{url}".format(PROJECT_ID=PROJECT_ID)
        data = { k: v for k,v in data.items() if v is not None or v != ''  }
        result = requests.post(url, json=data, headers=self.api_header()).json()
        print(result)
        if result.get('kind', '') != 'error':
            story_type = result.get("story_type", "")
            selected_story_type, headers, stories = self.transform_values(
                story_type, [result]
            )
            headers += [{"name": "description", "disp_name": "Description", "width": "10"}]
            rich_show_table("Created", stories, [], [])

    def fetch_story(self, ticket):
        """
        Fetch story data from server - story, comments, details
        """
        url = TRACKER_CONSTANTS["endpoints"].get("stories")
        PROJECT_ID = self.app.config.get("pt", "PROJECT_ID")
        story_url = f"{url}/{ticket}".format(PROJECT_ID=PROJECT_ID)
        headers = self.api_header()
        result = requests.get(story_url, headers=headers)

        comments_url = f"{story_url}/comments"
        comments = requests.get(comments_url, headers=headers)

        blockers_url = f"{story_url}/blockers"
        blockers = requests.get(blockers_url, headers=headers)
        return result.json(), comments.json(), blockers.json()

    @ex(
        help="view ticket",
        arguments=[
            (["ticket_id"], {"help": "ticket id", "action": "store"}),
        ],
    )
    def show(self):
        """
        Displays ticket details in a nice panel
        """
        ticket = self.app.pargs.ticket_id
        story_details, comments, blockers = self.fetch_story(ticket)
        story_type = story_details.get("story_type", "")
        selected_story_type, headers, stories = self.transform_values(
            story_type, [story_details]
        )
        headers += [{"name": "description", "disp_name": "Description", "width": "10"}]
        rich_show_table("Showing Story Details", stories, comments, blockers)

    @ex(
        help="comment on ticket",
        arguments=[
            (["ticket_id"], {"help": "ticket id", "action": "store"}),
        ],
    )
    def comment(self):
        """
        Comments in a ticket
        """
        ticket = self.app.pargs.ticket_id
        url = TRACKER_CONSTANTS["endpoints"].get("stories")
        PROJECT_ID = self.app.config.get("pt", "PROJECT_ID")
        url = f"{url}/{ticket}".format(PROJECT_ID=PROJECT_ID)
        headers = self.api_header()
        url = f"{url}/comments"
        comment = Prompt.ask("Type Comment: ")
        response = requests.post(url, headers=headers, data={"text": comment})
        if response.ok:
            print("Done")
        else:
            print("Fuck!")

    @ex(
        help="update ticket",
        arguments=[
            (["ticket_id"], {"help": "ticket id", "action": "store"}),
        ],
    )
    def update(self):
        """
        Updates the ticket
        """
        ticket = self.app.pargs.ticket_id
        result, comments, blockers = self.fetch_story(ticket)

        text = Prompt.ask("Task title: ", default=result.get("name"))
        description = Prompt.ask(
            "Task description: ", default=result.get("description")
        )
        options = ["unstarted", "unscheduled", "started", "planned"]
        current_state = Prompt.ask(
            "Task state: ", choices=options, default=result.get("current_state")
        )
        options = ["1", "2", "3", "5", "7"]
        estimate = Prompt.ask(
            "Task estimation points(1/5): ",
            choices=options,
            default=result.get("estimate"),
        )
        data = {
            "name": text,
            "description": description,
            "current_state": current_state,
            "estimate": estimate,
        }
        if story_type == "bug" or story_type == "chore":
            data.pop("estimate")
        if Confirm.ask("You sure you want to update this task?"):
            url = TRACKER_CONSTANTS["endpoints"].get("stories")
            url += f"/{ticket}"
            PROJECT_ID = self.app.config.get("pt", "PROJECT_ID")
            url = f"{url}".format(PROJECT_ID=PROJECT_ID)
            print(url)
            result = requests.put(url, data=data, headers=self.api_header())
            preety_print(result.json())
            print("Done")
        else:
            print("ok")
