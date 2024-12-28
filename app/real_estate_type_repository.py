from app.base_repository import BaseRepository

class RealEstateTypeRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.table_name = "real_estate_type_rates"
        self.table_name2 = "real_estate_type"
        self.columns = self.get_table_columns()
        
    def get_type_rates(self):
        query = f"""
        SELECT * FROM {self.table_name}, {self.table_name2}
        WHERE {self.table_name}.real_estate_type_id = {self.table_name2}.id
        """
        result = self.db.execute_query(query)
        return result