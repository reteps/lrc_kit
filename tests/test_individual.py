import lrc_kit
from lrc_kit import SearchRequest
import os

def test_kugeci():
    engine = lrc_kit.KugeciProvider()
    search = SearchRequest('cuco', 'lover is a day')
    result = engine.search(search)
    assert result == None
    return
    result.export(os.path.join('files', 'the_adults_are_talking'))

def test_mega():
    engine = lrc_kit.MegalobizProvider()
    search = SearchRequest('current joys', 'kids')
    result = engine.search(search)
    result.export(os.path.join('files', 'kids'))

def test_syair():
    engine = lrc_kit.SyairProvider()
    search = SearchRequest('Yung Gravy', 'Mr. Clean')
    result = engine.search(search)
    result.export(os.path.join('files', 'mr_clean'))
def test_flac123():
    engine = lrc_kit.Flac123Provider()
    res = engine.search(SearchRequest('Dababy', 'Goin Baby'))
    res.export(os.path.join('files', 'you'))