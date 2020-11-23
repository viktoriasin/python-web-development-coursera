from bs4 import BeautifulSoup
import unittest
import re

 
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


class TestParse(unittest.TestCase):
    def test_parse(self):
        test_cases = (
            ('wiki/Stone_Age', [13, 10, 12, 40]),
            ('wiki/Brain', [19, 5, 25, 11]),
            ('wiki/Artificial_intelligence', [8, 19, 13, 198]),
            ('wiki/Python_(programming_language)', [2, 5, 17, 41]),
            ('wiki/Spectrogram', [1, 2, 4, 7]),)

        for path, expected in test_cases:
            with self.subTest(path=path, expected=expected):
                self.assertEqual(parse(path), expected)


if __name__ == '__main__':
    unittest.main()