import requests
from gevent import Timeout
from lib.core.db import DBClient
from lib.log import logger as log
from utils import tree


class RunPoc:
    def __init__(self, task_queue, task_info, result_queue, fb):
        self.task_queue = task_queue
        self.result = result_queue
        self.task_id = task_info["TaskId"]
        self.verbose = task_info["Verbose"]
        self.mode = task_info["Mode"]
        self.fb = fb

    def start(self):
        task = self.task_queue.get(block=False)
        # [target, (vid1, [name1, class1])]
        target = task[0]
        poc_vid = task[1][0]
        poc_name = task[1][1][0].split(".")[-1]
        poc = task[1][1][1]()

        poc.scan_info = {
            'TaskId': self.task_id,
            'Target': target,
            'Verbose': self.verbose,
            'Error': '',
            'Mode': self.mode,
            'Success': False,
            'Ret': tree(),
            "risk_category": poc.scan_info.get('risk_category', '')
        }
        poc.poc_info["poc"]["Class"] =  task[1][1][1].__name__

        timeout = Timeout(self.fb.poc_setting.timeout)
        timeout.start()
        try:
            log.info("{} - {} start...".format(poc_vid, target))
            poc.run(fb=self.fb)
            log.info("{} - {} finish.".format(poc_vid, target))
        except Timeout:
            poc.scan_info['Error'] = "PoC run timeout."
            poc.scan_info['Success'] = False
            log.error("{} - {} error: PoC run timeout.".format(poc_vid, target))
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            poc.scan_info['Error'] = str(e)
            poc.scan_info['Success'] = False
            log.error("{} - {} error: {}.".format(poc_vid, target, e))
        except Exception:
            import traceback
            err = traceback.format_exc()
            poc.scan_info['Error'] = err
            poc.scan_info['Success'] = False
            log.error("{} - {} error: {}.".format(poc_vid, target, err))
        finally:
            timeout.cancel()
        if not poc.scan_info.get("Success", False):
            return
        if self.fb.poc_setting.return_resp:
            poc.scan_info["req_resp"] = self._get_http_data(poc_vid, target)
        self.result.put_nowait([poc_name, poc.poc_info, poc.scan_info])

    def _get_http_data(self, vid, target):
        self.db = DBClient()
        data = {"task_id": self.task_id, "target": target, "vid": vid}
        results = self.db.get_response(data)
        return results.get("response", "") if results else None
