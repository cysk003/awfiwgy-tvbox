from urllib.parse import unquote, quote
from bs4 import BeautifulSoup
from base.spider import Spider
import urllib3
import base64
import re
import requests
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#https://kanav.ad
#https://m1.kanav.fun
xurl = "https://v1.kanav.ink"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': xurl,
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0',
}

class Spider(Spider):

    def getName(self):
        return "KanAV"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def get_page_with_dynamic_cookie(self, target_url):
        local_headers = headers.copy()
        session = requests.Session()
        session.headers.update(local_headers)
        session.verify = False
        try:
            resp = session.get(target_url, timeout=10)
            if resp.status_code in [404, 503, 403]:
                if session.cookies:
                    resp = session.get(target_url, timeout=10)
                    if resp.status_code == 200:
                        return resp.text
            elif resp.status_code == 200:
                return resp.text
        except Exception:
            pass
        return None

    def homeContent(self, filter):
        result = {}
        classes = [
            {"type_id": "1", "type_name": "中文字幕"},
            {"type_id": "2", "type_name": "日韩有码"},
            {"type_id": "3", "type_name": "日韩无码"},
            {"type_id": "4", "type_name": "国产AV"},
            {"type_id": "30", "type_name": "自拍泄密"},
            {"type_id": "31", "type_name": "探花约炮"},
            {"type_id": "32", "type_name": "主播录制"},
            {"type_id": "25", "type_name": "里番"},
            {"type_id": "26", "type_name": "泡面番"},
            {"type_id": "27", "type_name": "Motion Anime"},
            {"type_id": "28", "type_name": "3D动画"},
            {"type_id": "29", "type_name": "同人作品"}
        ]
        result['class'] = classes
        return result

    def homeVideoContent(self):
        target_url = f'{xurl}/'
        html_content = self.get_page_with_dynamic_cookie(target_url)
        if not html_content:
            return {'list': []}
            
        doc = BeautifulSoup(html_content, "lxml")
        videos = []
        for item in doc.find_all('div', class_='video-item'):
            img_div = item.find('div', class_='featured-content-image') or item.find('div', class_='video-image')
            if not img_div:
                continue
                
            a_tag = img_div.find('a')
            if not a_tag:
                continue
                
            href = a_tag.get('href', '')
            img_tag = a_tag.find('img')
            if not img_tag:
                continue
                
            name = img_tag.get('alt', '')
            pic = img_tag.get('data-original', '') or img_tag.get('src', '')
            
            remark_tag = img_div.find('span', class_='model-view')
            remark = remark_tag.text.strip() if remark_tag else ''
            
            videos.append({
                "vod_id": href,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
            })
            
        return {'list': videos}

    def categoryContent(self, cid, pg, filter, ext):
        page = int(pg) if pg else 1
        target_url = f'{xurl}/index.php/vod/type/id/{cid}/page/{page}.html'
        html_content = self.get_page_with_dynamic_cookie(target_url)
        
        if not html_content:
            return {'list': [], 'page': page, 'pagecount': 9999, 'limit': 90, 'total': 999999}
            
        doc = BeautifulSoup(html_content, "lxml")
        videos = []
        for item in doc.find_all('div', class_='video-item'):
            img_div = item.find('div', class_='featured-content-image') or item.find('div', class_='video-image')
            if not img_div:
                continue
            a_tag = img_div.find('a')
            href = a_tag['href']
            img_tag = a_tag.find('img')
            name = img_tag.get('alt', '')
            pic = img_tag.get('data-original', '') or img_tag.get('src', '')
            
            remark_tag = img_div.find('span', class_='model-view')
            remark = remark_tag.text.strip() if remark_tag else ''
            
            videos.append({
                "vod_id": href,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
            })
            
        return {'list': videos, 'page': page, 'pagecount': 9999, 'limit': 90, 'total': 999999}

    def detailContent(self, ids):
        did = ids[0]
        if not did.startswith('http'):
            did = xurl + did
            
        html_content = self.get_page_with_dynamic_cookie(did)
        if not html_content:
            return {'list': []}
            
        doc = BeautifulSoup(html_content, "lxml")
        
        vod = {
            "vod_id": ids[0],
            "vod_name": "",
            "vod_pic": "",
            "type_name": "",
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": "",
            "vod_actor": "",
            "vod_director": "",
            "vod_content": "",
            "vod_play_from": "KanAV",
            "vod_play_url": ""
        }
        
        match = re.search(r'var player_[a-zA-Z0-9_]+\s*=\s*(\{.*?\})<', html_content)
        if match:
            try:
                player_data = json.loads(match.group(1))
                vod_data = player_data.get('vod_data', {})
                vod['vod_name'] = vod_data.get('vod_name', '')
                vod['vod_actor'] = vod_data.get('vod_actor', '')
                vod['vod_director'] = vod_data.get('vod_director', '')
                vod['type_name'] = vod_data.get('vod_class', '')
            except:
                pass

        if not vod['vod_name']:
            h1_tag = doc.find('h1')
            if h1_tag:
                vod['vod_name'] = h1_tag.text.strip()
            else:
                h3_tag = doc.find('h3')
                if h3_tag:
                    vod['vod_name'] = h3_tag.text.strip()
                    
        vod['vod_content'] = vod['vod_name']
        
        img_tag = doc.find('img', class_='countext-img')
        if img_tag:
            vod['vod_pic'] = img_tag.get('src', '')
            
        categories_div = doc.find('div', class_='video-countext-categories')
        if categories_div:
            cat_a = categories_div.find_all('a')
            cats = []
            for a in cat_a:
                text = a.text.strip()
                if text.startswith('上映日期：'):
                    vod['vod_year'] = text.replace('上映日期：', '')
                else:
                    cats.append(text)
            if not vod['type_name']:
                vod['type_name'] = ','.join(cats)
                
        tags_divs = doc.find_all('div', class_='video-countext-tags')
        for div in tags_divs:
            hr_tags = div.find('div', class_='hr-tags')
            if hr_tags:
                tags = [a.text.strip() for a in div.find_all('a')]
                if tags:
                    vod['vod_remarks'] = ','.join(tags)
            
            hr_actor = div.find('div', class_='hr-actor')
            if hr_actor and not vod['vod_actor']:
                actors = [a.text.strip() for a in div.find_all('a')]
                if actors:
                    vod['vod_actor'] = ','.join(actors)
                    
        play_list = []
        vod_tags_divs = doc.find_all('div', class_='video-countext-tags')
        for div in vod_tags_divs:
            if div.find('div', class_='hr-vod'):
                a_tags = div.find_all('a')
                for a in a_tags:
                    title = a.get('title', a.text.strip())
                    href = a.get('href', '')
                    play_list.append(f"{title}${href}")
        
        if not play_list:
            play_list.append(f"播放${ids[0]}")
            
        vod['vod_play_url'] = "#".join(play_list)
        
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags):
        did = id if id.startswith('http') else xurl + id
        html_content = self.get_page_with_dynamic_cookie(did)
        
        real_url = ''
        if html_content:
            match = re.search(r'player_[a-zA-Z0-9_]+\s*=\s*\{.*?"url"\s*:\s*"([^"]+)"', html_content)
            if match:
                encrypted_url = match.group(1).replace('\\', '')
                try:
                    padded_enc = encrypted_url + "=" * (-len(encrypted_url) % 4)
                    base64_decoded = base64.b64decode(padded_enc).decode('utf-8')
                    real_url = unquote(base64_decoded)
                except Exception:
                    real_url = encrypted_url
                    
        play_headers = {
            "User-Agent": headerx.get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'),
            "Referer": "https://kanav.ad/",
            "Origin": "https://kanav.ad"
        }
                    
        result = {
            "parse": 0,
            "playUrl": '',
            "url": real_url,
            "header": play_headers
        }
        return result

    def searchContentPage(self, key, quick, pg):
        page = int(pg) if pg else 1
        target_url = f'{xurl}/index.php/vod/search/page/{page}/wd/{quote(key)}.html'
        html_content = self.get_page_with_dynamic_cookie(target_url)
        
        if not html_content:
            return {'list': [], 'page': page, 'pagecount': 9999, 'limit': 90, 'total': 999999}
            
        doc = BeautifulSoup(html_content, "lxml")
        videos = []
        for item in doc.find_all('div', class_='video-item'):
            img_div = item.find('div', class_='featured-content-image') or item.find('div', class_='video-image')
            if not img_div:
                continue
            a_tag = img_div.find('a')
            href = a_tag['href']
            img_tag = a_tag.find('img')
            name = img_tag.get('alt', '')
            pic = img_tag.get('data-original', '') or img_tag.get('src', '')
            
            remark_tag = img_div.find('span', class_='model-view')
            remark = remark_tag.text.strip() if remark_tag else ''
            
            videos.append({
                "vod_id": href,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
            })
            
        return {'list': videos, 'page': page, 'pagecount': 9999, 'limit': 90, 'total': 999999}

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, pg)

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None
