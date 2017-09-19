import requests
import traceback
from functools import partial
from gevent import queue
from gevent.pool import Pool
from lib.log import logger as log



def start_gevent_pool_skip_empty(thread_num, func, *args, **kwargs):
    gevent_pool = Pool(thread_num)
    for i in range(thread_num):
        gevent_pool.spawn(partial(gevent_skip_empty_func, func, *args, **kwargs))
    gevent_pool.join()


def gevent_skip_empty_func(func, *args, **kwargs):
    while True:
        try:
            func(*args, **kwargs)
        except queue.Empty:
            break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            log.warn(e)
        except Exception:
            log.error(traceback.format_exc())
            continue