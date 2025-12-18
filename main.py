from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from main_pars import *
from TextComparison import *

import json


import uvicorn


class App:
    def __init__(self):
        self.app = FastAPI()
        self.app.mount("/static", StaticFiles(directory="static"), name="static")
        self.templates = Jinja2Templates(directory="templates")
        self._setup_routes()

        self.arr = {}

        data = None
        with open("lenta_news.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for elem in data:
            title = elem['title']
            if title not in self.arr:
                self.arr[title] = []

            content = elem['content']
            d_cont = content.split(" ")
            if len(d_cont) > 150:
                cpy = d_cont[0: 150]
                content = ' '.join(cpy)
                content += "..."

            self.arr[title].extend([content, elem['publish_date'], elem['article_url']])

        data = None
        with open("Kommersant_news.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for elem in data:
            title = elem['title']
            if title not in self.arr:
                self.arr[title] = []

            content = elem['content']
            d_cont = content.split(" ")
            if len(d_cont) > 150:
                cpy = d_cont[0: 150]
                content = ' '.join(cpy)
                content += "..."

            self.arr[title].extend([content, elem['publish_date'], elem['article_url']])

        data = None
        with open("ria_news.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for elem in data:
            title = elem['title']
            cnt = title.find("©")
            true_title = ""
            for i in range(cnt):
                true_title += title[i]
            if true_title not in self.arr:
                self.arr[true_title] = []

            content = elem['content']
            d_cont = content.split(" ")
            if len(d_cont) > 150:
                cpy = d_cont[0: 150]
                content = ' '.join(cpy)
                content += "..."

            self.arr[true_title].extend([content, elem['publish_date'], elem['article_url']])




    def _setup_routes(self):

        @self.app.get("/", response_class=HTMLResponse)
        async def root(request: Request):
            return await self.main_train(request)

        @self.app.get("/services", response_class=HTMLResponse)
        async def services_route(request: Request):
            return await self.services(request)

        @self.app.get("/news", response_class=HTMLResponse)
        async def news_route(request: Request):
            return await self.news(request)

        @self.app.get("/recomends", response_class=HTMLResponse)
        async def recomends_route(request: Request):
            return await self.recomends(request)

        @self.app.get("/about_us", response_class=HTMLResponse)
        async def about_us_route(request: Request):
            return await self.about_us(request)



    # Остальные методы остаются без изменений
    async def main_train(self, request: Request):

        return self.templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "arr": self.arr,
            }
        )

    async def services(self, request: Request):
        return self.templates.TemplateResponse(
                "services.html",
                {
                    "request": request,
                }
            )

    async def about_us(self, request: Request):
        return self.templates.TemplateResponse(
            "about_us.html",
            {
                "request": request,
            }
        )

    async def news(self, request: Request):
        comparator = SimpleArticleComparator()
        results = comparator.compare_articles(article1, article2)
        report = comparator.generate_report(
            results,
            "Верховный суд отказал Ларисе Долиной и вернул квартиру Полине Лурье.",
            "Долина проиграла в суде. Что дальше? Новости самые скверные"
        )
        return self.templates.TemplateResponse(
            "news.html",
            {
                "request": request,
                "article1": article1,
                "article2": article2,
                "report": report,
            }
        )

    async def recomends(self, request: Request):
        return self.templates.TemplateResponse(
            "recomends.html",
            {
                "request": request,
            }
        )



app_instance = App()
app = app_instance.app


if __name__ == "__main__":
    #main_func()
    uvicorn.run(app, host="0.0.0.0", port=8000)
