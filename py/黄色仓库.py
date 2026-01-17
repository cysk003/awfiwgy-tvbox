import json, re
from urllib.parse import quote
from base.spider import Spider

class Spider(Spider):
    def getName(self): return '黄色仓库'
    def init(self, extend=""): pass
    def isVideoFormat(self, url): return bool(re.search(r'\.(m3u8|mp4|avi|flv|wmv)$', url.split('?')[0]))
    def manualVideoCheck(self): return False

    def __init__(self):
        self.h = 'http://hsck0.69cctv.cc'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.h
        }
#http://96cctv.com
#http://cctv12306.com
    def homeContent(self, filter):
        c = [('wz','无码中文'),('rw','日本无码'),('dm','动漫剧情'),('ycgc','国产新片'),('yz','有码中文'),('ry','日本有码'),('gc','国产视频'),('om','欧美高清')]
        return {'class': [{'type_id': i, 'type_name': n} for i, n in c]}

    def homeVideoContent(self): return self._list(self.h)

    def categoryContent(self, tid, pg, filter, extend):
        return self._list(f'{self.h}/?type={tid}&p={pg}', pg)

    def searchContent(self, key, quick, pg=1):
        return self._list(f"{self.h}/?search2=ndafeoafa&search={quote(key)}", pg)

    def detailContent(self, ids):
        try:
            url = ids[0] if ids[0].startswith('http') else self.h + ids[0]
            t = self.fetch(url, headers=self.header).text
            tit = re.search(r'<title>(.*?) -', t).group(1).strip()
            pic = re.search(r'video_img".*?alt="([^"]+)"', t)
            if not pic: pic = re.search(r'lazyload"\s+src="([^"]+)"', t)
            return {'list': [{
                'vod_id': ids[0], 'vod_name': tit, 'vod_pic': pic.group(1) if pic else "",
                'vod_play_from': "黄色仓库", 'vod_play_url': f"直接播放${url}"
            }]}
        except: return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        try:
            t = self.fetch(id, headers=self.header).text
            m = re.search(r'id="video_img".*?src="([^"]+)"', t)
            if m:
                return {'parse': 0, 'url': m.group(1), 'header': self.header}
            return {'parse': 1, 'url': id}
        except: return {'parse': 1, 'url': id}

    def _list(self, url, pg=1):
        try:
            t = self.fetch(url, headers=self.header).text
            v = []
            p = r'stui-vodlist__thumb.*?href="([^"]+)".*?data-original="([^"]+)".*?text-right">([^<]+)</span>.*?title="([^"]+)"'
            for h, img, r, tit in re.findall(p, t, re.S):
                v.append({
                    'vod_id': h, 'vod_name': tit,
                    'vod_pic': img if img.startswith('http') else self.h + img,
                    'vod_remarks': r.strip()
                })
            return {'list': v, 'page': pg}
        except: return {'list': []}
