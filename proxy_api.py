#！/usr/bin/env python
# _*_coding:utf-8 _*_
import pymysql
from flask import Flask
import random
proxy_api=Flask(__name__)

sql_clean = "truncate table ip_adress;"
db = pymysql.connect('localhost', 'proxy', 'proxy', 'proxydb')

@proxy_api.route('/')
def hello():
    return '使用get_ip获得一个代理，使用get_iplist获得代理列表'
@proxy_api.route('/get_ip')
def get_ip():
    cursor = db.cursor()
    cursor.execute("select * from ip_adress;")
    result = cursor.fetchall()
    ip_pool = []
    for i in result:
        ip_pool.append(i)
    return random.choice(ip_pool)
@proxy_api.route('/get_list')
def get_iplist():
    cursor = db.cursor()
    cursor.execute("select * from ip_adress;")
    result = cursor.fetchall()
    ip_pool = []
    for (i,) in result:
        ip_pool.append(i)
    return str(ip_pool)
if __name__=='__main__':
    proxy_api.run(port=5002,debug=True)
