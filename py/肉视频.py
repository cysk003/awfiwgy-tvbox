import sys
import requests
import re
import json
import base64
from lxml import etree
sys.path.append('..')
from base.spider import Spider
#https://x98.icu
class Spider(Spider):
    def getName(self): return "RouVideo"
    
    def init(self, extend):
        self.home_url = 'https://rou1.sbs'
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", 
            "Referer": self.home_url
        }

    def get_list(self, html):
        try:
            root = etree.HTML(html)
            cards = root.xpath('//div[contains(@class, "aspect-video")]/..') or root.xpath('//div[@data-slot="card"]')
            videos = []
            for c in cards:
                try:
                    link = c.xpath('.//a[contains(@href, "/v/")]/@href')[0]
                    img = c.xpath('.//img[contains(@class, "object-contain")]/@src') or c.xpath('.//img/@src')
                    name = c.xpath('.//h3/text()') or c.xpath('.//img/@alt')
                    qual = c.xpath('.//span[contains(@class, "bg-yellow-500")]/text()')
                    dur = c.xpath('.//span[contains(@class, "bg-black")]/text()')
                    videos.append({
                        'vod_id': link, 
                        'vod_name': name[0], 
                        'vod_pic': img[0], 
                        'vod_remarks': f"{qual[0] if qual else ''} {dur[0] if dur else ''}".strip(), 
                        'style': {"type": "rect", "ratio": 1.5}
                    })
                except: continue
            return videos
        except: return []

    def homeContent(self, filter):
        return {'class': [
            {'type_name': '国产AV', 'type_id': '/t/國產AV'}, 
            {'type_name': '自拍流出', 'type_id': '/t/自拍流出'}, 
            {'type_name': '探花', 'type_id': '/t/探花'}, 
            {'type_name': 'OnlyFans', 'type_id': '/t/OnlyFans'}, 
            {'type_name': '日本', 'type_id': '/t/日本'}
        ]}

    def homeVideoContent(self):
        try:
            r = requests.get(f"{self.home_url}/home", headers=self.header)
            return {'list': self.get_list(r.text), 'parse': 0, 'jx': 0}
        except: return {'list': [], 'parse': 0, 'jx': 0}

    def categoryContent(self, cid, page, filter, ext):
        try:
            url = f"{self.home_url}{cid}{'&' if '?' in cid else '?'}order=createdAt&page={page}"
            return {'list': self.get_list(requests.get(url, headers=self.header).text), 'parse': 0, 'jx': 0}
        except: return {'list': [], 'parse': 0, 'jx': 0}

    def detailContent(self, did):
        try:
            ids = did[0] if isinstance(did, list) else did
            url = f"{self.home_url}{ids}"
            html = requests.get(url, headers=self.header).text
            
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
            if not match:
                return {'list': []}
                
            data = json.loads(match.group(1))
            page_props = data.get('props', {}).get('pageProps', {})
            video_info = page_props.get('video', {})
            ev = page_props.get('ev', {})
            
            video_url = ""
            
            if ev and 'd' in ev and 'k' in ev:
                try:
                    d = ev['d']
                    k = ev['k']
                    decoded_bytes = base64.b64decode(d)
                    decrypted_str = "".join([chr((b - k) % 256) for b in decoded_bytes])
                    video_url = json.loads(decrypted_str).get('videoUrl', '')
                except Exception as e:
                    pass
            elif 'videoUrl' in video_info:
                video_url = video_info['videoUrl']

            return {
                "list": [{
                    'vod_id': ids, 
                    'vod_name': video_info.get('name', ''), 
                    'vod_pic': video_info.get('coverImageUrl', ''),
                    'vod_play_from': '肉视频', 
                    'vod_play_url': f"播放${video_url}", 
                    'vod_content': f"Tags: {', '.join(video_info.get('tags', []))}"
                }], 
                'parse': 0, 
                'jx': 0
            }
        except Exception as e: 
            return {'list': []}

    def searchContent(self, key, quick, page='1'):
        try:
            url = f"{self.home_url}/search?q={key}&page={page}"
            return {'list': self.get_list(requests.get(url, headers=self.header).text), 'parse': 0, 'jx': 0}
        except: return {'list': [], 'parse': 0, 'jx': 0}

    def playerContent(self, flag, pid, vipFlags): return {'url': pid, "header": self.header, 'parse': 0, 'jx': 0}
    def isVideoFormat(self, url): pass
    def manualVideoCheck(self): pass
    def getDependence(self): return []
    def localProxy(self, params): pass
    def destroy(self): return 'Destroy'
