#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import MySQLdb
import os.path


class LagouPipeline(object):
    def process_item(self, item, spider):
        date_time = item['date_time']
        company = item['company']
        salary = item['salary']
        workYear = item['workYear']
        education = item['education']
        city = item['city']
        jobNature = item['jobNature']
        positionName = item['positionName']
        companyLabelList = item['companyLabelList']
        businessZones = item['businessZones']
        positionId = item['positionId']
        financeStage = item['financeStage']
        industryField = item['industryField']
        responseJob = item['responseJob']

        conn = MySQLdb.connect(host='10.35.22.91',
                               user='root',
                               port=3306,
                               passwd='adminadmin',
                               db='scrapydb',
                               charset='utf8')

        cur = conn.cursor()
        print("mysql connect succes")
        try:
#            cur.execute("INSERT INTO lagou(salary,company) values(%s,%s)",
#                        (str(s) for s in (salary,company)))
            cur.execute("INSERT INTO lagou(company,salary,workYear,education,city,jobNature,positionName,companyLabelList,businessZones,positionId,financeStage,industryField,responseJob) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (str(d) for d in (date_time,company, salary, workYear, education, city, jobNature, positionName, companyLabelList,businessZones, positionId, financeStage, industryField, responseJob)))
            print("insert success")
        except Exception as e:
            print('Insert error:', e)
        else:
            cur.close()
            conn.commit()
            conn.close()

        return item
