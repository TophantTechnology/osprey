import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from celery import Celery
from flask import Flask, jsonify, request, redirect, url_for
from core.PocManager import PoCManager
from settings import API_HOST, API_PORT, CELERY_BROKER
from web.check import check_task_id
from web.task import start_poc_task
os.chdir("../")


app = Flask(__name__, static_folder="{}/web/static".format(os.getcwd()))
celery = Celery("PoC-framework", broker=CELERY_BROKER)


@app.route('/')
def index():
    return redirect(url_for("static", filename="index.html"))


@app.route('/api/start', methods=["POST"])
def start_task():
    post_data = request.get_json(force=True)
    task_data = {}
    task_data["task_id"] = post_data.get("task_id", "")
    if not task_data["task_id"]:
        return jsonify(status=400, message="Missing Parameter 'task_id'.", data="POST[task_id]")
    if PoCManager.check_task_exist(task_data["task_id"]):
        return jsonify(status=400, message="Task exist.", data=task_data["task_id"])
    task_data["target"] = post_data.get("target", "")
    if not task_data["target"]:
        return jsonify(status=400, message="Missing Parameter 'target'.", data="POST[target]")
    task_data["vid"] = post_data.get("vid", "")
    if not task_data["vid"]:
        return jsonify(status=400, message="Missing Parameter 'vid'.", data="POST[vid]")
    task_data["mode"] = post_data.get("mode", "verify")
    task_data["verbose"] = post_data.get("verbose", True)
    task_data["cookies"] = post_data.get("cookies", "x")
    task_data["headers"] = post_data.get("headers", "x")
    task_data["proxy"] = post_data.get("proxy", "x")
    task_data["poc_dir"] = post_data.get("poc_dir", None)

    start_task_func.delay(task_data)
    return jsonify(status=200)


@app.route('/api/result', methods=["POST"])
def get_result():
    post_data = request.get_json(force=True)
    task_id = post_data.get("task_id", "")
    if not task_id:
        return jsonify(status=400, message="Missing Parameter 'task_id'.", data="POST[task_id]")

    if not check_task_id(task_id):
        return jsonify(status=400, message="task_id error")

    results = PoCManager.get_task_result(task_id)
    if not results:
        return jsonify(status=400, message="Task no found.")
    else:
        results_Success = list(results.values())[0]['scan_info'][0]['Success']
        if results_Success:
            return jsonify(results)
        else:
            return jsonify(status=201, message="not vuln")


@celery.task(queue="poc-queue")
def start_task_func(task_data):
    start_poc_task(task_data)


if __name__ == '__main__':
    app.run(host=API_HOST, port=API_PORT)
