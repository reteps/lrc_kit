import requests
import re
import html
from bs4 import BeautifulSoup
import unicodedata
import base64
import zlib
import json
import html

from abc import abstractmethod
from lrc_kit.lyrics import Lyrics
import logging
# https://github.com/ddddxxx/LyricsKit/tree/master/Sources/LyricsService/Provider
# https://github.com/blueset/project-lyricova/tree/master/packages/lyrics-kit
class LyricsProvider:
    user_agent = {'user-agent': 'lrc_kit'}
    def __init__(self, session=None):
        if session is None:
            session = requests.Session()
        self.session = session
    @abstractmethod
    def raw_search(self, search_request):
        pass
    @abstractmethod
    def fetch(self, input):
        raise NotImplementedError()
    def search(self, search_request):
        logging.debug(self.name + ' ' + search_request.as_string)
        try:
            val, meta = self.raw_search(search_request)
            if val:
                lrc = self.fetch(val)
                if lrc:
                    lrc.metadata['provider'] = self.name
                    logging.info(meta)
                    lrc.metadata = {**meta, **lrc.metadata}
                    if 'fetch' not in lrc.metadata:
                        lrc.metadata['fetch'] = val
                    return lrc
            return None
        except Exception as e:
            logging.error(e)
            raise e
        return None

class SearchRequest:
    def __init__(self, artist, song, duration=None):
        self.artist = artist.lower()
        self.song = song.lower()
        self.duration = duration
    @property
    def as_string(self):
        return self.artist + ' ' + self.song
    @property
    def artist_normalized(self):
        return ' '.join(re.sub(r'\W+',' ', self.artist).split(' '))
    @property
    def song_normalized(self):
        return ' '.join(re.sub(r'\W+',' ', self.song).split(' '))

class ComboLyricsProvider(LyricsProvider):
    name = "Combo"
    def __init__(self, providers=None, **kwargs):
        self.kwargs = kwargs
        super().__init__(self.kwargs)
        if providers == None:
            self.providers = PROVIDERS
        elif providers == 'EXTENDED':
            self.providers = EXTENDED_PROVIDERS
        elif providers == 'MINIMAL':
            self.providers = MINIMAL_PROVIDERS
        elif providers == 'ALL':
            self.providers = ALL_PROVIDERS
        else:
            self.providers = []
            provider_lookup = {provider.name: provider for provider in ALL_PROVIDERS}
            for provider in providers:
                if issubclass(provider, LyricsProvider):
                    self.providers.append(provider)
                elif isinstance(provider, str):
                    if provider in provider_lookup:
                        self.providers.append(provider_lookup[provider])
                    else:
                        raise ValueError('That provider does not exist.')
                else:
                    raise ValueError(f'Provider "{provider}" be "str" or "LyricsProvider" (Not an instance).')
    def search(self, search_request):
        for provider in self.providers:
            logging.info(provider.name)
            res = provider(**self.kwargs).search(search_request)
            if res:
                return res
        return None
class Flac123Provider(LyricsProvider):
    name = "Flac123"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def get_cookie_jar(self):
        login_url = 'https://www.flac123.com/login'
        res = self.session.get(login_url)
        token_re = re.compile(r'name="_token" value="([^"]*)"')
        token = re.search(token_re, res.text).group(1)
        logging.debug('Token is' + str(token))
        body = {
            'email': 'peter.promotions.stenger@gmail.com',
            'password': 'retep123',
            '_token': token
        }
        return self.session.post(login_url, body, cookies=res.cookies).cookies
    def raw_search(self, search_request):
        logging.debug(search_request.as_string)
        params = {
            'kw': search_request.as_string
        }
        html = self.session.get('https://www.flac123.com/search', params=params).text
        result_regex = re.compile(r'flex\">([\s\S]*?)<\/tr>')
        pair_regex = re.compile(r'[f|s]=\"([^"]*)\">([^<]*)')
        possible_matches = []
        for result in re.findall(result_regex, html)[:10]:
            result_html = result
            # logging.debug(result_html)
            pairs = re.findall(pair_regex, result_html)
            song = pairs[0]
            artists = pairs[1:-2]
            album = pairs[-2][1]
            logging.debug('{}={}'.format(song[1].lower(), ','.join([x[1].lower() for x in artists])))
            if song[1].lower() == search_request.song and search_request.artist in [x[1].lower() for x in artists]:
                possible_matches.append((song[0], {
                    'ti': song[1],
                    'ar': artists[0][1],
                    'al': album,
                    'length': pairs[-1][1],
                    'fetch': song[0]
                }))
        
        for link, metadata in possible_matches:
            result = self.session.get(link, cookies=self.get_cookie_jar()).text
            lyric_regex = re.compile(r'id="lyric-original" class="d-none">([\s\S]*?)<\/div>')
            text = re.search(lyric_regex, result)
            if text:
                return text, metadata

        logging.debug('None found')
        return None, None
        # \s?<a href=\"([^"]*)\">([^<]*)[\s\S]*?href=\"([^"]*)\">([^<]*)[\s\S]*?href=\"([^"]*)\">([^<]*)[\s\S]*?muted">([^<]*)<\/td>\s?
    def fetch(self, text):
        full_text = html.unescape(text.group(1))
        logging.debug(full_text)
        return Lyrics(full_text)
class KugouProvider(LyricsProvider):
    name = "Kugou"
    def raw_search(self, search_request):
        params = {
            'keyword': search_request.as_string,
            'client': 'pc',
            'ver': 1,
            'man': 1
        }
        if search_request.duration:
            params['duration'] = search_request.duration
        data = self.session.get('http://lyrics.kugou.com/search', params=params).json()
        logging.debug(f'{len(data.get("candidates", []))} ({self.name}) results')
        if data['candidates']:
            c = data['candidates'][0]
            return (c['id'], c['accesskey']), {
                'ti': c['song'],
                'ar': c['singer']
            }
        return None, None
    def fetch(self, token):
        token_id, token_key = token
        params = {
            "id": token_id,
            "accesskey": token_key,
            "fmt": "krc",
            "charset": "utf8",
            "client": "pc",
            "ver": 1,
        }
        data = self.session.get('http://lyrics.kugou.com/download', params=params).json()['content']
        # logging.info(self.decode_krc(base64.b64decode(data)))
        return Lyrics(self.decode_krc(base64.b64decode(data)), kind='krc')
    def decode_krc(self, krc):
        byte_krc = bytearray(krc)
        if byte_krc[:4] != b'krc1':
            return None
        byte_krc = byte_krc[4:]
        decode_bytes = [64, 71, 97, 119, 94, 50, 116, 71, 81, 54, 49, 45, 206, 210, 110, 105]
        for i in range(len(byte_krc)):
            byte_krc[i] ^= decode_bytes[i & 0b1111]
        
        lyric_text = zlib.decompress(byte_krc).decode('utf-8')
        logging.debug(lyric_text)
        return lyric_text

class XiamiProvider(LyricsProvider):
    name = 'Xiami'
    def raw_search(self, search_request):
        params = {
            'key': search_request.as_string,
            'limit': 10,
            'r': 'search/songs',
            'app_key': 1
        }
        headers = {
            'Referer': 'http://h.xiami.com/'
        }
        body = self.session.get('http://api.xiami.com/web', params=params, headers=headers).json()['data']
        logging.debug(f'{len(body.get("songs", []))} ({self.name}) results')

        for result in body['songs']:
            artist = result['artist_name']
            song = result['song_name']
            success = artist.lower() == search_request.artist and song.lower() == search_request.song and result['lyric']
            logging.debug(f'{artist} {song} {success}')
            if artist.lower() == search_request.artist and song.lower() == search_request.song and result['lyric']:
                metadata = {
                    'ar': artist,
                    'ti': song,
                    'al': result['album_name'],
                    'cover': result['album_logo'].replace('\\/', '/')
                }
                return result['lyric'].replace('\\/', '/'), metadata
        return None, None
    def fetch(self, lrc_url):
        lyric_text = self.session.get(lrc_url).text
        logging.debug('FETCHING Xiami')
        extension = lrc_url.split('.')[-1]
        logging.debug(f'Xiami KIND {extension}')
        if extension in ['lrc', 'trc', 'xtrc']:
            return Lyrics(lyric_text, kind=extension)
        return None
class QQProvider(LyricsProvider):
    name = 'QQ'
    def raw_search(self, search_request):
        params = {
            'w': search_request.as_string
        }
        body = json.loads(self.session.get('https://c.y.qq.com/soso/fcgi-bin/client_search_cp', params=params).text[9:-1])['data']
        logging.debug(f'{len(body["song"]["list"])} ({self.name}) results')

        for song in body['song']['list']:
            name = song['songname']
            artist = song['singer'][0]['name']
            if search_request.song == name.lower() and search_request.artist == artist.lower():
                metadata = {
                    'ti': name,
                    'ar': artist,
                    'al': song['albumname']
                }
                return song['songmid'], metadata
        return None, None
    def fetch(self, song_id):
        params = {
            'songmid': song_id,
            'g_tk': 5381
        }
        headers = {
            'Referer': 'y.qq.com/portal/player.html'
        }
        body = json.loads(self.session.get('https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg', params=params, headers=headers).text[18:-1])
        if body.get('lyric'):
            lyric_text = html.unescape(base64.b64decode(body['lyric']).decode('utf-8'))
            return Lyrics(lyric_text)
        return None

class GecimiLyricProvider(LyricsProvider):
    name = 'Gecimi'
    def raw_search(self, search_request):
        # http://gecimi.com/api/lyric/%E6%B5%B7%E9%98%94%E5%A4%A9%E7%A9%BA/Beyond
        songs = self.session.get('http://gecimi.com/api/lyric/{search_request.song}/{search_request.artist}').json()['result']
        logging.debug(f'{len(songs)} ({self.name}) results')
        for s in songs:
            song = s['song']
            if song.lower() == search_request.song:
                return s['lrc'], {
                    'ti': s['song']
                }
        return None, None

    def fetch(self, lrc_url):
        lyric_text = self.session.get(lrc_url).text
        return Lyrics(lyric_text)
class Music163Provider(LyricsProvider):
    name = 'Music163'
    def raw_search(self, search_request):
        search_url = 'http://music.163.com/api/search/pc'
        search_params = {
            'limit': 10,
            'type': 1,
            'offset': 0,
            's': search_request.as_string
        }
        resp = self.session.get(search_url, params=search_params).json()['result']
        logging.debug(f'{len(resp.get("songs", []))} ({self.name}) results')
        if resp.get('songs') and len(resp['songs']) > 0:
            for result in resp['songs']:
                song = result['name']
                artist = result['artists'][0]['name']
                if song.lower() == search_request.song and artist.lower() == search_request.artist:
                    metadata = {
                        'ti': song,
                        'ar': artist,
                        'al': result['album']['name'],
                        'cover': result['album']['picUrl']
                    }
                    return result['id'], metadata
        return None, None
    def fetch(self, song_id):
        lyric_url = 'http://music.163.com/api/song/lyric'
        lyric_params = {
            'id': song_id,
            'lv': 1,
            'kv': 1,
            'tv': -1
        }
        l_resp = self.session.get(lyric_url, params=lyric_params).json()
        lrc = l_resp.get('lrc')
        if lrc:
            lyric_text = lrc['lyric']
        
            return Lyrics(lyric_text)
        return None
class SogeciProvider(LyricsProvider):
    name = 'Sogeci'
    def raw_search(self, search_request):
        artist_fixed = re.sub(r'\W+', '', search_request.artist)
        artist_page = f'http://www.sogeci.net/geshou/{artist_fixed}.html'
        page = self.session.get(artist_page)
        if page.status_code == 404:
            return None, None
        soup = BeautifulSoup(page.text, 'lxml')
        links = soup.find('div', class_='showNewSong')
        links = links.find_all('a')
        logging.debug(f'{len(links)} ({self.name}) results')
        for link in links:
            if link['title'].lower() == search_request.song:
                return 'http://www.sogeci.net' + link['href'], {
                    'ti': link['title']
                }
                
        return None, None
    def fetch(self, lyric_url):
        lyric_regex = re.compile(r'<pre>([\s\S]*?)</pre>')
        lyric_page = self.session.get(lyric_url).text
        lyrics = re.search(lyric_regex, lyric_page).group(1)
        lyric_text = lyrics.strip()
        if '[' in lyric_text and ']' in lyric_text:
            return Lyrics(lyric_text)
        return None
class SyairProvider(LyricsProvider):
    name = 'Syair'
    def raw_search(self, search_request):
        search_page = self.session.get("https://www.syair.info/search", params={
        "q": f'{search_request.artist_normalized} {search_request.song}'
        }, headers = self.user_agent).text
        result_regex = re.compile(r'href=\"([^\"]+)\" target=\"_blank\" class=\"title\">([^<]+)<\/a><br>([^<]+)')
        results = re.findall(result_regex, search_page)
        best_result = (None, None)
        for result in results:
            href = result[0]
            text = result[1]
            lrc_preview = result[2]
            try:
                artist, song = text.replace('.lrc','').strip().lower().split(' - ', 1)
            except ValueError:
                continue
            if (search_request.artist in artist or search_request.artist_normalized in artist) and search_request.song in song:
                metadata = {
                    'ar': artist,
                    'ti': song
                }
                best_result = ("https://www.syair.info" + href, metadata)
                if '[offset' not in lrc_preview:
                    break
        return best_result
    def fetch(self, lyric_url):
        lyrics_page = self.session.get(lyric_url, headers=self.user_agent).text
        lyric_regex = re.compile(r'<div class=\"entry\">.*?<\/p>([\s\S]+?)}?<div')
        match = re.search(lyric_regex, lyrics_page).group(1)
        lyric_text = match.replace('<br>','')
        return Lyrics(lyric_text)
class MooflacProvider(LyricsProvider):
    name = 'Mooflac'
    def get_cookie_jar(self):
        login_url = 'https://www.mooflac.com/login'
        res = self.session.get(login_url)
        token_re = re.compile(r'name="_token" value="(.*)"')
        token = re.search(token_re, res.text).group(1)

        body = {
            'email': 'peter.promotions.stenger@gmail.com',
            'password': 'retep123',
            '_token': token
        }
        return self.session.post(login_url, body, cookies=res.cookies).cookies
    def __init__(self):
        super().__init__()
        self.cookies = self.get_cookie_jar()
    def fetch(self, url):
        lyrics_page = self.session.get(url, cookies=self.cookies).text
        has_lyrics = 'lyric-context' in lyrics_page
        if not has_lyrics:
            return None
        lyrics_re = re.compile(r'<div class="hidden" id="lyric-context">([\s\S]*?)</div>')
        lyrics = re.search(lyrics_re, lyrics_page)
        lrc_text = '\n'.join([html.unescape(line.split('<br>')[0]) for line in lyrics.group(1).split('\n')])
        if '[' not in lrc_text and ']' not in lrc_text:
            return None
        return Lyrics(lrc_text)
    def raw_search(self, search_request):

        search_page = self.session.get('https://www.mooflac.com/search', params={
            'q': search_request.song + ' ' + search_request.artist_normalized 
        }, cookies=self.cookies).text
        soup = BeautifulSoup(search_page, 'lxml')
        result_table = soup.find('tbody')
        if result_table:
            results = result_table.find_all('tr')[:10]
            logging.debug(f'{len(results)} ({self.name}) results')
            for result in results:
                links = result.find_all('td')
                href = links[0].find('a')['href']
                text = [unicodedata.normalize("NFKD", l.text.strip()) for l in links]
                song = text[0]
                artist = text[1]
                if search_request.song == song.lower() and (search_request.artist_normalized == artist.lower() or search_request.artist == artist.lower()):
                    return href, {
                        'ti': song,
                        'ar': artist
                    }
        return None, None

class RentanaAdvisorProvider(LyricsProvider):
    name = "RentAnAdviser"
    def raw_search(self, search_request):

        search_results = self.session.get("https://www.rentanadviser.com/en/subtitles/subtitles4songs.aspx", 
            params={'src': search_request.as_string})
        soup = BeautifulSoup(search_results.text, 'lxml')
        result_links = soup.find(id="tablecontainer").find_all("a")
        logging.debug(f'{len(result_links)} ({self.name}) results')

        for result_link in result_links:
            href = result_link["href"]
            if href != "subtitles4songs.aspx":
                lower_title = result_link.get_text().lower()
                if search_request.artist in lower_title and search_request.song in lower_title:
                    url = f"https://www.rentanadviser.com/en/subtitles/{href}&type=lrc" 
                    return (url, {})
        return None, None
    def fetch(self, lyric_url):
        possible_text = self.session.get(lyric_url)
        soup = BeautifulSoup(possible_text.text, 'html.parser')

        event_validation = soup.find(id="__EVENTVALIDATION")["value"]
        view_state = soup.find(id="__VIEWSTATE")["value"]

        lyric_text = requests.post(lyric_url, {"__EVENTTARGET": "ctl00$ContentPlaceHolder1$btnlyrics",
                                    "__EVENTVALIDATION": event_validation,
                                    "__VIEWSTATE": view_state}).text

        return Lyrics(lyric_text)

class MegalobizProvider(LyricsProvider):
    name = "Megalobiz"
    def raw_search(self, search_request):
        search_results = self.session.get("https://www.megalobiz.com/search/all", params={
            "qry": search_request.as_string
            # "display": "more"
        })
        search_regex = re.compile(r'<a c.*name=\"(.+)\"\s+.*\s+href=\"(.+)\" >')
        matches = re.findall(search_regex, search_results.text)
        for match in matches:
            name = match[0].lower()
            href = match[1]
            if search_request.artist in name and search_request.song in name:
                return "https://www.megalobiz.com" + href, {}
        return None, None

    def fetch(self, url):
        possible_text = self.session.get(url).text
        lyrics_regex = re.compile(r'<span id=\"lrc_\d+_lyrics\"\s>([\s\S]+?)<\/span>')
        lyrics = re.search(lyrics_regex,possible_text)
        lyric_text = lyrics[1].replace('<br />','')
        return Lyrics(lyric_text)


class LyricFindProvider(LyricsProvider):
    name = "LyricFind"
    # https://github.com/alan96320/camocist-radio/blob/7adcc4f0482b395d97ce296745fb475be7f98052/app/Http/Controllers/Frontend/ApiController.php#L141
    def __init__(self, apikey=None, lrckey=None, **kwargs):
        super().__init__(**kwargs)
        self.apikey = apikey
        self.lrckey = lrckey
        if self.apikey is None or self.lrckey is None:
            raise ValueError('APIKEY and LRCKEY must be provided.')
    def raw_search(self, search_request):
        base_params = {
            'apikey': self.apikey,
            'reqtype': 'default',
            'output': 'json',
            'territory': 'US',
            'format': 'lrc',
            'lrckey': self.lrckey
        }
        
        query = {
            'trackid': f'artistname:{search_request.artist},trackname:{search_request.song}'
        }
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        res = self.session.get('https://api.lyricfind.com/lyric.do', params={**base_params, **query}).json()

        if res.get('track') and res['track'].get('has_lrc'):
            logging.debug(f'1 {self.name}')
            return res['track']['lrc'], {
                'fetch': res['track']['lfid'],
                'ti': res['track']['title'],
                'ar': res['track']['artist']['name'],
                'length': res['track']['duration'],
                'au': res['track']['writer']
            }
        return None, None
    def fetch(self, lrc_object):
        lyric_text = '\n'.join(
            line['lrc_timestamp'] + line['line'] for line in filter(lambda x:len(x['line'])>0, lrc_object)
        )
        return Lyrics(lyric_text)

MINIMAL_PROVIDERS = [
    SogeciProvider,
    SyairProvider,
    Music163Provider,
    QQProvider,
]
PROVIDERS = MINIMAL_PROVIDERS + [
    RentanaAdvisorProvider,
    MegalobizProvider
]

EXTENDED_PROVIDERS = PROVIDERS + [
    MooflacProvider, # Uses an email/password
    Flac123Provider # Uses an email/password
]

ALL_PROVIDERS = EXTENDED_PROVIDERS + [
    LyricFindProvider, # Requires a valid API Key
    KugouProvider, # Provides little english lyrics
    XiamiProvider # Was taken offline 2/4.
]