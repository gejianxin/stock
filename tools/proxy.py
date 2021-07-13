import requests
from bs4 import BeautifulSoup
from fake_headers import Headers


def get_proxy(BASEURL, URL, proxies):
    headers = Headers(os="win", headers=True).generate()
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, features='lxml')
    table = soup.select('body > div:nth-child(4) > div.bl > div.data > table > tr')
    for row in table:
        ip = row.select('tr > td:nth-child(1)')[0]
        port = row.select('tr > td:nth-child(4) > span')[0]
        proxies.append(':'.join([ip.string, port.string]))

    page_ref = soup.select('body > div:nth-child(4) > div.bl > div > table > tfoot > tr > td > div > a')
    if len(page_ref) > 1:
        URL = BASEURL + page_ref[1]['href']
        get_proxy(BASEURL, URL, proxies)
    return proxies
