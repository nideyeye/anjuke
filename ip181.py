# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup


class ip181():
    def __init__(self):
        self.headers = {'User-Agent':"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"}
    def get_ip(self):#获取IP地址同时验证有效性
        '''
        从ip181获取代理地址-第一页
        :return: 提取的ip列表
        '''
        proxy_url = 'http://www.xicidaili.com/wt/'
        response = requests.get(proxy_url,headers=self.headers)
        soup = BeautifulSoup(response.content,'lxml')
        results=soup.find_all('tr',attrs={'class':['odd']})
        ip_list = []
        for result in results:
            soup_td = result.find_all('td')
            ip = str(soup_td[1].string)
            port = str(soup_td[2].string)
            ip_list.append(ip+':'+port)
        return ip_list
if __name__ == '__main__':
    test = ip181()
    ip_pool = test.get_ip()
    print(ip_pool)
