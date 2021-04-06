import requests

from time import strftime
from cement import Controller, ex

from .utils import preety_print
from .rich_uis import rich_table
from rich.prompt import Prompt, Confirm


class Pivotal(Controller):
    class Meta:
        label = "pivotal"
        extensions = ["tabulate"]
        output_handler = "tabulate"

    def api_header(self):
        self.app.log.info("Setting the tracker token")
        api_token = self.app.secrets.get("PIVOTAL_TRACKER_API_TOKEN")
        return {"X-TrackerToken": api_token}

    @ex(help="me in tracker")
    def me(self):
        from rich.console import Console

        console = Console()
        with console.status("[bold green]Working on tasks...") as status:
            url = self.app.config.get("pt", "endpoints").get("my_details")
            result = requests.get(url, headers=self.api_header())
            id = result.json()["id"]
            is_present_in_db = self.app.db.me.find_one({"id": id})
            if is_present_in_db is not None:
                self.app.db.me.update({"id": id}, result.json())
                self.app.log.info("Updated your tracker info to db..")
            else:
                self.app.db.me.insert(result.json())
                self.app.log.info("Added to db. Next time it will be synced only..")
            preety_print(result.json())

    @ex(help="my team in tracker")
    def team(self):
        api_token = self.app.config.get_dict().get("pt", {}).get("api_token", "")
        result = requests.get(
            "https://www.pivotaltracker.com/services/v5/my/people?project_id=1342442",
            headers={"X-TrackerToken": api_token},
        )
        print(result.json())

    @ex(help="notifications")
    def notifications(self):
        api_token = self.app.config.get_dict().get("pt", {}).get("api_token", "")
        results = requests.get(
            "https://www.pivotaltracker.com/services/v5/my/notifications?envelope=true",
            headers={"X-TrackerToken": api_token},
        )
        results = results.json()
        headers = ["id", "performer", "message", "notification_type", "action", "story"]
        data = []
        for item in results["data"]:
            record = []
            for k, v in item.items():
                if k in headers:
                    if k in ["performer", "story"]:
                        record.append(v["name"])
                    else:
                        record.append(v)
            data.append(record)
        self.app.render(data, headers=headers)

    @ex(help="mark notifications as read")
    def mark_all_read(self):
        api_token = self.app.config.get_dict().get("pt", {}).get("api_token", "")
        data = {"before": 502932671}
        result = requests.put(
            "https://www.pivotaltracker.com/services/v5/my/notifications/mark_read",
            data=data,
            headers={"X-TrackerToken": api_token},
        )
        print(result.status_code)

    @ex(
        help="list stories",
        arguments=[
            (["story_type"], {"help": "story type", "action": "store"}),
        ],
    )
    def list(self):
        story_type = self.app.pargs.story_type

        url = self.app.config.get("pt", "endpoints").get("stories")
        print(url)
        PROJECT_ID = self.app.secrets.get("PROJECT_ID")
        result = requests.get(f'{url}'.format(PROJECT_ID=PROJECT_ID), headers=self.api_header())
        results = result.json()['stories']['stories']
        
        base_headers = [
            {"name": "id", "disp_name": "ID", "width": "10"},
            {"name": "name", "disp_name": "Name", "width": "85"},
            {"name": "url", "disp_name": "Link", "width": "5"},
        ]

        if story_type in ['f', 'feature', 'features']:
            selected_story_type = 'feature'
            headers = base_headers + [
                #{"name": "estimate", "disp_name": "Est.", "width": "5"},
                {"name": "current_state", "disp_name": "State", "width": "10"},
            ]
            stories = [item for item in results if item.get("story_type") == "feature"]
        elif story_type in ['c', 'chore', 'chores']:
            selected_story_type = 'chore'
            headers = base_headers + [
                {"name": "requested_by_id", "disp_name": "Requester.", "width": "5"},
                {"name": "current_state", "disp_name": "State", "width": "10"},
            ]
            stories = [item for item in results if item.get("story_type") == "chore"]
        elif story_type in ['b', 'bug', 'bugs']:
            selected_story_type = 'bug'
            headers = base_headers + [
                {"name": "requested_by_id", "disp_name": "Requester", "width": "5"},
                {"name": "current_state", "disp_name": "State", "width": "10"},
            ]
            stories = [item for item in results if item.get("story_type") == "bug"]
        else:
            print('Only: f/c/b')
            return 1

        for table in [stories]:
            data = []
            for item in table:
                record = []
                for key in headers:
                    if key["name"] == "url":
                        link = f"[link={item[key['name']]}]🔗[/link]"
                        record.append(link)
                    else:
                        record.append(item[key["name"]])
                data.append(record)
            rich_table(
                selected_story_type.capitalize() + " Tickets",
                headers,
                data,
            )

    @ex(help="create ticket", arguments=[])
    def create(self):
        text = Prompt.ask("Task title: ")
        description = Prompt.ask("Task description: ")
        options = ["unstarted", "unscheduled", "started", "planned"]
        current_state = Prompt.ask("Task state: ", choices=options, default="unstarted")
        options = ["1", "2", "3", "5", "7"]
        estimate = Prompt.ask("Task estimation points(1/5): ", choices=options)

        data = {
            "name": text,
            "description": description,
            "current_state": current_state,
            "estimate": estimate,
        }
        if enquiries.confirm("You sure create task?"):
            url = self.app.config.get("pt", "endpoints").get("stories")
            result = requests.post(url, data=data, headers=self.api_header())
            preety_print(result.json())
        else:
            print("ok")

    def fetch_story(self, ticket):
        url = self.app.config.get("pt", "endpoints").get("stories")
        url += f"/{ticket}"
        result = requests.get(url, headers=self.api_header())
        return result.json()

    @ex(
        help="view ticket",
        arguments=[
            (["ticket_id"], {"help": "ticket id", "action": "store"}),
        ],
    )
    def show(self):
        ticket = self.app.pargs.ticket_id
        result = self.fetch_story(ticket)
        preety_print(result)

    @ex(
        help="update ticket",
        arguments=[
            (["ticket_id"], {"help": "ticket id", "action": "store"}),
        ],
    )
    def update(self):
        ticket = self.app.pargs.ticket_id
        result = self.fetch_story(ticket)

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
        if Confirm.ask("You sure you want to update this task?"):
            url = self.app.config.get("pt", "endpoints").get("stories")
            url += f"/{ticket}"
            result = requests.put(url, data=data, headers=self.api_header())
            preety_print(result.json())
        else:
            print("ok")

    @ex(help="deliver")
    def deliver(self):
        pass
