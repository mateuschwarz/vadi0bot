# vadio vadi0bot v0.4.2g

import asyncio
import getopt
import importlib
import json
import logging
import socket
import sys
import time
import websockets
from hashlib import sha256 as sha
from base64 import b64encode as b64
from vadi0bot import vadi0bot
from datetime import datetime as dtx

from vadi0bot import vadi0bot
from data.obsws import config as obsws
from data.twitch import config as twtx


if __name__ == '__main__':

    backoff, backoff_mult = 2, 2

    while True:
        try:
            asyncio.run(vadi0bot(twitch=True, obsws=False))

        except ConnectionResetError as e:
            importlib.reload(sys.modules['vadi0bot'])
            importlib.reload(sys.modules['logging'])

            stamp = dtx.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f'INFO: {stamp} - RESTARTING BOT IN {backoff}S')

            time.sleep(backoff)
            backoff *= backoff_mult

        except ConnectionAbortedError as e:
            print(e)
            break
