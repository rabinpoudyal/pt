APPS = {
    "pt": {
        "name": "Pivotal Tracker App",
        "endpoints": {    
            "my_details": "https://www.pivotaltracker.com/services/v5/me",
            "notifications": "https://www.pivotaltracker.com/services/v5/my/notifications?envelope=true",
            "teams": "https://www.pivotaltracker.com/services/v5/my/people?project_id={PROJECT_ID}",
            "mark_read": "https://www.pivotaltracker.com/services/v5/my/notifications/mark_read",
            "stories": "https://www.pivotaltracker.com/services/v5/projects/{PROJECT_ID}/stories",
            "labels": "https://www.pivotaltracker.com/services/v5/projects/{PROJECT_ID}/labels",
            "releases": "https://www.pivotaltracker.com/services/v5/projects/{PROJECT_ID}/releases",
            "epics": "https://www.pivotaltracker.com/services/v5/projects/{PROJECT_ID}/search?&fields=:default&query=mywork%3A%22RP%22",
            "stories_search": "https://www.pivotaltracker.com/services/v5/projects/{PROJECT_ID}/search?&fields=:default&query=mywork%3A%22RP%22"
        }
    }
}

TRACKER_CONSTANTS = APPS["pt"]