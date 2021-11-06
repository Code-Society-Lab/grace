from sqlalchemy.exc import PendingRollbackError, IntegrityError
from bot import app


class Model:
    """This class is the base class of all models.

    It basically defines class methods and methods to simplify using the models.
    """

    @classmethod
    def query(cls):
        """Return the model query object

        :usage
            Model.query()

        :raises
            PendingRollbackError, IntegrityError:
                In case an exception is thrown during the query, the system will rollback
        """

        try:
            return app.session.query(cls)
        except (PendingRollbackError, IntegrityError):
            app.session.rollback()
            raise

    @classmethod
    def get(cls, primary_key_identifier):
        """Retrieve and returns the records with the given primary key identifier

        :usage
            Model.get(5)

        :raises
            PendingRollbackError, IntegrityError:
                In case an exception is thrown during the query, the system will rollback
        """

        return cls.query().get(primary_key_identifier)

    @classmethod
    def all(cls):
        """Retrieve and returns all records of the model

        :usage
            Model.all()
        """

        return cls.query().all()

    @classmethod
    def where(cls, **kwargs):
        """Retrieve and returns all records filtered by the given conditions

        :usage
            Model.where(name="some name", id=5)
        """

        return cls.query().filter_by(**kwargs)

    @classmethod
    def count(cls):
        """Returns the number of records for the model

        Ex. ̀Model.count()`
        """

        return len(cls.all())

    def save(self, commit=True):
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

    def delete(self, commit=True):
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
