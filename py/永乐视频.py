import re
import sys
import urllib.parse
import requests
import time
import random
import json
import base64
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return "永乐视频"
    
    def init(self, extend=""):
        self.host = "https://www.ylys.tv"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': self.host
        }
        self.encoding = "UTF-8"
        
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update(self.headers)
        
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch(self, url, headers=None, timeout=30):
        try:
            if headers is None:
                headers = self.headers
            time.sleep(random.uniform(0.5, 1.5))
            response = self.session.get(url, headers=headers, timeout=timeout, verify=False)
            if response.encoding == 'ISO-8859-1':
                response.encoding = self.encoding
            return response
        except Exception as e:
            return None

    def homeContent(self, filter):
        result = {
            "class": [
                {'type_id': '4', 'type_name': '动漫'},
                {'type_id': '2', 'type_name': '剧集'},
                {'type_id': '1', 'type_name': '电影'},
                {'type_id': '3', 'type_name': '综艺'}
            ],
            "filters": self._get_filters(),
            "list": []
        }
        try:
            rsp = self.fetch(self.host)
            if rsp and rsp.status_code == 200:
                html = rsp.text
                videos = self._extract_videos_with_bs(html)
                result['list'] = videos
        except Exception as e:
            pass
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {"list": [], "page": int(pg), "pagecount": 99, "limit": 20, "total": 1980}
        try:
            class_filter = extend.get('class', '') if extend else ''
            area_filter = extend.get('area', '') if extend else ''
            lang_filter = extend.get('lang', '') if extend else ''
            year_filter = extend.get('year', '') if extend else ''
            letter_filter = extend.get('letter', '') if extend else ''
            sort_filter = extend.get('sort', '') if extend else 'time_update'
            
            main_id = class_filter if class_filter else tid
            
            params = [
                area_filter,
                sort_filter,
                "",
                lang_filter,
                letter_filter,
                "",
                "",
                "",
                "",
                "",
                year_filter
            ]
            
            param_str = "-".join(params)
            
            if int(pg) == 1:
                url = f"{self.host}/vodshow/{main_id}-{param_str}/"
            else:
                url = f"{self.host}/vodshow/{main_id}-{param_str}/page/{pg}/"
            
            rsp = self.fetch(url)
            
            if rsp and rsp.status_code == 200:
                html = rsp.text
                videos = self._extract_videos_with_bs(html)
                result['list'] = videos
        except Exception as e:
            pass
        return result

    def searchContent(self, key, quick, pg=1):
        result = {"list": []}
        try:
            search_key = urllib.parse.quote(key)
            search_url = f"{self.host}/vodsearch/{search_key}-------------/" if int(pg) == 1 else f"{self.host}/vodsearch/{search_key}-------------/page/{pg}/"
            
            rsp = self.fetch(search_url)
            if rsp and rsp.status_code == 200:
                html = rsp.text
                videos = self._extract_videos_with_bs(html)
                result['list'] = videos
        except Exception as e:
            pass
        return result

    def detailContent(self, ids):
        result = {"list": []}
        try:
            vid = ids[0]
            detail_url = f"{self.host}/voddetail/{vid}/"
            
            rsp = self.fetch(detail_url)
            if not rsp or rsp.status_code != 200:
                return result
                
            html = rsp.text
            soup = BeautifulSoup(html, 'html.parser')
            
            play_from = []
            tabs = soup.select('#y-playList .tab-item')
            if not tabs:
                tabs = soup.select('.player-heading .module-tab-item')
                
            for tab in tabs:
                span = tab.select_one('span')
                small = tab.select_one('small')
                
                if span:
                    line_name = span.get_text(strip=True)
                else:
                    line_name = tab.get('data-dropdown-value') or tab.get_text(strip=True)
                
                if small:
                    ep_count = small.get_text(strip=True)
                    if ep_count:
                        line_name = f"{line_name}(共{ep_count}集)"
                
                if line_name and line_name not in play_from:
                    play_from.append(line_name)
                    
            play_url = []
            lists = soup.select('.module-list.sort-list')
            for lst in lists:
                eps = lst.select('a.module-play-list-link')
                ep_links = []
                for ep in eps:
                    ep_name = ep.get_text(strip=True)
                    ep_href = ep.get('href', '')
                    if ep_href:
                        ep_id = ep_href.strip('/').split('/')[-1]
                        ep_links.append(f"{ep_name}${ep_id}")
                if ep_links:
                    play_url.append("#".join(ep_links))
                    
            if len(play_from) > len(play_url):
                play_from = play_from[:len(play_url)]
            elif len(play_url) > len(play_from):
                play_url = play_url[:len(play_from)]
                
            title = ""
            title_elem = soup.select_one('.module-info-heading h1')
            if title_elem:
                title = title_elem.get_text(strip=True)
            if not title:
                title_elem = soup.select_one('meta[property="og:title"]')
                if title_elem:
                    title = title_elem.get('content', '').split('-')[0].strip()
                    
            pic = ""
            pic_elem = soup.select_one('.module-info-poster .module-item-pic img')
            if pic_elem:
                pic = pic_elem.get('data-original') or pic_elem.get('src') or ""
            if pic and pic.startswith('/'):
                pic = self.host + pic
                
            desc = ""
            desc_elem = soup.select_one('.module-info-introduction-content p')
            if desc_elem:
                desc = desc_elem.get_text(strip=True)
                
            vod_director = ""
            vod_actor = ""
            vod_year = ""
            vod_area = ""
            type_name = ""
            vod_remarks = ""
            
            tags = soup.select('.module-info-tag-link a')
            tag_texts = [t.get_text(strip=True) for t in tags]
            if len(tag_texts) >= 3:
                vod_year = tag_texts[0]
                vod_area = tag_texts[1]
                type_name = "/".join(tag_texts[2:])
            elif tag_texts:
                type_name = "/".join(tag_texts)
            
            extra_desc = []
            info_items = soup.select('.module-info-item')
            for item in info_items:
                title_span = item.select_one('.module-info-item-title')
                if not title_span:
                    continue
                t_text = title_span.get_text(strip=True)
                c_div = item.select_one('.module-info-item-content')
                if not c_div:
                    continue
                
                a_tags = c_div.select('a')
                if a_tags:
                    c_text = ', '.join([a.get_text(strip=True) for a in a_tags])
                else:
                    c_text = c_div.get_text(strip=True)
                    
                if '导演' in t_text:
                    vod_director = c_text
                elif '主演' in t_text:
                    vod_actor = c_text
                elif '上映' in t_text:
                    if not vod_year:
                        vod_year = c_text
                elif '集数' in t_text:
                    vod_remarks = c_text
                elif '更新' in t_text:
                    if not vod_remarks:
                        vod_remarks = f"更新至: {c_text}"
                elif '编剧' in t_text:
                    extra_desc.append(f"编剧: {c_text}")
                elif '语言' in t_text:
                    extra_desc.append(f"语言: {c_text}")
                    
            if extra_desc:
                desc = "【" + " | ".join(extra_desc) + "】 " + desc

            if not vod_remarks:
                vod_remarks = type_name
            
            if play_from and play_url:
                result['list'] = [{
                    'vod_id': vid,
                    'vod_name': title,
                    'vod_pic': pic,
                    'type_name': type_name,
                    'vod_year': vod_year,
                    'vod_area': vod_area,
                    'vod_remarks': vod_remarks,
                    'vod_actor': vod_actor,
                    'vod_director': vod_director,
                    'vod_content': desc,
                    'vod_play_from': "$$$".join(play_from),
                    'vod_play_url': "$$$".join(play_url)
                }]
            
        except Exception as e:
            pass
            
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {"parse": 1, "playUrl": "", "url": ""}
        try:
            play_url = f"{self.host}/play/{id}/"
            rsp = self.fetch(play_url)
            if not rsp or rsp.status_code != 200:
                return result
                
            html = rsp.text
            real_url_pattern = r'var player_aaaa\s*=\s*(\{.*?\})'
            match = re.search(real_url_pattern, html)
            if match:
                try:
                    player_data = json.loads(match.group(1))
                    url = player_data.get("url", "")
                    if url:
                        encrypt = player_data.get("encrypt", 0)
                        if encrypt == 1:
                            url = urllib.parse.unquote(url)
                        elif encrypt == 2:
                            url = base64.b64decode(url).decode('utf-8')
                            url = urllib.parse.unquote(url)
                        result["parse"] = 0
                        result["url"] = url
                    else:
                        result["parse"] = 1
                        result["url"] = play_url
                except:
                    result["parse"] = 1
                    result["url"] = play_url
            else:
                result["parse"] = 1
                result["url"] = play_url
        except Exception as e:
            result["url"] = f"{self.host}/play/{id}/" if "-" in id else f"{self.host}/voddetail/{id}/"
        return result

    def _get_filters(self):
        return {
            "1": [{"key": "class", "name": "类型", "value": [
                {"n": "全部", "v": ""}, {"n": "动作片", "v": "6"}, {"n": "喜剧片", "v": "7"},
                {"n": "爱情片", "v": "8"}, {"n": "科幻片", "v": "9"}, {"n": "奇幻片", "v": "10"}, 
                {"n": "恐怖片", "v": "11"}, {"n": "剧情片", "v": "12"}, {"n": "战争片", "v": "20"}, 
                {"n": "纪录片", "v": "21"}, {"n": "动画片", "v": "26"}, {"n": "悬疑片", "v": "22"}, 
                {"n": "冒险片", "v": "23"}, {"n": "犯罪片", "v": "24"}, {"n": "惊悚片", "v": "45"}, 
                {"n": "歌舞片", "v": "46"}, {"n": "灾难片", "v": "47"}, {"n": "网络片", "v": "48"}
            ]},
            {"key": "area", "name": "地区", "value": [
                {"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"}, 
                {"n": "台湾", "v": "台湾"}, {"n": "美国", "v": "美国"}, {"n": "法国", "v": "法国"},
                {"n": "英国", "v": "英国"}, {"n": "日本", "v": "日本"}, {"n": "韩国", "v": "韩国"}, 
                {"n": "德国", "v": "德国"}, {"n": "泰国", "v": "泰国"}, {"n": "印度", "v": "印度"},
                {"n": "意大利", "v": "意大利"}, {"n": "西班牙", "v": "西班牙"}, {"n": "加拿大", "v": "加拿大"}, 
                {"n": "其他", "v": "其他"}
            ]},
            {"key": "lang", "name": "语言", "value": [
                {"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "英语", "v": "英语"}, 
                {"n": "粤语", "v": "粤语"}, {"n": "闽南语", "v": "闽南语"}, {"n": "韩语", "v": "韩语"},
                {"n": "日语", "v": "日语"}, {"n": "西班牙", "v": "西班牙"}, {"n": "德语", "v": "德语"}, 
                {"n": "泰语", "v": "泰语"}, {"n": "其它", "v": "其它"}
            ]},
            {"key": "year", "name": "年份", "value": [
                {"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, 
                {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, 
                {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, 
                {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, 
                {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, 
                {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "更早", "v": "更早"}
            ]},
            {"key": "letter", "name": "字母", "value": [
                {"n": "全部", "v": ""}, {"n": "A", "v": "A"}, {"n": "B", "v": "B"},
                {"n": "C", "v": "C"}, {"n": "D", "v": "D"}, {"n": "E", "v": "E"},
                {"n": "F", "v": "F"}, {"n": "G", "v": "G"}, {"n": "H", "v": "H"},
                {"n": "I", "v": "I"}, {"n": "J", "v": "J"}, {"n": "K", "v": "K"},
                {"n": "L", "v": "L"}, {"n": "M", "v": "M"}, {"n": "N", "v": "N"},
                {"n": "O", "v": "O"}, {"n": "P", "v": "P"}, {"n": "Q", "v": "Q"},
                {"n": "R", "v": "R"}, {"n": "S", "v": "S"}, {"n": "T", "v": "T"},
                {"n": "U", "v": "U"}, {"n": "V", "v": "V"}, {"n": "W", "v": "W"},
                {"n": "X", "v": "X"}, {"n": "Y", "v": "Y"}, {"n": "Z", "v": "Z"},
                {"n": "0-9", "v": "0-9"}
            ]},
            {"key": "sort", "name": "排序", "value": [
                {"n": "更新时间", "v": "time_update"}, {"n": "添加时间", "v": "time_add"}, 
                {"n": "人气排序", "v": "hits"}, {"n": "评分排序", "v": "score"}
            ]}],
            "2": [{"key": "class", "name": "类型", "value": [
                {"n": "全部", "v": ""}, {"n": "国产剧", "v": "13"}, {"n": "港台剧", "v": "14"},
                {"n": "日剧", "v": "15"}, {"n": "韩剧", "v": "33"}, {"n": "欧美剧", "v": "16"},
                {"n": "泰剧", "v": "34"}, {"n": "新马剧", "v": "35"}, {"n": "其他剧", "v": "25"}
            ]},
            {"key": "area", "name": "地区", "value": [
                {"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"}, 
                {"n": "台湾", "v": "台湾"}, {"n": "美国", "v": "美国"}, {"n": "法国", "v": "法国"},
                {"n": "英国", "v": "英国"}, {"n": "日本", "v": "日本"}, {"n": "韩国", "v": "韩国"}, 
                {"n": "德国", "v": "德国"}, {"n": "泰国", "v": "泰国"}, {"n": "印度", "v": "印度"},
                {"n": "意大利", "v": "意大利"}, {"n": "西班牙", "v": "西班牙"}, {"n": "加拿大", "v": "加拿大"}, 
                {"n": "其他", "v": "其他"}
            ]},
            {"key": "lang", "name": "语言", "value": [
                {"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "英语", "v": "英语"}, 
                {"n": "粤语", "v": "粤语"}, {"n": "闽南语", "v": "闽南语"}, {"n": "韩语", "v": "韩语"},
                {"n": "日语", "v": "日语"}, {"n": "西班牙", "v": "西班牙"}, {"n": "德语", "v": "德语"}, 
                {"n": "泰语", "v": "泰语"}, {"n": "其它", "v": "其它"}
            ]},
            {"key": "year", "name": "年份", "value": [
                {"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, 
                {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, 
                {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, 
                {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, 
                {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, 
                {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010-2000", "v": "2010-2000"},
                {"n": "90年代", "v": "90年代"}, {"n": "80年代", "v": "80年代"}, {"n": "更早", "v": "更早"}
            ]},
            {"key": "letter", "name": "字母", "value": [
                {"n": "全部", "v": ""}, {"n": "A", "v": "A"}, {"n": "B", "v": "B"},
                {"n": "C", "v": "C"}, {"n": "D", "v": "D"}, {"n": "E", "v": "E"},
                {"n": "F", "v": "F"}, {"n": "G", "v": "G"}, {"n": "H", "v": "H"},
                {"n": "I", "v": "I"}, {"n": "J", "v": "J"}, {"n": "K", "v": "K"},
                {"n": "L", "v": "L"}, {"n": "M", "v": "M"}, {"n": "N", "v": "N"},
                {"n": "O", "v": "O"}, {"n": "P", "v": "P"}, {"n": "Q", "v": "Q"},
                {"n": "R", "v": "R"}, {"n": "S", "v": "S"}, {"n": "T", "v": "T"},
                {"n": "U", "v": "U"}, {"n": "V", "v": "V"}, {"n": "W", "v": "W"},
                {"n": "X", "v": "X"}, {"n": "Y", "v": "Y"}, {"n": "Z", "v": "Z"},
                {"n": "0-9", "v": "0-9"}
            ]},
            {"key": "sort", "name": "排序", "value": [
                {"n": "更新时间", "v": "time_update"}, {"n": "添加时间", "v": "time_add"}, 
                {"n": "人气排序", "v": "hits"}, {"n": "评分排序", "v": "score"}
            ]}],
            "3": [{"key": "class", "name": "类型", "value": [
                {"n": "全部", "v": ""}, {"n": "内地综艺", "v": "27"}, {"n": "港台综艺", "v": "28"},
                {"n": "日本综艺", "v": "29"}, {"n": "韩国综艺", "v": "36"}, {"n": "欧美综艺", "v": "30"},
                {"n": "新马泰综艺", "v": "37"}, {"n": "其他综艺", "v": "38"}
            ]},
            {"key": "area", "name": "地区", "value": [
                {"n": "全部", "v": ""}, {"n": "内地", "v": "内地"}, {"n": "港台", "v": "港台"}, 
                {"n": "日韩", "v": "日韩"}, {"n": "欧美", "v": "欧美"}
            ]},
            {"key": "lang", "name": "语言", "value": [
                {"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "英语", "v": "英语"}, 
                {"n": "粤语", "v": "粤语"}, {"n": "闽南语", "v": "闽南语"}, {"n": "韩语", "v": "韩语"},
                {"n": "日语", "v": "日语"}, {"n": "其它", "v": "其它"}
            ]},
            {"key": "year", "name": "年份", "value": [
                {"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, 
                {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, 
                {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, 
                {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, 
                {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, 
                {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010-2000", "v": "2010-2000"},
                {"n": "90年代", "v": "90年代"}, {"n": "80年代", "v": "80年代"}, {"n": "更早", "v": "更早"}
            ]},
            {"key": "letter", "name": "字母", "value": [
                {"n": "全部", "v": ""}, {"n": "A", "v": "A"}, {"n": "B", "v": "B"},
                {"n": "C", "v": "C"}, {"n": "D", "v": "D"}, {"n": "E", "v": "E"},
                {"n": "F", "v": "F"}, {"n": "G", "v": "G"}, {"n": "H", "v": "H"},
                {"n": "I", "v": "I"}, {"n": "J", "v": "J"}, {"n": "K", "v": "K"},
                {"n": "L", "v": "L"}, {"n": "M", "v": "M"}, {"n": "N", "v": "N"},
                {"n": "O", "v": "O"}, {"n": "P", "v": "P"}, {"n": "Q", "v": "Q"},
                {"n": "R", "v": "R"}, {"n": "S", "v": "S"}, {"n": "T", "v": "T"},
                {"n": "U", "v": "U"}, {"n": "V", "v": "V"}, {"n": "W", "v": "W"},
                {"n": "X", "v": "X"}, {"n": "Y", "v": "Y"}, {"n": "Z", "v": "Z"},
                {"n": "0-9", "v": "0-9"}
            ]},
            {"key": "sort", "name": "排序", "value": [
                {"n": "更新时间", "v": "time_update"}, {"n": "添加时间", "v": "time_add"}, 
                {"n": "人气排序", "v": "hits"}, {"n": "评分排序", "v": "score"}
            ]}],
            "4": [{"key": "class", "name": "类型", "value": [
                {"n": "全部", "v": ""}, {"n": "国产动漫", "v": "31"}, {"n": "日本动漫", "v": "32"},
                {"n": "韩国动漫", "v": "39"}, {"n": "港台动漫", "v": "40"}, {"n": "新马泰动漫", "v": "41"}, 
                {"n": "欧美动漫", "v": "42"}, {"n": "其他动漫", "v": "43"}
            ]},
            {"key": "area", "name": "地区", "value": [
                {"n": "全部", "v": ""}, {"n": "国产", "v": "国产"}, {"n": "日本", "v": "日本"}, 
                {"n": "欧美", "v": "欧美"}, {"n": "其他", "v": "其他"}
            ]},
            {"key": "lang", "name": "语言", "value": [
                {"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "英语", "v": "英语"}, 
                {"n": "粤语", "v": "粤语"}, {"n": "闽南语", "v": "闽南语"}, {"n": "韩语", "v": "韩语"},
                {"n": "日语", "v": "日语"}, {"n": "其它", "v": "其它"}
            ]},
            {"key": "year", "name": "年份", "value": [
                {"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, 
                {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, 
                {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, 
                {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, 
                {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, 
                {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010-2000", "v": "2010-2000"},
                {"n": "90年代", "v": "90年代"}, {"n": "80年代", "v": "80年代"}, {"n": "更早", "v": "更早"}
            ]},
            {"key": "letter", "name": "字母", "value": [
                {"n": "全部", "v": ""}, {"n": "A", "v": "A"}, {"n": "B", "v": "B"},
                {"n": "C", "v": "C"}, {"n": "D", "v": "D"}, {"n": "E", "v": "E"},
                {"n": "F", "v": "F"}, {"n": "G", "v": "G"}, {"n": "H", "v": "H"},
                {"n": "I", "v": "I"}, {"n": "J", "v": "J"}, {"n": "K", "v": "K"},
                {"n": "L", "v": "L"}, {"n": "M", "v": "M"}, {"n": "N", "v": "N"},
                {"n": "O", "v": "O"}, {"n": "P", "v": "P"}, {"n": "Q", "v": "Q"},
                {"n": "R", "v": "R"}, {"n": "S", "v": "S"}, {"n": "T", "v": "T"},
                {"n": "U", "v": "U"}, {"n": "V", "v": "V"}, {"n": "W", "v": "W"},
                {"n": "X", "v": "X"}, {"n": "Y", "v": "Y"}, {"n": "Z", "v": "Z"},
                {"n": "0-9", "v": "0-9"}
            ]},
            {"key": "sort", "name": "排序", "value": [
                {"n": "更新时间", "v": "time_update"}, {"n": "添加时间", "v": "time_add"}, 
                {"n": "人气排序", "v": "hits"}, {"n": "评分排序", "v": "score"}
            ]}]
        }

    def _extract_videos_with_bs(self, html):
        videos = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            items = soup.select('.module-item')
            seen_ids = set()
            
            for item in items:
                a_tag = item if item.name == 'a' else item.select_one('a[href^="/voddetail/"]')
                if not a_tag:
                    continue
                    
                href = a_tag.get('href', '')
                vid_match = re.search(r'/voddetail/(\d+)/', href)
                if not vid_match:
                    continue
                    
                vid = vid_match.group(1)
                if vid in seen_ids:
                    continue
                seen_ids.add(vid)
                
                title = item.get('title', '') or a_tag.get('title', '')
                if not title:
                    title_elem = item.select_one('.module-poster-item-title, .module-card-item-title strong, .module-card-item-title a')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                
                img_elem = item.select_one('img')
                pic = ""
                if img_elem:
                    pic = img_elem.get('data-original') or img_elem.get('src') or ""
                    if not title:
                        title = img_elem.get('alt', '')
                        
                if pic and pic.startswith('/'):
                    pic = self.host + pic
                    
                note_elem = item.select_one('.module-item-note')
                remark = note_elem.get_text(strip=True) if note_elem else ""
                
                videos.append({
                    'vod_id': vid.strip(),
                    'vod_name': title.strip(),
                    'vod_pic': pic.strip(),
                    'vod_remarks': remark.strip()
                })
        except Exception as e:
            pass
        return videos
