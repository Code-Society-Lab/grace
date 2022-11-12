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
        for seed_module in get_seeds():
            try:
                info(f"Seeding {seed_module.__name__}")
                seed_module.seed_database()
            except IntegrityError as e:
                warning(f"Error: {e}, Skipping")
                pass

        info("Seeding completed successfully")
    except ProgrammingError as e:
        critical(f"Critical Error: {e}")


def create_all():
    if not app.database_exists:
        info(f"Creating all...")

        try:
            app.create_database()
            app.create_tables()

            info("Database created successfully!")
        except SQLAlchemyError as e:
            critical(f"Critical Error: {e}")
    else:
        warning("Database already exists")


def drop_all():
    if app.database_exists:
        warning("Dropping all...")

        try:
            app.drop_tables()
            app.drop_database()

            info("Database dropped successfully!")
        except SQLAlchemyError as e:
            critical(f"Critical Error: {e}")
    else:
        warning("Database doesn't exists")


def reset():
    warning("Resetting the database")

    drop_all()
    create_all()
    seed_tables()
