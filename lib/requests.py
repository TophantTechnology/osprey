import inspect
import urllib3
from lib.core.req import requests
from functools import wraps
from thirdparty.requests_toolbelt.utils import dump
from lib.core.db import DBClient
from lib.log import logger as log
from settings import save_http_dump, req_timeout


urllib3.disable_warnings()
PROXIES_DICT = ""


def request_config(func, *args, **kwargs):
    pass


def response_dump(resp):
    # save request and response raw data to Database
    try:
        caller_poc_object = inspect.currentframe().f_back.f_back.f_back.f_locals['self']
        caller_poc_object_scan_info = caller_poc_object.scan_info
        caller_poc_object_poc_info = caller_poc_object.poc_info
        data = {}
        data["task_id"] = caller_poc_object_scan_info.get("TaskId", "")
        data["target"] = caller_poc_object_scan_info.get("Target", "")
        data["vid"] = caller_poc_object_poc_info.get("poc", dict()).get("Id", "")
    except Exception as e:
        # log.warn(e)
        return
    if not (data["task_id"] and data["target"] and data["vid"]):
        return
    dump_data = dump.dump_all(resp)
    # dump_data has request_prefix=b'< ' and response_prefix=b'> ', use them to split line if necessary
    for codec in ["utf-8", "gbk"]:
        try:
            data["response"] = dump_data.decode(codec)
            break
        except Exception as e:
            continue
    if not data.get("response", ""):
        data["response"] = str(dump_data)
    response = data.pop("response")
    db = DBClient()
    db.save_response(data, response)


def requests_wapper(request_config, response_dump):
    def decorate(func):
        @wraps(func)
        def call(*args, **kwargs):
            request_config(func, *args, **kwargs)
            result = func(*args, **kwargs)
            if result is not None and save_http_dump:
                response_dump(result)
            return result
        return call
    return decorate


@requests_wapper(request_config, response_dump)
def req(url, method, **kwargs):
    try:
        kwargs.setdefault("timeout", req_timeout)
        kwargs.setdefault("verify", False)
        resp = getattr(requests, method)(url, **kwargs)
    except Exception:
        raise
    return resp


def get_html(url, **kwargs):
    response = req(url, "get", **kwargs)
    html = response.content if response else b""
    return html
