Структура проекта имеет следующий вид:
├── backend/                          # FastAPI бэкенд
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # Основной FastAPI app
│   │   ├── database.py               # Подключение к MongoDB
│   │   ├── models.py                 # Модели Pydantic/MongoDB
│   │   ├── schemas.py                # Pydantic схемы
│   │   ├── routers/                  # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── products.py           # Роутер товаров
│   │   │   ├── orders.py             # Роутер заказов
│   │   │   ├── auth.py               # Аутентификация 
│   │   │   └── admin.py              # Админ-панель
│   ├── requirements.txt              # Зависимости Python
|──bot/ (существующая часть)
│   ├── main.py
|──frontend/
    ├── index.html (главная страница MiniApp)
    ├── admin_panel.html (Админ-панель MiniApp)
    ├── images(папка для хранения изображений для каталога)



    http://localhost:5500
    python -m http.server 5500
    frontend/static

    uvicorn app.main:app --reload
ngrok http 5501