from bs4 import BeautifulSoup
from decimal import Decimal


def get_val(doc, cur_code):
    src = doc.find('CharCode', text=cur_code)
    if not src:
        print(f'Can not find code {cur_code}')
        return Decimal()
    val = Decimal(str(src.find_next_sibling('Value').string).replace(',', '.'))
    nominal = Decimal(str(src.find_next_sibling('Nominal').string).replace(',', '.'))
    return val / nominal


def convert(amount, cur_from, cur_to, date, requests):
    URL = 'https://www.cbr.ru/scripts/XML_daily.asp'
    # Использовать переданный requests
    response = requests.get(
        URL,
        params={
            'date_req':date
        }
    )
    soup = BeautifulSoup(response.content, 'xml')
    if cur_from == 'RUR':
        from_ = Decimal(1)
    else:
        from_ = get_val(soup, cur_from)
    if cur_to == 'RUR':
        to_ = Decimal(1)
    else:
        to_ = get_val(soup, cur_to)
    result = (amount * (1 / to_) * from_).quantize(Decimal('.0001'))
    return result  # не забыть про округление до 4х знаков после запятой

# решение преподавателей
# def convert(amount, cur_from, cur_to, date, requests):
#     result = requests.get("https://www.cbr.ru/scripts/XML_daily.asp", {"date_req": date})
#     soup = BeautifulSoup(result.content, 'xml')
#     rates = {i.CharCode.string: (
#         Decimal(i.Value.string.replace(',', '.')),
#         int(i.Nominal.string)
#     ) for i in soup('Valute')
#     }
#     rates['RUR'] = (Decimal(1), 1)

#     result = amount * rates[cur_from][0] * rates[cur_to][1] / rates[cur_from][1] / \
#              rates[cur_to][0]
#     return result.quantize(Decimal('.0001'))
