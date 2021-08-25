from bot import app


class Model:
    """This class is the base class of all models.

    It basically defines class methods and methods to simplify using the models.
    """

    @classmethod
    def query(cls):
        """Return the model query object

        Ex. ̀Model.query()`
        """

        return app.session.query(cls)

    @classmethod
    def get(cls, primary_key_identifier):
        """Retrieve and returns the records with the given primary key identifier

        Ex. ̀Model.get(5)`
        """

        return cls.query().get(primary_key_identifier)

    @classmethod
    def all(cls):
        """Retrieve and returns all records

        Ex. ̀Model.all()`
        """

        return cls.query().all()

    @classmethod
    def where(cls, **kwargs):
        """Retrieve and returns all records filtered by the given conditions

        Ex. ̀Model.where(name="some name", id=5)`
        """

        return cls.query().filter_by(**kwargs)

    @classmethod
    def count(cls):
        """Returns the number of records

        Ex. ̀Model.count()`
        """

        return len(cls.all())

    def save(self, commit=True):
        """Saves the model. If commit is set to `True` it will "[f]lush pending changes and commit
        the current transaction.". For more information about `commit`, read sqlalchemy docs.

        Ex. `model.save()`
        """

        app.session.add(self)

        if commit:
            app.session.commit()

    def delete(self, commit=True):
        """Delete the model. If commit is set to `True` it will "flush pending changes and commit
        the current transaction.". For more information about `commit`, read sqlalchemy docs.

        Ex. `model.delete()`
        """

        app.session.delete(self)

        if commit:
            app.session.commit()
