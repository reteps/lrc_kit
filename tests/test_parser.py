from lrc_kit import parse_lyrics, LRC

def test_parser():

    with open('files/stan.lrc') as f:
        contents = f.read()
        lines, metadata = parse_lyrics(contents)
        lrc = LRC(lines, metadata)
        assert lrc.metadata['by'] == 'test'
        assert len(lrc.lyrics) == 129
        assert lrc.lyrics[-1].text == 'Damn!'
        assert lrc.lyrics[-1].minutes == 6
        assert lrc.lyrics[-1].seconds == 7
        assert lrc.lyrics[-1].milliseconds == 630