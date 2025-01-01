from app.base_repository import BaseRepository
from app.salary_repository import SalaryRepository
import app.real_estate_type_repository as estate_type_base_repo

class RealEstateRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.db = database
        self.table_name = "real_estate"
        self.columns = self.get_table_columns()
        self.type_repo = estate_type_base_repo.RealEstateTypeRepository(database)
        self.estate_tax_repo = RealEstateTaxesRepository(database)
        self.real_estate_rates_repo = estate_type_base_repo.RealEstateRatesRepository(database)
    
    def get_all_ids(self):
        query = f"SELECT {self.columns[0]} FROM {self.table_name}"
        return self.db.execute_query(query)
    
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
    
    def get_first_record_by_type_id(self, type_id):
        query = f"""
        SELECT id FROM {self.table_name}
        WHERE {self.columns[-1]} = ?
        LIMIT 1
        """
        result = self.db.execute_query(query, (type_id,))
        return result[0] if result else None
        
    def get_area_and_typeid_by_id(self, estate_id):
        query = f"""
        SELECT area, real_estate_type_id
        FROM {self.table_name}
        WHERE {self.columns[0]} = ?
        LIMIT 1"""
        result = self.db.execute_query(query, (estate_id,))
        return result[0] if result else None
    
    def calculate_tax(self, year, area:float, type_id):
        salary = SalaryRepository(self.db).get_record_by_id(year)
        if not salary:
            raise Exception("Неможливо розрахувати податок - немає інформації про зарпалату!")
        salary = int(salary[1])
        
        type_rate = self.real_estate_rates_repo.get_by_year_and_typeid(year, type_id)
        if type_rate is None:
            raise Exception("Неможливо розрахувати податок - немає інформації про ставку податку!")
        area_limit = float(type_rate[3])
        tax_percent = float(type_rate[4]) # %
        
        area_taxable = float(area) - area_limit
        area_taxable = area_taxable if area_taxable > 0 else 0.0
        
        tax_rate = tax_percent / 100
        tax = round(salary * tax_rate * area_taxable, 2)
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
        
    def update_record(self, estate_id, year, estate_name, address, 
        area, paid, owner_id, estate_type_name, notes):
        area = float(area)
        type_record = self.type_repo.get_by_name(estate_type_name)
        if type_record is None:
            raise Exception("Помилка. Не знайдено такий тип нерухомості!")
        type_id = type_record[0]
        super().update_record(estate_id, (estate_name, address, area, notes, owner_id, type_id))
        
        tax = self.calculate_tax(year, area, type_id)
        paid = 1 if paid == "Так" or tax == 0 else 0
        if self.estate_tax_repo.get_by_id_and_year(estate_id, year):
            self.estate_tax_repo.update_record(estate_id, year, (tax, paid))
        else:
            self.estate_tax_repo.add_record((estate_id, year, tax, paid))
    
    def update_all_tax(self, year):
        estate_results = self.get_all_ids()
        if not estate_results:
            return
        
        unique_exeptions = set()
        i=0
        for estate in estate_results:
            try:
                self.update_tax(estate[0], year)
            except Exception as e:
                unique_exeptions.add(str(e))
                i+=1
        
        if unique_exeptions:
            raise Exception(f"для ({i}) рядків. Перелік унікальних помилок:\n" + "\n".join(unique_exeptions))
    
    def update_tax(self, estate_id, year):
        estate_record = self.get_area_and_typeid_by_id(estate_id)
        if not estate_record:
            raise Exception("Помилка, такий запис не знайдено!")
        area, type_id = estate_record
        
        new_tax = self.calculate_tax(year, area, type_id)
        
        if self.estate_tax_repo.get_by_id_and_year(estate_id, year):
            self.estate_tax_repo.update_tax(estate_id, year, new_tax)
        else:
            paid=0
            self.estate_tax_repo.add_record((estate_id, year, new_tax, paid))

class RealEstateTaxesRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.table_name = "real_estate_taxes"
        self.columns = self.get_table_columns()
        
    def get_by_id_and_year(self, record_id, year):
        query = f"""
        SELECT * FROM {self.table_name}
        WHERE {self.columns[0]} = ? AND {self.columns[1]} = ?
        """
        result = self.db.execute_query(query, (record_id, year))
        return result[0] if result else None
    
    def add_record(self, values):
        """Додавання нового запису в таблицю."""
        query = f"""
        INSERT INTO {self.table_name} ({', '.join(self.columns)})
        VALUES ({', '.join(['?' for _ in values])})
        """
        return self.db.execute_non_query(query, values)
    
    def update_record(self, record_id, year, values):
        query = f"""
        UPDATE {self.table_name} 
        SET {', '.join([f"{column} = ?" for column in self.columns[2:]])}
        WHERE {self.columns[0]} = ? AND {self.columns[1]} = ?
        """
        self.db.execute_non_query(query, tuple(values) + (record_id, year))
    
    def update_tax(self, record_id, year, tax):
        query = f"""
        UPDATE {self.table_name} 
        SET {self.columns[2]} = ?
        WHERE {self.columns[0]} = ? AND {self.columns[1]} = ?
        """
        self.db.execute_non_query(query, (tax, record_id, year))
    