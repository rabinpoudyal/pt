# It uses an pivotal tracker api and does lot of cool stuffs like creating tickets.

## Installing the app
```python
pip install pt-cli
```

## Add config file
You can find the token and ids in the tracker dashboard. For PERSON_ID, you might need to inspect json in network tab.
Create a file `~/.pt.yml` and add the following content.

```yml
pt:
  PIVOTAL_TRACKER_API_TOKEN: <token>
  PROJECT_ID: <id>
  PERSON_ID: <id>
```

### About you
![pt-cli index](./images/me.png)


### Create stories
![pt-cli index](./images/create.png)

### Index view / view all stories
![pt-cli index](./images/index.png)

### Show individual story
![pt-cli index](./images/show.png)

### Add Comment
![pt-cli index](./images/comment.png)


### Labels
![pt-cli index](./images/labels.png)

### Notifications
![pt-cli index](./images/notifications.png)

# Contributing

## Installation

```
$ pip install setup.py
```

## Development

This project includes a number of helpers in the `Makefile` to streamline common development tasks.

### Environment Setup

The following demonstrates setting up and working with a development environment:

```
### create a virtualenv for development

$ make virtualenv

$ source env/bin/activate


### run pt cli application

$ pt --help


### run pytest / coverage

$ make test
```

