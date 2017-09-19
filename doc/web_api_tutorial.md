# Web API接口使用说明文档

osprey提供了一个可供调用的Web API接口，可用于构建一个在线漏洞扫描器。

osprey-web使用Flask提供Web Service，使用Celery以任务队列的形式调度和下发检测任务。

### 接口说明

##### 下发任务

- url: http://domain:port/api/start
- method: POST
- type: JSON
- data: task_id, vid, target, [mode, verbose, cookies, headers, proxy]
- tips: target和vid参数可以为一个或多个，对该接口的每一次访问被视为一个检测任务

```python
import requests, json

url = "http://domain:port/api/start"
data = {"task_id": "xxxxxx", "vid": "vb_2017_0001", "target": "http://target_domain/", "mode": "verify", "verbose": "True", "cookies": "key1=value1&key2=value2", "headers": "h1=v1&h2=v2", "proxy": "http://host:port/"}

requests.post(url=url, data=json.dumps(data))

```

- return: JSON格式的结果

```python
{"status": 200}    # 任务下发成功
{"status": 400, "message": "xxxx", "data": "xxxx"}    # 任务下发失败与提示信息
```

##### 获取结果

- url: http://domain:port/api/result
- method: POST
- type: JSON
- data: task_id

```python
import requests, json

url = "http://domain:port/api/result"
data = {"task_id": "xxxxxx"}

requests.post(url=url, data=data)
```

- return: JSON格式的结果

```python
# 数据库中找不到对应的task_id号，表示无该任务，返回：
{"status": 400, "message": "Task no found."}

# 任务还未执行完，返回：
{"status": 201, "message": "Have Submitted Task, Please Wait."}

# 任务执行超时，返回：
{"status": 201, "message": "Process timeout and has terminated."}

# 任务执行成功，返回检测结果，检测结果数据结构如下：
result = {
"vb_xxxx": {"poc_info": {}, "scan_info": []},    # scan_info为一个列表，对应下发任务时指定的一个或多个target
"vb_yyyy": {"poc_info": {}, "scan_info": []},
     # 结果集中包含一个或多个vb_*键对应下发任务时指定的一个或多个vid
}
```