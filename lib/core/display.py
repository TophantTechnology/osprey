def display_result(results):
    print("\n", "-"*8, " scan result ", "-"*8, "\n")
    for poc_name, details in results.items():
        print(poc_name)
        for scan_info in details["scan_info"]:
            if scan_info.get("Success", False):
                message = "{}[32;1m{}{}[0m".format(chr(27), "".join(["[+] ", scan_info.get("Target", ""), " vulnerable"]), chr(27))
            else:
                message = "".join(["[-] ", scan_info.get("Target"), " not vulnerable"])
            print(message)
        print("")
    print("-"*32)


def display_json(results):
    import json
    try:
        json_result = json.dumps(results)
        print(json_result)
    except Exception as e:
        from lib.log import logger as log
        log.error("DUMP JSON RESULT WRONG! {}".format(e))


def print_info(message="", tag="", color=None):
    if color == "red":
        output = "{}[31;1m{} {} {}[0m".format(chr(27), tag, message, chr(27))
    elif color == "green":
        output = "{}[32;1m{} {} {}[0m".format(chr(27), tag, message, chr(27))
    else:
        output = "{} {}".format(tag, message)
    print(output)
