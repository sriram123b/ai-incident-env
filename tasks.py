def easy_task(env):
    return ["resolve"]

def medium_task(env):
    return ["investigate", "resolve"]

def hard_task(env):
    return ["investigate", "investigate", "resolve"]


def grader(env):
    state = env.state()   # ✅ FIXED
    if state["alert_level"] == 0:
        return 1.0
    return 0.0
