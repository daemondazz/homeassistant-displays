"""
Support for Fully Kiosk Browser
"""

from datetime import timedelta
import logging
import requests
import voluptuous as vol

from homeassistant.const import (CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT,
                                 STATE_OFF, STATE_ON, STATE_UNKNOWN)
#                                 SUPPORT_TURN_OFF, SUPPORT_TURN_ON)
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv


from . import DisplayDevice, SUPPORT_TURN_OFF, SUPPORT_TURN_ON


_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Fully Kiosk Browser'
DEFAULT_PORT = 2323
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=15)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Required(CONF_PASSWORD): cv.string
})

SUPPORT_FULLYKIOSK = SUPPORT_TURN_OFF | SUPPORT_TURN_ON


def setup_platform(hass, config, add_devices, discovery_info=None):
    fully = FullyKioskDevice(config.get(CONF_NAME),
                             config.get(CONF_HOST),
                             config.get(CONF_PORT),
                             config.get(CONF_PASSWORD))
    if fully.update():
        add_devices([fully])


class FullyKioskDevice(DisplayDevice):
    def __init__(self, name, host, port, password):
        self.password = password
        self.url = 'http://{}:{}/'.format(host, port)

        self._name = name
        self._attributes = {}
        self._brightness = None
        self._page = None
        self._state = STATE_UNKNOWN

    @property
    def device_state_attributes(self):
        return self._attributes

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        return self._page

    @property
    def state(self):
        return self._state

    @property
    def supported_features(self):
        return SUPPORT_FULLYKIOSK

    def turn_off(self):
        self._send_command('screenOff')
        self.update()

    def turn_on(self):
        self._send_command('screenOn')
        self.update()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        data = self._send_command('deviceInfo').json()
        if 'status' in data and data['status'] == 'Error':
            _LOGGER.error(data['statustext'])
            return False
        self._attributes = {
            'manufacturer': data['deviceManufacturer'],
            'model': data['deviceModel'],
            'device_id': data['deviceID'],
            'version': data['appVersionName'],
            'battery_level': data['batteryLevel'],
            'kiosk_mode': data['kioskMode'],
            'maintenance_mode': data['maintenanceMode'],
        }
        self._brightness = data['screenBrightness']
        self._page = data['currentPage']
        if data['isScreenOn']:
            self._state = STATE_ON
        else:
            self._state = STATE_OFF
        return True

    def _send_command(self, command, data=None):
        return requests.get(self.url, params={'cmd': command, 'password': self.password, 'type': 'json'})
