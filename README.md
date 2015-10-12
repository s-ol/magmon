Magnetman
=========

*Magnetman* is a small python tool that listens for keystrokes and lid-switch patterns, activated by tapping the lid-switch once.
It can be used to add little extra commands to trigger using magnetic implants.

Usage
-----
All rules must start with a tap in order to be recognized by *Magnetman*.
Other than taps, which are lid events shorter than .5 seconds, there are "lid holds" and keystrokes.
A sequence starts with a tap and consist of any number of other such events.
A rule maps a sequence to a system command to be executed when the sequence is matched.

Elevated privileges may be required to access the lidswitch or grab the keyboard focus.

### "standalone"
*Magnetman* comes with a convenient CLI for defining rules on the commandline.

    usage: magnetman.py [-h] [-l LID] [-k KBRD] [rule [rule ...]]

    positional arguments:
      rule                  a rule to follow

    optional arguments:
      -h, --help            show this help message and exit
      -l LID, --lid LID     evdev name of the Lid Switch
      -k KBRD, --kbrd KBRD  evdev name of the keyboard

A rule consists of the sequence to match, followed by a colon (`:`) and the command string to execute.
Sequences are strings of lowercase characters, didigts and periods, representing keypresses, lid holds (the digit is the hold length in seconds) and taps.

Example:

    sudo python magnetman.py '...:echo three taps' '.2a:echo tap, two second hold and an A'

### as a module
More sophisticated rules can be created via the method `add_rule`:

```python
from magnetman import MagnetMan
magnetman = MagnetMan("keyboard", "Lid")
magnetman.add_rule(['tap', 'a', 1, (1, 3), 'tap'], "echo test")
magnetman.watch()
```

Like on the CLI, there are three possible sequence entries:

* taps, which are .5s long, represented as the string `'tap'`,
* key presses, represented as a string containign the character they match
* lid holds, represented as the either the expected duration, matched +- MagnetMan.LID_TOLERANCE/2, or a tuple with upper and lower length boundaries (in seconds)
