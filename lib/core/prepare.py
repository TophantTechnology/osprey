from requests.cookies import RequestsCookieJar
from urllib.parse import urlparse
from lib.core.datatype import AttribDict
from lib.log import logger as log
from lib.payload import human_headers
from lib.core.req import request_init


def prepare(options):
    prepare_http_headers(options)
    fb = prepare_fb(options)
    return fb


def prepare_http_headers(options):
    headers = human_headers
    cookies = RequestsCookieJar()
    proxies = {}
    params = {}

    def check_cookies(cookies_setting):
        if not cookies_setting:
            return {}
        _cookies = RequestsCookieJar()
        try:
            for item in cookies_setting.split("&"):
                name, value = item.split("=", 1)
                _cookies.set(name.strip(), value.strip())
        except Exception as e:
            log.error("Cookies setting wrong, please specify a cookies string like vul=box&free=buff\n{}".format(str(e)))
            return RequestsCookieJar()
        return _cookies

    def check_proxy(proxy_setting):
        if not proxy_setting:
            return {}
        try:
            parse_result = urlparse(proxy_setting)
            scheme = parse_result.scheme
            netloc = parse_result.netloc.split(":")
            host = netloc[0]
            port = int(netloc[1])
            assert all([scheme, scheme in ["http", "socks5", "socks5"], host, port])
        except Exception as e:
            log.error("proxy setting wrong, please specify a string like http|socks4|socks5://address:port\n{}".format(str(e)))
            return {}
        _p = "{}://{}:{}".format(scheme, host, port)
        proxies = {"http": _p, "https": _p}
        return proxies

    def check_headers(headers_setting):
        if not headers_setting:
            return None
        header = {}
        try:
            for item in headers_setting.split("&"):
                name, value = item.split("=", 1)
                header[name.strip()] = value.strip()
        except Exception as e:
            log.error("HTTP headers setting wrong, please specify a string like vul=box&free=buff\n{}".format(str(e)))
            return None
        return header

    if options.cookies and options.cookies != "x":
        cookies = check_cookies(options.cookies)

    if options.proxy and options.proxy != "x":
        proxies = check_proxy(options.proxy)

    if options.headers and options.headers != "x":
        more_headers = check_headers(options.headers)
        if len(more_headers):
            for name, value in more_headers.items():
                headers[name] = value

    request_init(headers=headers, proxies=proxies, params=params, cookies=cookies)


def prepare_fb(options):
    fb = AttribDict()
    fb.targets = options.targets.split(",")
    try:
        fb.task_id = options.task_id
    except AttributeError:
        fb.task_id = None
    fb.vids = options.vids.strip().split(",")
    fb.mode = options.mode
    fb.verbose = False if options.quiet else True
    fb.console = options.from_console

    fb.poc_setting = AttribDict()
    fb.poc_setting.dir_name = options.poc_dir_name
    fb.poc_setting.timeout = options.timeout
    fb.poc_setting.thread_num = options.thread
    fb.poc_setting.return_resp = options.poc_return_dump

    fb.spider = options.spider

    return fb