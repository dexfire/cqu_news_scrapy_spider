# -*- coding: utf-8 -*-
import scrapy
import os
import re
import logging
from bs4 import BeautifulSoup
from scrapy import Request
from cqu_news.items import CquNewsItem

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from twisted.internet import reactor
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings


class CrawlSpider(scrapy.Spider):
    name = 'crawl'
    allowed_domains = ['news.cqu.edu.cn']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    }
    hits_api = "https://news.cqu.edu.cn/newsv2/api.php?op=count&id={newsid}&modelid=15"
    start_urls = [
        #'http://news.cqu.edu.cn/newsv2/news-126.html',  # 综合新闻
        'http://news.cqu.edu.cn/newsv2/news-127.html',  # 教学科研
        'http://news.cqu.edu.cn/newsv2/news-130.html',  # 招生就业
        'http://news.cqu.edu.cn/newsv2/news-129.html',  # 交流合作
        'http://news.cqu.edu.cn/newsv2/news-132.html',  # 校园生活
    ]
    blocks = {
        '126': "综合新闻",
        '127': "教学科研",
        '130': "招生就业",
        '129': "交流合作",
        '132': "校园生活"
    }

    def parse(self, response):
        url = response.url
        self.log("当前地址：" + response.url)
        if(response.status == 200):
            self.log("!" + "#"*20, level=logging.INFO)
            self.log("Loaded home page Okay.", level=logging.INFO)
            bs = BeautifulSoup(response.body, features="lxml")
            # 页面标题
            self.log(bs.find("title").text, level=logging.INFO)
            # 获取“下一页”div标签
            nextpage = bs.find("a", attrs={"class": "a1"}, text="下一页")
            # 获取总页码数
            pages = int(nextpage.find_previous_sibling().text)
            # 查询当前版块名称
            block_id = re.search("news-(\d+)\.html", url)[1]
            self.log("总计：" + str(pages) + " 条新闻", level=logging.INFO)
            self.log("!" + "#"*20, level=logging.INFO)
            for i in range(1, pages+1):
            #for i in range(2, 5):
                url0 = url + "?page="+str(i)
                self.log("获取新任务： " + url0, level=logging.INFO)
                yield Request(url0, callback=self.parse_page, errback=self.onerror, headers=self.headers, cb_kwargs={"src": url0, "block": self.blocks[block_id]})
        else:
            # 首页获取失败： 反复重试！
            self.log("获取首页错误： " + str(response.status), level=logging.ERROR)
            yield Request(url, headers=self.headers)
        
    def parse_page(self, response, src, block):
        self.log("!" + "#"*10 + " 获取页面 #" +
                 str(re.search("[\d]+$", response.url)[0]) + "#"*10, level=logging.INFO)
        self.log(response.url)
        bs = BeautifulSoup(response.body, features="lxml")
        title = bs.find("title").text
        self.log("标题：" + title)
        items = bs.findAll("div", attrs={"class": "item"})
        for it in items:
            data = CquNewsItem()
            data['title'] = re.sub("\s", "", it.find('div', attrs={"class": "title"}).text)
            data['time'] = re.sub("\s", "", it.find('div', attrs={"class": "rdate"}).text)
            postimg = it.find('img')
            if postimg is not None:
                cover = postimg.attrs['src']
                data['cover'] = "http://news.cqu.edu.cn" + it.find('img').attrs['src']
            data['abstract'] = re.sub("\s", "", it.find('div', attrs={"class": "abstract"}).text)
            data['link'] = it.find('a').attrs['href']
            data['block'] = block
            if not data['link'].startswith('http'):
                data['link'] = "http://news.cqu.edu.cn/newsv2/" + data['link']
            data['source'] = str(src)
            data['page'] = re.search("\d+$", str(src))[0]
            self.log("!" + "#"*10 + " 页面结束 #" +
                    str(re.search("[\d]+$", response.url)[0]) + "#"*10)
            yield Request(data['link'], callback=self.parse_news, cb_kwargs={"data": data})
            # yield data

    def parse_news(self, response, data):
        try:
            data['title'] = response.xpath("//h1[@class='dtitle']/text()").get()
            data["date"] = response.xpath("//div[@class='ibox']/span[2]/text()").get()
            data['content'] = "\r\n".join(response.xpath("//div[@class='acontent']//p/text()").getall())
            data['author'] = ", ".join(response.xpath("//div[@class='dinfoa']/p//*/text()").getall())
            data['tags'] = ', '.join(response.xpath("//div[@class='tags']/a/text()").getall())
            self.log("@标签：" + ' '.join(data['tags']), level=logging.INFO)
            newsid = re.search("(\d+-\d+\.html)", response.url)[1]
            yield Request(self.hits_api.format(newsid=newsid), callback=self.parse_hits, headers=self.headers, cb_kwargs={"data": data})
        except:
            self.log("识别摘要出错！ * " + response.url, level=logging.ERROR)
            newsid = re.search("(\d+-\d+\.html)", response.url)[1]
            yield Request(self.hits_api.format(newsid=newsid), callback=self.parse_hits, headers=self.headers, cb_kwargs={"data": data})

    def parse_hits(self, response, data):
        try:
            data['hits'] = re.search("\$\('#hits'\)\.html\('(\d+)'\);", response.text)[1]
            data['todayhits'] = re.search("\$\('#todaydowns'\)\.html\('(\d+)'\);", response.text)[1]
            data['weekhits'] = re.search("\$\('#weekdowns'\)\.html\('(\d+)'\);", response.text)[1]
            data['monthhits'] = re.search("\$\('#monthdowns'\)\.html\('(\d+)'\);", response.text)[1]
            yield data
        except:
            self.log("获取点击量错误！ * " + response.url, level=logging.ERROR)
            yield data

    def onerror(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

# settings = Settings({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
# runner = CrawlerRunner(settings)
# d = runner.crawl(CrawlSpider)
# d.addBoth(lambda _: reactor.stop())
# reactor.run()
