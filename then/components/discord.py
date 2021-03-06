# Thanks to https://github.com/Rapptz/discord.py
import json
import sys

import requests
from dataclasses import dataclass
from requests import RequestException

from then.components.http import HttpBase, HttpMessageApiBase, HttpException
from then.exceptions import ValidationError, ExecuteError


@dataclass
class DiscordMessage(HttpMessageApiBase):
    """:class:`DiscordMessage` instance created by :class:`Discord` component. Create It using::

        from then.components import Discord

        message = Discord(...).message(body="My message")
        message.send()

    :arg body: message to send.
    """
    body: str
    tts: bool = False
    embed: bool = None
    url_pattern = 'https://discordapp.com/api/v6/{}'
    component: 'Discord' = None
    is_connected: bool = False
    gateway = None

    def login(self):
        r = None
        try:
            r = requests.get(self.url_pattern.format('users/@me'), headers=self.component.get_headers())
            r.raise_for_status()
        except RequestException as e:
            if r is not None and r.status_code == 401:
                raise ValidationError('Improper token has been passed.') from e
            else:
                raise ExecuteError('Unknown error on {}: {}'.format(self.component.name, e))
        self.is_connected = True

    def create_gateway(self):
        from websocket import create_connection

        r = requests.get(self.url_pattern.format('gateway'), headers=self.component.get_headers())
        self.gateway = create_connection(r.json()['url'] + '?encoding=json&v=6')

    def gateway_send(self, data):
        self.gateway.send(json.dumps(data))

    def connect(self):
        self.create_gateway()
        self.gateway_send({
            'op': 2,
            'd': {
                'token': self.component.token,
                'properties': {
                    '$os': sys.platform,
                    '$browser': 'then',
                    '$device': 'then',
                    '$referrer': '',
                    '$referring_domain': ''
                },
                'compress': True,
                'large_threshold': 250,
                'v': 3
            }
        })

    def get_body(self):
        body = {
            'content': self.body
        }
        if self.tts:
            body['tts'] = self.tts
        if self.embed:
            body['embed'] = self.embed
        return body

    def get_url(self):
        return self.url_pattern.format('channels/{channel_id}/messages'.format(channel_id=self.component.to))

    def send(self):
        try:
            super(DiscordMessage, self).send()
        except HttpException as e:
            if e.response.status_code == 400 and not self.is_connected:
                # Discord bot requires a first login to send messages.
                # This is not necessary the following times.
                self.login()
                self.connect()
                self.send()
            else:
                raise


@dataclass
class Discord(HttpBase):
    """Create a Discord instance to send a message to a user or channel::

        from then.components import Discord

        Discord(token='NDF4NGQ5GzY6OTF3MAk2vDc1.D1xvWv.nMarFQh3UdjaDLXZZggL1xxxxxx',
                to='48014601482xxxx01')\\
            .send(body='My message body')

    :param token: Your secret bot token (``NDF4NGQ5GzY6OTF3MAk2vDc1.D1xvWv.nMarFQh3UdjaDLXZZggL1xxxxxx``).
    :param to: Channel id (``47874976890709XXXX``)
    :param bot_token: Bookean. Token is the bot token
    :param timeout: Connection timeout to send message.
    """
    token: str
    to: str
    #: Get your channel ID on your url (second id): https://discordapp.com/channels/4801460148299xxxx/4801460148299xxxx
    bot_token: bool = True
    timeout: int = 15
    method = 'POST'

    _message_class = DiscordMessage

    def get_headers(self):
        return {
            'Authorization': ('Bot ' + self.token) if self.bot_token else self.token
        }
