from app.base_repository import BaseRepository

class RealEstateRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.table_name = "real_estate"
        self.columns = self.get_table_columns()
        
    