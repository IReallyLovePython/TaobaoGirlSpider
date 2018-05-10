# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy.spiders import CrawlSpider
import re
import jsonpath

from TaobaoSpider.items import TaobaospiderItem


class TaobaoSpider(CrawlSpider):
    name = 'taobao'
    allowed_domains = ['taobao.com']
    start_urls = [
        'https://www.taobao.com/markets/nvzhuang/taobaonvzhuang',
    ]

    def parse_start_url(self, response):
        # 所有商品类别
        goods_category = response.xpath("//*[@id='sm-nav-2014']/div[2]/div[2]/div/div[2]/dl//a")
        for each in goods_category:
            item_dict = dict()
            # 所属类别名
            item_dict['good_belongs'] = each.xpath("./text()").extract()[0]
            # 类别链接,用来继续爬取类别下的商品
            item_dict['goods_url'] = each.xpath("./@href").extract()[0]

            item_dict['page_s'] = 0     # 当前第一页，每个新类别都重置一次

            yield scrapy.Request(item_dict['goods_url'], callback=self.parse_data, meta={'item_dict': item_dict})

    def parse_data(self, response):

        item = TaobaospiderItem()
        item['good_belongs'] = response.meta['item_dict']['good_belongs']

        # 商品json字符串：
        json_str = re.findall(r'g_page_config = ({.*});', response.body.decode('utf-8'))[0]

        # 将json字符串转换成python对象
        json_obj = json.loads(json_str)

        # 此类商品根节点
        json_base = jsonpath.jsonpath(json_obj, '$..itemlist.data.auctions[*]')

        for data in json_base:
            # 商品名称
            item['good_name'] = jsonpath.jsonpath(data, '$.title')[0]
            # 商品id
            item['good_id'] = jsonpath.jsonpath(data, '$.nid')[0]
            # 商品图片列表
            pic_list = list()
            for url in jsonpath.jsonpath(data, '$.sku..picUrl'):
                pic_list.append(url)
            item['good_pic'] = pic_list
            # 商品价格
            item['good_price'] = jsonpath.jsonpath(data, '$.view_price')[0]
            # 商品链接
            item['good_link'] = jsonpath.jsonpath(data, '$.detail_url')[0]
            # 已售数量
            item['good_sale'] = jsonpath.jsonpath(data, '$.view_sales')[0]

            yield item

        print("*"*50,response.meta['item_dict']['page_s'])
        if response.meta['item_dict']['page_s'] < 60*5:
            response.meta['item_dict']['page_s'] += 60  # 每次翻下一页时 page_s增加60
            page_str = '&bcoffset=12&s=' + str(response.meta['item_dict']['page_s'])
            next_page = re.sub('(.*seller_type=taobao)(.*)', r'\1' + page_str, response.url)
            print(item['good_belongs'],'的下一页：',next_page)
            yield scrapy.Request(next_page, callback=self.parse_data, meta=response.meta)
