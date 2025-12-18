import json


from newspaper import Config, Article

import requests
from bs4 import BeautifulSoup



#      Файл для парсинга

#      надо при этом сохранить id
#      тех статей что на одну и туже тему
#      т. е. это вухсвязный список


class Parser:

    def __init__(self):

        self.url_pars = {
            #   "url_pars" : [settings_1, settings_2, settings_3, settings_4, settings_5]
            #
            #   пример         |
            #                  v
            #
            #   "https://www.1tv.ru/news/" : ["h2", "class='news_pad'", span, h3, h4],
        }
        self.arr_resp = []
    
    def response_func (self):
        pass


def start_parsing ():
    # Кастомизация конфигурации
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0...'  # Меняем User-Agent
    config.request_timeout = 15
    config.number_threads = 10  # Для параллельной загрузки
    config.memoize_articles = False  # Отключаем кэш при разработке
    config.fetch_images = False  # Не скачиваем картинки (быстрее)
    config.keep_article_html = True  # Сохраняем HTML для отладки

    url = "https://newspaper.readthedocs.io/en/latest/"

    article = Article(url, config=config)

    article.download()
    article.parse()
    article.nlp()

    print(article.title)       # Заголовок
    print(article.text)        # Основной текст (без навигации, рекламы)
    print(article.authors)     # Авторы
    print(article.publish_date)  # Дата публикации
    print(article.top_image)   # Главное изображение
    print(article.summary)  
    

start_parsing()
