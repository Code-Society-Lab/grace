from bot import app


class Model:
    @classmethod
    def query(cls):
        return app.session.query(cls)

    @classmethod
    def get(cls, model_id):
        return app.session.query(cls).get(model_id)

    @classmethod
    def all(cls):
        return app.session.query(cls).all()

    @classmethod
    def where(cls, *args, **kwargs):
        return app.session.query(cls).filter_by(**kwargs)

    def save(self, commit=True):
        app.session.add(self)

        if commit:
            app.session.commit()

    def delete(self, commit=True):
        app.session.delete(self)

        if commit:
            app.session.commit()
