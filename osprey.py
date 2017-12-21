import os
import signal
from gevent import monkey
monkey.patch_all()
from core.PocManager import PoCManager
from lib.core.cmdparser import cmdline_parse
from lib.log import logger as log
from lib.core.prepare import prepare


def main():
    init_signal()
    options, args = cmdline_parse()
    fb = prepare(options)
    start(fb)


def init_signal():
    os.setpgrp()
    signal.signal(
        signal.SIGTERM,
        lambda *_: os.kill(0, signal.SIGKILL))


def start(fb):
    poc_manager = PoCManager(fb)
    results = poc_manager.run()
    if fb.console:
        return results if results else None
    else:
        if results: log.result(results)


if __name__ == "__main__":
    main()
