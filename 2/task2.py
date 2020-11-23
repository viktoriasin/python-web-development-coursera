import os
import re
from collections import defaultdict
from bs4 import BeautifulSoup
import unittest

 
def correct_width(width):
    if width is None:
        return False
    return int(width) > 199


def find_images(body):
    return len(body.find_all('img', width=correct_width))


def find_headers(body):
    headers = body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    headers = [tag.text for tag in headers]
    cnt = 0
    for h in headers:
        if h.startswith('E') or h.startswith('T') or h.startswith('C'):
                cnt += 1
    return cnt


def find_max_linkslen(body):
    all_links = body.find_all('a')
    linkslen = 0
    for link in all_links:
        current_count = 1
        siblings = link.find_next_siblings()
        for sibling in siblings:
            if sibling.name == 'a':
                current_count += 1
                linkslen = max(current_count, linkslen)
            else:
                current_count = 0
    return linkslen


def find_links(body):
    tags = body.find_all(['ul', 'ol'])
    cnt = 0
    for t in tags:
        if not t.find_parents(['ul','ol']):
            cnt += 1
    return cnt


def parse(path_to_file):    
    # Поместите ваш код здесь.
    # ВАЖНО!!!
    # При открытии файла, добавьте в функцию open необязательный параметр
    # encoding='utf-8', его отсутствие в коде будет вызвать падение вашего
    # решения на грейдере с ошибкой UnicodeDecodeError
    imgs, headers, linkslen, lists = [None] * 4
    with open(path_to_file, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')
        body = soup.find('div', id='bodyContent')
        imgs = find_images(body)
        headers = find_headers(body)
        linkslen = find_max_linkslen(body) 
        lists = find_links(body)
    return [imgs, headers, linkslen, lists]


def find_path(base, start, finish):
    
    visited = []
    queue = [[start]]
    if start == finish:
        return [os.path.basename(start)]

    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node not in visited:
            if os.path.exists(node):

                with open(node, encoding="utf-8") as file:
                    links = re.findall(r"(?<=/wiki/)[\w()]+", file.read())

                    for link in links:
                        
                        link = os.path.join(base, link)                
                        new_path = list(path)
                        new_path.append(link)
                        queue.append(new_path)

                        if link == finish:
                            return [os.path.basename(p) for p in new_path]

            visited.append(node)
    print('Path does not exist')
    return []


def build_bridge(path, start_page, end_page):
    """возвращает список страниц, по которым можно перейти по ссылкам со start_page на
    end_page, начальная и конечная страницы включаются в результирующий список"""

    return find_path(path, os.path.join(path, start_page), os.path.join(path, end_page))


def get_statistics(path, start_page, end_page):
    """собирает статистику со страниц, возвращает словарь, где ключ - название страницы,
    значение - список со статистикой страницы"""

    # получаем список страниц, с которых необходимо собрать статистику 
    pages = build_bridge(path, start_page, end_page)
    # напишите вашу реализацию логики по сбору статистики здесь
    statistic = list()
    for page in pages:
        stat = parse(os.path.join(path, page))
        statistic.append((os.path.basename(page), stat))
    return dict(statistic)
