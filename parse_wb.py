import requests
import pandas
import openpyxl
from bs4 import BeautifulSoup
from pandas import ExcelWriter

headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0"
}
books = []


def get_request():
    n = int(input(f"Сколько страниц нужно спарсить? "))
    return n


def get_html(url):
    response = requests.get(url, headers=headers)
    return response


def get_content(html):
    soup = BeautifulSoup(html, "lxml")
    ev = soup.find_all("div", "product-card j-card-item")

    for i in ev:
        books.append({
            'title': i.find("span", "goods-name").get_text(),
            'price': i.find(class_="lower-price").get_text(strip=True).replace("\xa0₽", ""),
            'image': "https:" + i.find("img", "j-thumbnail thumbnail")['src']
        })


def main():
    ur = "https://www.wildberries.ru/catalog/knigi/nehudozhestvennaya-literatura/internet-i-tehnologii?sort=popular&page={}"
    url = [ur.format(x) for x in range(1, get_request()+1)]
    for u in url:
        html = get_html(u)
        get_content(html.text)
    save(books)


def save(info):
    dataframe = pandas.DataFrame(info)
    newdataframe = dataframe.rename(columns = {
        "title": "Название",
        "price": "Цена",
        "image": "Обложка"
    })
    name = input("Введите имя файла: ")
    writer = ExcelWriter(f"{name}.xlsx")
    newdataframe.to_excel(writer, f"name")
    writer.save()
    print(f"Данные сохранены в файл '{name}.xlsx'")

if __name__ == "__main__":
    main()