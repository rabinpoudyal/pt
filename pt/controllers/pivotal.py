import requests

from time import strftime
from cement import Controller, ex

from .utils import preety_print
from .rich_uis import rich_table, rich_show_table
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

    def generate_headers_and_data(self, story_type, results):
        base_headers = [
            {"name": "id", "disp_name": "ID", "width": "10"},
            {"name": "name", "disp_name": "Name", "width": "85"},
            {"name": "url", "disp_name": "Link", "width": "5"},
        ]

        if story_type in ['f', 'feature', 'features']:
            selected_story_type = 'feature'
            headers = base_headers + [
                {"name": "estimate", "disp_name": "Est.", "width": "5"},
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
            selected_story_type = ''
            stories, headers = [], []
        stories_order = ['unscheduled', 'unstarted', 'planned', 'started' ,'finished', 'delivered']
        s = []
        for item in stories_order:
            result = filter(lambda x: x['current_state'] == item, stories)
            s += result

        stories = reversed(s)
        return stories, headers, selected_story_type


    def generate_index_table(self, story_type, results):
        ''' Index table '''
        stories, headers, selected_story_type = self.generate_headers_and_data(story_type, results)
        for table in [stories]:
            data = []
            for item in table:
                record = []
                for key in headers:
                    if key["name"] == "url":
                        link = f"[link={item[key['name']]}]🔗[/link]"
                        record.append(link)
                    elif key["name"] == "current_state":
                        state = item[key['name']]
                        if state == 'started':
                            s = '[b orchid not dim]Started[/]'
                            record[1] = f'🔥 [b orchid not dim]{record[1]}[/]'
                        elif state == 'finished':
                            s = '[b yellow not dim]Finished[/]'
                            record[1] = f'👍 [b yellow not dim]{record[1]}[/]'
                        elif state == 'delivered':
                            s = '[b green not dim]Delivered[/]'
                            record[1] = f'✅ [b green not dim]{record[1]}[/]'
                        elif state == 'planned':
                            s = '[b tan not dim]Planned[/]'
                            record[1] = f'📅 [b tan not dim]{record[1]}[/]'
                        elif state == 'unscheduled':
                            s = '[b black not dim]Unscheduled[/]'
                            record[1] = f'❌ [b black not dim]{record[1]}[/]'
                        elif state == 'unstarted':
                            s = '[b dim]Unstarted[/]'
                            record[1] = f'🚧 [b dim]{record[1]}[/]'
                        else:
                            s = '⭕'
                        record.append(s)
                    else:
                        record.append(item.get(key["name"], '-' ) )
                data.append(record)
            return selected_story_type, headers, data

    def generate_table(self, story_type, results):
        selected_story_type, headers, data = self.generate_index_table(story_type, results)
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
        story_type = self.app.pargs.story_type

        url = self.app.config.get("pt", "endpoints").get("stories_search")
        PROJECT_ID = self.app.secrets.get("PROJECT_ID")
        result = requests.get(f'{url}'.format(PROJECT_ID=PROJECT_ID), headers=self.api_header())
        results = result.json()['stories']['stories']
        self.generate_table(story_type, results)

    @ex(
        help="list labels",
    )
    def labels(self):
        url = self.app.config.get("pt", "endpoints").get("labels")
        PROJECT_ID = self.app.secrets.get("PROJECT_ID")
        result = requests.get(f'{url}'.format(PROJECT_ID=PROJECT_ID), headers=self.api_header())
        results = result.json()
        preety_print(results)

    @ex(
        help="list releases",
    )
    def releases(self):
        url = self.app.config.get("pt", "endpoints").get("releases")
        PROJECT_ID = self.app.secrets.get("PROJECT_ID")
        result = requests.get(f'{url}'.format(PROJECT_ID=PROJECT_ID), headers=self.api_header())
        results = result.json()
        preety_print(results)

    @ex(
        help="list epics",
    )
    def epics(self):
        url = self.app.config.get("pt", "endpoints").get("epics")
        PROJECT_ID = self.app.secrets.get("PROJECT_ID")
        result = requests.get(f'{url}'.format(PROJECT_ID=PROJECT_ID), headers=self.api_header())
        results = result.json()
        headers = [
            {"name": "name", "disp_name": "Name", "width": "50"},
            {"name": "label", "disp_name": "Label", "width": "30"},
        ]
        data = []
        for item in results:
            record = []
            for h in headers:
                if h['name'] == "label":
                    label = item.get(h['name'], {})['name']
                    record.append(label)
                else:
                    record.append(item.get(h['name'], ''))
            data.append(record)
        rich_table(
            "Epics",
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
        PROJECT_ID = self.app.secrets.get("PROJECT_ID")
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
        ticket = self.app.pargs.ticket_id
        story_details, comments, blockers = self.fetch_story(ticket)
        story_type = story_details.get('story_type', '')
        stories, headers, selected_story_type = self.generate_headers_and_data(story_type, [story_details])
        headers += [
            {"name": "description", "disp_name": "Description", "width": "10"}
        ]
        rich_show_table('Showing Story Details', headers, stories, comments, blockers)

    @ex(
        help="comment on ticket",
        arguments=[
            (["ticket_id"], {"help": "ticket id", "action": "store"}),
        ],
    )
    def comment(self):
        ticket = self.app.pargs.ticket_id
        url = self.app.config.get("pt", "endpoints").get("stories")
        PROJECT_ID = self.app.secrets.get("PROJECT_ID")
        url = f"{url}/{ticket}".format(PROJECT_ID=PROJECT_ID)
        headers = self.api_header()
        url = f"{url}/comments"
        comment = Prompt.ask("Type Comment: ")
        response = requests.post(url, headers=headers, data={'text': comment})
        if response.ok:
            print('Done')
        else:
            print('Fuck!')

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
