import sys
import re
import urllib.parse
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        self.name = '甜圈短剧'
        self.host = 'https://mov.cenguigui.cn'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def getName(self):
        return self.name

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def homeContent(self, filter):
        res = self.fetch(self.host)
        cats = re.findall(r"selectCategory\('([^']+)'\)", res.text)
        classes = [{'type_id': c, 'type_name': c} for c in cats]
        return {'class': classes}

    def homeVideoContent(self):
        return self.categoryContent('推荐榜', '1', False, {})

    def categoryContent(self, tid, pg, filter, extend):
        offset = '0' if str(pg) == '1' else str(pg)
        url = f"{self.host}/duanju/api.php?classname={urllib.parse.quote(tid)}&offset={offset}"
        res = self.fetch(url).json()
        data = res.get('data', [])
        videos = []
        for item in data:
            play_cnt = item.get('play_cnt', 0)
            if isinstance(play_cnt, (int, float)):
                play_cnt = f"{play_cnt/10000:.2f}万"
            videos.append({
                'vod_id': str(item.get('book_id', '')),
                'vod_name': item.get('title', ''),
                'vod_pic': item.get('cover', ''),
                'vod_remarks': str(play_cnt)
            })
        return {'list': videos}

    def detailContent(self, ids):
        bid = ids[0]
        url = f"{self.host}/duanju/api.php?book_id={bid}"
        res = self.fetch(url).json()
        vod = {
            'vod_id': bid,
            'vod_name': res.get('book_name', ''),
            'vod_pic': res.get('book_pic', ''),
            'vod_content': res.get('desc', ''),
            'vod_remarks': f"共{res.get('total', 0)}集",
            'type_name': ','.join(res.get('category_names', [])),
        }
        episodes = res.get('data', [])
        resolutions = [
            ('自动', 'auto'),
            ('2160p', '2160p'),
            ('1080p', '1080p'),
            ('720p', '720p'),
            ('540p', '540p'),
            ('480p', '480p'),
            ('360p', '360p')
        ]
        play_froms = []
        play_urls = []
        for res_name, res_code in resolutions:
            play_froms.append(res_name)
            ep_list = []
            for ep in episodes:
                title = ep.get('title', '未知')
                vid = ep.get('video_id', '')
                ep_list.append(f"{title}${vid}|{res_code}")
            play_urls.append('#'.join(ep_list))
        vod['vod_play_from'] = '$$$'.join(play_froms)
        vod['vod_play_url'] = '$$$'.join(play_urls)
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.host}/duanju/api.php?name={urllib.parse.quote(key)}&page={pg}&tab_type=11&showRawParams=false"
        res = self.fetch(url).json()
        data = res.get('data', [])
        videos = []
        for item in data:
            videos.append({
                'vod_id': str(item.get('book_id', '')),
                'vod_name': item.get('title', ''),
                'vod_pic': item.get('cover', ''),
                'vod_remarks': item.get('type', ''),
                'vod_content': item.get('intro', '')
            })
        return {'list': videos}

    def playerContent(self, flag, id, vipFlags):
        parts = id.split('|')
        vid = parts[0]
        level = parts[1] if len(parts) > 1 else 'auto'
        if level == 'auto':
            url = f"{self.host}/duanju/api.php?video_id={vid}&type=mp4"
        else:
            url = f"{self.host}/duanju/api.php?video_id={vid}&type=mp4&level={level}"
        return {'parse': 0, 'url': url, 'header': self.headers}

    def destroy(self):
        pass

    def localProxy(self, param):
        return None
