import re
import math
class LyricLine:
    def __init__(self, text, min, sec, fraction):
        self.text = text
        self.minutes = min
        self.seconds = sec
        self.milliseconds = int(fraction / 10**len(str(fraction)) * 1000)
    def __str__(self):
        return f'[{self.minutes:02}:{self.seconds:02}.{self.milliseconds:03}]{self.text}'
    def offset(self, minutes=0, seconds=0, milliseconds=0):
        new_time_in_milliseconds = self.time_millis + self.to_millis(minutes, seconds, milliseconds)
        self.minutes, self.seconds, self.milliseconds = self.to_min_sec_millis(new_time_in_milliseconds)
    @staticmethod
    def to_millis(m,s,mi):
        return m * 60 * 1000 + s * 1000 + mi
    @property
    def time_seconds(self):
        return self.time_millis / 1000
    @property
    def time_millis(self):
        return self.to_millis(self.minutes, self.seconds, self.milliseconds)
        
    @staticmethod
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