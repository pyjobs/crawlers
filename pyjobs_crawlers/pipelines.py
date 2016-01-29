# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class RecordJobPipeline(object):

    ACTION_SAVED = 'SAVED'

    def process_item(self, item, spider):
        spider.get_connector().add_job(job_item=item)
        spider.get_connector().log(spider.name, self.ACTION_SAVED, item['url'])
        return item

