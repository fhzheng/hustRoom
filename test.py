#!/usr/bin/env python
# coding=utf-8
import urllib2,urllib,httplib
from  bs4  import BeautifulSoup
import json
import datetime
import time
import md5
import threading
import re
#执行类
class Process:
    '***'
    VIEWSTATE=''
    EVENTVALIDATION='fuck'
    name=''
    doc=''
    startDate=''
    endDate=''
    response_txt=''
    start_page_con=''
    filename=''
    proctype=0
    def runtime():
        return datetime.time
#初始化类
    def __init__(self,build,sd,ed):
        self.name = build['name']
        self.proctype=build['proctype']
        self.buildnum=build['buildnum']
        self.doc=open(self.name+'.txt','w')
        self.doc.write("::"+self.name+'\n')
        self.doc.close()
        self.startDate=sd
        self.endDate=ed
        self.filename=self.name+'.txt'
#设置中间参数
    def setMiddleParameters(self,html):
        p1=re.compile(r'\_\_VIEWSTATE+\S+?\|+?')
        p2=re.compile(r'\_\_EVENTVALIDATION+\S+?\|+?')
        v=p1.findall(html)[0]
        e=p2.findall(html)[0]
        self.VIEWSTATE=v[12:len(v)-1]
        self.EVENTVALIDATION=e[18:len(e)-1]
        m=md5.new()
        m.update(html)
#设置初始参数
    def setStartParameters(self,html):
        soup = BeautifulSoup(html,"lxml")
        self.VIEWSTATE=soup.find_all("input",id="__VIEWSTATE")[0]['value']   #viewstate
        self.EVENTVALIDATION=soup.find_all("input",id="__EVENTVALIDATION")[0]['value'] #enentvalidation
        m=md5.new()
        m.update(html)
#获取两个变动的中间参数
    def getParameters(self):
        return {'VIEWSTATE':self.VIEWSTATE,'EVENTVALIDATION':self.EVENTVALIDATION}
#根据日期循环执行
    def loopDate(self):
        t= datetime.datetime.strptime(self.startDate,'%Y-%m-%d')
        et=datetime.datetime.strptime(self.endDate,'%Y-%m-%d')
        while t<=et:
            f=open(self.filename,'a')
            f.write('--'+t.strftime('%m/%d/%Y')+'\n')
            f.close()
            html=self.sendRequest(self.getPostData(t))
            self.parseHtml(html)
            self.setMiddleParameters(html)
            print self.name,t.strftime('%Y-%m-%d'),"done"
            t=t+datetime.timedelta(days=1)
            pass
    def start(self):
        req=urllib2.Request("http://202.114.5.131/")
        res = urllib2.urlopen(req).read()
        self.setStartParameters(res)
        self.setMiddleParameters(self.sendRequest(self.getPostData(time,True)))
        self.loopDate()
#个性化post参数
    def getPostData(self,date,init=False):
        data={}
        if init:
            if self.proctype==1:
                data['ScriptManagerTab']="upTab1|btSearch"
                data['__EVENTTARGET']=""
                data['__EVENTARGUMENT']=""
                data['__LASTFOCUS']=""
                data['__VIEWSTATE']=self.VIEWSTATE
                data['datepicker']=date.strftime('%Y-%m-%d')
                data['ddlBuild']=self.buildnum
                data['txtSelectedClass']=""
                data['datepicker2']=date.strftime('%Y-%m-%d')
                data['ddlBuild2']="1"
                data['ddlTime']="1"
                data['__EVENTVALIDATION']=self.EVENTVALIDATION
                data['btSearch']="查询"
            elif self.proctype==2:
                data['ScriptManagerTab']="upTab1|ddlBuild"
                data['__EVENTTARGET']="ddlBuild"
                data['__EVENTARGUMENT']=""
                data['__LASTFOCUS']=""
                data['__VIEWSTATE']=self.VIEWSTATE
                data['datepicker']=date.strftime('%Y-%m-%d')
                data['ddlBuild']=self.buildnum
                data['txtSelectedClass']=""
                data['datepicker2']=date.strftime('%Y-%m-%d')
                data['ddlBuild2']="1"
                data['ddlTime']="1"
                data['__EVENTVALIDATION']=self.EVENTVALIDATION
        else:
            data['checkBoxAll']="on"
            data['ScriptManagerTab']="upTab1|btSearch"
            data['__EVENTTARGET']=""
            data['__EVENTARGUMENT']=""
            data['__LASTFOCUS']=""
            data['__VIEWSTATE']=self.VIEWSTATE
            data['datepicker']=date.strftime('%Y-%m-%d')
            data['ddlBuild']=self.buildnum
            data['txtSelectedClass']=""
            data['datepicker2']=date.strftime('%Y-%m-%d')
            data['ddlBuild2']="1"
            data['ddlTime']="1"
            data['__EVENTVALIDATION']=self.EVENTVALIDATION
            data['btSearch']="查询"
        return data
#发送post请求
    def sendRequest(self,data):
        post_url="http://202.114.5.131/classroom.aspx"
        data=urllib.urlencode(data)
        headers={
            "Host": "202.114.5.131",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding":"gzip, deflate",
            "X-MicrosoftAjax":"Delta=true",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Referer": "http://202.114.5.131/",
            "Content-Length": len(data),
            "Connection":" keep-alive"
        }
        t=time.time()
        req=urllib2.Request(post_url,data,headers)
        response=urllib2.urlopen(req)
        res=response.read()
        m=md5.new()
        m.update(res)
        return res
#解析响应中的html数据
    def parseHtml(self,html):
        soup = BeautifulSoup(html,"lxml")

        tables=soup.find_all("table",id="gvMain")
        if len(tables)<1:
            return
        else:
            table=tables[0]
            self.doc=open(self.filename,'a')
            for tr in table.find_all("tr")[1:]:
                a=[]
                for val in tr.find_all("td"):
                    val=str(val)
                    a.append(val[4:len(val)-5])
                self.doc.write(','.join(a)+'\n')
            self.doc.close()
#继承构造线程类
class myThread(threading.Thread):
    def __init__(self,threadID,name,build,sd,ed):
        threading.Thread.__init__(self)
        self.threadID=threadID
        self.name=name
        self.build=build
        self.sd=sd
        self.ed=ed
    def run(self):
        p=Process(self.build,self.sd,self.ed)
        p.start()
#入口
# stream=open('classrooms.json').read()
# stream=json.loads(stream)
# thread=[]
# for idx,val in enumerate(stream['roomlist']):
#     thread.append(myThread(idx,val['name'],val,stream['startdate'],stream['enddate']))
# try:
#     for t in thread:
#         t.start()
# except Exception, e:
#     print e
#     print e.threadID
#     raise
# else:
#     pass
# finally:
#     pass
print time.localtime(time.time())