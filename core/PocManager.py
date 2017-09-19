import collections
import os
import sys
import time
import uuid
from gevent import queue
from core.RunPoc import RunPoc
from lib.core.db import DBClient
from lib.core.gevent import start_gevent_pool_skip_empty
from lib.log import logger as log
from utils import now


class PoCManager:
    def __init__(self, fb):
        self.fb = fb
        self.db = DBClient()

    def _load_poc(self, poc_vid):
        specify_pocs = {}
        poc_names = [name for name in os.listdir(self.fb.poc_setting.dir_name) if name.startswith("vb_") and name.endswith(".py")]
        if poc_vid == ["all"]:
            for poc_name in poc_names:
                vid = "_".join(poc_name.split("_")[:3])
                specify_pocs[vid] = poc_name
        else:
            for vid in poc_vid:
                for poc_name in poc_names:
                    if vid in poc_name:
                        specify_pocs[vid] = poc_name
                        break
        poc_classes = collections.defaultdict(list)
        # poc_classes = {vid1: [name1, class1], vid2: [name2, class2], vid3: [name3, class3]}
        for vid, poc in specify_pocs.items():
            try:
                module_name = "{}.{}".format(self.fb.poc_setting.dir_name, poc)[:-3].split("/")[-1]
                __import__(module_name)
                tmp = sys.modules[module_name]
                poc_classes[vid] = [module_name, getattr(tmp, getattr(tmp, "POC_NAME"))]
            except ImportError as e:
                log.warn("Failed to import PoC {}. {}".format(poc, e))
                continue
            except Exception as e:
                log.warn("Failed to load PoC {}. {}".format(poc, e))
                continue
        return poc_classes

    def run(self):
        """
        :return: result dict
                result = {task_id: {
                    poc_name1: {"poc_info": {}, "scan_info": [{}, {}, {}]},
                    poc_name2: {"poc_info": {}, "scan_info": [{}, {}, {}]},
                    poc_name3: "ERROR MESSAGE"
                }}
        """
        task_id = self.fb.task_id
        targets = self.fb.targets
        vids = self.fb.vids
        mode = self.fb.mode
        verbose = self.fb.verbose
        if not task_id:
            task_flag = False
            task_id = str(uuid.uuid4()).replace("-", "")
        else:
            task_flag = True

        start_time = time.time()
        log.info("Get task [{task_id}]: targets{targets}, mode[{mode}], verbose[{verbose}], poc_id{vid}".format(
            task_id=task_id, targets=targets, mode=mode, verbose=verbose, vid=vids))
        if task_flag:
            _now = now()[:-4]
            self.db.create_task(task_id, _now)
            self.db.create_basic(task_id, mode, _now, targets, vids)

        poc_classes = self._load_poc(vids)
        result_queue = queue.Queue()

        task_queue = queue.Queue()
        for target in targets:
            for poc_class in poc_classes.items():
                task_queue.put_nowait([target, poc_class])
                # [target, (vid1, [name1, class1])]

        task_info = {"TaskId": task_id, "Mode": mode, "Verbose": verbose}
        run_poc = [RunPoc(task_queue, task_info, result_queue, self.fb) for i in range(self.fb.poc_setting.thread_num)]

        def task():
            p = run_poc.pop()
            try:
                p.start()
            finally:
                run_poc.append(p)
        start_gevent_pool_skip_empty(self.fb.poc_setting.thread_num, task)

        results_list = []
        results = {task_id: collections.defaultdict(dict)}
        while not result_queue.empty():
            # tmp = [poc_name, poc.poc_info, poc.scan_info]
            tmp = result_queue.get_nowait()
            results_list.append(tmp)
            results[task_id][tmp[0]] = {"poc_info": {}, "scan_info": []}
        for result in results_list:
            results[task_id][result[0]]["scan_info"].append(result[2])
            if results[task_id][result[0]]["poc_info"]:
                continue
            results[task_id][result[0]]["poc_info"] = result[1]

        stop_time = time.time()
        log.info("Finish task [{task_id}](used {time}s): targets{targets}, mode[{mode}], verbose[{verbose}]".format(
            task_id=task_id, time=round(stop_time - start_time, 2), targets=targets, mode=mode, verbose=verbose))
        if task_flag:
            _now = now()[:-4]
            self.db.save_result(task_id, results[task_id], _now)
            self.db.save_basic(task_id, _now)
        else:
            return results[task_id]

    @classmethod
    def get_task_result(cls, task_id):
        cls.db = DBClient()
        results = cls.db.get_result(task_id)
        if results:
            return results
        else:
            return False

    @classmethod
    def exit_write2db(cls, task_id):
        cls.db = DBClient()
        cls.db.save_result(task_id, "Process timeout and has terminated.", now()[:-4])

    @classmethod
    def check_task_exist(cls, task_id):
        cls.db = DBClient()
        results = cls.db.get_result(task_id)
        return True if results else False
