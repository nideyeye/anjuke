#！/usr/bin/env python
# _*_coding:utf-8 _*_
# -*- coding:utf-8 -*-

import requests
import re
from bs4 import BeautifulSoup
import pymysql
import random
import logging
import sys

'''
全局配置日志文件
'''


class anjuke():

	def __init__(self):#初始化参数，包括主地址、头文件、页码、启动标识符
		self.main_url = 'https://fz.zu.anjuke.com/fangyuan'
		self.user_agent_list = [ \
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1" \
			"Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
			"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
			"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
			"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
			"Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
			"Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
			"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
			"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
			"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
			"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
			"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
			"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
			"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
			"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
		]
		self.ua = random.choice(self.user_agent_list)
		self.headers = {'User-Agent': self.ua}
		self.ip_pool=[]
		self.logger = logging.getLogger("Anjuke")
		self.formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

		self.console_handler = logging.StreamHandler(sys.stdout)
		self.console_handler.formatter = self.formatter

		self.logger.addHandler(self.console_handler)

		self.logger.setLevel(logging.INFO)
	def get_proxy(self):
		response = requests.get('http://60.205.201.137:5001/get_ip')
		ip=str(response.text)
		self.logger.info('已提取代理IP%s',ip)
		proxy = {'http':str(ip)}
		return proxy

	def get_next(self,url):
		headers = {
			'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}
		response = requests.get(url, headers=headers)
		soup = BeautifulSoup(response.text, 'lxml')
		try:
			next_page = soup.select('a[class=aNxt]')
			page = re.findall(r'href="(.*?)">', str(next_page), re.S)
			print(str(page[0]))
			return str(page[0])
		except:
			return None


	def get_page(self,url):#传入需要爬取的页面数量
		if url:
			response = requests.get(url,headers = self.headers,proxies = self.get_proxy())
			self.get_info(response.text)
			self.get_page(self.get_next(url))
		else:
			self.logger.info('done')

	def get_info(self,response):
		soup = BeautifulSoup(response, 'lxml')
		temp = soup.find_all('div', ['zu-info'])  # 提取出房源地有关信息
		temp1 = soup.find_all('div', 'zu-side')
		soup = BeautifulSoup(str(temp), 'lxml')
		pattern = re.compile('>(.*?)<', re.S)

		title = []
		detail = []
		rent = []
		prince = []

		for i in soup.select('h3 a'):  # 标题提取，保存至title列表
			title.append(str(i['title']))
		for i in soup('p', ['details-item tag']):  # 详细信息提取，保存至detail列表
			i = str(i)
			i = i.replace(' ', '')
			i = i.replace('\n', '')
			result = re.findall(pattern, i)
			del result[1], result[3], result[2], result[2]
			detail.append(result)
		for i in soup('span', ["cls-1"]):  # 出租类型提取，保存至rent列表
			result = re.findall(pattern, str(i))
			rent.append(str(result))
		for i in BeautifulSoup(str(temp1),'lxml').select('p strong'):
			prince.append(i.string)
		for j in range(0, 60):
			title_=str(title[j])

			detail_=str(detail[j][0])
			area=str(detail[j][1])
			name=str(detail[j][2])
			type_=str(rent[j][2]+rent[j][3])
			price=str(prince[j])
			self.save_anjuke(title_, detail_, area, name, type_, price)
	def save_anjuke(self,title, detail, area, name, type, price):
		db = pymysql.connect('localhost', 'proxy', 'proxy', 'proxydb',charset="utf8")
		cursor = db.cursor()
		try:
			cursor.execute("insert into anjuke(title,detail,area,name,type,price)values('%s','%s','%s','%s','%s','%s');" % (title, detail, area, name, type, price))
			db.commit()
			self.logger.info('入库完成')
		except:
			db.rollback()
			self.logger.info("Exception Logged")


#此为调度器进行爬取数据代码-仅供进行模块测试
if __name__=='__main__':
	test=anjuke()
	test.get_page(test.get_next('https://fz.zu.anjuke.com/'))
