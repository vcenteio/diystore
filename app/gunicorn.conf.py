from distutils.util import strtobool
from os import getenv
from multiprocessing import cpu_count


_host = getenv("HOST", "0.0.0.0")
_port = getenv("PORT", 5050)
bind = f"{_host}:{_port}"

workers = int(getenv("WEB_CONCURRENCY", cpu_count() * 2))
threads = 1
reload = bool(strtobool(getenv("WEB_RELOAD", "false")))

accesslog = "-"
