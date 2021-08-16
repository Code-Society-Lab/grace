from bot import app


class Model:
    @classmethod
    def get(cls, model_id):
        return app.session.query(cls).get(model_id)

    def save(self, commit=True):
        app.session.add(self)

        if commit:
            app.session.commit()

    def delete(self, commit=True):
        app.session.delete(self)

        if commit:
            app.session.commit()
