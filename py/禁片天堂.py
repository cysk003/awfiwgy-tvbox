import sys
import re
from base.spider import Spider
#https://ttvvcc.work
class Spider(Spider):
    def __init__(self):
        self.name = '禁片天堂'
        self.host = 'https://jptt.tv'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host
        }

    def getName(self): return self.name
    def init(self, extend=""): pass
    def isVideoFormat(self, url): return url.endswith('.m3u8') or url.endswith('.mp4')
    def manualVideoCheck(self): return False

    def homeContent(self, filter):
        categories = [
            {'type_id': '2', 'type_name': '最新发行'},
            {'type_id': '3', 'type_name': '今日热门'},
            {'type_id': '4', 'type_name': '本周热门'},
            {'type_id': '5', 'type_name': '本月热门'},
            {'type_id': '6', 'type_name': '总浏览数'}
        ]
        return {'class': categories}

    def homeVideoContent(self): return self.categoryContent('3', '1', False, {})

    def parse_list(self, html):
        videos = []
        blocks = re.findall(r'<div class="col oneVideo">.*?<div class="oneVideo-body">.*?</div>\s*</div>\s*</div>', html, re.S)
        for block in blocks:
            link = re.search(r'href=".*?/video/([^"]+)"', block)
            img = re.search(r'src="([^"]+)"', block)
            title = re.search(r'<(?:h3|h5)>(.*?)</(?:h3|h5)>', block, re.S)
            dur = re.search(r'class="p_duration">([^<]+)<', block)
            if link and img and title:
                pic = img.group(1)
                videos.append({
                    'vod_id': link.group(1),
                    'vod_name': title.group(1).strip(),
                    'vod_pic': pic if pic.startswith('http') else self.host + pic,
                    'vod_remarks': dur.group(1).strip() if dur else ''
                })
        return videos

    def categoryContent(self, tid, pg, filter, extend):
        try:
            res = self.fetch(f'{self.host}/cn/list?idx={pg}&sort={tid}', headers=self.headers)
            return {'list': self.parse_list(res.text), 'page': pg, 'pagecount': 999, 'limit': 20, 'total': 999}
        except: return {'list': []}

    def detailContent(self, ids):
        try:
            vid = ids[0]
            res = self.fetch(f'{self.host}/cn/video/{vid}', headers=self.headers)
            html = res.text
            title = re.search(r'<h1 class="h1_title">(.*?)</h1>', html, re.S)
            pic = re.search(r'poster="([^"]+)"', html)
            desc = re.search(r'<div class="info_original.*?<p>(.*?)</p>', html, re.S)
            src = re.search(r'<source src="([^"]+)"', html)
            play_url = src.group(1) if src else f'{self.host}/video/{vid}.m3u8'
            if play_url.startswith('//'): play_url = 'https:' + play_url
            vod_pic = pic.group(1) if pic else ''
            return {'list': [{
                'vod_id': vid,
                'vod_name': title.group(1).strip() if title else vid,
                'vod_pic': vod_pic if vod_pic.startswith('http') else self.host + vod_pic,
                'vod_content': desc.group(1).strip() if desc else '',
                'vod_play_from': '禁片天堂',
                'vod_play_url': f'立即播放${play_url}'
            }]}
        except: return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        try:
            res = self.fetch(f'{self.host}/cn/search?kw={key}&idx={pg}', headers=self.headers)
            return {'list': self.parse_list(res.text)}
        except: return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        url = id if 'http' in id else f'{self.host}/video/{id}.m3u8'
        return {'parse': 0, 'url': url, 'header': self.headers}

    def destroy(self): pass
