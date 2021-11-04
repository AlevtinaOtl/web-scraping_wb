"""
Web scraping popular books about the internet and technology from wildberries.ru
Also saving data to xlsx file and measuring program's execution time
"""

import requests
import pandas
import time
from pandas import ExcelWriter
from bs4 import BeautifulSoup

headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0"
}
books = []
start_time = time.time()


# Logic of program
def main():
    n = int(input("Сколько страниц раздела 'Интернет и технологии' нужно спарсить?\n"))
    url = "https://www.wildberries.ru/catalog/knigi/nehudozhestvennaya-literatura/internet-i-tehnologii?sort=popular&page="
    for i in range(1, n + 1):
        pages = str(i)
        u = url + pages
        html = get_request(u)
        get_content(html.text)
    save(books)


# Send get request and get the page
def get_request(url):
    response = requests.get(url, headers=headers)
    return response


# Scraping data from site
def get_content(html):
    soup = BeautifulSoup(html, "lxml")
    data = soup.find_all("div", class_="product-card j-card-item")

    for d in data:
        try:
            books.append({
                "title": d.find("span", class_="goods-name").get_text(),
                "old-price": int(d.find(
                    "del", class_="price-commission__old-price").get_text(strip=True).replace(
                    "\xa0₽", "").replace("\xa0", "")),
                "new-price": int(d.find(
                    "span", class_="price-commission__current-price").get_text().replace(
                    "\xa0₽", "").replace("\xa0", ""))
            })
        except AttributeError:
            books.append({
                "title": d.find("span", class_="goods-name").get_text(),
                "old-price": int(d.find(
                    "span", class_="lower-price").get_text().replace(
                    "\xa0₽", "").replace("\xa0", ""))
            })


# Saving data to xlsx file and measuring program's execution time
def save(info):
    dataframe = pandas.DataFrame(info)
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
    print(f"Время работы программы: {int(time.time() - start_time) // 60} минут "
          f"{int(time.time() - start_time) % 60} секунд")


if __name__ == '__main__':
    main()

