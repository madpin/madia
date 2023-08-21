from __future__ import annotations

import hashlib


def string_to_md5(*args):
    """Converts arguments to md5 hash.

    This function takes one or more string arguments, concatenates them
    together, encodes the result as utf-8, and computes the MD5 hash of the
    concatenated string.

    The MD5 hash algorithm generates a 128-bit hash value. The hash will be
    the same for identical strings, so can be used to verify data integrity.

    Args:
        *args: One or more string arguments to concatenate and hash.

    Returns:
        str: Hexadecimal MD5 hash of the concatenated input strings.

    Example:

        .. code-block:: python

            from madia.utils_string import string_to_md5

            hash = string_to_md5("hello", "world")
            print(hash)

        This will print:

        .. code-block:: python

            5eb63bbbe01eeed093cb22bb8f5acdc3

    Note: MD5 hashes can collide, so should not be used for cryptographic
    purposes. Use SHA-256 or similar for that.
    """
    merged_string = "".join(map(str, args))
    md5_hash = hashlib.md5()
    md5_hash.update(merged_string.encode("utf-8"))
    return md5_hash.hexdigest()
