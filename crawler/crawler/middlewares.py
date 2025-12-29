# 中间件核心逻辑
import random
import time
import requests
import threading
import json
from collections import deque

from scrapy.exceptions import NotConfigured, IgnoreRequest
from twisted.internet.error import (
    ConnectionRefusedError, TCPTimedOutError, ConnectionDone, ConnectError,
    ConnectionLost, DNSLookupError, TimeoutError as TwistedTimeoutError
)
from twisted.web.client import ResponseFailed
from scrapy.utils.log import logger

# 安全网关域名列表（识别异常代理）
SECURITY_GATEWAY_DOMAINS = [
    'zscaler', 'fortinet', 'barracuda', 'checkpoint', 'paloaltonetworks',
    'forcepoint', 'websense', 'cisco.com', 'trustwave', 'sophos', 'mcafee',
    'imperva', 'akamai', 'cloudflare'
]

class RandomUserAgentMiddleware:
    """随机User-Agent中间件"""
    def __init__(self, user_agent_list):
        self.user_agent_list = user_agent_list
        # 列表为空时使用默认UA
        if not self.user_agent_list:
            self.user_agent_list = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36 Scrapy/VERSION'
            ]
            logger.warning("USER_AGENT_LIST为空，使用默认User-Agent")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENT_LIST'))

    def process_request(self, request, spider):
        # 未设置UA时随机分配
        if self.user_agent_list and b'User-Agent' not in request.headers:
            user_agent = random.choice(self.user_agent_list)
            request.headers[b'User-Agent'] = user_agent.encode('utf-8')
        return None

class EnhancedProxyPoolMiddleware:
    """增强版代理池中间件：API拉取代理、自动轮换、失败重试"""
    # 代理重试异常类型
    PROXY_RETRY_EXCEPTIONS = (
        TwistedTimeoutError, TCPTimedOutError, ConnectionRefusedError,
        ConnectionDone, ConnectError, ConnectionLost, DNSLookupError,
        ResponseFailed,
        requests.exceptions.Timeout, requests.exceptions.ConnectionError,
        IOError,
    )
    # 代理重试HTTP状态码
    PROXY_RETRY_HTTP_CODES = {400, 403, 407, 429, 500, 502, 503, 504, 520, 522, 524}

    def __init__(self, settings):
        # 未启用则抛出异常
        if not settings.getbool('PROXY_POOL_ENABLED', False):
            raise NotConfigured("EnhancedProxyPoolMiddleware未启用（PROXY_POOL_ENABLED=False）")
        
        # 读取配置
        self.proxy_pool_url = settings.get('PROXY_POOL_URL')
        if not self.proxy_pool_url or self.proxy_pool_url == "YOUR_NEW_PROXY_POOL_API_URL_HERE":
            raise NotConfigured("PROXY_POOL_URL未配置或为占位符")
        
        self.api_timeout = settings.getint('PROXY_POOL_API_TIMEOUT', 10)
        self.proxy_request_timeout = settings.getint('PROXY_REQUEST_TIMEOUT', 20)
        self.max_proxy_retries_per_request = settings.getint('PROXY_POOL_MAX_REQUEST_RETRIES', 3)
        self.fetch_cooldown_seconds = settings.getint('PROXY_FETCH_COOLDOWN_SECONDS', 10)
        self.min_pool_size_to_fetch = settings.getint('PROXY_MIN_POOL_SIZE_FETCH', 5)
        self.max_consecutive_fails_remove = settings.getint('PROXY_MAX_CONSECUTIVE_FAILS_REMOVE', 3)
        self.min_score_remove = settings.getfloat('PROXY_MIN_SCORE_REMOVE', 0.1)

        # 代理池存储（双端队列）
        self.proxies_deque = deque()
        self.lock = threading.Lock()  # 线程锁（保护代理池操作）
        self.last_fetch_time = 0

        # 初始化请求会话
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'ScrapyProxyFetcher/1.0'})

        logger.info(f"增强版代理池中间件已启用，代理API地址：{self.proxy_pool_url}")
        self._fetch_new_proxies()  # 初始化拉取代理

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def _fetch_new_proxies(self):
        """从API拉取新代理（带冷却、数量校验）"""
        with self.lock:
            current_time = time.time()
            # 冷却时间内不请求
            if current_time - self.last_fetch_time < self.fetch_cooldown_seconds:
                return False
            # 代理池充足时不请求
            if self.proxies_deque and len(self.proxies_deque) >= self.min_pool_size_to_fetch:
                return False
            self.last_fetch_time = current_time

        logger.info(f"开始从API拉取新代理：{self.proxy_pool_url}")
        try:
            response = self.session.get(self.proxy_pool_url, timeout=self.api_timeout)
            response.raise_for_status()
            api_data = response.json()

            # 适配新API格式：{"status":"0", "list":[{"sever":"ip", "port":port_num}]}
            if api_data.get("status") == "0":
                proxy_items_from_api = api_data.get("list", [])
                if not isinstance(proxy_items_from_api, list):
                    logger.error("代理API返回成功状态，但list字段非列表")
                    return False

                fetched_proxies_count = 0
                newly_added_proxies_log = []
                with self.lock:
                    current_pool_ips = {p['ip_port'] for p in self.proxies_deque}
                    # 解析代理列表并去重添加
                    for item in proxy_items_from_api:
                        if isinstance(item, dict):
                            ip = item.get("sever")
                            port = item.get("port")
                            if ip and port:
                                try:
                                    ip_port_str = f"{ip}:{int(port)}"
                                    if ip_port_str not in current_pool_ips:
                                        proxy_obj = {
                                            "ip_port": ip_port_str, "score": 1.0, "last_used": 0,
                                            "fail_count": 0, "success_count": 0, "consecutive_fails": 0
                                        }
                                        self.proxies_deque.append(proxy_obj)
                                        newly_added_proxies_log.append(ip_port_str)
                                        fetched_proxies_count += 1
                                except ValueError:
                                    logger.warning(f"代理端口格式错误：{item}")
                            else:
                                logger.warning(f"代理字段缺失（sever/port）：{item}")
                        else:
                            logger.warning(f"代理格式错误：{item}")
                
                if fetched_proxies_count > 0:
                    logger.info(f"成功拉取{fetched_proxies_count}个新代理，当前池大小：{len(self.proxies_deque)}")
                else:
                    logger.info("代理API返回无新代理或列表为空")
                return True
            else:
                error_message = api_data.get('msg', '无错误信息')
                logger.error(f"代理API返回失败状态：{api_data.get('status')}，错误信息：{error_message}")

        except requests.exceptions.Timeout:
            logger.error(f"代理API请求超时（{self.api_timeout}s）")
        except requests.exceptions.RequestException as e:
            logger.error(f"代理API请求异常：{e}")
        except json.JSONDecodeError:
            logger.error(f"代理API返回非JSON格式：{response.text[:300] if 'response' in locals() else 'N/A'}")
        except Exception as e:
            logger.error(f"代理拉取未知异常：{e}", exc_info=True)
        
        return False

    def _get_proxy(self):
        """从代理池获取代理（轮询）"""
        if not self.proxies_deque:
            return None
        # 轮询：左出右入
        proxy = self.proxies_deque.popleft()
        self.proxies_deque.append(proxy)
        proxy['last_used'] = time.time()
        return proxy

    def _update_proxy_stats(self, proxy_ip_port, success):
        """更新代理状态（分数/失败次数），低于阈值则移除"""
        found_proxy_obj = None
        for p_obj in self.proxies_deque:
            if p_obj['ip_port'] == proxy_ip_port:
                found_proxy_obj = p_obj
                break
        if not found_proxy_obj:
            return

        # 更新状态
        if success:
            found_proxy_obj['score'] = min(1.0, found_proxy_obj['score'] + 0.05)
            found_proxy_obj['success_count'] += 1
            found_proxy_obj['consecutive_fails'] = 0
        else:
            found_proxy_obj['score'] = max(0.0, found_proxy_obj['score'] - 0.2)
            found_proxy_obj['fail_count'] += 1
            found_proxy_obj['consecutive_fails'] += 1

        # 低分/连续失败代理移除
        if found_proxy_obj['score'] < self.min_score_remove or found_proxy_obj['consecutive_fails'] >= self.max_consecutive_fails_remove:
            logger.warning(f"移除低质量代理：{found_proxy_obj['ip_port']}（分数：{found_proxy_obj['score']:.2f}，连续失败：{found_proxy_obj['consecutive_fails']}）")
            try:
                new_deque = deque(p for p in self.proxies_deque if p['ip_port'] != found_proxy_obj['ip_port'])
                self.proxies_deque.clear()
                self.proxies_deque.extend(new_deque)
            except Exception as e:
                logger.error(f"代理移除异常：{e}")

    def process_request(self, request, spider):
        """请求处理：分配代理（无代理则拉新）"""
        # 重试请求保留原有代理
        if request.meta.get('proxy') and request.meta.get('_proxy_retry_count', 0) > 0:
            return None

        # 代理池不足时拉新
        needs_fetch_check = False
        with self.lock:
            if not self.proxies_deque or len(self.proxies_deque) < self.min_pool_size_to_fetch:
                needs_fetch_check = True
        if needs_fetch_check:
            self._fetch_new_proxies()

        # 分配代理
        proxy_obj_to_use = None
        with self.lock:
            if self.proxies_deque:
                proxy_obj_to_use = self._get_proxy()

        if proxy_obj_to_use:
            ip_port = proxy_obj_to_use['ip_port']
            proxy_url = f"http://{ip_port}"  # 新代理无需认证
            request.meta['proxy'] = proxy_url
            request.meta['_current_proxy_obj'] = proxy_obj_to_use
            request.meta['download_timeout'] = self.proxy_request_timeout
            logger.debug(f"使用代理 {proxy_url} 访问 {request.url}（分数：{proxy_obj_to_use['score']:.2f}）")
        else:
            logger.warning(f"无可用代理，{request.url} 将直接请求")
        return None

    def _handle_proxy_failure(self, request, spider, reason_msg):
        """代理失败处理：更新状态+重试（未达最大次数则换代理）"""
        current_proxy_obj = request.meta.get('_current_proxy_obj')
        if current_proxy_obj:
            with self.lock:
                self._update_proxy_stats(current_proxy_obj['ip_port'], success=False)
            logger.info(f"代理 {current_proxy_obj['ip_port']} 访问 {request.url} 失败：{reason_msg}")

        # 重试次数校验
        retry_count = request.meta.get('_proxy_retry_count', 0)
        if retry_count < self.max_proxy_retries_per_request:
            new_request = request.copy()
            new_request.meta['_proxy_retry_count'] = retry_count + 1
            new_request.dont_filter = True  # 避免被去重过滤
            # 清空旧代理信息
            if 'proxy' in new_request.meta: del new_request.meta['proxy']
            if '_current_proxy_obj' in new_request.meta: del new_request.meta['_current_proxy_obj']
            
            logger.info(f"重试 {request.url}（代理重试次数：{retry_count + 1}/{self.max_proxy_retries_per_request}）")
            return new_request
        else:
            logger.error(f"{request.url} 代理重试次数达上限（{self.max_proxy_retries_per_request}），放弃重试")
            return None

    def process_response(self, request, response, spider):
        """响应处理：校验代理有效性（重定向/HTTP状态码/API返回）"""
        current_proxy_obj = request.meta.get('_current_proxy_obj')

        # 1. 检测重定向到安全网关（代理被识别）
        if response.status in (301, 302, 303, 307, 308) and 'Location' in response.headers:
            redirect_url = response.headers.get('Location', b'').decode('utf-8', errors='ignore').lower()
            for domain in SECURITY_GATEWAY_DOMAINS:
                if domain in redirect_url:
                    logger.warning(f"代理 {current_proxy_obj['ip_port'] if current_proxy_obj else 'N/A'} 访问 {request.url} 被重定向到安全网关：{redirect_url[:120]}")
                    if current_proxy_obj:
                        retry_req = self._handle_proxy_failure(request, spider, f"重定向到安全网关（{domain}）")
                        if retry_req: return retry_req

        # 2. 校验API返回有效性（200状态码+flag=true）
        if current_proxy_obj:
            proxy_ip_port = current_proxy_obj['ip_port']
            success_on_target_api_level = False

            if response.status == 200:
                try:
                    api_response_data = json.loads(response.text)
                    if api_response_data.get("flag") is True:
                        success_on_target_api_level = True
                    else:
                        error_info = api_response_data.get("errors", "无具体错误信息")
                        logger.warning(f"代理 {proxy_ip_port} 访问 {request.url} 返回200但API失败：{error_info}")
                except json.JSONDecodeError:
                    logger.warning(f"代理 {proxy_ip_port} 访问 {request.url} 返回非JSON数据：{response.text[:200]}")
                
                # 更新代理状态
                with self.lock:
                    self._update_proxy_stats(proxy_ip_port, success_on_target_api_level)
                
                # API返回失败则重试
                if not success_on_target_api_level:
                    retry_req = self._handle_proxy_failure(request, spider, "API返回失败（200 OK）")
                    if retry_req: return retry_req

            # 3. 处理需重试的HTTP状态码
            elif response.status in self.PROXY_RETRY_HTTP_CODES:
                logger.info(f"代理 {proxy_ip_port} 访问 {request.url} 返回HTTP {response.status}")
                retry_req = self._handle_proxy_failure(request, spider, f"HTTP {response.status}")
                if retry_req: return retry_req

            # 4. 其他4xx/5xx状态码标记代理失败
            elif response.status >= 400:
                logger.warning(f"代理 {proxy_ip_port} 访问 {request.url} 返回未处理的HTTP {response.status}")
                with self.lock:
                    self._update_proxy_stats(proxy_ip_port, success=False)

        return response

    def process_exception(self, request, exception, spider):
        """异常处理：代理相关异常则换代理重试"""
        current_proxy_obj = request.meta.get('_current_proxy_obj')
        if current_proxy_obj and isinstance(exception, self.PROXY_RETRY_EXCEPTIONS):
            retry_req = self._handle_proxy_failure(request, spider, exception.__class__.__name__)
            if retry_req:
                return retry_req
        return None