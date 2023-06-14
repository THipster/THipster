from thipster.engine import THipsterException


class ModelNotFoundError(THipsterException):
    def __init__(self, model: str, *args) -> None:
        super().__init__(*args)
        self.model = model

    @property
    def message(self):
        return f'Couldn\'t find {self.model} model'
