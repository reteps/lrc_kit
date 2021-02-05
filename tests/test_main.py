from lrc_kit import ComboLyricsProvider, SearchRequest, KugouProvider, Flac123Provider, MegalobizProvider, PROVIDERS
import lrc_kit
import logging, os
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel('DEBUG')

def test_flac123():
    engine = Flac123Provider()
    res = engine.search(SearchRequest('Mk.Gee', 'You'))
    res.export(os.path.join('files', 'you'))
def test_custom():
    providers = lrc_kit.MINIMAL_PROVIDERS + [lrc_kit.Flac123Provider]
    engine = ComboLyricsProvider(providers)
    res = engine.search(SearchRequest('Mk.Gee', 'You'))
    res.export(os.path.join('files', 'you'))
def test_mega():
    engine = MegalobizProvider()
    search = SearchRequest('current joys', 'kids')
    result = engine.search(search)
    result.export(os.path.join('files', 'kids'))
def test_individual_success_multi_word():
    search = SearchRequest('Playboi Carti', 'Broke Boi')
    LOGGER.info(list(map(lambda p:p.name, PROVIDERS)))
    for provider in PROVIDERS:
        engine = provider()
        result = engine.search(search)
        if result != None:
            result.export(os.path.join('files', f'{engine.name}_stan'))
            LOGGER.info(engine.name + ' Success!')
        else:
            LOGGER.info(engine.name + " Fail :(")
def test_individual_success():
    search = SearchRequest('eminem', 'stan')
    LOGGER.info(list(map(lambda p:p.name, PROVIDERS)))
    for provider in PROVIDERS:
        engine = provider()
        result = engine.search(search)
        if result != None:
            result.export(os.path.join('files', f'{engine.name}_stan'))
            LOGGER.info(engine.name + ' Success!')
        else:
            LOGGER.info(engine.name + " Fail :(")
def test_individual_fail():
    search = SearchRequest('Felly', 'Fabrics')
    for provider in PROVIDERS:
        engine = provider()
        result = engine.search(search)
        if result != None:
            result.export(os.path.join('files', f'{engine.name}_felly'))
def test_combo_fail_2():
    engine = ComboLyricsProvider()
    search = SearchRequest('431242424234', 'DJ adsfasdfsdafadsfsd')
    result = engine.search(search)
    assert result == None

def test_combo_success():
    engine = ComboLyricsProvider()
    search = SearchRequest('eminem', 'stan')
    result = engine.search(search)
    result.export(os.path.join('files', 'stan'), extension='.lrc')

    assert result != None


