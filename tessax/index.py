from pydantic import BaseModel


class Index(BaseModel):
    """
    Supported file formats:
        HTML
        ...

    """

    def create_index(self):
        pass

    def load_data(self):
        pass

    def _as_query(self):
        pass
