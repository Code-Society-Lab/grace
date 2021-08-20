from argparse import ArgumentParser
from logging import critical, warning, info
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError
from bot import app
from bot.__main__ import start
from bot.utils.models import load_models
from config.environments.environment import Environment
from db.seed import get_seeds

load_models()


def seed():
    warning("Seeding...")

    try:
        for seed_module in get_seeds():
            seed_module.seed_database()

            warning("Seeding completed successfully")
    except ProgrammingError as e:
        critical(f"Error: {e}")


def create():
    try:
        warning("Creating tables...")
        app.create_tables()

        warning("Tables created successfully.")
    except SQLAlchemyError as e:
        critical(f"Error: {e}")


def set_environment(environment):
    warning(f"setting up environment, {environment}")

    app.config.set_environment(environment)
    app.reload_database()


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('command', type=str, help="COMMAND [args]", choices=["start", "create", "seed"])
    parser.add_argument('-e', type=Environment, help="-e environment", choices=list(Environment))

    actions = {"create": create, "seed": seed, "start": start}

    args = parser.parse_args()
    command = actions.get(args.command)

    if args.e:
        set_environment(args.e)

    command()
