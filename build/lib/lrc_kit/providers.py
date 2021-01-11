import requests
import re
import html
from bs4 import BeautifulSoup
import unicodedata
import base64
import zlib
import json
from abc import abstractmethod
from lrc_kit.lrc import LRC
# https://github.com/ddddxxx/LyricsKit/tree/master/Sources/LyricsService/Provider
# https://github.com/blueset/project-lyricova/tree/master/packages/lyrics-kit
class LyricsProvider:
    service = ''
    UA = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Safari/537.36'}

    @abstractmethod
    def search(self, search_request):
        pass
    @abstractmethod
    def fetch(self, input):
        pass
    def search_and_fetch(self, search_request):
        val = self.search(search_request)
        if val:
            return self.fetch(val)
        return val

class SearchRequest:
    def __init__(self, artist, song, duration=None):
        self.artist = artist
        self.song = song
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

class ComboLyricProvider(LyricsProvider):
    def __init__(self, text_providers=None):
        if text_providers == None:
            self.providers = PROVIDERS
        else:
            self.providers = [provider for provider in PROVIDERS if provider.name in text_providers]
    def search(self, search_request):
        for provider in self.providers:
            res = provider().search_and_fetch(search_request)
            if res:
                return LRC(res), provider.name
        return None, None
class KugouProvider(LyricsProvider):
    name = "Kugou"
    def search(self, search_request):
        params = {
            'keyword': search_request.as_string,
            'client': 'pc',
            'ver': 1,
            'man': 1
        }
        if search_request.duration:
            params['duration'] = search_request.duration
        data = requests.get('http://lyrics.kugou.com/search', params=params).json()

        if data['candidates']:
            c = data['candidates'][0]
            return (c['id'], c['accesskey'], c['song'], c['singer'])
        return None
    def fetch(self, token):
        token_id, token_key, _, _ = token
        params = {
            "id": token_id,
            "accesskey": token_key,
            "fmt": "krc",
            "charset": "utf8",
            "client": "pc",
            "ver": 1,
        }
        data = requests.get('http://lyrics.kugou.com/download', params=params).json()['content']
        return self.decode_krc(base64.b64decode(data))
    def decode_krc(self, krc):
        byte_krc = bytearray(krc)
        if byte_krc[:4] != b'krc1':
            return None
        byte_krc = byte_krc[4:]
        decode_bytes = [64, 71, 97, 119, 94, 50, 116, 71, 81, 54, 49, 45, 206, 210, 110, 105]
        for i in range(len(byte_krc)):
            byte_krc[i] ^= decode_bytes[i & 0b1111]
        
        final = zlib.decompress(byte_krc)
        return final.decode('utf-8')
class GecimiLyricProvider(LyricsProvider):
    name = 'Gecimi'
    def search(self, search_request):
        # http://gecimi.com/api/lyric/%E6%B5%B7%E9%98%94%E5%A4%A9%E7%A9%BA/Beyond
        # Getting error: dial tcp 127.0.0.1:3306: connect: connection refused
        raise NotImplementedError()
        requests.get('http://gecimi.com/api/lyric/{song}/artist')
    def fetch(self, input):
        raise NotImplementedError()
class Music163Provider(LyricsProvider):
    name = 'Music163'
    def search(self, search_request):
        search_url = 'http://music.163.com/api/search/pc'
        search_params = {
            'limit': 10,
            'type': 1,
            'offset': 0,
            's': search_request.as_string
        }
        resp = requests.get(search_url, params=search_params).json()['result']['songs']
        if len(resp) > 0:
            for song in resp:
                if song['name'].lower() == search_request.song and song['artists'][0]['name'].lower() == search_request.artist:
                    return song['id']
        return None
    def fetch(self, song_id):
        lyric_url = 'http://music.163.com/api/song/lyric?id=1300287&lv=1&kv=1&tv=-1'
        lyric_params = {
            'id': song_id,
            'lv': 1,
            'kv': 1,
            'tv': -1
        }
        l_resp = requests.get(lyric_url, params=lyric_params).json()
        return l_resp['lrc']['lyric']
class SogeciProvider(LyricsProvider):
    name = 'Sogeci'
    def search(self, search_request):
        artist_fixed = re.sub(r'\W+', '', search_request.artist)
        artist_page = f'http://www.sogeci.net/geshou/{artist_fixed}.html'
        page = requests.get(artist_page)
        if page.status_code == 404:
            return None
        soup = BeautifulSoup(page.text, 'lxml')
        links = soup.find('div', class_='showNewSong')
        links = links.find_all('a')
        for link in links:
            if link['title'].lower() in search_request.song.lower():
                return 'http://www.sogeci.net' + link['href']
                
        return None
    def fetch(self, lyric_url):
        lyric_regex = re.compile('<pre>([\s\S]*?)</pre>')
        lyric_page = requests.get(lyric_url).text
        lyrics = re.search(lyric_regex, lyric_page).group(1)
        return lyrics.strip()
class SyairProvider(LyricsProvider):
    name = 'Syair'
    def search(self, search_request):
        search_page = requests.get("https://www.syair.info/search", params={
        "q": f'{search_request.artist_normalized} {search_request.song}'
        }, headers = self.UA).text
        soup = BeautifulSoup(search_page, 'lxml')
        result_container = soup.find("div", class_="sub")
        if result_container:
            result_list = result_container.find_all("div", class_="li")

            if result_list:
                for i, li in enumerate(result_list):
                    result = li.find('a')
                    name = result.text.lower()
                    if (search_request.artist.lower() in name or search_request.artist_normalized.lower() in name) and search_request.song.lower() in name:
                        url = "https://www.syair.info"
                        if '[offset:' in li.text:
                            # check next one just in case
                            next_link = result_list[i+1].find('a')
                            if next_link.text.lower() == name:
                                url += next_link['href']
                            else:
                                url += result['href']
                        else:
                            url += result['href']
                        return url
        return None
    def fetch(self, lyric_url):
        lyrics_page = requests.get(lyric_url, headers = self.UA)
        soup = BeautifulSoup(lyrics_page.text, 'lxml')
        lrc_link = None
        for download_link in soup.find_all("a", attrs={"rel": "nofollow"}):
            if "download.php" in download_link["href"]:
                lrc_link = "https://www.syair.info" + download_link["href"]
                return requests.get(lrc_link,
                                    cookies=lyrics_page.cookies, headers = self.UA).text
        return None
class MooflacProvider(LyricsProvider):
    name = 'mooflac'
    @staticmethod
    def get_cookie_jar():
        login_url = 'https://www.mooflac.com/login'
        res = requests.get(login_url)
        token_re = re.compile(r'name="_token" value="(.*)"')
        token = re.search(token_re, res.text).group(1)

        body = {
            'email': 'peter.promotions.stenger@gmail.com',
            'password': 'retep123',
            '_token': token
        }
        return requests.post(login_url, body, cookies=res.cookies).cookies
    def __init__(self):
        super().__init__()
        self.cookies = self.get_cookie_jar()
    def fetch(self, url):
        lyrics_page = requests.get(url, cookies=self.cookies).text
        has_lyrics = 'lyric-context' in lyrics_page
        if not has_lyrics:
            return None
        lyrics_re = re.compile(r'<div class="hidden" id="lyric-context">([\s\S]*?)</div>')
        lyrics = re.search(lyrics_re, lyrics_page)
        lyrics = '\n'.join([html.unescape(line.split('<br>')[0]) for line in lyrics.group(1).split('\n')])
        if '[' not in lyrics and ']' not in lyrics:
            return None
        return lyrics
    def search(self, search_request):

        search_page = requests.get('https://www.mooflac.com/search', params={
            'q': search_request.song + ' ' + search_request.artist_normalized 
        }, cookies=self.cookies).text
        soup = BeautifulSoup(search_page, 'lxml')
        result_table = soup.find('tbody')
        if result_table:
            for result in result_table.find_all('tr')[:10]:
                links = result.find_all('td')
                href = links[0].find('a')['href']
                text = [unicodedata.normalize("NFKD", l.text.strip()) for l in links]
                res_song = text[0].lower()
                res_artist = text[1].lower()
                if search_request.song.lower() == res_song and (search_request.artist_normalized.lower() == res_artist or search_request.artist.lower() == res_artist):
                    return href
        return None

class RentanaAdvisorProvider(LyricsProvider):
    name = "RentAnAdviser"
    def search(self, search_request):

        search_results = requests.get("https://www.rentanadviser.com/en/subtitles/subtitles4songs.aspx", 
            params={'src': search_request.as_string})
        soup = BeautifulSoup(search_results.text, 'html.parser')
        result_links = soup.find(id="tablecontainer").find_all("a")

        for result_link in result_links:
            if result_link["href"] != "subtitles4songs.aspx":
                lower_title = result_link.get_text().lower()
                if search_request.artist.lower() in lower_title and search_request.song.lower() in lower_title:
                    url = "https://www.rentanadviser.com/en/subtitles/%s&type=lrc" % result_link["href"]
                    return url
        return None
    def fetch(self, lyric_url):
        possible_text = requests.get(lyric_url)
        soup = BeautifulSoup(possible_text.text, 'html.parser')

        event_validation = soup.find(id="__EVENTVALIDATION")["value"]
        view_state = soup.find(id="__VIEWSTATE")["value"]

        lrc = requests.post(lyric_url, {"__EVENTTARGET": "ctl00$ContentPlaceHolder1$btnlyrics",
                                    "__EVENTVALIDATION": event_validation,
                                    "__VIEWSTATE": view_state}).text

        return lrc

class MegalobizProvider(LyricsProvider):
    name = "Megalobiz"
    def search(self, search_request):
        search_results = requests.get("https://www.megalobiz.com/search/all", params={
        "qry": search_request.as_string,
        "display": "more"
        })
        soup = BeautifulSoup(search_results.text, 'html.parser')
        result_links = soup.find(id="list_entity_container").find_all("a", class_="entity_name")

        for result_link in result_links:
            lower_title = result_link.get_text().lower()
            if search_request.artist.lower() in lower_title and search_request.song.lower() in lower_title:
                url = "https://www.megalobiz.com%s" % result_link["href"]
                return url
        return None

    def fetch(self, url):
        possible_text = requests.get(url)
        soup = BeautifulSoup(possible_text.text, 'html.parser')

        lrc = soup.find("div", class_="lyrics_details").span.get_text()
        return lrc

class LyricFindProvider(LyricsProvider):
    name = "LyricFind"
    # https://github.com/alan96320/camocist-radio/blob/7adcc4f0482b395d97ce296745fb475be7f98052/app/Http/Controllers/Frontend/ApiController.php#L141
    # TODO retain lost metadata
    def search(self, search_request):
        base_params = {
            'apikey': 'ac0974dcf282f1c67c64342159e42c05',
            'reqtype': 'default',
            'output': 'json',
            'territory': 'US',
            'format': 'lrc',
            'lrckey': 'd829393a83c0c0434cef9d451310be4b'
        }
        query = {
            'trackid': f'artistname:{search_request.artist},trackname:{search_request.song}'
        }
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        res = requests.get('https://api.lyricfind.com/lyric.do', {**base_params, **query}).json()

        if res.get('track') and res['track'].get('has_lrc'):
            return res['track']['lrc']
        return None
    def fetch(self, lrc_object):
        return '\n'.join(
            line['lrc_timestamp'] + line['line'] for line in filter(lambda x:len(x['line'])>0, lrc_object)
        )
PROVIDERS = [SogeciProvider, LyricFindProvider, Music163Provider, RentanaAdvisorProvider, MegalobizProvider, MooflacProvider, SyairProvider]
