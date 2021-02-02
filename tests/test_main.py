from lrc_kit import ComboLyricsProvider, SearchRequest, KugouProvider, Flac123Provider, MegalobizProvider, PROVIDERS
import logging, os
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel('DEBUG')
'''
def test_kug():
    engine = KugouProvider()
    search = SearchRequest('周深', '归处')
    result = engine.search(search)
    result.export(os.path.join('files', 'kugou_test'))
def test_flac():
    engine = Flac123Provider()
    search = SearchRequest('playboi carti', 'broke boi')
    result = engine.search(search)
    result.export(os.path.join('files', 'broke_boi'))
'''
def test_mega():
    engine = MegalobizProvider()
    search = SearchRequest('current joys', 'new flesh')
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


