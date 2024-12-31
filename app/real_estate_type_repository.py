from app.base_repository import BaseRepository

class DeleteExeption(Exception):
    pass

class RealEstateTypeBaseRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.rates_repo = RealEstateRatesRepository(database)
        self.table_name_rates = self.rates_repo.table_name
        
        self.type_repo = RealEstateTypeRepository(database)
        self.table_name_type = self.type_repo.table_name
        
    def get_type_rates(self, year:int):
        query = f"""
        SELECT {self.table_name_rates}.id, {self.table_name_type}.name, {self.table_name_rates}.tax_rate, {self.table_name_rates}.tax_area_limit
        FROM {self.table_name_type}
        LEFT JOIN {self.table_name_rates}
        ON {self.table_name_type}.id = {self.table_name_rates}.real_estate_type_id
        AND {self.table_name_rates}.tax_year = {year}
        """
        result = self.db.execute_query(query)
        return result

    def add_record(self, tax_year, type_name, tax_rate, tax_area_limit):
        # Додати інформацію і тип нерухомості, якщо його не існує
        type_record = self.type_repo.get_by_name(type_name) # id, name
        if not type_record:
            self.type_repo.add_record((type_name,))
        
        type_record = self.type_repo.get_by_name(type_name) # id, name        
        rate_record = self.rates_repo.get_by_year_and_typeid(tax_year, type_record[0])
        if not rate_record:
            self.rates_repo.add_record((tax_year, type_record[0], tax_area_limit, tax_rate))
        else:
            raise Exception("Такий запис вже існує!")

    def update_record(self, id, tax_year, type_name, tax_rate, tax_area_limit):
        # Оновити інформацію для типу нерухомості
        if id == "None":
            self.add_record(tax_year, type_name, tax_rate, tax_area_limit)
            return
        
        type_id = self.rates_repo.get_typeid_by_id(id)
        if not type_id:
            raise Exception("Дивна помилка!")

        type_record = self.type_repo.get_by_name(type_name) # id, name
        if not type_record: # Якщо типу за іменем немає - значить потрібно оновити стару назву
            self.type_repo.update_record(type_id, (type_name,))
        
        self.rates_repo.update_record(id, (tax_year, type_id, tax_area_limit, tax_rate))

    def delete_record(self, id, type_name):
        # Видалити інформацію для типу нерухомості
        if id == "None":
            type_record = self.type_repo.get_by_name(type_name) # id, name
            if not type_record:
                raise Exception("Такого типу не існує.")
            type_id = type_record[0]
        else:
            type_id = self.rates_repo.get_typeid_by_id(id)
            self.rates_repo.delete_record(id)
        
        records = self.rates_repo.get_record_by_type_id(type_id)
        if not records: # якщо існують записи для цьго типу - видаляти  не можна
            self.type_repo.delete_record(type_id)
        else:
            raise DeleteExeption("Не можливо видалити тип нерухомості, оскільки він використовується в інших записах! Спершу видаліть всю інформацію зв'язану з цим типом.")
        
        
class RealEstateTypeRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.table_name = "real_estate_type"
        self.columns = self.get_table_columns()
    
    def get_by_name(self, name:str):
        '''return (id, name)'''
        query = f"SELECT * FROM {self.table_name} WHERE name = ?"
        result = self.db.execute_query(query, (name,))
        return result[0] if result else None


class RealEstateRatesRepository(BaseRepository):
    def __init__(self, database):
        super().__init__(database)
        self.table_name = "real_estate_type_rates"
        self.columns = self.get_table_columns()
        
    def get_by_year_and_typeid(self, year, type_id):
        query = f"SELECT * FROM {self.table_name} WHERE tax_year = ? AND real_estate_type_id = ?"
        result = self.db.execute_query(query, (year, type_id))
        return result[0] if result else None
    
    def get_typeid_by_id(self, id):
        query = f"SELECT real_estate_type_id FROM {self.table_name} WHERE id = ?"
        result = self.db.execute_query(query, (id,))
        return result[0][0] if result else None
    
    def get_record_by_type_id(self, id):
        query = f"SELECT * FROM {self.table_name} WHERE real_estate_type_id = ?"
        return self.db.execute_query(query, (id,))
