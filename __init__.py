import asyncio
import MySQLdb
import aiohttp
from lxml import etree
import json


class WscSpider:
    loop = asyncio.get_event_loop()
    result = []
    @classmethod
    def get(cls, url, params={}, headers={}, cookies={}, proxy='', timeout=None):
        return cls.__request(urls=[url], method='GET', params=params, headers=headers, cookies=cookies, proxy=proxy,
                         timeout=timeout)[0]

    # 异步的gets方法，传入多个url，转到__request()方法
    @classmethod
    def gets(cls, urls, params={}, headers={}, cookies={}, proxy='', timeout=None):
        return cls.__request(urls=urls, method='GET', params=params, headers=headers, cookies=cookies, proxy=proxy,
                         timeout=timeout)

    # 异步的post方法，传入一个url，转到__request()方法
    @classmethod
    def post(cls, url, params={}, headers={}, cookies={}, proxy='', timeout=None):
        return cls.__request(urls=[url], method='POST', params=params, headers=headers, cookies=cookies,proxy=proxy, timeout=timeout)[0]

    @classmethod
    async def main(cls, url, method=None, params={}, headers={}, cookies={}, proxy='', timeout=None):
        # 创建一个session对象
        async with aiohttp.ClientSession() as sess:
            resp = await sess.request(url=url, method=method, params=params, headers=headers, cookies=cookies, proxy=proxy, timeout=timeout)
            body = await resp.read()
            resp = MyResponse(body)
            cls.result.append(resp)

    @classmethod
    def __request(cls, urls, method=None, params={}, headers={}, cookies={}, proxy='', timeout=None):
        tasks = []
        for url in urls:
            tasks.append(cls.main(url=url, method=method, params=params, headers=headers, cookies=cookies, proxy=proxy, timeout=timeout))
        cls.loop.run_until_complete(asyncio.wait(tasks))
        re = cls.result
        cls.result = []
        return re

    @staticmethod
    def get_dict_from_params(str):
        p = {}
        for s in str.split('\n'):
            datas = s.split(sep=':', maxsplit=1)
            p.update({datas[0].strip(): datas[1].strip()})
        return p


class MyResponse(object):
    def __init__(self, body):
        self.body = body

    @property
    def text(self):
        try:
            return self.body.decode('utf-8')
        except:
            return self.body.decode('gbk')

    # key 自动抽取json中的所有符合的数据  递归
    @property
    def json(self):
        return json.loads(self.body)

    def get_element_from_xpath(self, str):
        nodes = etree.HTML(self.body).xpath(str)
        return nodes[0]

    def get_elements_from_xpath(self, str):
        return etree.HTML(self.body).xpath(str)


class Db:
    def __init__(self):
        self.conn = MySQLdb.Connect(host='127.0.0.1', user='root', password='123456', db='crawler', port=3306,
                                    charset='utf8')
        self.cursor = self.conn.cursor()

    def storage(self, items):
        # print(item)  # sql语句，插入数据库
        sql = "insert into t_w_zl (title,position,salary,addr,company) values(%s, %s, %s, %s, %s)"
        self.cursor.execute(sql, [items['title'], items['position'], items['salary'], items['addr'], items['company']])
        self.conn.commit()
        #print('Db储存成功！')