# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json


class TaobaospiderPipeline(object):
    def process_item(self, item, spider):
        content = json.dumps(dict(item), ensure_ascii=False) + '，\n'
        filename = item['good_belongs'].replace('/','')
        with open("./Taobao/" + filename + ".txt", 'ab') as f:
            f.write(content.encode('utf-8'))
        return item
