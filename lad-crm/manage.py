import click
import sys

from flask.cli import FlaskGroup
from pathlib import Path

from lad_crm.app import init_app

TEST_PATH = Path(__file__).parent.joinpath("tests").absolute()


def init_click_app(info):
    app = init_app()

    @app.cli.command()
    def run_tests():
        """
        Runs the tests case with pytest
        """
        import pytest

        ret = pytest.main(["-vv", "-s", str(TEST_PATH)])
        sys.exit(ret)

    return app


@click.group(cls=FlaskGroup, create_app=init_click_app)
def cli():
    """
    An Entry point for command line handling.
    """
    pass


if __name__ == "__main__":
    cli()
