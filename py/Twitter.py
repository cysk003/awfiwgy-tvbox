import re
import json
import urllib.parse
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        self.name = 'Truvaze'
        self.host = 'https://truvaze.com'
        self.headers = {'User-Agent': 'Mozilla/5.0', 'Referer': self.host, 'Accept': 'application/json'}

    def getName(self):
        return self.name

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def homeContent(self, filter):
        classes = [{'type_id': 'daily', 'type_name': '每日'}, {'type_id': 'weekly', 'type_name': '每周'}, {'type_id': 'monthly', 'type_name': '每月'}, {'type_id': 'all', 'type_name': '所有时间'}]
        return {'class': classes, 'filters': {k: [{"key": "sort", "name": "排序", "value": [{"n": "按点赞", "v": "favorite"}, {"n": "按观看数", "v": "pv"}]}] for k in ['daily', 'weekly', 'monthly', 'all']}}

    def homeVideoContent(self):
        return self.categoryContent('daily', '1', False, {})

    def categoryContent(self, tid, pg, filter, extend):
        sort_type = extend.get('sort', 'favorite')
        range_val = '' if tid == 'daily' else tid
        url = f"{self.host}/api/media?range={range_val}&page={pg}&per_page=50&category=&ids=&isAnimeOnly=0&sort={sort_type}"
        try:
            res = self.fetch(url, headers=self.headers).json()
            videos = []
            for item in res.get('items', []):
                vid = str(item.get('url_cd', ''))
                if not vid: continue
                account = item.get('tweet_account', '未知')
                pv = item.get('pv', '0')
                fav = item.get('favorite', '0')
                raw_pic = item.get('thumbnail', '')
                pic = f"{self.host}/_next/image?url={urllib.parse.quote(raw_pic)}&w=640&q=75" if raw_pic else ""
                time_sec = item.get('time', 0)
                try:
                    h, m = divmod(int(time_sec) // 60, 60)
                    s = int(time_sec) % 60
                    t_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
                except:
                    t_str = ""
                try:
                    pv_str = f"{int(pv)/10000:.1f}万" if int(pv) > 10000 else str(pv)
                except:
                    pv_str = str(pv)
                
                play_url = item.get('url', '')
                vod_id = f"{vid}@@@{play_url}@@@{pic}"
                
                videos.append({
                    'vod_id': vod_id,
                    'vod_name': f"@{account}",
                    'vod_pic': pic,
                    'vod_remarks': f"{t_str} 👁{pv_str} ❤{fav}".strip()
                })
            return {'list': videos}
        except:
            return {'list': []}

    def detailContent(self, ids):
        parts = ids[0].split("@@@")
        vid = parts[0]
        play_url = parts[1] if len(parts) > 1 else ""
        pic = parts[2] if len(parts) > 2 else ""
        
        if not play_url:
            try:
                html = self.fetch(f"{self.host}/zh-CN/movie/{vid}", headers=self.headers).text
                m = re.search(r'<script type="application/ld\+json">(\{.*?"@type":"VideoObject".*?\})</script>', html)
                if m:
                    data = json.loads(m.group(1))
                    play_url = data.get('contentUrl', '')
                    raw_pic = data.get('thumbnailUrl', '')
                    pic = f"{self.host}/_next/image?url={urllib.parse.quote(raw_pic)}&w=640&q=75" if raw_pic else pic
                else:
                    pu = re.search(r'"url":"(https://video\.twimg\.com/[^"]+\.mp4[^"]*)"', html)
                    pm = re.search(r'"thumbnail":"([^"]+)"', html)
                    play_url = pu.group(1).replace('\\u002F', '/').replace('\\/', '/') if pu else ''
                    raw_pic = pm.group(1).replace('\\u002F', '/').replace('\\/', '/') if pm else ''
                    pic = f"{self.host}/_next/image?url={urllib.parse.quote(raw_pic)}&w=640&q=75" if raw_pic else pic
            except:
                pass
                
        return {'list': [{
            'vod_id': vid,
            'vod_name': f"X(Twitter) - {vid}",
            'vod_pic': pic,
            'type_name': 'Twitter视频',
            'vod_play_from': 'Truvaze',
            'vod_play_url': f"播放${play_url}" if play_url else ""
        }]}

    def searchContent(self, key, quick, pg="1"):
        return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        return {'parse': 0, 'url': id, 'header': {'User-Agent': 'Mozilla/5.0'}}

    def destroy(self):
        pass

    def localProxy(self, param):
        return None
