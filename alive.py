from time import sleep
from os import environ
from requests import get as rget
from logging import error as logerror

BASE_URL = environ.get('BASE_URL', None)
try:
    if len(BASE_URL) == 0:
        raise TypeError
    BASE_URL = BASE_URL.rstrip("/")
except TypeError:
    BASE_URL = None
SERVER_PORT = environ.get('SERVER_PORT', None)
if SERVER_PORT is not None and BASE_URL is not None:
    while True:
        try:
            rget(BASE_URL).status_code
            sleep(600)
        except Exception as e:
            logerror(f"alive.py: {e}")
            sleep(2)
            continue
