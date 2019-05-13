# Home Assistant Display Platform

###### With Fully Kiosk Browser Component

This project is for a display platform for Home Assistant that can be remotely controlled. The initial use-case for this is to control [Fully Kiosk Browser](http://www.ozerov.de/fully-kiosk-browser/) using it's built-in REST API.

> **Warning**: This is my first platform and component for Home Assistant, so
> it is still VERY rough. It works for me but there is no guarantee that it
> will work for anyone else or their neighbors.

## Features

This component currently supports the following features of Fully Kiosk Browser:

   * turning the screen of the tablet on and off,
   * reloading the start page,
   * loading a provided URL,
   * adjusting the tablet screen brightness,
   * turning the tablet screensaver on, off and adjusting the screensaver brightness.

## Installation

If you have no other custom components, you can simplly check out the respository directly into *$CONFIGDIR/custom_components/*.

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

## Limitations

This component does not currently handle the tablets being offline when HA is started.
