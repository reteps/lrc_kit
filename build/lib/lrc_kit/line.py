import re
import math
class LyricLine:
    line_regex = re.compile(r'\[(?:(\d+):)?(\d+)(?:\.(\d+))?\]([^\[]+)')
    def __init__(self, text, min, sec, fraction):
        self.text = text
        self.min = min
        self.sec = sec
        self.millis = int(fraction / 10**len(str(fraction)) * 1000)
    def __str__(self):
        display = f'{self.min:02}:{self.sec:02}.{self.millis:03}'
        return f'[{display}]{self.text}'
    def offset(self, min_offset=0, sec_offset=0, millis_offset=0):
        self.min, self.sec, self.millis = self.to_time(self.to_millis(self.min + min_offset, self.sec + sec_offset, self.millis + millis_offset))
    @staticmethod
    def to_millis(m,s,mi):
        return m * 60 * 1000 + s * 1000 + mi
    @property
    def time_seconds(self):
        return self.time_millis / 1000
    @property
    def time_millis(self):
        return self.to_millis(self.min, self.sec, self.millis)
        
    @staticmethod
    def to_time(millis):
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