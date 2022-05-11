"""Database commands

This module contains the additional database commands for the `grace` script.
"""

from logging import warning, critical, info, error
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError, IntegrityError
from bot import app
from db.seed import get_seeds


def seed_tables():
    info("Seeding tables...")

    try:
        try:
            for seed_module in get_seeds():
                info(f"Seeding {seed_module.__name__}")
                seed_module.seed_database()
        except IntegrityError as e:
            error(f"Error: {e}, Skipping")

        info("Seeding completed successfully")
    except ProgrammingError as e:
        critical(f"Critical Error: {e}")


def create_all():
    info(f"Creating all...")

    try:
        app.create_database()
        app.create_tables()

        info("Database created successfully!")
    except SQLAlchemyError as e:
        critical(f"Critical Error: {e}")


def drop_all():
    warning("Dropping all...")

    try:
        app.drop_tables()
        app.drop_database()

        info("Database dropped successfully!")
    except SQLAlchemyError as e:
        critical(f"Critical Error: {e}")

