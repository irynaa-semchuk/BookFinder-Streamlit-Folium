# coding: cp1251
import re
from urllib.request import urlopen, Request
from urllib.parse import quote, quote_plus
from bs4 import BeautifulSoup as bs
from math import inf

TRANSLITERATION = {' ': '-', '�': 'a', '�': 'b', '�': 'v', '�': 'g', '�': 'd', '�': 'e',
                   '�': 'je', '�': 'zh', '�': 'z', '�': 'i', '�': 'i', '�': 'j', '�': 'k',
                   '�': 'l', '�': 'm', '�': 'n', '�': 'o', '�': 'p', '�': 'r', '�': 's',
                   '�': 't', '�': 'u', '�': 'f', '�': 'h', '�': 'c', '�': 'ch', '�': 'sh',
                   '�': 'sch', '�': 'ju', '�': 'ja', '�': '', }


def translit(s):
    res = ''
    for item in s:
        res += TRANSLITERATION[item.lower()]
    return res


def get_price(author, title, site):

    if site == 'bookclub.ua':
        query = quote_plus(title, encoding="windows-1251")
        url = f"https://{site}/ukr/search/index.html?search={query}"
        req = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}))
        html = bs(req.read(), features="html.parser")
        obj = html.find("div", "search-results")
        if "�������� 0" in obj.find("div", "main-search").string:
            return None
        url = f"https://bookclub.ua/{obj.find('a').attrs['href']}"
        html = bs(urlopen(url).read(), "html.parser")
        check = html.findAll('div', 'prd-attr-descr')
        if not (title.lower() in check[1].string.lower()
                and author.lower() in check[2].string.lower()):
            return None
        price = html.find('div', 'prd-your-price-numb').get_text().split()[0]
        return float(price), url


    if site == 'yakaboo.ua':

        query = quote_plus(title)
        # � ������ � ��� ����� ������� HTTPS:
        url = f"https://{site}/ua/search/?multi=0&cat=&q={query}"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        obj = bs(urlopen(req).read(), features="html.parser")
        tags = obj.find_all("div", "dynamic-info", limit=4)
        for item in tags:
            url = f"https:{item.find('a').attrs['href']}"
            check_1 = item.find('a', 'product-name').get_text()
            check_2 = item.find('div', 'product-author').get_text()
            if not (title.lower() in check_1.lower()
                    and author.lower() in check_2.lower()):
                continue
            if not item.find('div', 'day_delivery'):
                continue
            price = item.find('span', 'price').get_text().split()[0]
            return float(price), url

        query = translit(title)
        # � ������ � ��� ����� ������� HTTPS:
        url = f"https://{site}/ua/{query}.html"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            obj = bs(urlopen(req).read(), features="html.parser")
        except:
            return None
        check_1 = obj.find('div', 'base-product__title').find('h1').get_text()
        check_2 = obj.find('div', 'preview__info').find('div', 'base-product__author').get_text()
        if (title.lower() in check_1.lower() and author.lower() in check_2.lower()
                and '�������� �����' in obj.find('div', 'status__format').get_text()):
            price = obj.find('div', 'ui-price-display__main').find('span').get_text()
            return float(price), url



def get_delivery(site):
    if site == 'bookclub.ua':
        url = f"https://{site}/ukr/help/delivery/"
        html = bs(urlopen(url).read(), features="html.parser")
        obj = html.find('div', 'newscontent').find('ul').find_all('li')[1]
        delivery = float(obj.get_text().split()[6])
        free = float(obj.get_text().split()[3])
        return delivery, free


    if site == 'yakaboo.ua':
        url = f"https://{site}/ua/delivery/"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        obj = bs(urlopen(req).read(), features="html.parser")
        for item in obj.find_all('p'):
            text = item.get_text()
            exp = '������� �������� ��������� � ������ '
            if exp in text:
                index = text.find(exp)
                delivery = float(text[len(exp):text.find(' ���')])
                return delivery, inf

    if site == 'starylev.com.ua':
        return 45, 500


if __name__ == '__main__':
    pass
