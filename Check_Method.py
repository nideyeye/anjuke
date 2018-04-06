#！/usr/bin/env python
# _*_coding:utf-8 _*_

import requests
import pymysql
import re
import logging
import sys
import time
from ip181 import ip181
'''
全局配置日志文件
'''


class Check_Methhod():
	'''
	提供以下四种方法进行调用：
	check_ip(ip):检测IIP地址是否符合ip:prot形式
	check_proxy_useful(ip):检测传入ip是否可以使用
	save_into_proxydb(ip):将传入的ip存入数据库
	check_dbip():检查库中的地址是否可用，不可用则删除，返回一个可用的ip列表
	'''
	def __init__(self):
		self.db = pymysql.connect('localhost', 'proxy', 'proxy', 'proxydb')

		self.logger = logging.getLogger("Proxy1")

		self.console_handler = logging.StreamHandler(sys.stdout)
		self.console_handler.formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

		self.logger.addHandler(self.console_handler)

		self.logger.setLevel(logging.INFO)
	def check_ip(self, ip):
		'''
		用于检查传入的地址是否为标准IP：port形式
		:param ip: 传入的待检查的地址
		:return: 返回值用于判断是否正确
		'''
		p = re.compile('([\d]*.){3}[\d]*:[\d]*', re.S)
		if p.match(ip):
			return True
		else:
			return False

	def delete_ip(self,ip):
		ip = str(ip)
		try:
			cursor = self.db.cursor()
			cursor.execute("delete from ip_adress where adress = '%s' limit 1;" % (ip))
			self.db.commit()
			return True
		except:
			self.db.rollback()
			self.logger.debug("Exception Logged")

	def check_proxy_useful(self, ip):
		'''
		检查传入的ip地址是否可用
		:param ip: 待检查的ip：port形式
		:return: 真为可用，假为不可用
		'''
		proxies = {"http": str(ip)}

		if self.check_ip(ip):
			try:
				html=requests.get('http://www.baidu.com/', proxies=proxies, timeout=5)
				self.logger.debug(html.text)
				return True
			except :
				self.delete_ip(ip)
				self.logger.info('%s  不可用，已删除',ip)
		else:
			self.logger.debug("Exception Logged")



	def save_into_proxydb(self, ip):
		'''
		数据库存储函数，得到一个ip并存入数据库
		:param ip: 要存入数据库的ip地址
		:return: 返回True代表存入成功，反之失败
		'''
		ip = str(ip)
		cursor = self.db.cursor()
		cursor.execute("select * from ip_adress where adress = '%s'" % str(ip))
		result = cursor.fetchall()
		if result:
			pass
		else:
			try:
				cursor.execute("insert into ip_adress(adress) values('%s');" % ip)
				self.db.commit()
				self.logger.info('%s已入库', ip)
				self.logger.removeHandler(self.console_handler)
				return True
			except:
				self.db.rollback()
				self.logger.exception("Exception Logged")
				self.logger.removeHandler(self.console_handler)
				return False



	def check_Repeated_IP(self,ip):
		cursor = self.db.cursor()
		try:
			cursor.execute("select * from ip_adress where adress = '%s'" % ip)
			result = cursor.fetchall()
			count = len(result)
		except:
			self.logger.exception("Exception Logged")

		try:
			if count > 2:
				self.logger.info('地址出现重复，即将删除%s',ip)
				self.delete_ip(ip)
				return False
			else:
				if count == 1:
					return True
				else:
					self.logger.exception("Exception Logged")

		except:
			self.logger.exception("Exception Logged")

	def check_dbip(self):
		cursor = self.db.cursor()
		cursor.execute('select * from ip_adress;')
		result = cursor.fetchall()
		ip_pool=[]

		for (ip,) in result:
			temp = self.check_proxy_useful(ip)
			if temp == True:
				if self.check_Repeated_IP(ip):
					self.logger.info('%s 校验完成，地址可用',ip)
					ip_pool.append(ip)
				else:
					self.delete_ip(ip)
			else:
				self.delete_ip(ip)/
		num = int(len(ip_pool))
		self.logger.info('检查完成,现有%d个代理可用',num)
		if num < 20:
			self.logger.info('代理数低于20个，开始重新拉取')
			temp = ip181()
			result=temp.get_ip()
			for i in result:
				try:
					self.save_into_proxydb(i)
				except:
					self.logger.exception("Exception Logged")
			self.logger.info('新代理入库完成，即将开始重新检测')
		time.sleep(2)
		return ip_pool

if __name__ == '__main__':
	test = Check_Methhod()
	count =0
	while True:
		test.check_dbip()
		time.sleep(10)
		count = count + 1
		print('检查已完成'+str(count)+'次')