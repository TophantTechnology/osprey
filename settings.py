default_config_yaml = "./config.yaml"


log_path = "/tmp/poc.log"


use_mongo = False
mongo_url = "mongodb://127.0.0.1/"
mongo_db_name = "poc"
mongo_task_coll = "tasks"
mongo_resp_coll = "response"
mongo_basic_coll = "basic"


use_sqlite = True
sqlite_path = "/tmp/poc.db"


save_http_dump = False


req_timeout = (10, 10)



# Web API
API_HOST = "0.0.0.0"
API_PORT = "5500"
CELERY_BROKER = "amqp://usename:password@127.0.0.1/vhost"

# task call
PROGRAM = "python3"
DST_FILE = "./osprey.py"
PROCESS_TIMEOUT = 300
