from lrc_kit import LyricLine

def test_line():
    line = LyricLine('Damn', 6, 7, 63)
    line.offset(minutes=-7)
    assert line.minutes == 0
    assert line.seconds == -52
    assert line.milliseconds == 370