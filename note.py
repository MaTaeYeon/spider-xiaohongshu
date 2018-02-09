# coding=UTF-8
from bs4 import BeautifulSoup
import urllib.request
from urllib import request
import re
from selenium import webdriver
import time
import csv
from fake_useragent import UserAgent
import json
import random

#获取文章链接
def get_note_url_list(urls):
    driver = webdriver.PhantomJS()
    for url in urls :
        driver.get('http://www.xiaohongshu.com/user/profile/' + url)
        #获取条目数量
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        num = soup.select('div[class="tab-item active owl-imp-showed"] div small')
        if num == []:
            num = soup.select('div[class="tab-item active"] div small')
        try:
            num = num[0].string[1:]
            page = int(num) // 10 + 3
        except:
            page = 10
        # 将页面滚动条拖到底部
        js = "document.documentElement.scrollTop=1000000"
        for s in range(0, page):
            driver.execute_script(js)
            time.sleep(3)
        # 解析链接
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        url_list = soup.select('div[class="note-item note-item"] a')
        url_list = url_list + soup.select('div[class="note-item note-item owl-imp-showed"] a')
        for url in url_list:
            note_url = url.get('href')
            if note_url[:10] == '/discovery':
                print(note_url)
                get_note('https://www.xiaohongshu.com' + note_url)
    driver.close()

#获取文章内容
def get_note(url):
    try:
        req = request.Request(url)
        response = urllib.request.urlopen(req)
    except :
        try :
            req = request.Request(url)
            response = urllib.request.urlopen(req)
        except :
            return

    # 读取Html
    data = response.read()
    soup = BeautifulSoup(data, 'html.parser', from_encoding="UTF-8")

    try:
        nickname = soup.select('h3[class="nickname"] a')[0].string #昵称
    except:
        nickname = ''
    try:
        avatar = soup.select('img[class="avatar-img"]')[0].get('src') #头像
    except:
        avatar = ''
    try:
        title = soup.select('h1[class="title"]')[0].string #标题
        print(title)
        time.sleep(16)
        title = str(title).encode('utf-8', 'ignore').decode('utf-8', 'ignore')
    except:
        title = ''
    publish_date = soup.select('div[class="publish-date"]')[0].string[4:] #发布时间
    tags = soup.select('a[class="hash-tag topic"]') #标签
    if tags != []:
        tag_list = []
        for tag in tags:
            tag = str(tag)
            svg = tag.index('</svg>')
            a = tag.index('</a>')
            tag_list.append(tag[svg+6:a])
        tag_str = ','.join(tag_list)
    else:
        tag_str = ''

    try :
        cover = soup.select('div[class="multi-note-cover cube-image normal-image"] img')[0].get('src') #封面图
    except:
        cover = ''

    #轮播图
    note_img = soup.select('img[class="note-image"]')  # 图片
    img_list = ''
    for img in note_img:
        img_list = img_list + ',' + img.get('src')
    img_list = img_list[1:]

    #如果cover不存在用轮播图补全
    try :
        if cover == '':
            cover = note_img[0].get('src')
    except:
        cover = ''

    # 富文本
    content_list = soup.select('div[class="content"]')
    content_str = ''
    dr_a = re.compile(r'<a.*?href="(.*?)">(.*?)</a>', re.S)#去除标签的超链接
    for content in content_list:
        content = str(content).replace(' data-v-57ee69ec=""', '').replace(' data-v-798decb0=""', '').replace(' alt="小红书"', '').replace(' data-v-52254b4c=""', '').replace(' data-v-4b7a01f4="" ', '').replace(' data-v-0ffb6d22=""', '').replace(u"\u200b", '').replace(u"\u2022", '')
        content = re.sub('[\r\n\t]', '', content)
        content = dr_a.sub('', str(content))
        content_str = content_str + content
    try:
        index = content_str.index('<div class="cell item-cell">')
    except:
        index = 0
    if index > 0:
        content_str = content_str[:index] + '</div>'

    # 写入CSV
    if cover != '':
        with open('note.csv', 'a+', newline ='',encoding='gb18030') as csvfile:
            spamwriter = csv.writer(csvfile)
            data = ([str(nickname), str(avatar), str(title), str(cover), str(img_list), str(content_str), str(tag_str), str(publish_date), str(url)])
            spamwriter.writerow(data)

#代理获取
def proxy_get():
    url = 'http://127.0.0.1:8000/select?name=httpbin&order=speed&sort=asc&count=20'
    req = request.Request(url)
    response = urllib.request.urlopen(req)
    data = response.read()
    try:
        json_str = json.loads(data)
        proxy =  random.sample(json_str, 1)
    except:
        req = request.Request(url)
        response = urllib.request.urlopen(req)
        data = response.read()
        json_str = json.loads(data)
        proxy = random.sample(json_str, 1)
    return proxy[0]

#m站个人主页的地址
get_note_url_list([
    '554d98baa46e9626b84ebe39',
    '57367ccf50c4b4528a90f723',
    '54b0f079b4c4d65f85e76bdc',
    '5756621a82ec39663c40c45d',
    '59a65a295e87e75966563793',
    '561f967641a2b3550b12fd4c',
    '54f697fb4fac6379b6f3bc95',
    '596c805750c4b4218d929a59',
                  ])
