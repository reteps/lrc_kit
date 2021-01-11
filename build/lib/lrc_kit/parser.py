from lrc_kit.line import LyricLine
import re

line_regex = re.compile(r'\[(?:(\d+):)?(\d+)(?:\.(\d+))?\]([^\[]+)')
metadata_regex = re.compile(r'\[([^\d:\.]+):([^\[]+)?\]')
def dirty_int(integer):
    if integer.isdigit():
        return int(integer)
    return 0
def parse_lyrics(lyrics):
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