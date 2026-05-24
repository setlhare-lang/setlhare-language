def qubit(state=0):
    return {"alpha": 1 if state == 0 else 0, "beta": 1 if state == 1 else 0}


def measure(q):
    return 1 if abs(q.get("beta", 0)) > abs(q.get("alpha", 0)) else 0
