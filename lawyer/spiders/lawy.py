# -*- coding: utf-8 -*-
import json
import scrapy
from lawyer.items import DistrictItem,CityDistrictItem,LawFirmItem,LawyerItem

class LawySpider(scrapy.Spider):
    name = 'lawy'
    def start_requests(self):#post请求，获取省级地域名称，编号
        url = 'http://www.12348.gov.cn/selectdistrict/getselectdistrict' #省级地域
        yield scrapy.http.Request(url,method='POST', callback=self.parse, dont_filter=True, encoding='utf-8')

    def parse(self, response):#获取省级地域内容
        dis_item = DistrictItem()
        mytext = json.loads(response.text)#转换格式
        # print(mytext)
        for eachdata in mytext :#循环存入名称和编号
            dis_item['name'] = eachdata['name']
            dis_item['code'] = eachdata['code']
            yield dis_item#回溯存入
            #对每一个省级地域，进行下列操作，进入此链接，爬取市级地域内容
            url = 'http://www.12348.gov.cn/lawerdeptlist/getcitylist'  # 市级地域
            raw = '{district: "'+eachdata['code']+'"}'#raw是post请求所需参数，对于每个省级的而市级地域区别在于此参数的district的值
            meta = {'code' : eachdata['code']}#将省级地域编号传递下去
            yield scrapy.http.FormRequest(url, body = raw, meta=meta,
                                          method='POST', callback=self.parse_city_district, dont_filter=True, encoding='utf-8')

    def parse_city_district(self, response):#获取市级地域内容
        city_item = CityDistrictItem()
        mytext = json.loads(response.text)
        # print(mytext)
        for eachdata in mytext :
            city_item['name'] = eachdata.get('name')
            city_item['city_code'] = eachdata['code']
            city_item['english_name'] = eachdata['english_name']
            city_item['code'] = response.meta['code']#参数获取
            yield city_item
            #对于每一个市级地域，进行下列操作
            url = 'http://www.12348.gov.cn/lawerdeptlist/getlawerdeptlist'#律师事务所列表
            raw = '{pageSize: 12, pageNum: 1, xzqh: "'+eachdata['code']+'", yw: "", pzslsj: 0, nums: 0}'#与xzqh的值有关
            meta = {'district' : eachdata['name'], 'code' : eachdata['code']}#将市级地域名称和编号传递
            yield scrapy.http.FormRequest(url, body=raw,meta=meta,
                                          method='POST', callback=self.parse_law_firm_list, dont_filter=True, encoding='utf-8')

    def parse_law_firm_list(self, response):#获取律师事务所的列表
        mytext = json.loads(response.text)
        # print(mytext)
        #此json文件是一个字典，字典的list是列表，故此进行循环
        for eachdata in mytext['list'] :#获取事务所的行政区号和链接id
            xzqh = eachdata.get('xzqh')
            lsswsbs = eachdata.get('lsswsbs')
            district = response.meta['district']
            code = response.meta['code']
            #对于每个律师事务所爬取详细内容
            url = 'http://www.12348.gov.cn/lawdeptinfo/getlawdeptinfo'  # 律师事务所详情
            raw = '{lsswsbs: "' + lsswsbs + '"}'
            meta = {'xzqh' : eachdata['xzqh'], 'district' : district,'code' : code, 'lsswsbs' : eachdata['lsswsbs']}  # 参数传递
            yield scrapy.http.FormRequest(url, body=raw, meta=meta,
                                          method='POST', callback=self.parse_law_firm, dont_filter=True, encoding='utf-8')
        #由于此列表不仅仅只有一页，故通过此循环进行爬取
        if 12 * mytext['page'] < mytext['total'] :
                url = 'http://www.12348.gov.cn/lawerdeptlist/getlawerdeptlist'  # 律师事务所
                page = mytext['page'] + 1
                raw = '{pageSize: 12, pageNum: '+str(page)+', xzqh: "'+xzqh+'", yw: "", pzslsj: 0, nums: 0}'
                meta = {'district': district, 'code' : code}  #每一页都需要传递
                yield scrapy.http.FormRequest(url, body=raw, meta=meta,
                                              method='POST', callback=self.parse_law_firm_list, dont_filter=True, encoding='utf-8')


    def parse_law_firm(self, response):
        lawfirm_item = LawFirmItem()
        mytext = json.loads(response.text)
        # print(mytext)
        lawfirm_item['city_code'] = response.meta['code']
        lawfirm_item['xzqh'] = response.meta['xzqh']
        lawfirm_item['pzslsj'] = mytext.get('pzslsj')
        lawfirm_item['ZSDH'] = mytext.get('zsdh')
        lawfirm_item['lsswsmc'] = mytext.get('lsswsmc')
        lawfirm_item['zyzh'] = mytext.get('zyzh')
        lawfirm_item['zsd'] = mytext.get('zsd')
        lawfirm_item['city_district'] = response.meta['district']
        lsswsbs = response.meta['lsswsbs']
        yield lawfirm_item
        url = 'http://www.12348.gov.cn/lawdeptinfo/getlawerlist'  # 律师
        raw = '{pkid: "' + lsswsbs + '", pageNum: 1, pageSize: 8}'
        meta = {'lsswsmc': mytext['lsswsmc'],'city_code' : response.meta['code']}  # 每一页都需要传递
        yield scrapy.http.FormRequest(url, body=raw, meta=meta,
                                      method='POST', callback=self.parse_lawyer, dont_filter=True, encoding='utf-8')

    def parse_lawyer(self, response):
        law_item = LawyerItem()
        mytext = json.loads(response.text)
        # print(mytext)
        # print(mytext['total'])
        # print(mytext['page'])
        # print(mytext['list'])
        for eachdata in mytext['list'] :
            zyjg = eachdata.get('zyjg')
            pic = eachdata.get('PIC')
            city_code = response.meta['city_code']
            code = city_code[0:2]
            if pic is not None :
                pic = 'http://www.12348.gov.cn/imagetype/'+code+'00/lsfw/lsuser/'+pic[0:-4]+'/jpg'
            else :
                pic = 'http://www.12348.gov.cn/resources/images/liz/peo_pict1.png'
            law_item['lsswsmc'] = response.meta['lsswsmc']
            law_item['xzqh'] = eachdata.get('XZQH')
            law_item['pic'] = pic
            law_item['xm'] = eachdata.get('xm')
            law_item['years'] = eachdata.get('years')
            law_item['zyzh'] = eachdata.get('zyzh')
            yield law_item
        if 8 * mytext['page'] < mytext['total'] :
            url = 'http://www.12348.gov.cn/lawdeptinfo/getlawerlist'#律师
            page = mytext['page'] +1
            raw = '{pkid: "'+zyjg+'", pageNum: '+str(page)+', pageSize: 8}'
            meta = {'lsswsmc': response.meta['lsswsmc'],'city_code' : city_code}  # 每一页都需要传递
            yield scrapy.http.FormRequest(url, body=raw, meta=meta,
                                          method='POST', callback=self.parse_lawyer, dont_filter=True,
                                          encoding='utf-8')