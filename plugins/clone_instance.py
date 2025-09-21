_clone_clients = {}

def set_client(bot_id: int, client):
    _clone_clients[int(bot_id)] = client

def get_client(bot_id: int):
    return _clone_clients.get(int(bot_id))

def parse_time(value: str) -> int:
    """
    Parse a time string into seconds.
    
    Examples:
    - '30s' -> 30 seconds
    - '10m' -> 600 seconds
    - '2h'  -> 7200 seconds
    - '45'  -> 162000 seconds (default: hours, so 45h)
    """
    if not value:
        return 3600

    value = str(value).strip().lower()

    if value.endswith("s"):
        return int(value[:-1])
    elif value.endswith("m"):
        return int(value[:-1]) * 60
    elif value.endswith("h"):
        return int(value[:-1]) * 3600
    else:
        return int(value) * 3600
