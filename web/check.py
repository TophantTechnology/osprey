import string


def check_task_id(task_id):
    def _(x): return True if x in string.ascii_letters + string.digits + "-" else False
    return True if all(map(_, task_id)) else False