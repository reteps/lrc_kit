# lrc_kit

A very simple API for searching for LRC files in python

```python3
from lrc_kit import ComboLyricProvider, SearchRequest

engine = ComboLyricProvider()
search = SearchRequest('eminem', 'stan')
result, engine_used = engine.search(search)
result.export('stan.lrc')
```

See some more advanced usage in my [real time lyrics](https://github.com/reteps/real-time-lyrics) project :)
