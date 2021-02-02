from lrc_kit.line import LyricLine, Word
import re
from base64 import b64decode
import logging

line_regex = re.compile(r'\[(?:(\d+):)?(\d+)(?:\.(\d+))?\]([^\[]+)')
trc_word_regex = re.compile(r'<(\d*)>([^<]*)')
krc_word_regex = re.compile(r'<(\d*),(\d*),\d*>([^<]*)')
metadata_regex = re.compile(r'\[([^\d:\.]+):([^\[]+)?\]')
def dirty_int(integer):
    if integer.isdigit():
        return int(integer)
    return 0
def parse_lyrics(lyrics, kind='lrc'):
    if kind == 'lrc':
        lines, metadata = parse_lrc(lyrics)
    elif kind == 'trc' or kind == 'xtrc':
        # TODO xtrc translation
        lines, metadata = parse_trc(lyrics)
    elif kind == 'krc':
        lines, metadata = parse_krc(lyrics)
    else:
        logging.warning(lyrics)
        logging.warning(kind)
        raise NotImplementedError()
    metadata['kind'] = kind
    return lines, metadata
def parse_trc(lyrics):
    lines, metadata = parse_lrc(lyrics)
    for line in lines:
        word_timings = re.findall(trc_word_regex, line.text)
        words = list(map(lambda x: Word(int(x[0]), x[1]), word_timings))
        line.text = ''.join(w.text for w in words)
        line.timing = words
    return lines, metadata
def parse_lrc(lyrics):
    line_matches = re.findall(line_regex, lyrics)
    metadata_matches = re.findall(metadata_regex, lyrics)
    parsed_lines = []
    for match in line_matches:
        times = map(lambda x: dirty_int(x), match[:3])
        parsed_lines.append(LyricLine(match[3].strip(), *times))
    metadata = {}
    for match in metadata_matches:
        metadata[match[0]] = match[1]
    return parsed_lines, metadata

def parse_krc(lyrics):
    metadata_matches = re.findall(metadata_regex, lyrics)
    metadata = {}
    for match in metadata_matches:
        val = match[1]
        if match[0] == 'language':
            val = b64decode(val).decode('utf-8')
        metadata[match[0]] = val
    krc_word_matches = re.findall(krc_word_regex, lyrics)
    words = list(map(lambda x: Word(int(x[1]), x[2], offset=int(x[0])), krc_word_matches))
    lyric_line = LyricLine('', 0, 0, 0, timing=words)
    return [lyric_line], metadata