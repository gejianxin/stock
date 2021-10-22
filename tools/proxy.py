import random
import time
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers


def get_proxy(URL='http://www.xiladaili.com/http'):
    headers = Headers(os="win", headers=True).generate()
    proxies = []

    for i in range(1, 50):
        response = requests.get("{url}/{i}".format(url=URL, i=i), headers=headers)
        time.sleep(random.uniform(0.1, 2.2))

        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.text, features='lxml')
        tr = soup.select('body > div > div > div > table > tbody > tr')
        for td in tr:
            if '高匿' in td.select('tr > td:nth-child(3)')[0].text and '天' in td.select('tr > td:nth-child(6)')[0].text:
                proxy = td.select('tr > td:nth-child(1)')[0].text
                proxies.append(proxy)
    print(proxies)
    return proxies

def check_proxy(proxy, CHECK_URL='http://icanhazip.com'):
    headers = Headers(os="win", headers=True).generate()
    proxy_dict = {'https': 'https://' + proxy}

    try:
        time.sleep(1)
        # 发送测试请求
        response = requests.get(CHECK_URL, headers=headers, proxies=proxy_dict, timeout=1)
        if response.status_code == 200:
            print('有效IP: ' + proxy)
            with open('xila_https_list.txt', 'a') as f:
                f.write(proxy)
                f.write('\n')
        else:
            print('无效IP: ' + proxy)
    except requests.HTTPError as e:
        print('Http Error: ' + e + ' 无效IP: ' + proxy)
