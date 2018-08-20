from dataclasses import dataclass

from then.components.http import Http, HttpMessageOwnApiBase, HttpBase


class HomeAssistantMessage(HttpMessageOwnApiBase):
    """:class:`HomeAssistantMessage` instance created by :class:`HomeAssistant` component. Create It using::

        from then.components import HomeAssistant

        message = HomeAssistant(...).message(event='otherevent', data={"extra": 1})
        message.send()

    :arg event: You can use any event name.
    """

    def __init__(self, event: str, body: dict = None, default_port: int = 8123, component: 'HomeAssistant' = None):
        self.event = event
        self.body = body
        self.default_port = default_port
        self.component = component
        self.__post_init__()

    def get_url(self):
        """Home assistant url

        :return: url
        :rtype: str
        """
        url = super().get_url()
        url += '/api/events/{}'.format(self.event)
        return url


@dataclass
class HomeAssistant(HttpBase):
    """Create a HomeAssistant instance to send a message to a user or channel::

        from then.components import HomeAssistant

        HomeAssistant(url="hass.io")\\
            .send(event='myevent')

    :param url: Home Assistant address. Syntax: ``[<protocol>://]<server>[:<port>]``.
    :param access: HomeAssistant password for API (``x-ha-access`` header).
    :param timeout: Connection timeout to send message.
    """
    url: str
    access: str = None
    timeout: int = 15
    method: str = 'post'
    _message_class = HomeAssistantMessage

    def get_headers(self):
        return {
            'x-ha-access': self.access
        } if self.access else {}
