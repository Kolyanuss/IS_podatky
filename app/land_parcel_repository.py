from app.base_repository import BaseRepository
import app.land_parcel_type_repository as land_type_base_repo

class LandParcelRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.db = database
        self.table_name = "land_parcel"
        self.columns = self.get_table_columns()
        self.land_type_repo = land_type_base_repo.LandParcelTypeRepository(database)
        self.land_tax_repo = LandParcelTaxesRepository(database)
        self.land_parcel_rates_repo = land_type_base_repo.LandParcelRatesRepository(database)
        self.normative_monetary_value_repo = NormativeMonetaryValuesRepository(database)
        
    def get_all_ids(self):
        query = f"SELECT {self.columns[0]} FROM {self.table_name}"
        return self.db.execute_query(query)
    
    def get_all_record_by_year(self, year):
        query = """
        SELECT 
            land_parcel.id, 
            users.id AS user_id,
            land_parcel.address, 
            land_parcel.area,
            CASE 
                WHEN land_parcel.privileged = 1 THEN 'Так'
                WHEN land_parcel.privileged = 0 THEN 'Ні'
                ELSE ''
            END AS privileged,
            COALESCE(normative_monetary_values.value,''),
            COALESCE(land_parcel_taxes.tax,''),
            CASE 
                WHEN land_parcel_taxes.paid = 1 THEN 'Так'
                WHEN land_parcel_taxes.paid = 0 THEN 'Ні'
                ELSE ''
            END AS paid,
            users.last_name || ' ' || users.name || ' ' || users.middle_name AS fullname,
            land_parcel_type.name || ' (' || COALESCE(land_parcel_type_rates.tax_rate,' _') || '%)' AS type_name,
            COALESCE(land_parcel.notes,'')
        FROM land_parcel
        INNER JOIN land_parcel_type 
            ON land_parcel.land_parcel_type_id = land_parcel_type.id
        INNER JOIN users 
            ON land_parcel.user_id = users.id
        LEFT JOIN normative_monetary_values 
            ON land_parcel.id = normative_monetary_values.land_id
            AND normative_monetary_values.year = ?
        LEFT JOIN land_parcel_taxes 
            ON land_parcel_taxes.land_parcel_id = land_parcel.id
            AND land_parcel_taxes.tax_year = ?
        LEFT JOIN land_parcel_type_rates 
            ON land_parcel_type_rates.land_parcel_type_id = land_parcel.land_parcel_type_id
            AND land_parcel_type_rates.tax_year = ?
        """
        return self.db.execute_query(query, (year,year,year))
    
    def get_first_record_by_type_id(self, type_id):
        query = f"""
        SELECT id FROM {self.table_name}
        WHERE {self.columns[2]} = ?
        LIMIT 1
        """
        result = self.db.execute_query(query, (type_id,))
        return result[0] if result else None
        
    def get_area_typeid_privileged_by_id(self, land_id):
        query = f"""
        SELECT area, land_parcel_type_id, privileged
        FROM {self.table_name}
        WHERE {self.columns[0]} = ?
        LIMIT 1"""
        result = self.db.execute_query(query, (land_id,))
        return result[0] if result else None
    
    def calculate_tax(self, year, area:float, type_id, normative_monetary_value:float):
        type_rate = self.land_parcel_rates_repo.get_by_year_and_typeid(year, type_id)
        if type_rate is None:
            raise Exception("Неможливо розрахувати податок - немає інформації про ставку податку!")
        tax_percent = float(type_rate[3]) # %
        
        tax_rate = tax_percent / 100
        tax = round(normative_monetary_value * tax_rate * area, 2)
        return tax
    
    def add_record(self, year, address, area, privileged, 
            normative_monetary_value, paid, owner_id, land_type_name, notes):
        area = float(area)
        normative_monetary_value = float(normative_monetary_value)
        type_record = self.land_type_repo.get_by_name(land_type_name)
        if type_record is None:
            raise Exception("Помилка. Не знайдено такий тип нерухомості!")
        type_id = type_record[0]
        privileged = 1 if privileged == "Так" else 0
        new_land_id = super().add_record((owner_id, type_id, address, area, privileged, notes))
        
        self.normative_monetary_value_repo.add_record((new_land_id, year, normative_monetary_value))
        
        tax = self.calculate_tax(year, area, type_id, normative_monetary_value) if privileged == 0 else 0
        paid = 1 if paid == "Так" or tax == 0 else 0
        self.land_tax_repo.add_record((new_land_id, year, tax, paid))
        
    def update_record(self, land_id, year, address, area, privileged, 
            normative_monetary_value, paid, owner_id, land_type_name, notes):
        area = float(area)
        normative_monetary_value = float(normative_monetary_value)
        type_record = self.land_type_repo.get_by_name(land_type_name)
        if type_record is None:
            raise Exception("Помилка. Не знайдено такий тип нерухомості!")
        type_id = type_record[0]
        privileged = 1 if privileged == "Так" else 0
        super().update_record(land_id, (owner_id, type_id, address, area, privileged, notes))
        
        # update\add NMV
        if self.normative_monetary_value_repo.get_by_id_and_year(land_id, year):
            self.normative_monetary_value_repo.update_record(land_id, year, normative_monetary_value)
        else:
            self.normative_monetary_value_repo.add_record((land_id, year, normative_monetary_value))
        
        # update\add tax
        tax = self.calculate_tax(year, area, type_id, normative_monetary_value) if privileged == 0 else 0
        paid = 1 if paid == "Так" or tax == 0 else 0
        if self.land_tax_repo.get_by_id_and_year(land_id, year):
            self.land_tax_repo.update_record(land_id, year, (tax, paid))
        else:
            self.land_tax_repo.add_record((land_id, year, tax, paid))
    
    def update_all_tax(self, year):
        land_results = self.get_all_ids()
        if not land_results:
            return
        
        unique_exeptions = set()
        i=0
        for land in land_results:
            try:
                self.update_tax(land[0], year)
            except Exception as e:
                unique_exeptions.add(str(e))
                i+=1
        
        if unique_exeptions:
            raise Exception(f"для ({i}) рядків. Перелік унікальних помилок:\n" + "\n".join(unique_exeptions))
    
    def update_tax(self, land_id, year):
        land_record = self.get_area_typeid_privileged_by_id(land_id)
        if not land_record:
            raise Exception("Помилка, такий запис не знайдено!")
        area, type_id, privileged = land_record
        
        normative_monetary_value = self.normative_monetary_value_repo.get_by_id_and_year(land_id, year)
        if not normative_monetary_value:
            raise Exception("Неможливо розрахувати податок - немає інформації нормативно грошову оцінку!")
        normative_monetary_value = int(normative_monetary_value[2])
        
        new_tax = self.calculate_tax(year, area, type_id, normative_monetary_value) if privileged == 0 else 0
        
        if self.land_tax_repo.get_by_id_and_year(land_id, year):
            self.land_tax_repo.update_tax(land_id, year, new_tax)
        else:
            paid=0
            self.land_tax_repo.add_record((land_id, year, new_tax, paid))


class NormativeMonetaryValuesRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.db = database
        self.table_name = "normative_monetary_values"
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
    
    def update_record(self, record_id, year, value):
        query = f"""
        UPDATE {self.table_name} 
        SET {self.columns[-1]} = ?
        WHERE {self.columns[0]} = ? AND {self.columns[1]} = ?
        """
        self.db.execute_non_query(query, (value, record_id, year))

class LandParcelTaxesRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.table_name = "land_parcel_taxes"
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
    