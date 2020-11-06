# Home Assistant Display Platform

###### With Fully Kiosk Browser Component

This project is for a display platform for Home Assistant that can be remotely controlled. The initial use-case for this is to control [Fully Kiosk Browser](http://www.ozerov.de/fully-kiosk-browser/) using it's built-in REST API.

> **Warning**: If you are upgrading from a previous version, please note that some of the service calls have changed!!

## Features

This component currently supports the following features of Fully Kiosk Browser:

   * turning the screen of the tablet on and off,
   * reloading the start page,
   * loading a provided URL,
   * adjusting the tablet screen brightness,
   * turning the tablet screensaver on, off and adjusting the screensaver brightness.
   * playing a mp3 file located on the tablet or on a http url

## Installation

If you have no other custom components, you can simply check out the respository directly into *$CONFIGDIR/custom_components/*.

```
$ git clone https://github.com/daemondazz/homeassistant-displays.git $CONFIGDIR/custom_components
```

If you are using other custom components, then check out the repository then copy the folders *display* and *fully_kiosk* into *$CONFIGDIR/custom_components/*

```
$ git clone https://github.com/daemondazz/homeassistant-displays.git /tmp/homeassistant-displays
$ mkdir $CONFIGDIR/custom_components/{display,fully_kiosk}
$ cp /tmp/homeassistant-displays/display/* $CONFIGDIR/custom_components/display
$ cp /tmp/homeassistant-displays/fully_kiosk/* $CONFIGDIR/custom_components/fully_kiosk
```

And then you need to add a `display:` section to your configuration file with the IP addresses of the displays you want to control:

```
display:
  - platform: fully_kiosk
    name: Kitchen Tablet
    host: 192.168.1.100
    password: 1234
```

On the tablet, you will need to enable the Remote Administration (from local network only should be fine) and set a Remote Admin Password.

## Usage

Once installed, you should have a new **displays** card on your main HA Overview page. The state card for each tablet will show some information about the tablet, such as manufacturer, model and battery status and allow the screen to be turned on and off.

### Display Platform Services

The display component supports the following services:

   * display.load_url
   * display.set_brightness
   * display.turn_off
   * display.turn_on

### Fully Browser Kiosk Specific Services

The fully_kiosk platform provides the following services:

   * fully_kiosk.load_start_url
   * fully_kiosk.say
   * fully_kiosk.screensaver_start
   * fully_kiosk.screensaver_stop
   * fully_kiosk.set_screensaver_brightness
   * fully_kiosk.sound_play
   * fully_kiosk.sound_stop
