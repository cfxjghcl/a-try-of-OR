# crawler/crawler/spiders/jobs.py
import scrapy
import json
import os
import time
from urllib.parse import urlencode
from crawler.items import JobItem

class JobsSpider(scrapy.Spider):
    name = 'jobs'
    allowed_domains = ['24365.ncss.cn']
    base_url = 'https://24365.ncss.cn/student/jobs/jobslist/ajax/'

    # 固定参数可以保留在类中
    DEFAULT_SOURCES_NAME = ""
    DEFAULT_SOURCES_TYPE = ""
    DEFAULT_LIMIT = 20

    def __init__(self, target_cities_json=None, target_keywords_str=None,
                 target_categories_json=None, target_industries_json=None,
                 run_type="default", *args, **kwargs):
        super(JobsSpider, self).__init__(*args, **kwargs)
        
        self.province_code_to_name_map = {}
        options_data = {} # 存储target_options.json中的数据

        # 构造target_options.json文件的相对位置
        options_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                         '..', 'data', 'target_options.json')
        
        try:
            if os.path.exists(options_file_path):
                with open(options_file_path, 'r', encoding='utf-8') as f:
                    options_data = json.load(f)
                
                # 创建省份编码到省份名字的映射表
                for province_entry in options_data.get("provinces", []):
                    code = province_entry.get("code")
                    name = province_entry.get("name")
                    if code and name:
                        self.province_code_to_name_map[code] = name
                
                if not self.province_code_to_name_map:
                    self.logger.warning(f"Province code to name map is empty after loading {options_file_path}.")
                else:
                    self.logger.info(f"Successfully loaded {len(self.province_code_to_name_map)} province mappings from {options_file_path}.")
            else:
                self.logger.error(f"target_options.json not found at {options_file_path}. Province information and default targets might be missing.")
        except json.JSONDecodeError:
            self.logger.error(f"Error decoding JSON from {options_file_path}. Province information and defaults might be affected.")
            options_data = {}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while loading data from {options_file_path}: {e}")
            options_data = {}

        self.run_type = run_type

        # 工作地点
        if target_cities_json:
            try: self.TARGET_CITIES = json.loads(target_cities_json)
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse target_cities_json. Using default from target_options.json or fallback.")
                self.TARGET_CITIES = options_data.get("citys", [])
        else:
            self.TARGET_CITIES = options_data.get("citys", [])
        if not self.TARGET_CITIES:
            self.TARGET_CITIES = [{"code": "", "name": "全国"}]


        # 关键词（默认不筛选）
        if target_keywords_str:
            self.TARGET_KEYWORDS = [kw.strip() for kw in target_keywords_str.split(',') if kw.strip()]
            if not self.TARGET_KEYWORDS: 
                self.TARGET_KEYWORDS = [""]
        else:
            self.TARGET_KEYWORDS = [""]
        

        # 职位类别
        if target_categories_json:
            try: self.TARGET_CATEGORY_CODES = json.loads(target_categories_json)
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse target_categories_json. Using default from target_options.json or fallback.")
                self.TARGET_CATEGORY_CODES = options_data.get("jobcategoryItems", [])
        else:
            self.TARGET_CATEGORY_CODES = options_data.get("jobcategoryItems", [])
        if not self.TARGET_CATEGORY_CODES:
            self.TARGET_CATEGORY_CODES = [{"code": "", "name": "不限类别"}]

        
        # 所属行业
        if target_industries_json:
            try: self.TARGET_INDUSTRY_CODES = json.loads(target_industries_json)
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse target_industries_json. Using default from target_options.json or fallback.")
                self.TARGET_INDUSTRY_CODES = options_data.get("industriesNew", [])
        else:
            self.TARGET_INDUSTRY_CODES = options_data.get("industriesNew", [])
        
        
        if not self.TARGET_INDUSTRY_CODES:
            self.TARGET_INDUSTRY_CODES = [{"code": "", "name": "不限行业"}]


        self.logger.info(f"Spider initialized with run_type: {self.run_type}")
        self.logger.info(f"Targeting {len(self.TARGET_CITIES)} cities, {len(self.TARGET_KEYWORDS)} keywords, "
                         f"{len(self.TARGET_CATEGORY_CODES)} categories, {len(self.TARGET_INDUSTRY_CODES)} industries.")
        if not options_data:
             self.logger.warning("target_options.json was not loaded or was empty. Defaults may be minimal.")


    def start_requests(self):
        if not self.TARGET_CITIES: 
            self.logger.error("TARGET_CITIES 为空。爬虫将不发送请求。")
            return
        # 遍历城市维度
        for city_info in self.TARGET_CITIES:
            city_code = city_info.get('code', "") 
            city_name = city_info.get('name', "未知城市")

            search_province_name = "未知省份" 
            if not city_code or city_name == "全国": 
                search_province_name = "全国" 
            elif len(city_code) >= 2:
                province_code_prefix = city_code[:2]
                search_province_name = self.province_code_to_name_map.get(
                    province_code_prefix, 
                    f"未知省份(市代码前缀: {province_code_prefix})"
                )
            else: 
                search_province_name = f"未知省份(市代码: {city_code})"

            for keyword in self.TARGET_KEYWORDS:
                # 遍历职位类别维度
                for category_info in self.TARGET_CATEGORY_CODES:
                    category_code = category_info.get('code', "")
                    category_name = category_info.get('name', "未知类别") 
                    # 遍历行业维度
                    for industry_info in self.TARGET_INDUSTRY_CODES:
                        industry_code = industry_info.get('code', "")
                        industry_name = industry_info.get('name', "未知行业") 
                        # 补充字段
                        search_params_base = {
                            'areaCode': city_code,
                            'jobName': keyword,
                            'categoryCode': category_code,
                            'industrySectors': industry_code,
                            'limit': self.DEFAULT_LIMIT,
                            'sourcesName': self.DEFAULT_SOURCES_NAME,
                            'sourcesType': self.DEFAULT_SOURCES_TYPE,
                            'jobType': '', 'monthPay': '', 'property': '',
                            'memberLevel': '', 'recruitType': '', 'keyUnits': '', 'degreeCode': ''
                        }

                        current_page_params = search_params_base.copy()
                        current_page_params['offset'] = 1 
                        current_page_params['_'] = int(time.time() * 1000)

                        url = f"{self.base_url}?{urlencode(current_page_params)}"
                        self.logger.info(
                            f"请求URL (省份: {search_province_name}, 城市: {city_name}({city_code}), 关键字: '{keyword}', "
                            f"类别: {category_name}({category_code}), 行业: {industry_name}({industry_code}))"
                        )

                        # 任务调度器 发送初始请求（提交第一页爬取任务）
                        yield scrapy.Request(
                            url=url,
                            callback=self.parse_job_list,
                            meta={
                                'search_params_base': search_params_base, 
                                'search_area_name': city_name, 
                                'search_province_name': search_province_name, 
                                'request_category_code': category_code, 
                                'request_category_name': category_name, 
                                'request_industry_code': industry_code, 
                                'request_industry_name': industry_name, 
                                'current_offset': 1
                            }
                        )

    # 解析请求返回的岗位信息列表
    def parse_job_list(self, response):
        search_params_base = response.meta['search_params_base']
        search_area_name = response.meta['search_area_name'] 
        search_province_name = response.meta['search_province_name'] 
        
        request_category_code = response.meta['request_category_code']
        request_category_name = response.meta['request_category_name']
        request_industry_code = response.meta['request_industry_code']
        request_industry_name = response.meta['request_industry_name']
        current_offset = response.meta['current_offset']

        try:
            data = response.json()
        except json.JSONDecodeError:
            self.logger.error(f"URL 的 JSONDecodeError：{response.url}。响应文本：{response.text[:500]}")
            return

        if not data.get("flag"):
            self.logger.error(f"URL 的 API 请求失败：{response.url}。错误：{data.get('errors')}。标志：{data.get('flag')}")
            return

        api_data = data.get("data", {})
        job_list_data = api_data.get("list", [])

        if not job_list_data:
            self.logger.info(
                f"在页面 {current_offset} 未找到工作岗位，参数："
                f"省份: {search_province_name}, 地区：{search_params_base['areaCode']}, 关键字：'{search_params_base['jobName']}', "
                f"类别：{request_category_name}({request_category_code}), 行业：{request_industry_name}({request_industry_code})。 "
                f"URL：{response.url}"
            )
        else:
            self.logger.info(
                f"在页面 {current_offset} 找到 {len(job_list_data)} 个工作岗位，参数："
                f"省份: {search_province_name}, 地区：{search_params_base['areaCode']}, 关键字：'{search_params_base['jobName']}', "
                f"类别：{request_category_name}({request_category_code}), 行业：{request_industry_name}({request_industry_code})。"
            )
            for job_data in job_list_data:
                item = JobItem()
                item['job_id'] = job_data.get('jobId')
                item['job_name'] = job_data.get('jobName')
                item['high_month_pay'] = job_data.get('highMonthPay')
                item['low_month_pay'] = job_data.get('lowMonthPay')
                item['update_date'] = job_data.get('updateDate')
                item['publish_date'] = job_data.get('publishDate')
                item['head_count'] = job_data.get('headCount')
                item['member_level'] = job_data.get('memberLevel')
                item['recruit_type'] = job_data.get('recruitType')
                item['degree_name'] = job_data.get('degreeName')
                item['company_name'] = job_data.get('recName')
                item['company_logo'] = job_data.get('recLogo')
                item['area_code_name'] = job_data.get('areaCodeName') 
                
                item['prinvce_code_nme'] = search_province_name 

                item['company_scale'] = job_data.get('recScale')
                item['sort_priority'] = job_data.get('sortPriority')
                item['sources_name_ch'] = job_data.get('sourcesNameCh')
                item['sources_type'] = job_data.get('sourcesType')
                item['company_tags'] = job_data.get('recTags')
                item['major_required'] = job_data.get('major')
                item['company_property'] = job_data.get('recProperty')
                item['user_type'] = job_data.get('userType')
                item['company_id'] = job_data.get('recId')
                item['key_units'] = job_data.get('keyUnits')
                item['sources_name'] = job_data.get('sourcesName')

                item['job_catory'] = request_category_name  
                item['job_industry'] = request_industry_name 

                item['search_area_code'] = search_params_base['areaCode']
                item['search_area_name'] = search_area_name 
                item['search_keyword'] = search_params_base['jobName']
                item['search_category_code'] = request_category_code 
                item['search_industry_code'] = request_industry_code 
                item['source_url'] = response.url
                
                # 提交 “结构化数据”，管道处理数据，然后存储到本地
                yield item

        pagenation_info = api_data.get("pagenation", {})
        total_pages = pagenation_info.get("total")

        if total_pages and current_offset < total_pages:
            next_offset = current_offset + 1

            params_for_next_page = search_params_base.copy()
            params_for_next_page['offset'] = next_offset
            params_for_next_page['_'] = int(time.time() * 1000)

            next_url = f"{self.base_url}?{urlencode(params_for_next_page)}"
            self.logger.info(
                f"请求下一页 {next_offset}/{total_pages}，参数："
                f"省份: {search_province_name}, 地区：{search_params_base['areaCode']}, 关键字：'{search_params_base['jobName']}', "
                f"类别：{request_category_name}({request_category_code}), 行业：{request_industry_name}({request_industry_code})。"
            )

            next_meta = response.meta.copy() 
            next_meta['current_offset'] = next_offset
            
            # 提交下一页爬取任务
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_job_list,
                meta=next_meta 
            )
        else:
            self.logger.info(
                f"没有更多页面了，参数：省份: {search_province_name}, 地区：{search_params_base['areaCode']}, "
                f"关键字：'{search_params_base['jobName']}', "
                f"类别：{request_category_name}({request_category_code}), 行业：{request_industry_name}({request_industry_code})。 "
                f"当前页 {current_offset}，总页数 {total_pages if total_pages is not None else '未知'}。"
            )