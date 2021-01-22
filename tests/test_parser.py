from lrc_kit import parse_lyrics, Lyrics
import logging, os
def test_parser():

    with open('files/stan.lrc') as f:
        contents = f.read()
        lines, metadata = parse_lyrics(contents)
        lrc = Lyrics(lines, metadata)
        assert lrc.metadata['by'] == '野吉他'
        assert len(lrc.lyrics) == 129
        assert lrc.lyrics[-1].text == 'Damn!'
        assert lrc.lyrics[-1].minutes == 6
        assert lrc.lyrics[-1].seconds == 7
        assert lrc.lyrics[-1].milliseconds == 630


def test_trc():

    with open('files/Xiami_felly.lrc') as f:
        contents = f.read()
        lines, metadata = parse_lyrics(contents, kind='trc')
        lrc = Lyrics(lines, metadata)
        lrc.export(os.path.join('files', 'out_felly'))
        for line in lrc.lyrics:
            text = ''
            for word in line.timing:
                text += str(word.offset) + word.text 
            logging.info(text)
