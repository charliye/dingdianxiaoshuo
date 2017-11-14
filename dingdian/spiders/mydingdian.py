import scrapy
import re
from bs4 import BeautifulSoup
from scrapy.http import Request
from dingdian.items import DingdianItem
from dingdian.items import DcontentItem
from dingdian.mysqlpipelines.sql import Sql


class Myspider(scrapy.Spider):

    name = "dingdian"
    allowed_domains = ['23wx.cc']
    bash_url = 'http://www.23wx.cc/class/'
    bashurl = '.html'

    def start_requests(self):
        #for i in range(1, 11):
        for i in range(1, 2):
            url = self.bash_url + str(i) + '_1' + self.bashurl
            yield Request(url, self.get_name)


    #def parse(self, response):
    #   print response.text
    #    max_num = BeautifulSoup(response.text, 'lxml').find('div', class_='pagelink')[0].find_all('a')[-1].get_text()
    #    bashurl = str(response.url)[:-7]
    #    for num in range(1, int(max_num) +1):
    #       url = bashurl + '_' + str(num) + self.bashurl
    #       yield Request(url, callback=self.get_name)

    def get_name(self, response):
        #print response.text
        tds = BeautifulSoup(response.text, 'lxml').find_all('div', class_='item')
        for td in tds:
            #novelinfo = td.find('dt').get_text()
            novelauth = td.find('span').get_text()
            novelurl = td.find('a')['href']
            category = BeautifulSoup(response.text, 'lxml').find('title').get_text()
            # print novelurl
            # print noverauth
            yield Request(url=novelurl, callback=self.get_chapterurl, meta={'url': novelurl,'category': category, 'auth': novelauth})

    def get_chapterurl(self, response):
        #print response.text
        item = DingdianItem()
        item['name'] = BeautifulSoup(response.text, 'lxml').find('h1').get_text()
        item['novelurl'] = response.meta['url']
        #category = BeautifulSoup(response.text, 'lxml').find('div', class_='con_top').find('a').get_text()
        item['author'] = response.meta['auth']
        baseurl = response.meta['url']
        name_id = str(baseurl)[-6:-1].replace('/', '')
        #item['category'] = str(category).replace('/', '')
        item['name_id'] = name_id
        item['category'] = response.meta['category']
        yield item
        yield Request(url=baseurl, callback=self.get_chapter, meta={'name_id': name_id},dont_filter=True)

    def get_chapter(self, response):
        #print response.text
        urls = re.findall(r'<dd><a href="(.*?)">(.*?)</a></dd>', response.text)
        num = 0
        for url in urls:
            num = num+1
            chapterurl = response.url + url[0]
            chaptername = url[1]
            #print chaptername
            rets = Sql.sclect_chapter(chapterurl)
            if rets[0] == 1:
                print('chapter is already exist.')
                pass
            else:
                yield Request(chapterurl, callback=self.get_chaptercontent, meta={'num': num, 'name_id': response.meta['name_id'], 'chaptername': chaptername, 'chapterurl': chapterurl},dont_filter=True)

    def get_chaptercontent(self, response):
        #print response.text
        item = DcontentItem()
        item['num'] = response.meta['num']
        item['id_name'] = response.meta['name_id']
        #item['chaptername'] = str(response.meta['chaptername']).replace('\xa0', '')
        item['chaptername'] = response.meta['chaptername']
        item['chapterurl'] =response.meta['chapterurl']
        #content = BeautifulSoup(response.text, 'lxml').find('div', id="content").get_text()
        #print response.text
        base = BeautifulSoup(response.text, 'lxml')
        if base.find('dd', id="contents") != None:
            item['chaptercontent'] = base.get_text()
            pass
        else:
            content = base.find('div', id='content')
            item['chaptercontent'] = content
            #print content
            #print item
        return item

