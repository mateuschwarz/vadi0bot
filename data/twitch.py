# vadio twitch irc client configuration file

class config():

    IRC_ADDR = (SERVER, PORT) = 'irc.twitch.tv', 6667
    NICK     = 'canalvadio'
    CHANNEL  = 'canalvadio'
    OAUTH    = ""

    CMD_PREFIX = '!'
    MSG_PREFIX = '>> '
    TAGS_ADM   = ['broadcaster']
    TAGS_MODS  = ['moderator', *TAGS_ADM]

    AUTH_STR = f'PASS {OAUTH}\r\nNICK {NICK}\r\nJOIN #{CHANNEL}\r\nCAP REQ :twitch.tv/membership\r\nCAP REQ :twitch.tv/tags\r\nCAP REQ :twitch.tv/commands'