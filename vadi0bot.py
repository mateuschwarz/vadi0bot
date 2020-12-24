# vadio vadi0bot v0.4.2g

import asyncio
import json
import logging
import socket
import websockets

from base64 import b64encode as b64
from hashlib import sha256 as sha
from datetime import datetime as dtx

from data.obsws import config as obsws
from data.twitch import config as twtx


async def vadi0bot(twitch=True, obsws=True):

    def console_logger() -> logging.Logger:
        logger = logging.getLogger(__name__)
        file_handler = logging.FileHandler('log/console.log')
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt='%(levelname)s: %(asctime)s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        return logger

    global backoff
    backoff, message, logger = 2, "", console_logger()

    async def vd_twirct() -> None:
        """ twitch irc client """

        class flags():

            def admin(func) -> None:
                def wrapper(*ctx, **kwargs):
                    if any(x in ctx[0]['badges'] for x in twtx.TAGS_ADM):
                        return func(*ctx, **kwargs)
                    raise PermissionError(
                        f'\'{func.__name__}\' needs admin permission')
                return wrapper

            def moderator(func) -> None:
                def wrapper(*ctx, **kwargs):
                    if any(x in ctx[0]['badges'] for x in twtx.TAGS_MODS):
                        return func(*ctx, **kwargs)
                    raise PermissionError(
                        f'\'{func.__name__}\' needs moderator+ permission')
                return wrapper

        class commands():

            async def hello(ctx: dict) -> None:
                await send_privmsg('olá, @{}!'.format(ctx['user']))

            @flags.moderator
            async def uptime(ctx: dict) -> None:
                await delete_message(ctx['id'])
                uptime = dtx.now() - st_time
                await send_privmsg('@{}: bot uptime: {}'.format(ctx['user'], uptime))

            @flags.moderator
            async def scene(ctx: dict) -> None:
                await delete_message(ctx['id'])
                emit_to_obsws('SetCurrentScene', {'scene-name': ctx['args']})

            @flags.admin
            async def disconnect(ctx: dict) -> None:
                await send_privmsg('vadi0bot desligando')
                raise ConnectionAbortedError

            @flags.admin
            async def restart(ctx: dict) -> None:
                await delete_message(ctx['id'])
                await send_privmsg('vadi0bot reiniciando')
                raise ConnectionResetError

        def emit_to_obsws(request_type: str, data: dict) -> None:
            nonlocal message
            message = json.dumps({'request-type': request_type, **data})

        async def delete_message(id: str) -> None:
            await send_privmsg('/delete {}'.format(id), prefix="")

        with socket.socket() as irc:

            async def recv() -> str:
                return irc.recv(1024).decode().split('\r\n')

            async def send(message: str, log: bool = True) -> None:
                if log:
                    logger.info('< ' + message)
                irc.send((message + "\r\n").encode())

            async def send_privmsg(message: str, channel: str = twtx.CHANNEL, prefix: str = twtx.MSG_PREFIX) -> None:
                await send(f'PRIVMSG #{channel} :{prefix}{message}')

            async def handle(line: str) -> None:
                spline = line.split(':')
                logger.info('> ' + ' '.join(spline[1:]))

                if 'PING ' in spline:
                    await send("PONG :tmi.twitch.tv")

                elif 'PRIVMSG' in spline[1]:
                    message = spline[2]

                    if message[0] == twtx.CMD_PREFIX:
                        msg_split = message.split()
                        function = msg_split[0][1:]
                        context = {
                            'args': ' '.join(msg_split[1:]),
                            'user': spline[1].split("!")[0],
                            'channel': spline[1].split()[2],
                            **{t.split('=')[0]: t.split('=')[1] for t in spline[0][1:].split(';')}}

                        try:
                            nonlocal commands
                            await eval('commands.{}({})'.format(function, context))
                        except ConnectionResetError as e:
                            raise e
                        except Exception as e:
                            logger.info(e)

            # mainloop

            nonlocal logger
            st_time = dtx.now()

            try:
                irc.connect(twtx.IRC_ADDR)
                await send(twtx.AUTH_STR, log=False)
                logger.info(f'* {twtx.NICK} connected')

                while True:
                    for line in await recv():
                        if line:
                            await handle(line)
                    await asyncio.sleep(3)

            except Exception as exc:
                raise exc

    async def vd_obsws() -> None:
        """ obs websocket client """

        def id_generator() -> str:
            __uuid = 0
            while True:
                __uuid += 1
                yield str(__uuid)

        async with websockets.connect(obsws.URI, ping_interval=None) as ws:

            async def send(payload: dict):
                payload['message-id'] = next(msg_id)
                logger.info('> ' + str(payload)[:72])
                await ws.send(json.dumps(payload))

            async def recv() -> dict:
                res = json.loads(await ws.recv())
                logger.info('< ' + str(res)[:72])
                return res

            async def call(request_type: str, payload: dict = {}, timeout: int = 15) -> dict:
                await send({'request-type': request_type, **payload})
                return await recv()

            async def auth(**res):
                password = obsws.PASS
                salt = res['salt']
                challenge = res['challenge']

                secret = b64(sha((password + salt).encode('utf-8')).digest())
                auth_response = b64(
                    sha(secret + challenge.encode('utf-8')).digest()).decode('utf-8')

                res = await call('Authenticate', {'auth': auth_response})

                if not 'ok' in res['status']:
                    raise ConnectionError

                logger.info('- vadi0bot authenticated')

            async def handle(message):
                payload = json.loads(message)
                await send(payload)

            # mainloop

            nonlocal logger
            msg_id = id_generator()

            while True:
                try:
                    res = await call("GetAuthRequired")

                    if not 'ok' in res['status']:
                        raise ConnectionError
                    if res['authRequired']:
                        await auth(**res)

                    while True:
                        res = await recv()
                        nonlocal message
                        if message:
                            await handle(message)
                            message = ""
                        await asyncio.sleep(1)

                except Exception as e:
                    logger.warn(e)
                    await asyncio.sleep(1)

    # asyncio mainloop

    try:
        if twitch and obsws:
            await asyncio.gather(vd_twirct(), vd_obsws())
        elif twitch:
            await asyncio.gather(vd_twirct())
        elif obsws:
            await asyncio.gather(vd_obsws())
    except ConnectionResetError as e:
        raise e


if __name__ == '__main__':
    asyncio.run(vadi0bot())
