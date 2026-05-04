import html
import re
import requests
import urllib3
from bs4 import BeautifulSoup
from base.spider import Spider

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Spider(Spider):
    
    def getName(self):
        return "快播影院"
#http://9155.net
    def init(self, extend=""):
        self.xurl = "https://uk4.9155net.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.xurl
        }

    def get_page(self, url):
        try:
            resp = requests.get(url, headers=self.headers, verify=False, timeout=10)
            if resp.status_code == 200:
                resp.encoding = 'utf-8'
                return resp.text
        except Exception as e:
            pass
        return ""

    def parse_video_item(self, li_soup):
        pic_div = li_soup.find('div', class_='pic')
        a_tag = pic_div.find('a')
        
        vod_id = a_tag['href']
        vod_pic = a_tag.get('data-original', '') 
        
        span = a_tag.find('span')
        vod_remarks = span.text.strip() if span else ""
        
        biaoti_div = li_soup.find('div', class_='biaoti')
        vod_name = biaoti_div.find('a').text.strip() if biaoti_div else ""
        
        return {
            "vod_id": vod_id,
            "vod_name": vod_name,
            "vod_pic": vod_pic,
            "vod_remarks": vod_remarks
        }

    def homeContent(self, filter):
        result = {}
        result['class'] = [
            {"type_id": "250", "type_name": "国产情色"},
            {"type_id": "260", "type_name": "韩国伦理"},
            {"type_id": "251", "type_name": "日本无码"},
            {"type_id": "262", "type_name": "精品推荐"},
            {"type_id": "253", "type_name": "中文字幕"},
            {"type_id": "256", "type_name": "欧美情色"},
            {"type_id": "254", "type_name": "网红主播"},
            {"type_id": "252", "type_name": "AV明星"},
            {"type_id": "259", "type_name": "邻家人妻"},
            {"type_id": "255", "type_name": "成人动漫"},
            {"type_id": "261", "type_name": "香港伦理"},
            {"type_id": "258", "type_name": "长腿丝袜"},
            {"type_id": "257", "type_name": "国模私拍"},
            {"type_id": "266", "type_name": "AV明星"},
            {"type_id": "265", "type_name": "大桥未久"}
        ]
        return result

    def homeVideoContent(self):
        html_content = self.get_page(self.xurl + "/site_8/")
        if not html_content:
            return {'list': []}
            
        doc = BeautifulSoup(html_content, "lxml")
        videos = []
        
        boxes = doc.find_all('div', class_='box')
        for box in boxes:
            list2 = box.find('div', class_='list2')
            if list2:
                for li in list2.find_all('li'):
                    videos.append(self.parse_video_item(li))
                    
        return {'list': videos}

    def categoryContent(self, cid, pg, filter, ext):
        if str(pg) == "1":
            url = f"{self.xurl}/site_8/{cid}/"
        else:
            url = f"{self.xurl}/site_8/{cid}-{pg}/"
            
        html_content = self.get_page(url)
        if not html_content:
            return {'list': []}
            
        doc = BeautifulSoup(html_content, "lxml")
        videos = []
        
        list2 = doc.find('div', class_='list2')
        if list2:
            for li in list2.find_all('li'):
                videos.append(self.parse_video_item(li))
                
        return {'list': videos, 'page': pg}

    def detailContent(self, ids):
        vod_id = ids[0]
        url = vod_id if vod_id.startswith('http') else self.xurl + vod_id
            
        html_content = self.get_page(url)
        if not html_content:
            return {'list': []}
            
        doc = BeautifulSoup(html_content, "lxml")
        
        h1 = doc.find('h1', class_='h1')
        vod_name = h1.text.strip() if h1 else "未知影片"
        
        dplayer = doc.find('div', id='dplayer')
        playurl = dplayer.get('playurl', '') if dplayer else ""
        
        vod = {
            "vod_id": vod_id,
            "vod_name": vod_name,
            "vod_play_from": "默认直连",
            "vod_play_url": f"播放${playurl}" if playurl else ""
        }
        
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags):
        return {
            "parse": 0,
            "playUrl": "",
            "url": id,
            "header": self.headers
        }
        
    def searchContent(self, key, quick, pg="1"):
        search_url = f"{self.xurl}/site_8/cgi/search"
        try:
            resp = requests.post(search_url, data={"keywords": key}, headers=self.headers, verify=False, timeout=10, allow_redirects=True)
            resp.encoding = 'utf-8'
            html_content = resp.text
            current_url = resp.url
            
            if str(pg) != "1":
                match = re.search(r'/so/([^.]+)\.html', current_url)
                if match:
                    hash_key = match.group(1)
                    page_url = f"{self.xurl}/site_8/so/{hash_key}-{pg}.html"
                    html_content = self.get_page(page_url)
        except Exception:
            return {'list': []}
            
        doc = BeautifulSoup(html_content, "lxml")
        videos = []
        
        list2 = doc.find('div', class_='list2')
        if list2:
            for li in list2.find_all('li'):
                videos.append(self.parse_video_item(li))
                
        return {'list': videos, 'page': pg}

    def localProxy(self, params):
        pass
