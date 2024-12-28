from app.base_repository import BaseRepository

class RealEstateTaxesRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.table_name = "real_estate_taxes"
        self.columns = self.get_table_columns()