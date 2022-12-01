from typing import Any, Sized, Optional, List, Tuple, Union
from sqlalchemy.orm import Query
from sqlalchemy.exc import PendingRollbackError, IntegrityError
from bot import app


class Model:
    """Base class of all models containing collection of command to query records."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def query(cls) -> Query:
        """Return the model query object

        :usage
            Model.query()

         :raises
            PendingRollbackError, IntegrityError:
                In case an exception is thrown during the query, the system will roll back
        """

        try:
            return app.session.query(cls)
        except (PendingRollbackError, IntegrityError):
            app.session.rollback()
            raise

    @classmethod
    def get(cls, primary_key_identifier: int) -> Any:
        """Retrieve and returns the records with the given primary key identifier. None if none is found.

        :usage
            Model.get(5)

        :raises
            PendingRollbackError, IntegrityError:
                In case an exception is thrown during the query, the system will rollback
        """

        return cls.query().get(primary_key_identifier)

    @classmethod
    def get_by(cls, **kwargs: Any):
        """Retrieve and returns the record with the given keyword argument. None if none is found.

        Only one argument should be passed. If more than one argument are supplied,
        a TypeError will be thrown by the function.

        :usage
            Model.get_by(name="Dr.Strange")

        :raises
            PendingRollbackError, IntegrityError, TypeError:
                In case an exception is thrown during the query, the system will rollback
        """
        kwargs_count = len(kwargs)

        if kwargs_count > 1:
            raise TypeError(f"Only one argument is accepted ({kwargs_count} given)")

        return cls.where(**kwargs).first()

    @classmethod
    def all(cls) -> List:
        """Retrieve and returns all records of the model

        :usage
            Model.all()
        """

        return cls.query().all()

    @classmethod
    def first(cls, limit: int = 1) -> Query:
        """Retrieve N first records

        :usage
            Model.first()
            Model.first(limit=100)
        """

        if limit == 1:
            return cls.query().first()
        # noinspection PyUnresolvedReferences
        return cls.query().limit(limit).all()

    @classmethod
    def where(cls, **kwargs: Any) -> Query:
        """Retrieve and returns all records filtered by the given conditions

        :usage
            Model.where(name="some name", id=5)
        """

        return cls.query().filter_by(**kwargs)

    @classmethod
    def filter(cls, *criterion: Tuple[Any]) -> Query:
        """Shorter way to call the sqlalchemy query filter method

        :usage
            Model.filter(Model.id > 5)
        """

        return app.session.query(cls).filter(*criterion)

    @classmethod
    def count(cls) -> int:
        """Returns the number of records for the model

        :usage
            Model.count()
        """

        return cls.query().count()

    @classmethod
    def create(cls, auto_save: bool = True, **kwargs: Optional[Any]) -> Any:
        """Creates, saves and return a new instance of the model.

        :usage
            Model.create(name="A name", color="Blue")
        """
        model = cls(**kwargs)

        if auto_save:
            model.save()
        return model

    def save(self, commit: bool = True):
        """Saves the model. If commit is set to `True` it will "[f]lush pending changes and commit
        the current transaction.". For more information about `commit`, read sqlalchemy docs.

        :usage
            model.save()

        :raises
            PendingRollbackError, IntegrityError:
                In case an exception is thrown during the query, the system will rollback
        """

        try:
            app.session.add(self)

            if commit:
                app.session.commit()
        except (PendingRollbackError, IntegrityError):
            app.session.rollback()
            raise

    def delete(self, commit: bool = True):
        """Delete the model. If commit is set to `True` it will "flush pending changes and commit
        the current transaction.". For more information about `commit`, read sqlalchemy docs.

        :usage
            model.delete()

        :raises
            PendingRollbackError, IntegrityError:
                In case an exception is thrown during the query, the system will rollback
        """

        try:
            app.session.delete(self)

            if commit:
                app.session.commit()
        except (PendingRollbackError, IntegrityError):
            app.session.rollback()
            raise
