import sys
import re
import urllib.parse
from base.spider import Spider
#https://x98.one
class Spider(Spider):
    def __init__(self):
        self.name = 'Jable'
        self.host = 'https://jable.cfd'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Referer': self.host
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
        url = f"{self.host}/categories/"
        res = self.fetch(url, headers=self.headers)
        
        pattern = r'<div class="img-box">\s*<a href="[^"]+/categories/([^/]+)/">.*?<h4>([^<]+)</h4>'
        matches = re.findall(pattern, res.text, re.DOTALL)
        
        classes = []
        if matches:
            for m in matches:
                classes.append({
                    'type_id': m[0],
                    'type_name': m[1]
                })
        else:
            classes = [
                {"type_id": "chinese-subtitle", "type_name": "中文字幕"},
                {"type_id": "bdsm", "type_name": "主奴调教"},
                {"type_id": "sex-only", "type_name": "直接开啪"},
                {"type_id": "insult", "type_name": "凌辱快感"},
                {"type_id": "uniform", "type_name": "制服诱惑"},
                {"type_id": "roleplay", "type_name": "角色剧情"},
                {"type_id": "private-cam", "type_name": "盗摄偷拍"},
                {"type_id": "uncensored", "type_name": "无码解放"},
                {"type_id": "pov", "type_name": "男友视角"},
                {"type_id": "groupsex", "type_name": "多P群交"},
                {"type_id": "pantyhose", "type_name": "丝袜美腿"},
                {"type_id": "lesbian", "type_name": "女同欢愉"}
            ]

        return {'class': classes}

    def homeVideoContent(self):
        return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        pg = str(pg)
        if pg == '1':
            url = f"{self.host}/categories/{tid}/"
        else:
            url = f"{self.host}/categories/{tid}/{pg}/"
            
        res = self.fetch(url, headers=self.headers)
        
        pattern = r'<div class="video-img-box mb-e-20">.*?<a href="[^"]+/videos/([^/]+)/">.*?data-src="([^"]+)".*?<span class="label">([^<]+)</span>.*?<h6 class="title"><a[^>]*>([^<]+)</a></h6>'
        matches = re.findall(pattern, res.text, re.DOTALL)
        
        videos = []
        for m in matches:
            videos.append({
                'vod_id': m[0],
                'vod_pic': m[1],
                'vod_remarks': m[2],
                'vod_name': m[3].strip()
            })
            
        return {'list': videos}

    def detailContent(self, ids):
        vod_id = ids[0]
        url = f"{self.host}/videos/{vod_id}/"
        res = self.fetch(url, headers=self.headers)
        text = res.text

        title_match = re.search(r'<meta property="og:title" content="([^"]+)">', text)
        pic_match = re.search(r'<meta property="og:image" content="([^"]+)">', text)
        desc_match = re.search(r'<meta property="og:description" content="([^"]+)">', text)
        keywords_match = re.search(r'<meta name="keywords" content="([^"]+)">', text)
        
        hls_match = re.search(r"var hlsUrl\s*=\s*'([^']+)'", text)

        vod = {
            'vod_id': vod_id,
            'vod_name': title_match.group(1) if title_match else vod_id,
            'vod_pic': pic_match.group(1) if pic_match else '',
            'vod_content': desc_match.group(1) if desc_match else '',
            'vod_remarks': '1080p',
            'type_name': keywords_match.group(1) if keywords_match else '',
        }

        if hls_match:
            vod['vod_play_from'] = 'Jable播放'
            vod['vod_play_url'] = f"正片${hls_match.group(1)}"
        else:
            vod['vod_play_from'] = 'Jable播放'
            vod['vod_play_url'] = "未解析到源$"

        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        pg = str(pg)
        if pg == '1':
            url = f"{self.host}/search/{urllib.parse.quote(key)}/"
        else:
            url = f"{self.host}/search/{urllib.parse.quote(key)}/{pg}/"
            
        res = self.fetch(url, headers=self.headers)
        
        pattern = r'<div class="video-img-box mb-e-20">.*?<a href="[^"]+/videos/([^/]+)/">.*?data-src="([^"]+)".*?<span class="label">([^<]+)</span>.*?<h6 class="title"><a[^>]*>([^<]+)</a></h6>'
        matches = re.findall(pattern, res.text, re.DOTALL)
        
        videos = []
        for m in matches:
            videos.append({
                'vod_id': m[0],
                'vod_pic': m[1],
                'vod_remarks': m[2],
                'vod_name': m[3].strip()
            })
            
        return {'list': videos}

    def playerContent(self, flag, id, vipFlags):
        return {
            'parse': 0,
            'url': id, 
            'header': self.headers
        }

    def destroy(self):
        pass

    def localProxy(self, param):
        return None
