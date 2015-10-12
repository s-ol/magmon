import asyncio
from subprocess import Popen
from evdev import InputDevice, ecodes, categorize, list_devices

class MagnetMan(object):
    TAP_LENGTH      = .5
    SUBMIT_DELAY    = .7
    LID_TOLERANCE   = .5

    def __init__(self, user=None, kbname="keyboard", lidname="Lid"):
        self.user = user
        self.key = next(InputDevice(dev) for dev in list_devices() if kbname in InputDevice(dev).name)
        self.lid = next(InputDevice(dev) for dev in list_devices() if lidname in InputDevice(dev).name)
        self.loop = asyncio.get_event_loop()
        self.listening = False
        self.sequence = []
        self.finish_handle = None
        self.lastlid = 0

        self.patterns = []

    def add_command(self, pattern, action):
        for i,v in enumerate(pattern):
            if type(v) == int or type(v) == float:
                pattern[i] = (v - self.LID_TOLERANCE/2, v + self.LID_TOLERANCE/2)
        self.patterns.append((pattern, action))

    def watch(self):
        self.loop.add_reader(self.lid, self.handle_lid_evts)
        self.loop.add_reader(self.key, self.handle_key_evts)
        self.loop.run_forever()

    def process(self, sequence):
        for (pat, action) in self.patterns:
            if len(pat) != len(sequence):
                continue

            for exp, act in zip(pat, sequence):
                if exp == act:
                    continue

                if type(act) not in (int, float):
                    break

                if type(exp) == tuple:
                    if act < exp[0] or act > exp[1]:
                        break
                else:
                    break
            else:
                print("executing '{}'...".format(action))
                if self.user:
                    Popen(['/usr/bin/su', self.user, '-c', action])
                else:
                    Popen(action, shell=True)
                break
        else:
            print("no command found for {}".format(sequence))

    def finish(self):
        if self.listening:
            try:
                self.key.ungrab()
                self.listening = False
            except IOError: pass

        self.process(self.sequence)
        self.sequence.clear()

    def reschedule(self):
        if self.finish_handle:
            self.finish_handle.cancel()
        self.finish_handle = self.loop.call_later(self.SUBMIT_DELAY, self.finish)

    def handle_lid_evts(self):
        for evt in self.lid.read():
            if evt.type == ecodes.EV_SW and evt.code == ecodes.SW_LID:
                if evt.value == 0: # lid released
                    if self.lastlid + self.TAP_LENGTH > evt.timestamp(): # short tap
                        self.sequence.append('tap')
                        self.lastlid = evt.timestamp()
                        self.reschedule()
                        if not self.listening:
                            try:
                                self.key.grab()
                                self.listening = True
                            except IOError: pass
                    elif self.listening:
                        self.sequence.append(evt.timestamp()-self.lastlid)
                        self.reschedule()
                else: # lid down
                    self.lastlid = evt.timestamp()
                    if self.finish_handle:
                        self.finish_handle.cancel()

    def handle_key_evts(self):
        for evt in self.key.read():
            if evt.type == ecodes.EV_KEY and self.listening:
                if evt.value == 0: # key up
                    self.sequence.append(ecodes.KEY[evt.code][4:].lower())
                    self.reschedule()

if __name__ == "__main__":
    from textwrap import dedent
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            epilog=dedent("""\
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
                            """))
    parser.add_argument('-l', '--lid', default="Lid",
                        help="evdev name of the Lid Switch")
    parser.add_argument('-k', '--kbrd', default="keyboard",
                        help="evdev name of the keyboard")
    parser.add_argument('-u', '--user',
                        help="user to 'su' into before executing commands")
    parser.add_argument('-p', '--python-rule', nargs='*', default=[],
                        help="specify a rule with python sequence syntax")
    parser.add_argument('-r', '--rule', nargs='*', default=[],
                        help="specify a rule with simplified sequence syntax")
    args = parser.parse_args()

    magnetman = MagnetMan(user=args.user, kbname=args.kbrd, lidname=args.lid)

    if len(args.python_rule) + len(args.rule) == 0:
        args.rule = ['.1.1:killall i3lock', '..a:echo test']

    for rule in args.python_rule:
        rule, action = rule.split(":", 1)
        magnetman.add_command(eval(rule), action)

    for rule in args.rule:
        rule, action = rule.split(":", 1)
        seq = []
        for char in rule:
            if char == ".":
                seq.append('tap')
            else:
                try:
                    seq.append(int(char))
                except ValueError:
                    seq.append(char)
        magnetman.add_command(seq, action)

    magnetman.watch()
