import re
import math

def to_millis(m,s,mi):
    return m * 60 * 1000 + s * 1000 + mi
def to_min_sec_millis(millis):
    sign = 1
    if millis < 0:
        sign = -1
    m, s = divmod(millis, sign * 60 * 1000)
    s, mi = divmod(s, sign * 1000)
    mi = abs(mi)
    if sign == -1:
        if m != 0:
            m *= sign
        elif s != 0:
            s *= sign
        elif mi != 0:
            mi *= sign
    return m, s, mi

class Word:
    def __init__(self, duration, text, offset=None):
        self.text = text
        self.duration = duration
        self.offset = offset
    def __str__(self):
        return f'{self.text}' # TODO export as TRC
class LyricLine:
    def __init__(self, text, min, sec, fraction, timing=None):
        self.text = text
        self.minutes = min
        self.seconds = sec
        self.milliseconds = int(fraction / 10**len(str(fraction)) * 1000)
        self.timing = timing
    @property
    def timing(self):
        return self._timing
    @timing.setter
    def timing(self, value):
        if value is not None:
            offset = -value[0].duration
            for word in value:
                offset += word.duration
                word.offset = offset
        self._timing = value
    def __str__(self):
        text = self.text
        if self.timing:
            text = ''.join(str(w) for w in self.timing)
        return f'[{self.minutes:02}:{self.seconds:02}.{self.milliseconds:03}]{text}'
    def offset(self, minutes=0, seconds=0, milliseconds=0):
        new_time_in_milliseconds = self.time_millis + to_millis(minutes, seconds, milliseconds)
        self.minutes, self.seconds, self.milliseconds = to_min_sec_millis(new_time_in_milliseconds)

    @property
    def time_seconds(self):
        return self.time_millis / 1000
    @property
    def time_millis(self):
        return to_millis(self.minutes, self.seconds, self.milliseconds)
    