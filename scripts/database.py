from logging import warning, critical
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from bot import app
from utils.models import load_models
from db.seed import get_seeds


def seed_tables():
    warning("Seeding tables...")

    try:
        load_models()

        for seed_module in get_seeds():
            seed_module.seed_database()

            warning("Seeding completed successfully")
    except ProgrammingError as e:
        critical(f"Error: {e}")


def create_all():
    warning("Creating all...")

    try:
        load_models()

        app.create_database()
        app.create_tables()

        warning("Database created successfully!")
    except SQLAlchemyError as e:
        critical(f"Error: {e}")


def delete_all():
    warning("Deleting all...")

    try:
        load_models()

        app.drop_tables()
        app.drop_database()

        warning("Database deleted successfully!")
    except SQLAlchemyError as e:
        critical(f"Error: {e}")

