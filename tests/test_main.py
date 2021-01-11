from lrc_kit import ComboLyricProvider, SearchRequest

def test_combo_fail_2():
    engine = ComboLyricProvider()
    search = SearchRequest('431242424234', 'DJ adsfasdfsdafadsfsd')
    result, engine_used = engine.search(search)
    assert result == None

def test_combo_success():
    engine = ComboLyricProvider()
    search = SearchRequest('eminem', 'stan')
    result, engine_used = engine.search(search)

    assert result != None

def test_combo_fail():
    engine = ComboLyricProvider()
    search = SearchRequest('Felly', 'Fabrics')
    result, engine_used = engine.search(search)
    assert result == None

print('Tests passed.')