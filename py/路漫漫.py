# -*- coding: utf-8 -*-
import requests, re
from bs4 import BeautifulSoup
from base.spider import Spider

class Spider(Spider):
    siteUrl = "https://www.lmm50.com"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36', 'Referer': siteUrl}

    def getName(self): return "路漫漫动漫"
    def init(self, extend): pass
    def isVideoFormat(self, url): pass
    def manualVideoCheck(self): pass

    def _get(self, url):
        try:
            r = requests.get(url, headers=self.headers, timeout=5)
            r.encoding = 'utf-8'
            return BeautifulSoup(r.text, 'lxml')
        except: return None

    def _parse_item(self, item):
        try:
            t = item.select_one('.title a, .module-item-title a')
            img = item.select_one('img')
            pic = img.get('data-src') or img.get('src', '')
            if pic.startswith('//'): pic = 'https:' + pic
            rem = item.select_one('.label, .module-item-note')
            return {
                'vod_id': t['href'], 'vod_name': t.text.strip(),
                'vod_pic': pic, 'vod_remarks': rem.text.strip() if rem else ''
            }
        except: return None

    def homeContent(self, filter):
        return {"class": [
            {"type_id": "guochandongman", "type_name": "国产动漫"},
            {"type_id": "dongtaiman", "type_name": "动态漫画"},
            {"type_id": "ribendongman", "type_name": "日本动漫"},
            {"type_id": "guochandonghuadianying", "type_name": "国产电影"},
            {"type_id": "ribendonghuadianying", "type_name": "日本电影"},
            {"type_id": "teshepian", "type_name": "日本特摄剧"},
            {"type_id": "oumeidongman", "type_name": "欧美动漫"},
            {"type_id": "oumeidonghuadianying", "type_name": "欧美电影"}
        ]}

    def homeVideoContent(self): return {'list': []}

    def categoryContent(self, cid, pg, filter, ext):
        pg = int(pg) if pg else 1
        url = f'{self.siteUrl}/type/{cid}_{pg}.html' if pg > 1 else f'{self.siteUrl}/type/{cid}.html'
        soup = self._get(url)
        if not soup: return {'list': [], 'page': pg}
        
        videos = [v for i in soup.select('.col-6, .module-item') if (v := self._parse_item(i))]
        
        # 获取总页数
        pagecount = pg
        if last := soup.find('a', string=re.compile(r'最后|尾页')):
            if m := re.search(r'_(\d+)\.html', last.get('href', '')):
                pagecount = int(m.group(1))
        
        return {'list': videos, 'page': pg, 'pagecount': pagecount, 'limit': 20, 'total': 999}

    def detailContent(self, ids):
        url = ids[0] if ids[0].startswith('http') else self.siteUrl + ids[0]
        soup = self._get(url)
        if not soup: return {'list': []}

        # 基础信息
        title = soup.select_one('h1.page-title, h4').text.split(' - ')[0].strip()
        pic = (soup.select_one('.url_img, .lazyload, .detail-pic img') or {}).get('src', '')
        if pic.startswith('//'): pic = 'https:' + pic
        desc = (soup.select_one('.video-info-content, .detail-content') or {}).get_text(strip=True) or "暂无简介"
        
        # 演员/导演提取
        acts, dirs = [], []
        for row in soup.select('.video-info-items, .video-info-item'):
            txt = row.text
            if '主演' in txt or '演员' in txt: acts = [a.text.strip() for a in row.select('a')]
            elif '导演' in txt: dirs = [a.text.strip() for a in row.select('a')]

        # 播放列表处理
        p_from, p_url = [], []
        cn_num = '一二三四五六七八九十'
        for i, list_node in enumerate(soup.select('.module-player-list, .module-list')):
            uname = f"线路{cn_num[i] if i < 10 else i + 1}"
            u_list = [f"{a.text.strip()}${a['href'] if a['href'].startswith('http') else self.siteUrl + a['href']}" 
                      for a in list_node.select('a') if '/play/' in a.get('href', '')]
            if u_list:
                p_from.append(uname)
                p_url.append('#'.join(u_list))

        return {'list': [{
            "vod_id": ids[0], "vod_name": title, "vod_pic": pic,
            "vod_actor": '/'.join(acts), "vod_director": '/'.join(dirs),
            "vod_content": desc, "vod_play_from": '$$$'.join(p_from), "vod_play_url": '$$$'.join(p_url)
        }]}

    def searchContent(self, key, quick):
        soup = self._get(f'{self.siteUrl}/vod/search.html?wd={key}')
        return {'list': [v for i in soup.select('.video-img-box, .module-item') if (v := self._parse_item(i))]} if soup else {'list': []}

    def playerContent(self, flag, id, vipFlags):
        url = id if id.startswith('http') else (self.siteUrl + id if id.startswith('/') else f"{self.siteUrl}/play/{id}.html")
        return {'parse': 1, 'playUrl': '', 'url': url, 'header': self.headers}
