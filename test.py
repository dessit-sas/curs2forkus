import json

# Открываем файл для чтения
with open("lenta_news.json", "r", encoding="utf-8") as f:
    # Загружаем данные из файла в переменную
    data = json.load(f)

for elem in data:
    print(elem['title'])

