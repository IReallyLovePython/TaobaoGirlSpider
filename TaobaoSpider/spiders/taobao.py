# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider


class TaobaoSpider(CrawlSpider):
    name = 'taobao'
    allowed_domains = ['taobao.com']
    start_urls = ['https://www.taobao.com/markets/nvzhuang/taobaonvzhuang']

    def parse_start_url(self, response):
        # 所有商品类别
        goods_category = response.xpath("//*[@id='sm-nav-2014']/div[2]/div[2]/div/div[2]/dl//a")
        for each in goods_category:
            item_dict = {}
            # 所属类别名
            item_dict['good_belongs'] = each.xpath("./text()").extract()[0]
            # 类别链接,用来继续爬取类别下的商品
            item_dict['goods_url'] = each.xpath("./@href").extract()[0]
            yield scrapy.Request(item_dict['goods_url'], callback=self.parse_data, meta={'item_dict': item_dict})

    def parse_data(self, response):
        print(response.url)
