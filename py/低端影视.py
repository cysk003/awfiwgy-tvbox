import sys
import re
from bs4 import BeautifulSoup
from base.spider import Spider
#https://www.ddys.diy
class Spider(Spider):
    def __init__(self):
        self.name = '低端影视'
        self.host = 'https://www.ddys.run'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
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
        classes = [
            {'type_id': 'dianying', 'type_name': '电影'},
            {'type_id': 'juji', 'type_name': '剧集'},
            {'type_id': 'dongman', 'type_name': '动漫'}
        ]
        return {'class': classes}

    def homeVideoContent(self):
        res = self.fetch(self.host, headers=self.headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        videos = []
        recommend_list = soup.select_one('.stui-pannel__bd .stui-vodlist')
        if recommend_list:
            for item in recommend_list.select('li'):
                box = item.select_one('.stui-vodlist__box')
                if not box: continue
                
                a = box.select_one('a.stui-vodlist__thumb')
                title_node = box.select_one('.title a')
                if not a or not title_node: continue
                
                href = a.get('href', '')
                vid_match = re.search(r'/video/(.*?)\.html', href)
                if not vid_match: continue
                
                videos.append({
                    'vod_id': vid_match.group(1),
                    'vod_name': title_node.get('title', ''),
                    'vod_pic': a.get('data-original', ''),
                    'vod_remarks': box.select_one('.pic-text').text.strip() if box.select_one('.pic-text') else ''
                })
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        page = int(pg)
        url = f"{self.host}/category/{tid}.html" if page == 1 else f"{self.host}/category/{tid}-{page}.html"
        
        res = self.fetch(url, headers=self.headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        videos = []
        for box in soup.select('.stui-vodlist__box'):
            a = box.select_one('a.stui-vodlist__thumb')
            title_node = box.select_one('.title a')
            if not a or not title_node: continue
            
            vid_match = re.search(r'/video/(.*?)\.html', a.get('href', ''))
            if vid_match:
                videos.append({
                    'vod_id': vid_match.group(1),
                    'vod_name': title_node.get('title', ''),
                    'vod_pic': a.get('data-original', ''),
                    'vod_remarks': box.select_one('.pic-text').text.strip() if box.select_one('.pic-text') else ''
                })
        return {'list': videos}

    def detailContent(self, ids):
        vod_id = ids[0]
        url = f"{self.host}/video/{vod_id}.html"
        res = self.fetch(url, headers=self.headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        content_node = soup.select_one('.stui-content__detail')
        vod = {
            'vod_id': vod_id,
            'vod_name': content_node.select_one('h1.title').text.strip() if content_node.select_one('h1.title') else '',
            'vod_pic': soup.select_one('.stui-content__thumb img').get('data-original', '') if soup.select_one('.stui-content__thumb img') else '',
            'vod_content': soup.select_one('.detail-content').text.strip() if soup.select_one('.detail-content') else '',
        }
        
        for p in content_node.select('.data'):
            text = p.text.replace('\xa0', ' ')
            if '类型：' in text:
                vod['type_name'] = text.split('类型：')[-1].split('/')[0].strip()
                vod['vod_year'] = text.split('年份：')[-1].strip()
                vod['vod_area'] = text.split('地区：')[-1].split('/')[0].strip()
            if '主演：' in text:
                vod['vod_actor'] = text.replace('主演：', '').strip()
            if '导演：' in text:
                vod['vod_director'] = text.replace('导演：', '').strip()

        play_froms = []
        play_urls = []
        
        heads = soup.select('.stui-pannel__bd .stui-vodlist__head')
        for head in heads:
            source_title = head.select_one('h3').text.strip()
            if '猜你喜欢' in source_title: continue
            
            ul = head.find_next_sibling('ul', class_='stui-content__playlist')
            if not ul: continue
            
            play_froms.append(source_title)
            links = [f"{a.text.strip()}${a.get('href')}" for a in ul.select('li a')]
            play_urls.append('#'.join(links))
            
        vod['vod_play_from'] = '$$$'.join(play_froms)
        vod['vod_play_url'] = '$$$'.join(play_urls)
        
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        search_url = f"{self.host}/search/-------------.html"
        res = self.fetch(search_url, headers=self.headers, postData={'wd': key})
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        videos = []
        for box in soup.select('.stui-vodlist__box'):
            a = box.select_one('a.stui-vodlist__thumb')
            title_node = box.select_one('.title a')
            if not a or not title_node: continue
            
            vid_match = re.search(r'/video/(.*?)\.html', a.get('href', ''))
            if vid_match:
                videos.append({
                    'vod_id': vid_match.group(1),
                    'vod_name': title_node.get('title', ''),
                    'vod_pic': a.get('data-original', ''),
                    'vod_remarks': box.select_one('.pic-text').text.strip() if box.select_one('.pic-text') else ''
                })
        return {'list': videos}

    def playerContent(self, flag, id, vipFlags):
        return {'parse': 1, 'url': self.host + id, 'header': self.headers}

    def destroy(self):
        pass
