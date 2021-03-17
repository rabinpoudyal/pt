
from time import strftime
from cement import Controller, ex

import requests

class Pivotal(Controller):
    class Meta:
        label = 'pivotal'
        extensions = ['tabulate']
        output_handler = 'tabulate'

    @ex(help='me in tracker')
    def me(self):
        api_token = self.app.config.get_dict().get('pt', {}).get('api_token', '')
        result = requests.get("https://www.pivotaltracker.com/services/v5/me", headers={'X-TrackerToken': api_token} ) 
        print(result.json())

    @ex(help='my team in tracker')
    def team(self):
        api_token = self.app.config.get_dict().get('pt', {}).get('api_token', '')
        result = requests.get("https://www.pivotaltracker.com/services/v5/my/people?project_id=1342442", headers={'X-TrackerToken': api_token} ) 
        print(result.json())

    @ex(help='notifications')
    def notifications(self):
        api_token = self.app.config.get_dict().get('pt', {}).get('api_token', '')
        results = requests.get('https://www.pivotaltracker.com/services/v5/my/notifications?envelope=true', headers={'X-TrackerToken': api_token} )
        results = results.json()
        headers = ['id', 'performer', 'message', 'notification_type', 'action', 'story']
        data = []
        for item in results['data']:
            record = []
            for k,v in item.items():
                if k in headers:
                    if k in ['performer', 'story']:
                        record.append(v['name'])
                    else:
                        record.append(v)
            data.append(record)
        self.app.render(data, headers=headers)

    @ex(help='mark notifications as read')
    def mark_all_read(self):
        api_token = self.app.config.get_dict().get('pt', {}).get('api_token', '')
        data = { 'before': 502932671 }
        result = requests.put("https://www.pivotaltracker.com/services/v5/my/notifications/mark_read", data=data, headers={'X-TrackerToken': api_token} ) 
        print(result.status_code)
    
    @ex(help='list stories')
    def list(self):
        headers = ['id', 'name', 'current_state']
        records = []
        api_token = self.app.config.get_dict().get('pt', {}).get('api_token', '')
        result = requests.get("https://www.pivotaltracker.com/services/v5/projects/1342442/stories?with_state=started&owner_ids=3299561", headers={'X-TrackerToken': api_token} ) 
        print(result.text)
        # for item in result.json():
        #     records.append([item['id'], item['name'], item['current_state'] ])
        # self.app.render(records, headers=headers)

    @ex(
        help='create ticket',
        arguments=[
            (['task_title'], {'help': 'create a ticket', 'action': 'store'}),
            (['task_description'], {'help': 'task description', 'action': 'store'}),
            (['current_state'], {'help': 'current state', 'action': 'store'}),
            (['estimate'], {'help': 'current state', 'action': 'store'})
        ]
    )
    def create(self):
        text = self.app.pargs.task_title
        description = self.app.pargs.task_description
        current_state = self.app.pargs.current_state
        estimate = self.app.pargs.estimate

        api_token = self.app.config.get_dict().get('pt', {}).get('api_token', '')
        data = { 'name': text, 'description': description, 'current_state': current_state, 'estimate': estimate }
        result = requests.post("https://www.pivotaltracker.com/services/v5/projects/1342442/stories", data=data, headers={'X-TrackerToken': api_token} ) 
        print(result.content)
        # payload = {'task': text}
        # self.app.db.insert(payload)


    @ex(help='deliver')
    def deliver(self):
        pass
