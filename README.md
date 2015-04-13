# MouseTrap

License: GPL v2.0 (see LICENSE)


## Software Requirements

* Linux (developed on Fedora 20 and Ubuntu)
* Python 2.7+
* PyYAML 3
* OpenCV 2+
* Python-Xlib 0.12+
* Gnome Common
* Python setup-tools
* Numpy

## Install Dependencies for Fedora21, Python3, OpenCV3
Uses script bin/install_dependencies_fedora21_python3_opencv3.bash
to install the mousetrap dependencies for Fedora21, Python3 and OpenCV3.
* Using terminal, navigate to the mousetrap folder.
* Enter the following command in the terminal:
  ./bin/install_dependencies_fedora21_python3_opencv3.bash
* This will begin the installation process of the dependencies:
  *     Installation of Python, gnome common and python setup-tools
  *     Installs Numpy
  *     Installs Python library x-lib
  *     Installs openCV 3
* Let Script run through until finished.


## Download

### Stable

    $ git clone git://git.gnome.org/mousetrap

### Development

    $ git clone git://git.gnome.org/mousetrap --branch gnome3-wip


## Installing

### Using `pip`

    cd mousetrap
    sudo pip install .

### Using `autotools`

    cd mousetrap
    # For python3: 
    PYTHON=$(which python3) ./autogen.sh # On Fedora, add --prefix=/usr
    # For python2:
    ./autogen.sh # On Fedora, add --prefix=/usr
    make
    sudo make install

## Uninstalling

When uninstalling, make sure that you are in the Mousetrap folder that you used to install Mousetrap.

### Using 'autotools'

    sudo make uninstall

## Running

    mousetrap --help # Print the list of possible command-line options
    mousetrap


## Using

By default, MouseTrap tracks your face, allowing you to control the
mouse pointer using a joystick metaphor. When you look left,
the pointer moves left; look right, it moves right; look up, it moves up;
look down, it moves down; look straight ahead, it stops moving. To click,
close your left eye for about 1.5 seconds.


## Configuring

To customize MouseTrap's configuration, place a copy of the annotated built-in
configuration in ~/.mousetrap.yaml, and then edit it.

    mousetrap --dump-annotated > ~/.mousetrap.yaml

MouseTrap loads its configuration from the following locations in order. Later
locations may override values of those that come before it.

* Built-in: something like `/usr/local/lib/python2.7/mousetrap/mousetrap.yaml`
* User: `~/.mousetrap.yaml`
* Command-line: `mousetrap --config path/to/myconfig.yaml`

Load and dump configuration:

    mousetrap --dump-config

Dump built-in annotated configuration.

    mousetrap --dump-annotated

## Translating

Use `src/mousetrap/locale/_language_/LC_MESSAGES/mousetrap.po` as your template (POT file).

## Plugin Information

There are currently 5 different plugins.

*  Camera
*  Display
*  Nose
*  Eyes
*  Vision

The camera plugin is responsible for loading in the webcam so that it can read the user's image.

The display plugin is responsible for writing the user's image onto the screen so that the user can see their own image.

The nose plugin is responsible for detecting the user's nose and uses the user's nose as a point to detect movement.

The eyes plugin is responsible for detecting the user's eyes. It detects motion of the eyes, checks whether or not an eye has been closed and has a class to detect the user's left eye.

The vision plugin corresponds with OpenCV which also loads in the haar files, the camera, and the feature detectors.

## Writing a Plugin

### Example plugin class

```python
# Import the interface for plugins.
import mousetrap.plugins.interface as interface

# Create a logger for logging.
import logging
LOGGER = logging.getLogger(__name__)


# Define a class that inherits from mousetrap.plugins.interface.Plugin
class MyPlugin(interface.Plugin):

    # Define a constructor that takes an instance of mousetrap.config.Config
    # as the first parameter (after self).
    def __init__(self, config):
        self._config = config

        # Access class configuration by using self as a key.
        # Here we retrieve 'x' from our class configuration.
        self._x = config[self]['x']

    # Define a run method that takes an instance of mousetrap.main.App as the
    # first parameter (after self). Run is called on each pass of the main
    # loop.
    def run(self, app):

        # App contains data shared between the system and plugins.
        # See mousetrap.main.App for attributes that are defined by mousetrap.
        # For example, we can access the pointer:
        app.pointer.set_position((0, 0))

        # We can access attributes that are populated by other plugins.
        image = app.image

        # We can make attributes available to other plugins by adding them
        # to app.
        app.greeting = 'Just saying %s!' % (self._x)
```

### 2. Edit configuration file to tell MouseTrap about your plugin.
(This is also an example of how to enable any plugin: just add your plugin path underneath ```assembly:```.)

```yaml
#~/.mousetrap.yaml

assembly:
- mousetrap.plugins.camera.CameraPlugin     # sets app.image
- mousetrap.plugins.display.DisplayPlugin   # displays app.image in a window
- python.path.to.MyPlugin                   # runs after CameraPlugin

classes:
  python.path.to.MyPlugin:
    x: hi
```

To disable a plugin, either comment out, or delete, the corresponding line underneath ```assembly:```.

For more examples, see the plugins in `src/mousetrap/plugins`.

## Developing

Makefile targets
* `all` - builds
* `install` - installs
* `run` - runs without install
* `check` - tests
* `lint` - style checker
* `clean` - deletes files created by `make` or `make all`
* `devclean` - deletes all files ignored by git
* `pristine` - `devclean` plus deletes all files not tracked by git
* `dist` - makes distribution
* `distcheck` - makes and tests distribution
* `distclean` - cleans extra files generated by `dist`
