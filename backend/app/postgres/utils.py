import datetime

def unix_timestamp() -> int:
    """
    Returns the current unix timestamp.

    Args:
        None

    Returns:
        int: The current unix timestamp.
    """
    return int(datetime.datetime.now(datetime.UTC).timestamp())