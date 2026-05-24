def pin(number, mode="out"):
    return {"pin": number, "mode": mode, "value": 0}


def write(pin_obj, value):
    pin_obj["value"] = value
    return pin_obj


def read(pin_obj):
    return pin_obj.get("value", 0)
