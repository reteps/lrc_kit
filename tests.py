from lrc_kit import ComboLyricProvider, SearchRequest

engine = ComboLyricProvider()
search = SearchRequest('eminem', 'stan')
result, engine_used = engine.search(search)
result.export('stan.lrc')