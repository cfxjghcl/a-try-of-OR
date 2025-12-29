# Scrapy 项目核心配置文件
BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# 不遵守robots.txt（API爬取场景通用配置）
ROBOTSTXT_OBEY = False

# --- User-Agent 配置 ---
# 随机User-Agent列表，用于反反爬
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
]

# --- 默认请求头配置 ---
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://24365.ncss.cn/student/jobs/jobslist/',  # 模拟前端请求来源
    'X-Requested-With': 'XMLHttpRequest',  # 标识AJAX请求
}

# --- 数据管道配置 ---
# 仅启用JobPipeline处理爬取到的JobItem数据（JSON存储）
ITEM_PIPELINES = {
   'crawler.pipelines.JobPipeline': 500
}

# --- 下载中间件配置（顺序影响执行逻辑） ---
DOWNLOADER_MIDDLEWARES = {
    # 1. 随机User-Agent中间件（反反爬核心）
    'crawler.middlewares.RandomUserAgentMiddleware': 300,
    # 2. 代理池中间件（IP轮换，避免封禁）
    'crawler.middlewares.EnhancedProxyPoolMiddleware': 500,
    # 3. Scrapy内置重试中间件（处理非代理类请求失败）
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    # 4. 重定向中间件
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    # 5. HTTP代理中间件（应用request.meta中的proxy配置）
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    # 6. 下载超时中间件
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
}

# --- 代理池配置 ---
PROXY_POOL_ENABLED = True
PROXY_POOL_URL = "http://api.89ip.cn/tqdl.html?api=1&num=60&port=&address=&isp="
PROXY_POOL_API_TIMEOUT = 5          # 代理API请求超时时间
PROXY_REQUEST_TIMEOUT = 10          # 代理请求超时时间
PROXY_POOL_MAX_REQUEST_RETRIES = 3  # 单请求最大代理重试次数
PROXY_FETCH_COOLDOWN_SECONDS = 180  # 代理API请求冷却时间
PROXY_MIN_POOL_SIZE_FETCH = 5       # 代理池最小数量阈值（低于则拉新）

# --- 并发与延迟配置（反爬关键） ---
DOWNLOAD_DELAY = 1                  # 同域名请求基础延迟
CONCURRENT_REQUESTS = 16            # 全局最大并发请求数
CONCURRENT_REQUESTS_PER_DOMAIN = 4  # 单域名最大并发请求数

# --- 自动限速配置 ---
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = DOWNLOAD_DELAY
AUTOTHROTTLE_MAX_DELAY = 5
AUTOTHROTTLE_TARGET_CONCURRENCY = 2
AUTOTHROTTLE_DEBUG = False

# --- 内置重试中间件配置 ---
RETRY_ENABLED = True
RETRY_TIMES = 2                     # 基础重试次数（不含代理重试）
RETRY_HTTP_CODES = [500, 502, 503, 504, 520, 522, 524, 408, 429]  # 需重试的HTTP状态码
RETRY_EXCEPTIONS = [
    "twisted.internet.defer.TimeoutError",
    "twisted.internet.error.TimeoutError",
    "twisted.internet.error.DNSLookupError",
    "twisted.internet.error.ConnectionRefusedError",
    "twisted.internet.error.ConnectionDone",
    "twisted.internet.error.ConnectError",
    "twisted.internet.error.ConnectionLost",
    "twisted.internet.error.TCPTimedOutError",
    "twisted.web.client.ResponseFailed",
    "scrapy.core.downloader.handlers.http11.TunnelError",
    TimeoutError,
]

# --- Cookie配置 ---
COOKIES_ENABLED = False  # 无状态API场景禁用Cookie

# --- HTTP缓存配置（动态数据禁用） ---
HTTPCACHE_ENABLED = False

# --- 日志配置 ---
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# --- 全局下载超时 ---
DOWNLOAD_TIMEOUT = 10