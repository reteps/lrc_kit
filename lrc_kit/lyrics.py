from lrc_kit.parser import parse_lyrics
import json

class Lyrics:
    def __init__(self, lyrics, metadata={}, kind='lrc'):
        self.kind = metadata.get('kind', kind)
        if isinstance(lyrics, str):
            self.lyrics, self.metadata = parse_lyrics(lyrics, kind)
        else:
            self.lyrics = lyrics
            self.metadata = metadata
    
    def offset(self, minutes=0, seconds=0, milliseconds=0):
        for line in self.lyrics:
            line.offset(min_offset=minutes, sec_offset=seconds, millis_offset=milliseconds)

    def export(self, fp_or_str, extension=None):
        self.metadata.pop('kind', None)
        if isinstance(fp_or_str, str):
            if extension is None:
                extension = '.' + self.kind
                fp_or_str += extension
            fp = open(fp_or_str, 'w')
        str_metadata = '\n'.join(f'[{key}:{value}]' for key, value in self.metadata.items()) + '\n'
        fp.write(str_metadata)
        fp.write(self.__str__())
    def __str__(self):
        return '\n'.join(str(l) for l in self.lyrics)