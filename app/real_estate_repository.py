from app.base_repository import BaseRepository
from app.real_estate_type_repository import RealEstateTypeRepository

class RealEstateRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.table_name = "real_estate"
        self.columns = self.get_table_columns()
        self.type_repo = RealEstateTypeRepository(database)
        
    def get_all_record_by_year(self, year):
        query = """
        SELECT 
            real_estate.id, 
            users.id AS user_id,
            real_estate.name, 
            real_estate.address, 
            real_estate.area, 
            COALESCE(real_estate_type_rates.tax_area_limit,''),
            COALESCE(real_estate_taxes.tax,''),
            COALESCE(real_estate_taxes.paid,''),
            users.last_name || ' ' || users.name || ' ' || users.middle_name AS fullname,
            real_estate_type.name || ' (' || COALESCE(real_estate_type_rates.tax_rate,' _') || '%)' AS type_name,
            COALESCE(real_estate.notes,'')
        FROM real_estate
        INNER JOIN real_estate_type 
            ON real_estate.real_estate_type_id = real_estate_type.id
        INNER JOIN users 
            ON real_estate.user_id = users.id
        LEFT JOIN real_estate_taxes 
            ON real_estate_taxes.real_estate_id = real_estate.id
            AND real_estate_taxes.tax_year = ?
        LEFT JOIN real_estate_type_rates 
            ON real_estate_type_rates.real_estate_type_id = real_estate.real_estate_type_id
            AND real_estate_type_rates.tax_year = ?
        """
        return self.db.execute_query(query, (year,year))
    
    def add_record(self, year, estate_name, address, 
        area, paid, owner_id, estate_type_name, notes):
        type_record = self.type_repo.get_by_name(estate_type_name)
        if type_record is None:
            raise Exception("Помилка. Не знайдено такий тип нерухомості!")
        
        super().add_record((estate_name, address, area, notes, owner_id, type_record[0]))
        
        # calc tax
        # insert tax info
        

class RealEstateTaxesRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.table_name = "real_estate_taxes"
        self.columns = self.get_table_columns()