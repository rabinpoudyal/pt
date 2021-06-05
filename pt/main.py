import os
# from dotenv import dotenv_values
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from cement.utils import fs
from .core.exc import PivotalTrackerError
from .controllers.base import Base
from .controllers.pivotal import Pivotal

# from pymongo import MongoClient

CONFIG = fs.join(os.path.dirname(__file__), "..", "config", "pt.yml")


# def load_variables(app):
#     app.log.info("Loading variables")
#     secrets = dotenv_values(fs.join(os.path.dirname(__file__), "..", "config", ".env"))
#     app.extend("secrets", secrets)

class PivotalTracker(App):
    """Pivotal Tracker primary application."""

    class Meta:
        label = "pt"

        config_files = [CONFIG]

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = ["yaml", "colorlog", "jinja2", "tabulate"]

        # configuration handler
        config_handler = "yaml"

        # configuration file suffix
        config_file_suffix = ".yml"

        # set the log handler
        log_handler = "colorlog"

        # set the output handler
        output_handler = "tabulate"

        # register handlers
        handlers = [
            Base,
            Pivotal,
        ]

        # hooks
        # hooks = [
        #     ("post_setup", load_variables),
        # ]


class PivotalTrackerTest(TestApp, PivotalTracker):
    """A sub-class of PivotalTracker that is better suited for testing."""

    class Meta:
        label = "pt"


def main():
    with PivotalTracker() as app:
        try:
            app.run()

        except AssertionError as e:
            print("AssertionError > %s" % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback

                traceback.print_exc()

        except PivotalTrackerError as e:
            print("PivotalTrackerError > %s" % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback

                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print("\n%s" % e)
            app.exit_code = 0


if __name__ == "__main__":
    main()
