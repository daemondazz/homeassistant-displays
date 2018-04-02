"""
Support for Fully Kiosk Browser
"""

from datetime import timedelta
import logging
import requests
import voluptuous as vol

from homeassistant.const import (ATTR_ENTITY_ID,
                                 CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT,
                                 STATE_OFF, STATE_ON, STATE_UNKNOWN)
#                                 SUPPORT_TURN_OFF, SUPPORT_TURN_ON)
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv


from . import (
    DisplayDevice, DOMAIN,
    SUPPORT_TURN_OFF, SUPPORT_TURN_ON
)


_LOGGER = logging.getLogger(__name__)

ATTR_MESSAGE = 'message'
ATTR_LOCALE = 'locale'

DEFAULT_LOCALE = 'en'
DEFAULT_NAME = 'Fully Kiosk Browser'
DEFAULT_PORT = 2323
DEVICES = []
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=15)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Required(CONF_PASSWORD): cv.string
})

SCREENSAVER_START_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
})

SCREENSAVER_STOP_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
})

TTS_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required(ATTR_MESSAGE): cv.string,
    vol.Optional(ATTR_LOCALE, default=DEFAULT_LOCALE): cv.string
})

SUPPORT_FULLYKIOSK = SUPPORT_TURN_OFF | SUPPORT_TURN_ON

SERVICE_SAY = 'fullykiosk_say'
SERVICE_SCREENSAVER_START = 'fullykiosk_screensaver_start'
SERVICE_SCREENSAVER_STOP = 'fullykiosk_screensaver_stop'


def setup_platform(hass, config, add_devices, discovery_info=None):
    device = FullyKioskDevice(config.get(CONF_NAME),
                              config.get(CONF_HOST),
                              config.get(CONF_PORT),
                              config.get(CONF_PASSWORD))

    if device.update():
        DEVICES.append(device)
        add_devices([device])
        register_services(hass)


def register_services(hass):
    """Register all services for Fully Kiosk devices."""
    hass.services.register(DOMAIN,
                           SERVICE_SCREENSAVER_START,
                           _service_screensaver_start,
                           schema=SCREENSAVER_START_SCHEMA)
    hass.services.register(DOMAIN,
                           SERVICE_SCREENSAVER_STOP,
                           _service_screensaver_stop,
                           schema=SCREENSAVER_STOP_SCHEMA)
    hass.services.register(DOMAIN,
                           SERVICE_SAY,
                           _service_say,
                           schema=TTS_SCHEMA)


def _apply_service(service, service_func, *service_func_args):
    """Handle services to apply."""
    entity_ids = service.data.get('entity_id')

    if entity_ids:
        _devices = [device for device in DEVICES
                    if device.entity_id in entity_ids]
    else:
        _devices = DEVICES

    for device in _devices:
        service_func(device, *service_func_args)
        device.schedule_update_ha_state(True)


def _service_screensaver_start(service):
    _apply_service(service, FullyKioskDevice.turn_screensaver_on)


def _service_screensaver_stop(service):
    _apply_service(service, FullyKioskDevice.turn_screensaver_off)


def _service_say(service):
    _apply_service(service,
                   FullyKioskDevice.tts,
                   service.data[ATTR_MESSAGE],
                   service.data[ATTR_LOCALE]
                   )


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
        self._send_command(command='screenOff')
        self.update()

    def turn_on(self):
        self._send_command(command='screenOn')
        self.update()

    def turn_screensaver_on(self):
        self._send_command(command='startScreensaver')
        self.update()

    def turn_screensaver_off(self):
        self._send_command(command='stopScreensaver')
        self.update()

    def tts(self, message, locale):
        self._send_command(command='textToSpeech', text=message, locale=locale)
        self.update()


    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        try:
            data = self._send_command('deviceInfo').json()
        except OSError:
            return False

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

    def _send_command(self, command, **kwargs):
        payload = {
            'cmd': command,
            'password': self.password,
            'type': 'json',
            **kwargs
        }

        return requests.get(self.url, params=payload)
