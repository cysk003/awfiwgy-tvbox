import sys
import re
import json
import urllib.parse
import requests
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        self.name = 'HStream'
        self.host = 'https://hstream.moe'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host
        }
        self.list_pattern = re.compile(r'<a[^>]+href="https://hstream\.moe/hentai/([^"]+)"[^>]*>([\s\S]*?)</a\s*>')

    def getName(self):
        return self.name

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def _parse_video_list(self, html):
        matches = self.list_pattern.findall(html)
        videos = []
        seen_ids = set()
        
        for match in matches:
            vod_id = match[0]
            if vod_id in seen_ids:
                continue
            seen_ids.add(vod_id)
            
            html_content = match[1]
            
            pic_match = re.search(r'<img[^>]+src="([^"]+)"', html_content)
            vod_pic = pic_match.group(1) if pic_match else ''
            if vod_pic:
                vod_pic = vod_pic if vod_pic.startswith('http') else self.host + vod_pic
                vod_pic = re.sub(r'cover-ep-(\d+)\.webp', r'gallery-ep-\1-0-thumbnail.webp', vod_pic)
            
            name_match = re.search(r'<p class="text-sm[^>]*>([\s\S]*?)</p>', html_content)
            vod_name = name_match.group(1).strip() if name_match else vod_id
            vod_name = re.sub(r'<[^>]+>', '', vod_name).strip()
            
            remarks_match = re.search(r'<p[^>]+bg-rose-700[^>]*>([\s\S]*?)</p>', html_content)
            vod_remarks = remarks_match.group(1).strip() if remarks_match else 'HD'
            vod_remarks = re.sub(r'<[^>]+>', '', vod_remarks).strip()
            
            videos.append({
                'vod_id': vod_id,
                'vod_name': vod_name,
                'vod_pic': vod_pic,
                'vod_remarks': vod_remarks
            })
            
        return videos

    def homeContent(self, filter):
        classes = [
            {'type_id': 'uncensored', 'type_name': '无码'},
            {'type_id': 'milf', 'type_name': '人妻'},
            {'type_id': 'maid', 'type_name': '女仆'},
            {'type_id': 'school-girl', 'type_name': '学生'},
            {'type_id': 'succubus', 'type_name': '魅魔'},
            {'type_id': 'tentacle', 'type_name': '触手'},
            {'type_id': 'big-boobs', 'type_name': '巨乳'},
            {'type_id': 'bdsm', 'type_name': '调教'},
            {'type_id': 'elf', 'type_name': '精灵'},
            {'type_id': '4k-48fps', 'type_name': '4K专区'}
        ]
        return {'class': classes}

    def homeVideoContent(self):
        res = self.fetch(self.host, headers=self.headers)
        videos = self._parse_video_list(res.text)
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        url = f"{self.host}/search?order=recently-uploaded&tags%5B0%5D={tid}&page={pg}"
        res = self.fetch(url, headers=self.headers)
        videos = self._parse_video_list(res.text)
        return {'list': videos}

    def detailContent(self, ids):
        vod_id = ids[0]
        url = f"{self.host}/hentai/{vod_id}"
        res = self.fetch(url, headers=self.headers)
        html = res.text

        title_match = re.search(r'<h1[^>]*>([\s\S]*?)</h1>', html)
        if title_match:
            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
            title = re.sub(r'\s+', ' ', title)
        else:
            title = vod_id

        pic_match = re.search(r'[\s\S]*?<img[^>]+src="([^"]+)"', html)
        pic = (pic_match.group(1) if pic_match.group(1).startswith('http') else self.host + pic_match.group(1)) if pic_match else ''
        pic = re.sub(r'cover-ep-(\d+)\.webp', r'gallery-ep-\1-0-thumbnail.webp', pic)

        desc_match = re.search(r'Description\s*</p>\s*<p[^>]*>([\s\S]*?)</p>', html)
        desc = desc_match.group(1).strip() if desc_match else ''

        tags_pattern = re.compile(r'tags%5B0%5D=[^"]+"[^>]*>\s*([^<]+)\s*</a>')
        tags_matches = tags_pattern.findall(html)
        type_name = ', '.join([tag.strip() for tag in tags_matches])

        vod = {
            'vod_id': vod_id,
            'vod_name': title,
            'vod_pic': pic,
            'vod_content': desc,
            'vod_remarks': '原画 4K', 
            'type_name': type_name,
            'vod_play_from': '4K全球节点1$$$4K全球节点2$$$4K亚洲节点1$$$4K亚洲节点2',
            'vod_play_url': f"正片播放${url}|global_0$$$正片播放${url}|global_1$$$正片播放${url}|asia_0$$$正片播放${url}|asia_1"
        }

        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.host}/search?s={urllib.parse.quote(key)}&page={pg}"
        res = self.fetch(url, headers=self.headers)
        videos = self._parse_video_list(res.text)
        return {'list': videos}

    def playerContent(self, flag, id, vipFlags):
        target_url = id
        cdn_type = 'asia'
        node_idx = 0
        
        if '|' in id:
            parts = id.split('|')
            target_url = parts[0]
            if '_' in parts[1]:
                cdn_type, idx_str = parts[1].split('_')
                node_idx = int(idx_str)
            else:
                cdn_type = parts[1]

        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': self.headers['User-Agent'],
                'Accept-Encoding': 'gzip, deflate'
            })
            
            res = session.get(target_url, timeout=5)
            html = res.text
            
            e_id_match = re.search(r'id="e_id"[^>]*value="(\d+)"', html)
            if not e_id_match:
                return {}
            
            e_id = int(e_id_match.group(1))
            
            xsrf_token = session.cookies.get('XSRF-TOKEN', '')
            if xsrf_token:
                xsrf_token = urllib.parse.unquote(xsrf_token)
                
            api_headers = {
                'User-Agent': self.headers['User-Agent'],
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': target_url
            }
            
            if xsrf_token:
                api_headers['X-XSRF-TOKEN'] = xsrf_token
            else:
                csrf_match = re.search(r'data-csrf="([^"]+)"', html)
                if csrf_match:
                    api_headers['X-CSRF-TOKEN'] = csrf_match.group(1)
            
            payload = {"episode_id": e_id}
            api_res = session.post('https://hstream.moe/player/api', headers=api_headers, json=payload, timeout=5)
            
            if api_res.status_code == 200:
                data = api_res.json()
                stream_url = data.get('stream_url', '')
                
                if cdn_type == 'asia':
                    domains = data.get('asia_stream_domains', [])
                    if not domains:
                        domains = data.get('stream_domains', [])
                else:
                    domains = data.get('stream_domains', [])
                    if not domains:
                        domains = data.get('asia_stream_domains', [])
                
                domain = domains[node_idx % len(domains)] if domains else "https://shinobu-str.rorikon-h.xyz"
                
                domain = domain.rstrip('/')
                stream_url = stream_url.strip('/')
                
                mpd_url = f"{domain}/{stream_url}/2160/manifest.mpd"
                
                play_headers = {
                    'User-Agent': self.headers['User-Agent'],
                    'Referer': 'https://hstream.moe/',
                    'Origin': 'https://hstream.moe',
                    'Connection': 'keep-alive'
                }
                
                return {
                    'parse': 0, 
                    'playUrl': '',
                    'url': mpd_url,
                    'header': play_headers 
                }
        except Exception as e:
            pass
            
        return {}

    def destroy(self):
        pass

    def localProxy(self, param):
        return None
