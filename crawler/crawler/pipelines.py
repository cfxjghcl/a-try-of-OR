import pymysql,json,openpyxl
from datetime import datetime
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class BasePipeline:
    """基础管道类，提供通用方法"""
    def get_collection_name(self, spider):
        """根据爬虫名称获取集合/表名"""
        return spider.name  # cities/positions/jobs
    
    def get_current_time(self):
        """获取当前时间字符串"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class JobPipeline:
    def open_spider(self, spider):
        if spider.name == 'jobs':
            self.file = open('crawler\data1\jobs.json', 'w', encoding='utf-8')
            self.file.write('[\n')
            self.first_item = True
    
    def close_spider(self, spider):
        if spider.name == 'jobs':
            self.file.write('\n]')
            self.file.close()
    
    def process_item(self, item, spider):
        if spider.name == 'jobs':
            line = json.dumps(dict(item), ensure_ascii=False)
            if self.first_item:
                self.file.write(line)
                self.first_item = False
            else:
                self.file.write(',\n' + line)
        return item