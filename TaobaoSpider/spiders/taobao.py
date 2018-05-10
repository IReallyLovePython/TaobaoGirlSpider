# -*- coding: utf-8 -*-
import json

import requests
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

            item_dict['page_s'] = 0  # 当前第一页，每个新类别都重置一次

            yield scrapy.Request(item_dict['goods_url'], callback=self.parse_data, meta={'item_dict': item_dict})

    def parse_data(self, response):

        item = TaobaospiderItem()
        item['good_belongs'] = response.meta['item_dict']['good_belongs']

        # 正则获取商品json字符串：
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
            # 商品评论
            item['good_comment'] = self.get_comment(item['good_id'])

            yield item

        print("*" * 50, response.meta['item_dict']['page_s'])
        if response.meta['item_dict']['page_s'] < 60 * 5:
            response.meta['item_dict']['page_s'] += 60  # 每次翻下一页时 page_s增加60
            page_str = '&bcoffset=12&s=' + str(response.meta['item_dict']['page_s'])
            next_page = re.sub('(.*seller_type=taobao)(.*)', r'\1' + page_str, response.url)
            print(item['good_belongs'], '的下一页：', next_page)
            yield scrapy.Request(next_page, callback=self.parse_data, meta=response.meta)

    def get_comment(self, good_id):
        current_page = '1'
        max_page = '0'
        good_comment = list()
        while True:
            comment_url = 'https://rate.taobao.com/feedRateList.htm?auctionNumId={}&currentPageNum={}&pageSize=&folded=0&callback=jsonp_tbcrate_reviews_list'.format(good_id,current_page)
            print("当前评论地址:",comment_url)
            print("当前页面:",current_page)
            print("最大页数:",max_page)
            result = requests.get(comment_url,headers={
                'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
            })

            html = result.text

            # 通过正则获取评论信息列表、当前评论页数、最大评论页数
            comment_list= re.findall(r'"content":"(.*?)"',html)
            current_page= re.search(r'"currentPageNum":(.*),',html).group(1)
            max_page = re.search(r'"maxPage":(.+)}',html).group(1)

            good_comment += comment_list

            if current_page == max_page:
                break
            else:
                current_page = str(int(current_page) + 1)
        return good_comment



