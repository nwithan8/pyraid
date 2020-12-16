from bs4 import BeautifulSoup as bs


def get_soup(html):
    return bs(html, 'html.parser')


def parse_table_row(row):
    return [td.getText() for td in row.find_all('td')]


def parse_table_rows(table):
    return table.find_all('tr')
