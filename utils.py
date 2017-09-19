import datetime
import re
import requests
from collections import defaultdict
from lib.log import logger as log
from lib.requests import req
from os.path import normpath
from posixpath import normpath
from urllib.parse import urlparse, urljoin, urlunparse



def tree():
    """create data struct tree"""
    return defaultdict(tree)


def now():
    """return current time, 2017-01-01 12:26:10,567"""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]


def is_same_domain(url1, url2):
    """
    check site origin between two url
    notice that urls with different port/protocol will be regarded as same origin
    """
    try:
        return True if urlparse(url1).netloc.split(':')[0] == urlparse(url2).netloc.split(':')[0] else False
    except Exception as e:
        return False


def retrieve_url_from_page(p_url, keyword=None, depth=1):
    """get specify url in src/action/href in html page
       keyword(optional) must be list type
    """
    pattern = re.compile(b'''(?:href|action|src)\s*?=\s*?(?:"|')\s*?([^'"]+)(?:"|')''')
    results = []
    pool = [p_url]
    while depth:
        tmp = []
        for url in pool:
            try:
                page_content = get_html(url)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                continue
            match = re.findall(pattern, page_content)
            for item in match:
                item = get_absolute_url(url, item.decode())
                if is_same_domain(url, item):
                    tmp.append(item)
        results.extend(tmp)
        pool = tmp
        depth = depth - 1

    if keyword:
        tmp = []
        for url in results:
            for word in keyword:
                if word in url:
                    tmp.append(url)
                    break
        results = tmp
    return results


def retrieve_url_from_spider(spider):
    if spider != "x":
        try:
            with open(spider, "r") as f:
                return [url.strip() for url in f.readlines()]
        except Exception as e:
            log.error("open spider file failed. {}".format(e))
            return []
    else:
        return []


def get_absolute_url(base, url):
    """get absolute URL"""
    url1 = urljoin(base, url)
    arr = urlparse(url1)
    path = normpath(arr[2])
    return urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))


def normalize_url(url):
    """normalize the URL as http://xxxx/"""
    url = url.strip()
    if not url.startswith('http'):
        url = "http://" + url
    if urlparse(url).path == "":
        url = url + '/'
    return url


def valid_status_code(status_code):
    """valid the response's status_code
    return False if status_code is >= 400
    """
    if not (str(status_code).startswith('4') or str(status_code).startswith('5')):
        return True
    return False


def target_handler(target, port=None, payload=None):
    """join the port and payload"""
    list_temp = []
    target_up = urlparse(target)

    if target_up.scheme and target_up.netloc:
        schm = target_up.scheme
        netloc = target_up.netloc
        if port and not payload:
            port = str(port)
            if target_up.port:
                temp_netloc = netloc[:netloc.find(':' + str(target_up.port))]
                temp_target = schm + '://' + temp_netloc + ':' + port + '/'
                list_temp.append(temp_target)
            else:
                temp_target = schm + '://' + netloc + ':' + port + '/'
                list_temp.append(temp_target)
        if payload and not port:
            temp_target = urljoin(target, payload)
            list_temp.append(temp_target)
            if target_up.port:
                temp_netloc = netloc[:netloc.find(':' + str(target_up.port))]
                temp_target = schm + '://' + temp_netloc + '/'
                temp_target = urljoin(temp_target, payload)
                list_temp.append(temp_target)
        if payload and port:
            port = str(port)
            temp_target = urljoin(target, payload)
            list_temp.append(temp_target)
            if target_up.port:
                temp_netloc = netloc[:netloc.find(':' + str(target_up.port))]
                temp_target = schm + '://' + temp_netloc + ':' +  port + '/'
                list_temp.append(temp_target)
                temp_target = urljoin(temp_target, payload)
                list_temp.append(temp_target)
            else:
                temp_target = schm + '://' + netloc + ':' + port + '/'
                temp_target = urljoin(temp_target, payload)
                list_temp.append(temp_target)
        if target_up.path and target_up.path != '/':
            temp_target = schm + '://' + netloc + '/'
            list_temp.append(temp_target)
        list_temp.append(target)
    return list_temp


def get_scan_info(scan_info):
    """get Target and Verbose in scan_info"""
    return normalize_url(scan_info.get('Target', '')), scan_info.get('Verbose', False)


def isIP(target):
    """is IP or not"""
    regexp = '^(\d{1,3}\.){3}\d{1,3}$'
    res = re.match(regexp, target)
    return False if res is None else True


def get_html(url, **kwargs):
    """initiate a GET request and return the response body(bytes)"""
    response = req(url, "get", **kwargs)
    html = response.content if hasattr(response, "content") else b""
    return html


def url_join(base, url):
    """join url"""
    url1 = urljoin(base, url)
    arr = urlparse(url1)
    path = normpath(arr[2])
    if url[-1] == '/':
        return urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment)) + '/'
    return urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))


def info(message):
    """info log"""
    log.info(message)


def warn(message):
    """warn log"""
    log.warn(message)


def error(message):
    """error log"""
    log.error(message)


def highlight(message):
    """highlight log"""
    log.highlight(message)
