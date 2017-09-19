import os
import psutil
import signal
from core.PocManager import PoCManager
from lib.log import logger as log
from settings import PROGRAM, DST_FILE
from web.SubProcess import SubProcess


def start_poc_task(task_data):
    def kill_child_processes(parent_pid, sig=signal.SIGTERM):
        try:
            p = psutil.Process(parent_pid)
        except psutil.NoSuchProcess:
            return
        child_pid = p.children(recursive=True)
        for pid in child_pid:
            os.kill(pid.pid, sig)

    cmd_list = [PROGRAM, DST_FILE]
    cmd_list.extend(['''--target={}'''.format(task_data.get("target", ""))])
    cmd_list.extend(['''--vid={}'''.format(task_data.get("vid", ""))])
    cmd_list.extend(['''--task_id={}'''.format(task_data.get("task_id", ""))])
    cmd_list.extend(['''--mode={}'''.format(task_data.get("mode", "verify"))])
    cmd_list.extend(['''--quiet''' if not task_data.get("verbose", True) else ""])
    cmd_list.extend(['''--cookies={}'''.format(task_data.get("cookies", "x"))])
    cmd_list.extend(['''--proxy={}'''.format(task_data.get("proxy", "x"))])
    cmd_list.extend(['''--headers={}'''.format(task_data.get("headers", "x"))])
    if task_data.get("poc_dir"):
        cmd_list.extend(['''--poc-dir={}'''.format(task_data.get("poc_dir"))])

    manager_process = SubProcess(cmd_list).run()

    # Process timeout
    if manager_process['status'] == 1:
        process = manager_process['proc']
        log.info("process {} is timeout when scanning [{}]-[{}]-[{}],terminating...".format(
            process.pid, task_data.get("task_id"), task_data.get("vid", ""), task_data.get("target", "")))
        PoCManager.exit_write2db(task_data.get("task_id", ""))

        kill_child_processes(process.pid)
        process.kill()
        process.wait()

    if manager_process['status'] == -1:
        process = manager_process['proc']
        log.info("process {} is been revoked when scanning [{}]-[{}].".format(
            process.pid, task_data.get("vid", ""), task_data.get("target", "")))
