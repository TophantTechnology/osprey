import sys
import yaml
from lib.log import logger as log


class ConfigLoader:
    def __init__(self, config_file, options=None):
        try:
            y = yaml.load(config_file)
        except Exception as e:
            log.error("Load config error, please check.")
            sys.exit(0)

        poc = y.get("PoC")
        self.poc_dir_name = poc.get("DIR_NAME")
        self.timeout = poc.get("TIMEOUT")
        self.thread = poc.get("THREAD_NUM")
        self.poc_return_dump = poc.get('RETURN_REQ_RESP')

        if options:
            options_dict = options if isinstance(options, dict) else options.__dict__
            for k, v in options_dict.items():
                if v is not None:
                    setattr(self, k, v)
