import datetime
import inspect
import logging
import os
import sys
from lib.core.display import display_result, display_json
from settings import log_path


class Logger:
    def __init__(self):
        self._log_file = log_path
        self._logger = logging.getLogger("poc")
        self._logger.setLevel(logging.DEBUG)
        # self._logger.handlers = []
        file_handler = logging.FileHandler(self._log_file)
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(hdlr=file_handler)
        if "--quiet" in sys.argv or "-q" in sys.argv:
            return
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(hdlr=stream_handler)
        # self._logger.propagate = False

    def _format_message(self, level, message):
        """格式化将要输出日志信息

        :param level: str, 日志等级, INFO/WARN/ERROR/HIGHLIGHT
        :param message: str, 日志信息条目
        :return: str, 格式化的日志信息条目
        """
        frame = inspect.currentframe().f_back.f_back
        frame_info = inspect.getframeinfo(frame)
        line_no = frame_info.lineno
        file_name = frame_info.filename
        module_name = os.path.splitext(os.path.split(file_name)[1])[0]
        if module_name and line_no:
            message = "{time} - [{module}#{line}] - {level} - {message}".format(
                time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3],
                module=module_name, line=line_no, level=level, message=message)
        return message

    def info(self, message):
        self._logger.info(self._format_message("INFO", message))

    def warn(self, message):
        self._logger.warning(self._format_message("WARN", message))

    def error(self, message):
        self._logger.error(self._format_message("ERROR", message))

    def highlight(self, message):
        self._logger.info(self._format_message("HIGHLIGHT", "{}[32;1m{}{}[0m".format(chr(27), message, chr(27))))

    def result(self, results):
        if "--json" in sys.argv:
            display_json(results)
        else:
            display_result(results)


logger = Logger()
