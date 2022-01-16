"""
Async web scraping popular books about the internet and technology from wildberries.ru
Also saving data to xlsx file and measuring program's execution time
"""

import time
import pandas
from pandas import ExcelWriter
from bs4 import BeautifulSoup
import asyncio
import aiohttp

books = []
start_time = time.time()


# get async scraping task done
async def get_page(session, page):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0"
    }
    url = f"https://www.wildberries.ru/catalog/knigi/nehudozhestvennaya-literatura/internet-i-tehnologii?sort=popular&page={page}"
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, "lxml")
        data = soup.find_all("div", class_="product-card j-card-item")

        for d in data:
            try:
                books.append({
                    "title": d.find("span", class_="goods-name").get_text(),
                    "old-price": int(d.find(
                        "span", class_="price-old-block").get_text(strip=True).replace(
                        "\xa0₽", "").replace("\xa0", "")),
                    "new-price": int(d.find(
                        "ins", class_="lower-price").get_text().replace(
                        "\xa0₽", "").replace("\xa0", ""))
                })
            except AttributeError:
                books.append({
                    "title": d.find("span", class_="goods-name").get_text(),
                    "old-price": int(d.find(
                        "span", class_="lower-price").get_text().replace(
                        "\xa0₽", "").replace("\xa0", ""))
                })


# create tasks query
async def collect_data():
    async with aiohttp.ClientSession() as session:
        pages = int(input("Сколько страниц раздела 'Интернет и технологии' нужно спарсить?\n"))

        for page in range(1, pages + 1):
            book = asyncio.create_task(get_page(session, page))
            books.append(book)
        await asyncio.gather(*books)
    save()


# save information to xlsx file
def save():
    books_list = []

    for book in books:
        if type(book) == dict:
            books_list.append(book)
    dataframe = pandas.DataFrame(books_list)
    dataframe['difference'] = dataframe['old-price'] - dataframe['new-price']
    newdataframe = dataframe.rename(columns={
        "title": "Название",
        "new-price": "Со скидкой",
        "old-price": "Без скидки",
        "difference": "Экономия"
    })
    name = input("Введите имя файла без указания формата: ")
    writer = ExcelWriter(f"{name}.xlsx")
    newdataframe.to_excel(writer, index=False)
    writer.save()
    print(f"Данные сохранены в файл '{name}.xlsx'")


def main():
    try:
        asyncio.run(collect_data())
    except BaseException:
        print("Problem. Try to scrape less pages.")
    print(f"Время работы программы: {int(time.time() - start_time) // 60} минут "
          f"{int(time.time() - start_time) % 60} секунд")


if __name__ == '__main__':
    main()
