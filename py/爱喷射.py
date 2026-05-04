from urllib.parse import unquote, quote
from base.spider import Spider
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import requests
import urllib3
import base64
import html
import json
import re
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.path.append('..')
#https://aipenshe.com
xurl = "https://apsapsapsapsapsaps.903286.xyz"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': xurl,
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

class Spider(Spider):
    
    def getName(self):
        return "爱喷射"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeVideoContent(self):
        html_content = self.get_page_with_dynamic_cookie(xurl)
        if not html_content:
            return {'list': []}
        doc = BeautifulSoup(html.unescape(html_content), "lxml")
        videos = self.extract_videos(doc)
        return {'list': videos}

    def get_page_with_dynamic_cookie(self, target_url):
        local_headers = headers.copy()
        local_headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        })
        session = requests.Session()
        session.headers.update(local_headers)
        session.verify = False
        try:
            resp = session.get(target_url, timeout=15)
            if resp.status_code == 200:
                return resp.text
            elif resp.status_code in [404, 503, 403, 521]:
                if session.cookies:
                    resp = session.get(target_url, timeout=15)
                    if resp.status_code == 200:
                        return resp.text
            return None
        except Exception:
            return None

    def homeContent(self, filter):
        classes = [
            {"type_id": "24", "type_name": "主播秀色"},
            {"type_id": "47", "type_name": "国产人妻"},
            {"type_id": "48", "type_name": "国产SM"},
            {"type_id": "49", "type_name": "国产丝袜"},
            {"type_id": "50", "type_name": "国产乱伦"},
            {"type_id": "51", "type_name": "明星换脸"},
            {"type_id": "52", "type_name": "同性恋"},
            {"type_id": "53", "type_name": "探花嫖娼"},
            {"type_id": "61", "type_name": "偷拍自拍"},
            {"type_id": "62", "type_name": "主播网红"},
            {"type_id": "63", "type_name": "门事件"},
            {"type_id": "64", "type_name": "探花系列"},
            {"type_id": "65", "type_name": "抖阴视频"},
            {"type_id": "57", "type_name": "网曝系列"},
            {"type_id": "58", "type_name": "自拍偷拍"},
            {"type_id": "59", "type_name": "精品推荐"}
        ]
        result = {"class": classes}
        return result

    def categoryContent(self, cid, pg, filter, ext):
        page = self.get_page_number(pg)
        target_url = f'{xurl}/index.php/vod/type/id/{cid}/page/{page}.html'
        html_content = self.get_page_with_dynamic_cookie(target_url)
        if not html_content:
            return self.build_category_result([], pg)
            
        doc = BeautifulSoup(html.unescape(html_content), "lxml")
        videos = self.extract_videos(doc)
        return self.build_category_result(videos, pg)

    def get_page_number(self, pg):
        return int(pg) if pg else 1

    def extract_videos(self, doc):
        videos = []
        soups = doc.select('ul.thumbnail-group li')
        for vod in soups:
            a_tag = vod.select_one('div.video-info h5 a')
            if not a_tag:
                continue
                
            name = a_tag.get('title', '').strip()
            href = a_tag.get('href', '')
            
            match = re.search(r'/id/(\d+)\.html', href)
            vod_id = match.group(1) if match else href
            
            img_tag = vod.select_one('a.thumbnail img')
            pic = img_tag.get('src', '') if img_tag else ''
            if pic and not pic.startswith('http'):
                pic = xurl + pic
                
            p_tag = vod.select_one('div.video-info p')
            remark = p_tag.text.strip() if p_tag else ""
            
            videos.append({
                "vod_id": vod_id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
            })
        return videos

    def build_category_result(self, videos, pg):
        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 20
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        vod_id = ids[0]
        target_url = f"{xurl}/index.php/vod/detail/id/{vod_id}.html"
        html_content = self.get_page_with_dynamic_cookie(target_url)

        vod_name = "未知视频"
        vod_pic = ""
        type_name = ""
        vod_actor = "未知"
        vod_director = "未知"
        vod_content = "暂无简介"
        play_url_str = f"播放${xurl}/index.php/vod/play/id/{vod_id}/sid/1/nid/1.html"

        if html_content:
            doc = BeautifulSoup(html.unescape(html_content), "lxml")

            title_tag = doc.select_one('title')
            if title_tag:
                full_title = title_tag.text
                vod_name = full_title.split('-')[0].replace('在线观看', '').strip()

            type_tag = doc.select_one('div.breadcrumbs a[href*="/type/id/"]')
            if type_tag:
                type_name = type_tag.text.strip()

            img_tag = doc.select_one('.detail img, .vod-img img, .pic img')
            if img_tag:
                vod_pic = img_tag.get('src', '')
                if vod_pic and not vod_pic.startswith('http'):
                    vod_pic = xurl + vod_pic

            play_list_tags = doc.select('ul.ff-playurl li a')
            if play_list_tags:
                play_list = []
                for a_tag in play_list_tags:
                    ep_name = a_tag.text.strip()
                    ep_href = a_tag.get('href', '')
                    if ep_href:
                        play_list.append(f"{ep_name}${xurl}{ep_href}")
                if play_list:
                    play_url_str = "#".join(play_list)

        video = {
            "vod_id": vod_id,
            "vod_name": vod_name,
            "vod_pic": vod_pic,
            "type_name": type_name,
            "vod_actor": vod_actor,
            "vod_director": vod_director,
            "vod_content": vod_content,
            "vod_play_from": "爱喷射",
            "vod_play_url": play_url_str
        }

        return {"list": [video]}

    def playerContent(self, flag, id, vipFlags):
        html_content = self.get_page_with_dynamic_cookie(id)
        url = ''
        if html_content:
            match = re.search(r'var player_aaaa=({.+?})[;<]', html_content)
            if match:
                try:
                    player_data = json.loads(match.group(1))
                    url = player_data.get('url', '')
                    encrypt = player_data.get('encrypt', 0)
                    
                    if encrypt == 1:
                        url = unquote(url)
                    elif encrypt == 2:
                        url = unquote(base64.b64decode(url).decode('utf-8'))
                except Exception:
                    pass
        
        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = url
        result["header"] = headerx
        return result

    def searchContentPage(self, key, quick, pg):
        page = self.get_page_number(pg)
        target_url = f'{xurl}/index.php/vod/search/page/{page}/wd/{quote(key)}.html'
        html_content = self.get_page_with_dynamic_cookie(target_url)
        if not html_content:
            return self.build_category_result([], pg)
            
        doc = BeautifulSoup(html.unescape(html_content), "lxml")
        videos = self.extract_videos(doc)
        return self.build_category_result(videos, pg)

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
