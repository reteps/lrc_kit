from lrc_kit.parser import parse_lyrics
import json

class LRC:
    def __init__(self, lyrics, metadata={}):
        if isinstance(lyrics, str):
            self.lyrics, self.metadata = parse_lyrics(lyrics)
        else:
            self.lyrics = lyrics
            self.metadata = metadata
    
    def offset(self, min_offset=0, sec_offset=0, millis_offset=0):
        for line in self.lyrics:
            line.offset(min_offset=min_offset, sec_offset=sec_offset, millis_offset=millis_offset)
    
    def export(self, fp_or_str):
        if isinstance(fp_or_str, str):
            fp = open(fp_or_str, 'w')
        str_metadata = '\n'.join(f'[{key}:{value}]' for key, value in self.metadata.items()) + '\n'
        fp.write(str_metadata)
        fp.write(self.lyric_str)
    @property
    def lyric_str(self):
        return '\n'.join(str(l) for l in self.lyrics)