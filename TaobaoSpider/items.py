# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TaobaospiderItem(scrapy.Item):
    # define the fields for your item here like:
    good_belongs = scrapy.Field()       # 所属类别
    good_name = scrapy.Field()          # 商品名称
    good_id = scrapy.Field()            # 商品id,用来提取商品评论
    # good_popularity = scrapy.Field()    # 商品人气,需要进入商品详情页面提取
    good_pic = scrapy.Field()           # 商品图片
    good_price = scrapy.Field()         # 商品价格
    good_link = scrapy.Field()          # 商品链接
    good_sale = scrapy.Field()          # 已售数量
    good_comment = scrapy.Field()       # 商品评论

