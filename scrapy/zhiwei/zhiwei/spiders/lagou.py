# -*- coding: utf-8 -*-
'''爬取好比是开采石油，Item装的都是原油，需要通过一系列的管道
和工艺进行提炼,而这些原油都是通过pipeline进行加工的，才能真正的到我们所能使用的油(数据)'''
import scrapy
#import sys
#reload(sys)
#python默认环境编码时ascii
#sys.setdefaultencoding("utf-8")
import re
import urllib
import time
from scrapy.http import Request
from zhiwei.items import ZhiweiItem
class LagouSpider(scrapy.Spider):
    name = 'lagou'
    allowed_domains = ['lagou.com']
    start_urls = ['https://www.baidu.com']
#获取拉勾的网页
    def parse(self, response):
        api_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Host":"www.lagou.com",
            "Cookie":"JSESSIONID=ABAAABAABFGAAIFA35462408CE26E5341AC152099A3C652; _ga=GA1.2.1322254821.1502959169; user_trace_token=20170817163929-da4343f5-5598-4265-b70f-ae62fa390825; LGRID=20170825142852-a96f8aca-895e-11e7-aefa-525400f775ce; LGUID=20170817163929-9554b0cf-8327-11e7-897f-5254005c3644; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1502959170; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1503642532; X_HTTP_TOKEN=34aec411ecdde3f6ff22540dd52d6fa8; _ga=GA1.3.1322254821.1502959169; _putrc=""; login=false; unick=""; index_location_city=%E5%8C%97%E4%BA%AC; _gat=1; LGSID=20170825142720-7302f38a-895e-11e7-aef9-525400f775ce; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fzhaopin%2F1%2F",
        }
        for i in range(1, 31):
            url = 'https://www.lagou.com/zhaopin/' + str(i)
#            print url
            yield Request(url=url, callback=self.page,headers=api_headers,errback=self.error)
        pass
#获取各招聘页的详细页
    def page(self, response):
        api_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Cookie":"JSESSIONID=ABAAABAABFGAAIFA35462408CE26E5341AC152099A3C652; _ga=GA1.2.1322254821.1502959169; user_trace_token=20170817163929-da4343f5-5598-4265-b70f-ae62fa390825; LGRID=20170825142852-a96f8aca-895e-11e7-aefa-525400f775ce; LGUID=20170817163929-9554b0cf-8327-11e7-897f-5254005c3644; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1502959170; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1503642532; X_HTTP_TOKEN=34aec411ecdde3f6ff22540dd52d6fa8; _ga=GA1.3.1322254821.1502959169; _putrc=""; login=false; unick=""; index_location_city=%E5%8C%97%E4%BA%AC; _gat=1; LGSID=20170825142720-7302f38a-895e-11e7-aef9-525400f775ce; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fzhaopin%2F1%2F",
	    }
        positionid = response.xpath("//li[@class='con_list_item default_list']/@data-positionid").extract()
        for i in range(0, len(positionid)):
            position_id = positionid[i]
            url = 'https://www.lagou.com/jobs/' + str(position_id) +'.html'
            yield Request(url=url, callback=self.next,headers=api_headers,errback=self.error)
        pass
#获取招聘详细页的信息
    def next(self,response):
        items=[]
        item = ZhiweiItem()
#获取发布日期
        date1 = response.xpath("//p[@class='publish_time']/text()").extract()[0]
        item['date_time'] = time.strftime('%Y%m%d',time.localtime()) + ' ' + str(date1).split(' ',1)[0]
#获取职位
        item['positionName'] = response.xpath("//div[@class='job-name']/@title").extract()
#获取公司名称
        item['company'] = response.xpath("//div[@class='company']/text()").extract()
#获取要求工作经验
        subSelector = response.xpath('//dd[@class="job_request"]')
        for sub in subSelector:
            item['workYear'] = sub.xpath('./p/span[3]/text()').extract()[0].rstrip('/')
#获取要求教育程度
            item['education'] = sub.xpath('./p/span[4]/text()').extract()[0].rstrip('/')
#获取工作性质
            item['jobNature'] = sub.xpath('./p/span[5]/text()').extract()
#获取工作城市
            item['city'] = sub.xpath('./p/span[2]/text()').extract()[0].rstrip('/')
#获取工资薪资
            item['salary'] = sub.xpath('./p/span[1]/text()').extract()
#获取工作区域
            item['businessZones'] = response.xpath("//input[@name='positionAddress']/@value").extract()
#获取公司福利
            item['companyLabelList'] = response.xpath("//dd[@class='job-advantage']/p/text()").extract()
#获取公司人数
            company_Size = response.xpath("//dd/ul[@class='c_feature']/li[4]/text()").extract()[1].rstrip()
#获取公司阶段
            item['financeStage'] = response.xpath("//dd/ul[@class='c_feature']/li[2]/text()").extract()[1].rstrip()
#获取公司类型
            item['industryField'] = response.xpath("//dd/ul[@class='c_feature']/li[1]/text()").extract()[1].rstrip()
#职位id
            body = response.body.decode('utf-8','ignore')
            position_Id = "window.global.positionId = '(.*?)'"
            item['positionId'] = re.compile(position_Id).findall(body)
#获取岗位职责
            subSelector = response.xpath("//dd[@class='job_bt']/div/p")
            Job = ''
            for sub in subSelector:
                if sub.xpath("./text()").extract_first() is not None:
                    Job = Job + sub.xpath("./text()").extract_first().replace('\"','')
            item ['responseJob'] = Job
            items.append(item)
            return items
    def error(self,response):
            print("error")

