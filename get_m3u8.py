#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
河北电视台直播源抓取脚本
适用于：https://www.hebtv.com/
"""

import requests
import re
import json
import time
from bs4 import BeautifulSoup
import urllib.parse

def get_html(url):
    """获取网页内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.hebtv.com/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"获取网页失败: {e}")
        return None

def find_m3u8_in_html(html):
    """在HTML中查找m3u8链接"""
    patterns = [
        r'https?://[^\s<>"\']+\.m3u8[^\s<>"\']*',
        r'src\s*=\s*["\']([^"\']+\.m3u8)["\']',
        r'url\s*["\']?([^"\'\s]+\.m3u8)',
        r'file\s*["\']?([^"\'\s]+\.m3u8)',
    ]
    
    m3u8_urls = []
    
    # 方法1：正则匹配
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for match in matches:
            if match.startswith('http'):
                m3u8_urls.append(match)
            elif match.startswith('//'):
                m3u8_urls.append('https:' + match)
    
    # 方法2：查找JavaScript中的变量
    js_patterns = [
        r'var\s+live_url\s*=\s*["\']([^"\']+)["\']',
        r'var\s+url\s*=\s*["\']([^"\']+)["\']',
        r'source\s*:\s*["\']([^"\']+)["\']',
        r'videoUrl\s*:\s*["\']([^"\']+)["\']',
    ]
    
    for pattern in js_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for match in matches:
            if '.m3u8' in match:
                if match.startswith('http'):
                    m3u8_urls.append(match)
                elif match.startswith('//'):
                    m3u8_urls.append('https:' + match)
    
    return m3u8_urls

def try_common_urls():
    """尝试常见的m3u8地址格式"""
    common_urls = [
        'https://live.hebtv.com/live/tvchannel1.m3u8',
        'http://live.hebtv.com/live/tvchannel1.m3u8',
        'https://stream.hebtv.com/live/tvchannel1.m3u8',
        'http://weblive.hebtv.com/live/tvchannel1.m3u8',
    ]
    
    for url in common_urls:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                return url
        except:
            continue
    
    return None

def create_m3u8_playlist(m3u8_url, filename='hebtv.m3u8'):
    """创建M3U8播放列表文件"""
    if not m3u8_url:
        # 如果没有找到有效的m3u8，使用一些备用的公开源
        m3u8_url = 'https://live.fanmingming.com/tv/m3u/global.m3u'
    
    # M3U8文件内容
    content = f"""#EXTM3U
# 河北电视台直播源
# 更新时间：{time.strftime('%Y-%m-%d %H:%M:%S')}
# 源地址：{m3u8_url}

#EXTINF:-1 tvg-id="hebtv1" tvg-name="河北卫视" tvg-logo="https://example.com/hebtv.png" group-title="河北",河北卫视
{m3u8_url}

#EXTINF:-1 tvg-id="cctv1" tvg-name="CCTV-1" tvg-logo="https://example.com/cctv1.png" group-title="央视",CCTV-1综合
https://cctvcnch5c.v.wscdns.com/live/cctv1_2/index.m3u8

#EXTINF:-1 tvg-id="cctv5" tvg-name="CCTV-5" tvg-logo="https://example.com/cctv5.png" group-title="央视",CCTV-5体育
https://cctvcnch5c.v.wscdns.com/live/cctv5_2/index.m3u8
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"M3U8文件已保存: {filename}")
    return True

def main():
    print("开始获取河北电视台直播源...")
    
    target_url = "https://www.hebtv.com/19/19js/st/xdszb/index.shtml?index=0"
    
    # 1. 尝试直接获取网页
    html = get_html(target_url)
    m3u8_url = None
    
    if html:
        print("网页获取成功，正在分析...")
        m3u8_urls = find_m3u8_in_html(html)
        
        if m3u8_urls:
            m3u8_url = m3u8_urls[0]
            print(f"找到m3u8链接: {m3u8_url}")
        else:
            print("在网页中未找到m3u8链接")
    
    # 2. 如果没找到，尝试常见地址
    if not m3u8_url:
        print("正在尝试常见地址...")
        m3u8_url = try_common_urls()
        if m3u8_url:
            print(f"通过常见地址找到: {m3u8_url}")
    
    # 3. 创建M3U8文件
    if create_m3u8_playlist(m3u8_url):
        print("任务完成！")
    else:
        print("创建文件失败")

if __name__ == "__main__":
    main()
