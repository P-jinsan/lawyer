# -*- coding: utf-8 -*-
import pymysql
from twisted.enterprise import adbapi
import copy
from .items import DistrictItem,CityDistrictItem,LawFirmItem,LawyerItem#导入item类

class LawyerPipeline(object):
    def __init__(self,dbpool):
        self.dbpool=dbpool

    @classmethod
    def from_settings(cls,settings):
        """
                数据库建立连接
                :param settings: 配置参数
                :return: 实例化参数
                """
        adbparams = dict(
            host=settings['MYSQL_HOST'],  # 读取settings中的配置
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',#不要"-"
            cursorclass=pymysql.cursors.DictCursor,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **adbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        return cls(dbpool)  # 相当于dbpool付给了这个类，self中可以得到

        # pipeline默认调用
    def process_item(self, item, spider):
        if isinstance(item, DistrictItem):
            asynItem = copy.deepcopy(item)  # 深度拷贝 为解决爬取与插入速度不统一导致的数据重复
            query = self.dbpool.runInteraction(self._conditional_insert_district, asynItem)  # 调用插入的方法
            query.addCallback(self.handle_error)  # 调用异常处理方法
        elif isinstance(item, CityDistrictItem):
            asynItem = copy.deepcopy(item)  # 深度拷贝 为解决爬取与插入速度不统一导致的数据重复
            query = self.dbpool.runInteraction(self._conditional_insert_city_district, asynItem)  # 调用插入的方法
            query.addCallback(self.handle_error)  # 调用异常处理方法
        elif isinstance(item, LawFirmItem):
            asynItem = copy.deepcopy(item)  # 深度拷贝 为解决爬取与插入速度不统一导致的数据重复
            query = self.dbpool.runInteraction(self._conditional_insert_law_firm, asynItem)  # 调用插入的方法
            query.addCallback(self.handle_error)  # 调用异常处理方法
        elif isinstance(item, LawyerItem):
            asynItem = copy.deepcopy(item)  # 深度拷贝 为解决爬取与插入速度不统一导致的数据重复
            query = self.dbpool.runInteraction(self._conditional_insert_lawyer, asynItem)  # 调用插入的方法
            query.addCallback(self.handle_error)  # 调用异常处理方法

        # 写入数据库中
    def _conditional_insert_district(self, course, item):
        sql = """insert into district (name,code) value (%s, %s)"""
        params = (item['name'], item['code'])
        course.execute(sql, params)

    def _conditional_insert_city_district(self, course, item):
        sql = """insert into city_district (name, code, english_name,city_code) value (%s, %s, %s, %s)"""
        params = (item['name'], item['code'], item['english_name'],item['city_code'])
        course.execute(sql, params)

    def _conditional_insert_law_firm(self, course, item):
        sql = """insert into law_firm (lsswsmc, zyzh, zsd, ZSDH, pzslsj, city_district, city_code, xzqh) value (%s, %s, %s, %s, %s, %s, %s, %s)"""
        params = (item['lsswsmc'], item['zyzh'], item['zsd'], item['ZSDH'], item['pzslsj'], item['city_district'], item['city_code'], item['xzqh'])
        course.execute(sql, params)

    def _conditional_insert_lawyer(self, course, item):
        sql = """insert into lawyer (lsswsmc, zyzh, pic, xzqh, xm, years) value (%s, %s, %s, %s, %s, %s)"""
        params = (item['lsswsmc'], item['zyzh'], item['pic'], item['xzqh'], item['xm'], item['years'])
        course.execute(sql, params)

    def handle_error(self, failure):
        if failure:
            # 打印错误信息
            print(failure)
