import os
import re

_filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")


# https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.utils.secure_filename
# https://github.com/pallets/werkzeug/blob/504a8c4fbda9b8b2fd09e817544ffd228f23458e/src/werkzeug/utils.py#L195
def secure_filename(filename: str) -> str:
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")

    normalized_filename = _filename_ascii_strip_re.sub("", "_".join(filename.split()))
    filename = str(normalized_filename).strip("._")
    return filename
