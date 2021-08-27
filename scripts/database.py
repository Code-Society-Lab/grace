"""Database commands

This module contains the additional database commands for the `grace` script.
"""

from logging import warning, critical, info, error
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError, IntegrityError
from bot import app
from utils.models import load_models
from db.seed import get_seeds

load_models()


def seed_tables():
    warning("Seeding tables...")

    try:
        try:
            for seed_module in get_seeds():
                info(f"Seeding {seed_module.__name__}")
                seed_module.seed_database()
        except IntegrityError as e:
            error(f"Error: {e}, Skipping")

        warning("Seeding completed successfully")
    except ProgrammingError as e:
        critical(f"Critical Error: {e}")


def create_all():
    warning(f"Creating all...")

    try:
        app.create_database()
        app.create_tables()

        warning("Database created successfully!")
    except SQLAlchemyError as e:
        critical(f"Critical Error: {e}")


def delete_all():
    warning("Deleting all...")

    try:
        app.drop_tables()
        app.drop_database()

        warning("Database deleted successfully!")
    except SQLAlchemyError as e:
        critical(f"Critical Error: {e}")

