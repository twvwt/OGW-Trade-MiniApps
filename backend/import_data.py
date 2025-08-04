<<<<<<< HEAD
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import os
from pathlib import Path

def clean_data(value):
    """Очистка данных от лишних пробелов и преобразование пустых строк в None"""
    if isinstance(value, str):
        value = value.strip()
        return None if value == '' else value
    return value

def main():
    # Подключение к MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("DB_NAME", "OGW")
    
    client = MongoClient(mongo_uri)
    db = client[db_name]

    # Путь к файлу
    file_path = Path("uploads/price.xlsx")

    # Словарь для перевода названий колонок
    column_translation = {
        'Подкатегория': 'subcategory',
        'Наименование товара': 'product_name',
        'Цвет': 'color',
        'Обьем памяти': 'storage',
        'Страна': 'country',
        'Краткое описание': 'short_description',
        'Характеристики': 'specifications',
        'Цена': 'price',
        'Конфигурация': 'configuration',
        'Фото1': 'photo1',
        'Фото2': 'photo2',
        'Фото3': 'photo3'
    }

    # Получаем коллекцию products
    collection = db['products']

    try:
        # Чтение Excel файла
        xls = pd.ExcelFile(file_path)

        # Очищаем коллекцию перед добавлением новых данных
        collection.delete_many({})

        total_products = 0

        # Обработка каждого листа
        for sheet_name in xls.sheet_names:
            # Пропускаем пустые листы
            if sheet_name.lower() in ['other', 'лист1', 'sheet1']:
                continue
                
            # Чтение данных листа
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # Переименование колонок
            df.rename(columns=column_translation, inplace=True)
            
            # Очистка данных
            for col in df.columns:
                df[col] = df[col].apply(clean_data)
            
            # Добавляем поле category с именем листа
            df['category'] = sheet_name.strip()
            
            # Добавляем дату создания
            df['created_at'] = datetime.now()
            
            # Преобразование в список словарей
            data = df.to_dict('records')
            
            # Вставляем данные в коллекцию
            if data:
                result = collection.insert_many(data)
                inserted_count = len(result.inserted_ids)
                total_products += inserted_count
                print(f"Из листа {sheet_name} добавлено {inserted_count} товаров")

        print(f"Всего добавлено {total_products} товаров в коллекцию products")
        return True

    except Exception as e:
        print(f"Ошибка при импорте данных: {str(e)}")
        return False
    finally:
=======
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import os
from pathlib import Path

def clean_data(value):
    """Очистка данных от лишних пробелов и преобразование пустых строк в None"""
    if isinstance(value, str):
        value = value.strip()
        return None if value == '' else value
    return value

def main():
    # Подключение к MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("DB_NAME", "OGW")
    
    client = MongoClient(mongo_uri)
    db = client[db_name]

    # Путь к файлу
    file_path = Path("uploads/price.xlsx")

    # Словарь для перевода названий колонок
    column_translation = {
        'Подкатегория': 'subcategory',
        'Наименование товара': 'product_name',
        'Цвет': 'color',
        'Обьем памяти': 'storage',
        'Страна': 'country',
        'Краткое описание': 'short_description',
        'Характеристики': 'specifications',
        'Цена': 'price',
        'Конфигурация': 'configuration',
        'Фото1': 'photo1',
        'Фото2': 'photo2',
        'Фото3': 'photo3'
    }

    # Получаем коллекцию products
    collection = db['products']

    try:
        # Чтение Excel файла
        xls = pd.ExcelFile(file_path)

        # Очищаем коллекцию перед добавлением новых данных
        collection.delete_many({})

        total_products = 0

        # Обработка каждого листа
        for sheet_name in xls.sheet_names:
            # Пропускаем пустые листы
            if sheet_name.lower() in ['other', 'лист1', 'sheet1']:
                continue
                
            # Чтение данных листа
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # Переименование колонок
            df.rename(columns=column_translation, inplace=True)
            
            # Очистка данных
            for col in df.columns:
                df[col] = df[col].apply(clean_data)
            
            # Добавляем поле category с именем листа
            df['category'] = sheet_name.strip()
            
            # Добавляем дату создания
            df['created_at'] = datetime.now()
            
            # Преобразование в список словарей
            data = df.to_dict('records')
            
            # Вставляем данные в коллекцию
            if data:
                result = collection.insert_many(data)
                inserted_count = len(result.inserted_ids)
                total_products += inserted_count
                print(f"Из листа {sheet_name} добавлено {inserted_count} товаров")

        print(f"Всего добавлено {total_products} товаров в коллекцию products")
        return True

    except Exception as e:
        print(f"Ошибка при импорте данных: {str(e)}")
        return False
    finally:
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
        client.close()