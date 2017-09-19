import cmd
import copy
import os
import sys
import yaml
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from lib.core.config import ConfigLoader
from lib.core.display import display_result, print_info
from lib.core.prepare import prepare
from settings import default_config_yaml
import osprey
os.chdir("../")


GLOBAL_OPTS = {"quiet": False, "mode": "verify", "from_console": True, "thread": 5, "timeout": 60, "proxy": "x", "headers": "x", "cookies": "x", "spider": "x"}
option_desc = {"target": "specify one target",
               "target-file": "specify several target in file",
               "mode": "verify or exploit",
               "quiet": "quiet mode",
               "thread": "set thread number",
               "timeout": "set PoC run timeout",
               "proxy": "set proxy when running",
               "headers": "add more things in http header",
               "cookies": "add your own cookies pair",
               "spider": "set spider urls file"}


class TccInterpreter(cmd.Cmd):
    prompt = "osprey > "

    def emptyline(self):
        pass

    def index_poc_module(self):
        try:
            with open(default_config_yaml) as f:
                y = yaml.load(f)
            self.poc_dir_name = y.get('PoC').get("DIR_NAME")
            self.modules = [name.split(".")[0] for name in os.listdir(self.poc_dir_name) if name.startswith("vb_")]
        except Exception as e:
            print("Open config file error, {}".format(e))
            self.modules = []

    def do_show(self, line):
        """show poc
        show all PoC modules"""
        thing = line.strip().lower()
        if thing == 'poc':
            for module in self.modules:
                print_info(module)

    def complete_show(self, text, line, begidx, endidx):
        completions = ["poc"]
        if text:
            completions = [key for key in completions if key.startswith(text)]
        return completions

    def do_use(self, line):
        """use vul_id
        choose a PoC module"""
        line = line.strip()
        vid = None
        path = None
        for module in self.modules:
            if line in module:
                vid = "_".join(line.split("_")[:3])
                path = ".".join([self.poc_dir_name, module]).split("/")[-1]
                break
        if vid:
            execute = Execute()
            execute.prompt = "osprey ({}) ".format(vid)
            GLOBAL_OPTS["vids"] = vid
            execute.prepare_execute(path, self.modules, self.poc_dir_name)
            execute.cmdloop()
        else:
            print_info("can not find PoC module", "[-]", "red")

    def complete_use(self, text, line, begidx, endidx):
        if text:
            completions = [key for key in self.modules if key.startswith(text)]
            return completions

    def do_setg(self, line):
        """set option value
        set global option"""
        args = line.split()
        if not len(args) >= 1:
            print_info("nothing specify", "[-]", "red")
            return
        key = args[0]
        try:
            value = args[1]
        except IndexError:
            value = ""
        if key in ["mode", "proxy", "headers", "cookies"]:
            GLOBAL_OPTS[key] = value
        elif key in ["thread", "timeout"]:
            GLOBAL_OPTS[key] = int(value)
        elif key == "quiet":
            GLOBAL_OPTS["quiet"] = False if value.lower() == "false" else True
        else:
            print_info("unrecognized configuration", "[-]", "red")

    def do_search(self, line):
        """search for appropriate PoC"""
        if not line.strip():
            return
        for module in self.modules:
            if line.strip().lower() in module.lower():
                print_info(module)

    def do_exit(self, line):
        """exit console"""
        print_info("Bye")
        return True


class Execute(TccInterpreter):
    options = {}
    poc_info = None

    def prepare_execute(self, module, modules, poc_dir):
        self.modules = modules
        self.poc_dir_name = poc_dir
        try:
            __import__(module)
        except ImportError as e:
            print_info("can not get poc detailed information.\n{}".format(e), "[-]", "red")
            return
        tmp = sys.modules[module]
        self.poc_info = getattr(tmp, getattr(tmp, "POC_NAME")).poc_info

    def do_back(self, line):
        """go back"""
        return True

    def do_exit(self, line):
        """go back"""
        return True

    def do_show(self, line):
        """show options/info
        show all PoC modules or information in specify PoC"""
        thing = line.strip().lower()
        if thing == "options":
            print_info("\ntarget options:\n")
            print_info("{:<12}: {}".format("target", self.options.get("target", "")))
            print_info("{:<12}: {}".format("target-file", self.options.get("target-file", "")))
            print_info("\nother options:\n")
            desc = copy.deepcopy(option_desc)
            desc.pop("target")
            desc.pop("target-file")
            self._show_group(self.options, GLOBAL_OPTS, desc)
            print_info()
        elif thing == 'info':
            self._show_poc_info()
    
    def complete_show(self, text, line, begidx, endidx):
        completions = ["options", "info"]
        if text:
            completions = [key for key in completions if key.startswith(text)]
        return completions

    def do_run(self, line):
        """run
        run PoC module"""
        _fb = self._set_argument()
        if not _fb:
            print_info("wrong", "[-]", "red")
            return
        fb = prepare(_fb)
        results = osprey.start(fb)
        self._print_result(results)

    def do_set(self, line):
        """set target/target-file/mode/quiet/thread/timeout/proxy/headers value
        set configuration"""
        args = line.split()[:2]
        if not len(args) >= 1:
            print_info("nothing specify", "[-]", "red")
            return
        key = args[0]
        try:
            value = args[1]
        except IndexError:
            value = ""
        if key in ["target", "target-file", "mode", "proxy", "headers", "cookies", "spider"]:
            self.options[key] = value
        elif key in ["thread", "timeout"]:
            self.options[key] = int(value)
        elif key == "quiet":
            self.options["quiet"] = False if value.lower() == "false" else True
        else:
            print_info("unrecognized configuration", "[-]", "red")

    def complete_set(self, text, line, begidx, endidx):
        if not text:
            completions = list(option_desc.keys())
        else:
            completions = [key for key in list(option_desc.keys()) if key.startswith(text)]
        return completions

    def _set_argument(self):
        tmp = []
        if self.options.get("target-file", ""):
            with open(self.options.get("target-file")) as f:
                targets = f.readlines()
            if len(targets):
                tmp.extend(targets)
        if self.options.get("target", ""):
            tmp.append(self.options["target"])
        if len(tmp):
            self.options["targets"] = ",".join([t.strip() for t in tmp])
        else:
            print_info("no target specify", "[-]", "red")
            return False

        for k, v in GLOBAL_OPTS.items():
            self.options.setdefault(k, v)

        try:
            with open(default_config_yaml) as f:
                config = ConfigLoader(f, self.options)
        except Exception as e:
            return False
        return config

    def _show_group(self, options, default, opt_desc):
        headers = ["name", "current settings", "description"]
        options_group = []
        for name, desc in opt_desc.items():
            options_group.append([name, str(options.get(name, default.get(name, ""))), desc])
        opt_name_len = [len(headers[0])]
        opt_desc_len = [len(headers[1])]
        opt_len = [len(headers[2])]
        for opt in options_group:
            opt_name_len.append(len(opt[0]))
            opt_desc_len.append(len(opt[1]))
            opt_len.append(len(opt[2]))
        length = [l for l in map(max, [opt_name_len, opt_desc_len, opt_len])]
        print_info("   ".join(["{:<{}}".format(headers[i], length[i]) for i in range(3)]))
        options_group.insert(0, ["-"*4, "-"*16, "-"*11])
        for option in options_group:
            print_info("   ".join(["{:<{}}".format(option[i], length[i]) for i in range(3)]))

    def _show_poc_info(self):
        if not self.poc_info:
            return
        poc = self.poc_info["poc"]
        poc_name = poc.get("Name", "")
        print_info("\n----- {} -----".format(poc_name))
        for item in ["Name", "Author"]:
            print_info("{}: {}".format(item, poc.get(item, "").strip()), "[*]")
        print_info()
        vul = self.poc_info["vul"]
        for key, value in vul.items():
            print_info("{}: {}".format(key, str(value).strip()), "[*]")
        print_info((len(poc_name) + 13) * "-")
        print_info()

    def _print_result(self, results):
        if results:
            display_result(results)


if __name__ == "__main__":
    banner = """
                        ___  ___ _ __  _ __ ___ _   _
                       / _ \/ __| '_ \| '__/ _ \ | | |
                      | (_) \__ \ |_) | | |  __/ |_| |
                       \___/|___/ .__/|_|  \___|\__, |
                                |_|             |___/

                    Powered by TCC - https://www.vulbox.com/
                              Version: 1.0.0
        """
    p = "{}[31;1m {} {}[0m".format(chr(27), banner, chr(27))
    print(p)
    PoCli = TccInterpreter()
    PoCli.index_poc_module()
    PoCli.cmdloop()