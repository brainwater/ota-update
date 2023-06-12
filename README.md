# ota-update
 CircuitPython code for updating a microcontroller over the air

At boot, downloads the contents of the repository at secrets.py secrets['github_code_url'], with an optional github access token at secrets['github_token'] to increase the rate limit.
Required libraries include adafruit_requests and adafruit_binascii, which can be found in the circuitpython library bundle from https://circuitpython.org/libraries . It's only been tested with circuitpython version 8.

You need to perform a hard reset, which can be done in code with Circuitpython with `microcontroller.reset()`, in order to re-download the latest source files.

## Instructions

- Install adafruit_requests and adafruit_binascii into the `lib` folder of your microcontroller.
- Copy `boot.py` from ota-update onto your microcontroller
- Write into your `secrets.py` file the value for `secrets['github_code_url']` and optionally `secrets['github_token']` (to increase the rate limit to avoid having requrests denied by github for throttling)
- `secrets['github_code_url'] is the api repo path of the branch you want, e.g. "https://api.github.com/repos/brainwater/weather-monitor/commits/master"
- Write your wifi network name and password into `secrets.py` as `secrets['ssid']` and `secrets['password']`
- Press the reset button on your microcontroller, or run `microcontroller.reset()` on your microcontroller
- Note that there are intermittent bugs, look at the `boot_out.txt` for the output of `boot.py`, sometimes trying again works.
