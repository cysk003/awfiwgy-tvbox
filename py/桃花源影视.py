import json
import re
import sys
import urllib.parse
from pyquery import PyQuery as pq
from base64 import b64decode, b64encode
from requests import Session

sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def init(self, extend=""):
        self.headers['referer'] = f'{self.host}/'
        self.session = Session()
        self.session.headers.update(self.headers)

    def getName(self):
        return "桃花源影视"

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass
#https://a.hxtx.vip
#https://a.hxtx.org
    host = "https://e.thyys.cc"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }

    def homeContent(self, filter):
        result = {}
        classes = [
            {'type_name': '中文无码', 'type_id': '6'},
            {'type_name': '日本无码', 'type_id': '9'},
            {'type_name': '卡通动漫', 'type_id': '12'},
            {'type_name': '中文有码', 'type_id': '7'},
            {'type_name': '日本有码', 'type_id': '8'},
            {'type_name': '国产精品', 'type_id': '10'},
            {'type_name': '糖心Vlog', 'type_id': '13'},
            {'type_name': '欧美性爱', 'type_id': '11'}
        ]
        result['class'] = classes
        return result

    def homeVideoContent(self):
        data = self.getpq('/')
        return {'list': self.getlist(data(".vodlist > li"))}

    def categoryContent(self, tid, pg, filter, extend):
        url = f'/vodshow/{tid}--------{pg}---.html'
        data = self.getpq(url)
        return {'list': self.getlist(data('.vodlist > li')), 'page': pg}

    def detailContent(self, ids):
        vod_id = ids[0]
        url = f'/voddetail/{vod_id}.html'
        data = self.getpq(url)
        
        title = data('.pannel_head h2.title').text() or data('h2.title').text()
        pic = data('.content_thumb .vodlist_detail').attr('data-original') or ''
        
        type_name = ''
        actor = ''
        date = ''
        duration = ''
        
        for li in data('.content_detail ul li.data').items():
            text = li.text()
            if '分类：' in text:
                type_name = text.replace('分类：', '').strip()
            elif '演员：' in text:
                actor = text.replace('演员：', '').strip()
            elif '日期：' in text:
                date = text.replace('日期：', '').strip()
            elif '时长：' in text:
                duration = text.replace('时长：', '').strip()
        
        vod = {
            'vod_id': vod_id,
            'vod_name': title,
            'vod_pic': pic,
            'type_name': type_name,
            'vod_actor': actor,
            'vod_year': date,
            'vod_remarks': duration,
            'vod_play_from': '桃花源影视',
            'vod_play_url': f'播放${vod_id}-1-1'
        }
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        url = f'/vodsearch/{urllib.parse.quote(key)}----------{pg}---.html'
        data = self.getpq(url)
        return {'list': self.getlist(data(".vodlist > li")), 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        url = f'{self.host}/vodplay/{id}.html'
        res = self.session.get(url, headers=self.headers).text
        match = re.search(r'var player_data=(.*?)</script>', res)
        if match:
            try:
                jo = json.loads(match.group(1))
                vurl = jo.get('url', '')
                encrypt = jo.get('encrypt', 0)
                
                if encrypt == 1:
                    vurl = urllib.parse.unquote(vurl)
                elif encrypt == 2:
                    vurl = urllib.parse.unquote(self.d64(vurl))
                    
                return {'parse': 0, 'url': vurl, 'header': self.headers}
            except Exception as e:
                pass
        return {}

    def localProxy(self, param):
        pass

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            return ""

    def d64(self, encoded_text):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            return ""

    def getlist(self, data):
        vlist = []
        for i in data.items():
            a = i('a.vodlist_detail')
            if not a:
                continue
            href = a.attr('href')
            if not href:
                continue
            vid = href.split('/')[-1].split('.')[0]
            vlist.append({
                'vod_id': vid,
                'vod_name': a.attr('title'),
                'vod_pic': a.attr('data-original'),
                'vod_remarks': a('.pic-tag-b').text(),
                'style': {'ratio': 1.33, 'type': 'rect'}
            })
        return vlist

    def getpq(self, path=''):
        url = path if path.startswith('http') else f'{self.host}{path}'
        response = self.session.get(url, headers=self.headers).text
        try:
            return pq(response)
        except Exception as e:
            return pq(response.encode('utf-8'))
