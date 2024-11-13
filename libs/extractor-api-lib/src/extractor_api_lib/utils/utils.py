from hashlib import sha256
import datetime


def hash_datetime():
    now_bytes = datetime.datetime.now().isoformat().encode()
    return sha256(now_bytes).hexdigest()
