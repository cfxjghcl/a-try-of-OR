# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from typing import List, Optional

class JobItem(scrapy.Item): # Renamed from NcssJobItem to JobItem
    # 接口原生字段
    job_id = scrapy.Field()           # jobId
    job_catory = scrapy.Field()       # jobcatory
    job_industry = scrapy.Field()     #jobindustry
    job_name = scrapy.Field()         # jobName
    high_month_pay = scrapy.Field()   # highMonthPay
    low_month_pay = scrapy.Field()    # lowMonthPay
    update_date = scrapy.Field()      # updateDate
    publish_date = scrapy.Field()     # publishDate
    head_count = scrapy.Field()       # headCount
    member_level = scrapy.Field()     # memberLevel
    recruit_type = scrapy.Field()     # recruitType
    degree_name = scrapy.Field()      # degreeName
    company_name = scrapy.Field()     # recName
    company_logo = scrapy.Field()     # recLogo
    area_code_name = scrapy.Field()   # areaCodeName
    prinvce_code_nme = scrapy.Field() #provincesCodeName
    company_scale = scrapy.Field()    # recScale
    sort_priority = scrapy.Field()    # sortPriority
    sources_name_ch = scrapy.Field()  # sourcesNameCh
    sources_type = scrapy.Field()     # sourcesType
    company_tags = scrapy.Field()     # recTags (福利)
    major_required = scrapy.Field()   # major (专业要求)
    company_property = scrapy.Field() # recProperty
    user_type = scrapy.Field()        # userType
    company_id = scrapy.Field()       # recId
    key_units = scrapy.Field()        # keyUnits
    sources_name = scrapy.Field()     # sourcesName

    # 补充溯源字段
    search_area_code = scrapy.Field() # area_code
    search_area_name = scrapy.Field() # area_name
    search_keyword = scrapy.Field()
    search_category_code = scrapy.Field()
    search_industry_code = scrapy.Field()
    source_url = scrapy.Field()         # URL