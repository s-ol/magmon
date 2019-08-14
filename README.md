Magmon
=========

*Magmon* is a small python tool that listens for keystrokes and lid-switch patterns, activated by tapping the lid-switch once.
It can be used to add little extra commands to trigger using magnetic implants.

Usage
-----
All rules must start with a tap in order to be recognized by *Magmon*.
Other than taps, which are lid events shorter than .5 seconds, there are "lid holds" and keystrokes.
A sequence starts with a tap and consist of any number of other such events.
A rule maps a sequence to a system command to be executed when the sequence is matched.

Elevated privileges may be required to access the lidswitch or grab the keyboard focus.

### "standalone"
*Magmon* comes with a convenient CLI for defining rules on the commandline.

    usage: magmon.py [-h] [-l LID] [-k KBRD] [-u USER]
                     [-p [PYTHON_RULE [PYTHON_RULE ...]]]
                     [-r [RULE [RULE ...]]]

    optional arguments:
      -h, --help            show this help message and exit
      -l LID, --lid LID     evdev name of the Lid Switch
      -k KBRD, --kbrd KBRD  evdev name of the keyboard
      -u USER, --user USER  user to 'su' into before executing commands
      -p [PYTHON_RULE [PYTHON_RULE ...]], --python-rule [PYTHON_RULE [PYTHON_RULE ...]]
                            specify a rule with python sequence syntax
      -r [RULE [RULE ...]], --rule [RULE [RULE ...]]
                            specify a rule with simplified sequence syntax
      -s, --show            print list of rules

    all rules are formatted as sequence:command.

    simplified sequence syntax:
        .       a tap
        [0-9]   that many seconds of holding
        [a-z]   that key

    python sequence syntax:
        python syntax expects a python list of values like so:

        "tap"       a tap
        any number  a hold of that length (seconds)
        (min, max)  a hold between min and max seconds
        any string  that key

A rule consists of the sequence to match, followed by a colon (`:`) and the command string to execute.
Simplified sequences are strings of lowercase characters, didigts and periods, representing keypresses, lid holds (the digit is the hold length in seconds) and taps.

Example:

    sudo python magmon.py -u s-ol -r '...:echo three taps' -r '.2a:echo tap, two second hold and an A key'

Python sequences work like in the python module and are simply parsed using `eval()`.

### as a module
More sophisticated rules can be created via the python syntax and the method `add_rule`.
The python function takes a callback as it's second argument:

```python
from magmon import Magmon
magmon = Magmon("keyboard", "Lid")
magmon.add_rule(['tap', 'a', 1, (1, 3), 'tap'], lambda: print "test")
magmon.watch()
```

Like on the CLI, there are three possible sequence entries:

* taps, which are .5s long, represented as the string `'tap'`,
* key presses, represented as a string containign the character they match
* lid holds, represented as the either the expected duration, matched +- Magmon.LID_TOLERANCE/2, or a tuple with upper and lower length boundaries (in seconds)
