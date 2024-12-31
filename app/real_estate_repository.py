from app.base_repository import BaseRepository
from app.real_estate_type_repository import RealEstateTypeRepository
from app.salary_repository import SalaryRepository
from app.real_estate_type_repository import RealEstateRatesRepository

class RealEstateRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.table_name = "real_estate"
        self.columns = self.get_table_columns()
        self.type_repo = RealEstateTypeRepository(database)
        self.estate_tax_repo = RealEstateTaxesRepository(database)
        self.salary_repo = SalaryRepository(database)
        self.estate_type_rates_repo = RealEstateRatesRepository(database)
        
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
    
    def calculate_tax(self, year, area:float, type_id):
        salary = self.salary_repo.get_record_by_id(year)
        if not salary:
            raise Exception("Немає інформації про зарпалату!")
        salary = int(salary[1])
        
        record = self.estate_type_rates_repo.get_by_year_and_typeid(year, type_id)
        area_limit = float(record[3])
        tax_percent = float(record[4]) # %
        
        area_taxable = float(area) - area_limit
        area_taxable = area_taxable if area_taxable > 0 else 0.0
        
        tax_rate = tax_percent / 100
        tax = salary * tax_rate * area_taxable
        return tax
    
    def add_record(self, year, estate_name, address, 
        area, paid, owner_id, estate_type_name, notes):
        area = float(area)
        type_record = self.type_repo.get_by_name(estate_type_name)
        if type_record is None:
            raise Exception("Помилка. Не знайдено такий тип нерухомості!")
        type_id = type_record[0]
        new_estate_id = super().add_record((estate_name, address, area, notes, owner_id, type_id))
        
        tax = self.calculate_tax(year, area, type_id)
        paid = 1 if paid == "Так" or tax == 0 else 0
        self.estate_tax_repo.add_record((new_estate_id, year, tax, paid))

class RealEstateTaxesRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.table_name = "real_estate_taxes"
        self.columns = self.get_table_columns()
    
    def add_record(self, values):
        """Додавання нового запису в таблицю."""
        query = f"""
        INSERT INTO {self.table_name} ({', '.join(self.columns)})
        VALUES ({', '.join(['?' for _ in values])})
        """
        return self.db.execute_non_query(query, values)
    