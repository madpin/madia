from __future__ import annotations

import hashlib


def string_to_md5(*args):
    merged_string = "".join(map(str, args))
    md5_hash = hashlib.md5()
    md5_hash.update(merged_string.encode("utf-8"))
    return md5_hash.hexdigest()
