import sys
from optparse import OptionGroup, OptionParser
from lib.core.config import ConfigLoader
from lib.log import logger as log
from settings import default_config_yaml


def cmdline_parse():
    usage = "usage: python %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--target", type="string", dest="targets", help="One or more target, separate with comma(,)")
    parser.add_option("--target-file", type="string", dest="target_file", help="Target in file, one target per line")
    parser.add_option("-v", "--vid", type="string", dest="vids", help="One or more PoC-id, separate with comma(,)")
    parser.add_option("--task_id", type="string", dest="task_id", help="Specify a task_id to save result in database")

    control = OptionGroup(parser, "PoC setting")
    control.add_option("-m", "--mode", type="choice", choices=["verify", "exploit"], dest="mode", help="PoC run mode, verify or exploit", default="verify")
    control.add_option("-q", "--quiet", action="store_true",default=False, help="Do not print details when running")
    control.add_option("--spider", type="string", dest="spider", default="x", help="spider URLs data in a file")
    control.add_option("--json", action="store_true", default=False, help="Print results in JSON")
    control.add_option("--config", type="string", dest="config", help="Specify a config file")
    control.add_option("--from-console", action="store_true",default=False, help="Use console mode")
    control.add_option("--timeout", type="int", dest="timeout", help="Set timeout for each PoC")
    control.add_option("--thread", type="int", dest="thread", help="Thread number")
    control.add_option("--poc-dir", type="string", dest="poc_dir_name", help="The PoC directory")

    http = OptionGroup(parser, "HTTP setting")
    http.add_option("--cookies", type="string", dest="cookies", default="x", help="Add cookies, eg. vul=box&free=buff")
    http.add_option("--proxy", type="string", dest="proxy", default="x", help="Use proxy, eg. http|socks4|socks5://address:port")
    http.add_option("--headers", type="string", dest="headers", default="x", help="Add headers, eg. vul=box&free=buff")

    parser.add_option_group(control)
    parser.add_option_group(http)

    options, args = parser.parse_args()
    if options.targets:
        tmp = ",".join([t.strip() for t in options.targets.split(",")])
        options.targets = tmp
    if options.vids:
        tmp = ",".join([v.strip() for v in options.vids.split(",")])
        options.vids = tmp
    if options.target_file:
        with open(options.target_file, "r") as f:
            targets = f.readlines()
        if targets:
            options.targets = ",".join([target.strip() for target in targets])
    if not (options.targets and options.vids):
        parser.print_help()
        sys.exit(0)
    if not options.config:
        options.config = default_config_yaml

    try:
        f = open(options.config)
    except Exception as e:
        log.error("Open config file error, {}".format(e))
        sys.exit(0)
    try:
        config = ConfigLoader(f, options)
    except Exception as e:
        log.error("Load yaml config error, {}".format(e))
        sys.exit(0)
    try:
        if config.spider != "x":
            open(options.spider).close()
    except Exception as e:
        log.error("Failed to open spider file")
        config.spider = None
    if config:
        return config, args
    else:
        sys.exit(0)
