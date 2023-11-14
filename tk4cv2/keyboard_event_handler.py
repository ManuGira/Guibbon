import dataclasses
import enum
import tkinter as tk



class KeyboardEventHandler:
    class KEYCODE(enum.Enum):
        SHIFT = 16
        CTRL = 17
        ALT = 18

    @dataclasses.dataclass()
    class Modifier:
        SHIFT: bool = False
        CTRL: bool = False
        ALT: bool = False

    def __init__(self):
        self.modifier = KeyboardEventHandler.Modifier()
        self.keysdown = set()
        self.last_keypressed = -1
        self.last_keyreleased = -1
        self.is_keypress_updated = False
        self.is_keyrelease_updated = False

        cv_row1 = [   27, 7340032, 7405568, 7471104, 7536640, 7602176, 7667712, 7733248, 7798784, 7864320, 7929856, 7995392, 8060928]
        ic_row1 = [65307,   65470,   65471,   65472,   65473,   65474,   65475,   65476,   65477,   65478,   65479,   65480,   65481]
        cv_row2 = [167, 49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 39, 176, 43, 34, 42, 231, 37, 38, 47, 40, 41, 61, 63,     8]
        ic_row2 = [167, 49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 39, 176, 43, 34, 42, 231, 37, 38, 47, 40, 41, 61, 63, 65288]
        cv_numpad = [2949120, 3014656,    13, 2293760, 2621440, 2228224, 2424832, 2555904, 43, 2359296, 2490368, 2162688, 47, 42, 45]
        ic_numpad = [  65379,   65535, 65293,   65367,   65364,   65366,   65361,   65363, 43,   65360,   65362,   65365, 47, 42, 45]
        cv_tab = [    9]
        ic_tab = [65289]
        cv_spec = [232, 233, 224, 36, 60, 44, 46, 45, 32]
        ic_spec = [232, 233, 224, 36, 60, 44, 46, 45, 32]
        cv_spec_shift = [252,    33, 246, 228, 163, 62, 59, 58, 95]
        ic_spec_shift = [252, 65312, 246, 228, 163, 62, 59, 58, 95]
        cv_spec_altgr = [ 91,    93, 123, 125, 92]
        ic_spec_altgr = [232, 65312, 224,  36, 60]
        self.map_ic2cv = dict(zip(
            ic_row1 + ic_row2 + ic_numpad + ic_tab + ic_spec + ic_spec_shift + ic_spec_altgr,
            cv_row1 + cv_row2 + cv_numpad + cv_tab + cv_spec + cv_spec_shift + cv_spec_altgr
        ))

    def is_modifier_key(self, event):
        return any([event.keycode == kc.value for kc in self.KEYCODE])

    def update_modifier(self, event, is_down):
        if event.keycode == self.KEYCODE.SHIFT.value:
            self.modifier.SHIFT = is_down

        if event.keycode == self.KEYCODE.CTRL.value:
            self.modifier.CTRL = is_down

        if event.keycode == self.KEYCODE.ALT.value:
            self.modifier.ALT = is_down

    def on_event(self, event):
        # def printkey(event, keywords):
        #     print(", ".join([f"{kw}: {event.__getattribute__(kw)}".ljust(5) for kw in keywords]))
        #     print(", ".join([(kw + ": " + str(event.__getattribute__(kw))).ljust(5) for kw in keywords]))
        # printkey(event, "char delta keycode keysym keysym_num num state type".split())

        # The obvious information
        is_keypress = event.type == tk.EventType.KeyPress
        is_keyrelease = event.type == tk.EventType.KeyRelease
        assert(is_keypress or is_keyrelease)

        if self.is_modifier_key(event):
            self.update_modifier(event, is_keypress)
            return

        num = self.map_ic2cv[event.keysym_num] if event.keysym_num in self.map_ic2cv else event.keysym_num

        if num not in self.keysdown and is_keypress:
            self.is_keypress_updated = True
            self.last_keypressed = num
            self.keysdown.add(num)
        elif num in self.keysdown and is_keyrelease:
            self.is_keyrelease_updated = True
            self.last_keyreleased = num
            self.keysdown.remove(num)
