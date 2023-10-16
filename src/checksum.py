import hashlib


def get_md5(content):
    return hashlib.md5(content.encode()).hexdigest()
