# vadio twitch irc client configuration file

class config():

    IRC_ADDR = (SERVER, PORT) = 'irc.twitch.tv', 6667
    NICK     = 'canalvadio'
    CHANNEL  = 'canalvadio'
    OAUTH    = 'oauth:yzp5iba4xwfmgp3lqnhsfyz4cgpuji'

    CMD_PREFIX = '!'
    MSG_PREFIX = '>> '
    TAGS_ADM   = ['broadcaster']
    TAGS_MODS  = ['moderator', *TAGS_ADM]

    AUTH_STR = f'PASS {OAUTH}\r\nNICK {NICK}\r\nJOIN #{CHANNEL}\r\nCAP REQ :twitch.tv/membership\r\nCAP REQ :twitch.tv/tags\r\nCAP REQ :twitch.tv/commands'

    # canalvadio
    # oauth:yzp5iba4xwfmgp3lqnhsfyz4cgpuji

    # vadi0
    # 'oauth:vfoay7t26rq2kzbsxjknh0jiga3qhh'