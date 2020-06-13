# cqu_news_scrapy_spider
重大新闻网的爬虫试作

## 使用方法
```
cd ${project_dir}
scrapy runspider cqu_news/spiders/crawl.py -o <output_file_name.json|csv>
```

或者使用额外的命令指定日志级别
```
scrapy runspider cqu_news/spiders/crawl.py -o <output_file_name.json|csv> --loglevel=INFO
scrapy runspider cqu_news/spiders/crawl.py -o <output_file_name.json|csv> --loglevel=VERBOSE --logfile=cqu_news_2020061301.log
```

## 详细说明

参见博客：[[Python][Scrapy][爬虫]爬虫应用实战--重大新闻网新闻摘要.py](https://dexfire.cn/2020/06/12/Python-Scrapy-%E7%88%AC%E8%99%AB-%E7%88%AC%E8%99%AB%E5%BA%94%E7%94%A8%E5%AE%9E%E6%88%98-%E9%87%8D%E5%A4%A7%E6%96%B0%E9%97%BB%E7%BD%91%E6%96%B0%E9%97%BB%E6%91%98%E8%A6%81-py/)

## License
[MIT](LICENSE)
