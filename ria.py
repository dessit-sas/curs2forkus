import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import time


@dataclass
class NewsItem:
    """Класс для хранения данных о новости"""
    source_page: str
    article_url: str
    title: Optional[str] = None
    content: Optional[str] = None
    publish_date: Optional[str] = None
    category: Optional[str] = None


class RiaNewsParser:

    def __init__(self, base_url: str = 'https://ria.ru/'):
        """
        Инициализация парсера

        Args:
            base_url: Базовый URL сайта
        """
        self.base_url = base_url
        self.url_helper = 'https://ria.ru'
        self.session = requests.Session()
        self.categ = {}
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Категории для классификации новостей
        self.serious = ["/politics/", "/economy/",
                        ]
        self.cultural = ["/culture/", "/science/",
                         "/sport/"]
        self.sport = "/sport/"

    def check_connection(self) -> bool:
        """Проверка подключения к сайту"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            print(f"Статус подключения: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False

    def get_main_page_links(self) -> List[str]:

        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            allfd = soup.find_all('div', class_="cell-extension__item m-with-title")

            links = []
            for href in allfd:
                link_element = href.find('a', href=True)
                if link_element:
                    links.append(link_element['href'])
                    self.categ[link_element['href']] = href.get_text()
            return links
        except Exception as e:
            print(f"Ошибка при получении ссылок с главной страницы: {e}")
            return []

    def _parse_article_page(self, url: str) -> Optional[Dict[str, Any]]:

        try:
            response = self.session.get(url)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'lxml')

            title = ''
            publish_date = ''
            content = ''

            title_elem = soup.find_all('div', class_="article__header")
            for element in title_elem:
                title += element.get_text()
            # Извлечение даты публикации
            date_elem = soup.find_all('div', class_="article__info-date")
            for element in date_elem:
                publish_date += element.get_text()
            # Извлечение содержимого статьи
            content_elem = soup.find_all('div', class_="article__text")
            for element in content_elem:
                content += element.get_text()

            return {
                'title': title,
                'content': content,
                'publish_date': publish_date,
                'url': url
            }
        except Exception as e:
            print(f"Ошибка при парсинге статьи {url}: {e}")
            return None

    def parse_category_pages(self, category_links: List[str]) -> List[NewsItem]:
        """
        Парсинг страниц категорий и извлечение ссылок на статьи

        Args:
            category_links: Список ссылок на страницы категорий

        Returns:
            Список объектов NewsItem
        """
        news_items = []

        for link in category_links:
            # Формируем полный URL
            if not link.startswith('http'):
                full_link = f'{self.url_helper}{link}' if link.startswith('/') else f'{self.url_helper}/{link}'
            else:
                full_link = link

            try:
                response = self.session.get(full_link)
                if response.status_code != 200:
                    print(f"Ошибка загрузки {full_link}: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, 'lxml')

                # Определяем, какие элементы искать в зависимости от категории
                if link in self.serious:
                    news_blocks = soup.find_all('div', class_='list list-tags')
                elif link in self.cultural:
                    news_blocks = soup.find_all('div', class_='section_set')
                elif self.sport in link:
                    news_blocks = soup.find_all('div', class_='cell-list__item')
                else:
                    continue

                # Извлекаем ссылки на статьи
                hrefs_seen = set()
                i = 0
                for news_block in news_blocks:
                    a_tags = news_block.find_all('a', href=True)
                    for a_tag in a_tags:
                        href = a_tag['href']
                        if('sport' in link):
                            href =link + href
                        if href and href.startswith('http') and href not in hrefs_seen:
                            news_item = NewsItem(
                                source_page=full_link,
                                article_url=href,
                                category=self.categ[link]
                            )
                            news_items.append(news_item)
                            hrefs_seen.add(href)
                            i+=1
                        if (i > 5 ):
                            break

                print(f"Обработана страница: {full_link} (найдено {len(hrefs_seen)} статей)")

            except Exception as e:
                print(f"Ошибка при обработке {full_link}: {e}")

        return news_items

    def parse_articles_content(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """
        Парсинг содержимого статей

        Args:
            news_items: Список объектов NewsItem без контента

        Returns:
            Список объектов NewsItem с заполненным контентом
        """
        for i, news_item in enumerate(news_items, 1):
            print(f"Парсинг статьи {i}/{len(news_items)}: {news_item.article_url}")

            article_data = self._parse_article_page(news_item.article_url)
            if article_data:
                news_item.title = article_data['title']
                news_item.content = article_data['content']
                news_item.publish_date = article_data['publish_date']


        return news_items

    def save_to_json(self, news_items: List[NewsItem], filename: str = 'ria_news.json'):
        """Сохранение результатов в JSON файл"""
        data = []
        for item in news_items:
            if item.content and item.title and item.article_url and item.category and item.publish_date and item.source_page:  # Сохраняем только статьи с контентом
                data.append({
                    'source_page': item.source_page,
                    'article_url': item.article_url,
                    'title': item.title,
                    'content': item.content,
                    'publish_date': item.publish_date,
                    'category': item.category
                })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Сохранено {len(data)} статей в файл {filename}")

    def run_full_parsing(self, output_file: str = 'ria_news.json') -> List[NewsItem]:
        """
        Запуск полного процесса парсинга

        Args:
            output_file: Имя файла для сохранения результатов

        Returns:
            Список спарсенных новостей
        """
        print("=== Начало парсинга RIA.ru ===")

        # Проверяем подключение
        if not self.check_connection():
            print("Нет подключения к сайту")
            return []

        # Получаем ссылки с главной страницы
        print("Получение ссылок с главной страницы...")
        category_links = self.get_main_page_links()
        print(f"Найдено {len(category_links)} ссылок на категории")

        # Парсим страницы категорий
        print("\nПарсинг страниц категорий...")
        news_items = self.parse_category_pages(category_links)
        print(f"Найдено {len(news_items)} ссылок на статьи")

        # Парсим содержимое статей
        print("\nПарсинг содержимого статей...")
        news_items = self.parse_articles_content(news_items)

        # Сохраняем результаты
        print("\nСохранение результатов...")
        self.save_to_json(news_items, output_file)

        print("\n=== Парсинг завершен ===")
        return news_items
