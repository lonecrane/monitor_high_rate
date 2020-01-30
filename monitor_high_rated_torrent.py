# coding:utf-8
# 根据电影名称和年份到PT站上查询种子
# 2020/01/30 未被任何标签包含的文本无法用.text()方法取到。可先__html__()方法得到所有源代码，再次用pq解析
import os
import time
import re
import json
from selenium import webdriver
from pyquery import PyQuery as pq
from construct_result_html import construct_result_html

DEGUG_RECORD_LIMIT = 1000

output_file_path = r".\\"
output_file_name = "record_arranged.html"
output_file_name = output_file_path + os.sep + output_file_name
# print(output_file_name)


def getFieldValue(row, cells, fieldIndex, fieldName, returnCell=False):
    parent = row
    cell = None
    if cells and fieldName in fieldIndex and fieldIndex[fieldName] != -1:
        # print(fieldIndex[fieldName])
        cell = cells.eq(fieldIndex[fieldName])
        # print(cell)
        parent = cell or row

    # 将所有相对链接替换为绝对链接
    if cell:
        a_href = cell('a[href]')
        for i in range(a_href.size()):
            # print(a_href.eq(i))
            href = a_href.eq(i).attr('href')
            # print('\t', href)

            # 排除javascript:
            if re.match(r'^javascript:', href):
                continue

            # 替换相对链接
            if re.match(r'^https*://', href):
                continue
            href_new = site['domain'] + href
            a_href.eq(i).attr('href', href_new)

    result = None
    if cell:
        if returnCell:
            return cell.__html__()  # 直接返回html td元素

        # print(cell.remove('br').text())
        result = cell.remove('br').text()
        if not result:
            return cell.__html__()  # 直接返回html td元素
    return result


def getIMDBrate(cell):
    result = None
    # img的class/title/source含有imdb即可认定是评分所在的td
    # 寻找imdb的img元素
    # ttg: <span class="imdb_rate"><a href="https://www.imdb.com/title/tt6193408/">7.0</a></span>
    # ourbits: <label class="imdb_rate" style="padding-left: 25px;font-style: normal;" data-imdbid="9625664">5.0</label>
    imdb = cell('.imdb_rate')   # ttg
    # hdchina: <a class="imdb" title="IMDB评分" href="retriver.php?id=377393&amp;type=1&amp;siteid=1"><em class="t icon_t i_imdb"></em>7.5</a>
    if not imdb:
        imdb = cell('a.imdb')   # hdchina
    # CMCT:     <a href="https://www.imdb.com/title/tt10584272/" target="_blank"><img class="imdb" src="pic/trans.gif" style="vertical-align: text-bottom;" alt="imdb" title="IMDb评分"> <span style="font-size: 8pt">6.4</span></a>
    # MT: <a href="http://www.imdb.com/title/tt08380776/">4.6</a>
    if not imdb:
        imdb = cell('a[href*="imdb"]')   # cmct, mt
    if not imdb:
        imdb = cell('img[src*="imdb"]')   # chdbits
    if not imdb:
        return None
    print(imdb)

    # 取img元素所在的td元素
    # 取td元素的文字
    # imdb = pq(imdb.__html__(), parser="html")  # 这一步将在self-closing标签的外面自动加上<span></span>，否则.text()方法取不到未被任何标签包含的文本
    imdb.wrap('<span>')
    result = imdb.text()
    # print(result)
    if not result:
        return None

    # 转换为数字
    try:
        result = float(result)
    except ValueError:
        return None
    except Exception as e:
        print(e.__class__, e)
        return None

    return result

'''
site_dict = {
    "chdbits": {"name": "chdbits",
                "check": True,
                "selector": "table.torrents:last",
                "domain": "https://chdbits.co/",
                "url_torrents": "https://chdbits.co/torrents.php",
                "url_search": ["https://chdbits.co/torrents.php?search=", "&notnewword=1"]},
    "cmct": {"name": "cmct",
             "check": True,
             "selector": "table.torrents:last",
             "domain": "https://springsunday.net/",
             "url_torrents": "https://springsunday.net/torrents.php",
             "url_search": ["https://springsunday.net/torrents.php?incldead=1&spstate=0&pick=0&inclbookmarked=0&search=",
                            "&search_area=0&search_mode=0"]},
    "hdchina": {"name": "hdchina",
                "check": True,
                "selector": "table.torrent_list:last",
                "domain": "https://hdchina.org/",
                "url_torrents": "https://hdchina.org/torrents.php",
                "url_search": ["https://hdchina.org/torrents.php?incldead=1&spstate=0&inclbookmarked=0&boardid=3&seeders=&search=",
                    "&search_area=0&search_mode=0"]},
    "hdsky": {"name": "hdsky",
              "check": True,
              "selector": "table.torrents",
              "domain": "https://hdsky.me/",
              "url_torrents": "https://hdsky.me/torrents.php",
              "url_search": ["https://hdsky.me/torrents.php?incldead=1&spstate=0&inclbookmarked=0&search=",
                             "&search_area=0&search_mode=0"]},
    "ttg": {"name": "ttg",
            "check": True,
            "selector": "table#torrent_table",
            "domain": "https://totheglory.im/",
            "url_torrents": "https://totheglory.im/browse.php?c=M",
            "url_search": ["https://totheglory.im/browse.php?search_field=", "&c=M"]},
    "mt": {"name": "mt",
           "check": True,
           "selector": "table.torrents",
           "domain": "https://pt.m-team.cc/",
           "url_torrents": "https://pt.m-team.cc/movie.php",
           "url_search": ["https://pt.m-team.cc/movie.php?incldead=1&spstate=0&inclbookmarked=0&search=",
                          "&search_area=0&search_mode=0"]},
    "ourbits": {"name": "ourbits",
                "check": True,
                "selector": "table.torrents",
                "domain": "https://ourbits.club/",
                "url_torrents": "https://ourbits.club/torrents.php",
                "url_search": ["https://ourbits.club/torrents.php?incldead=1&spstate=0&inclbookmarked=0&search=",
                               "&search_area=0&search_mode=0"]},
    "hdhome": {"name": "hdhome",
               "check": False,
               "selector": "table.torrents",
               "domain": "http://hdhome.org/",
               "url_torrents": "http://hdhome.org/torrents.php",
               "url_search": ["https://hdhome.org/torrents.php?incldead=1&spstate=0&inclbookmarked=0&search=",
                              "&search_area=0&search_mode=0"]},
    "gztown": {"name": "gztown",
               "check": False,
               "selector": "table.torrents",
               "domain": "https://discfan.net/",
               "url_torrents": "https://discfan.net/torrents.php",
               "url_search": ["https://discfan.net/torrents.php?incldead=1&spstate=0&inclbookmarked=0&search=",
                              "&search_area=0&search_mode=0"]}
}
with open('site_dict.json', 'w') as f:
    json.dump(site_dict, f)
'''
with open('site_dict.json', 'r') as f:
    site_dict = json.load(f)
# print(json.dumps(site_dict, indent=4))

driverOptions = webdriver.ChromeOptions()
driverOptions.add_argument(r"user-data-dir=C:\Users\yellow\AppData\Local\Google\Chrome\User Data")
use_local_file = True
site = site_dict['cmct']
site = site_dict['chdbits']
site = site_dict['hdchina']
site = site_dict['hdsky']
site = site_dict['ttg']
# site = site_dict['mt']
# site = site_dict['ourbits']
# site = site_dict['hdhome']
# site = site_dict['gztown']
html = ''
if use_local_file:
    local_file_name = site['name'] + '.html'
    if os.path.exists(local_file_name):
        with open(local_file_name, 'r', encoding='utf-8') as f:
            html = f.read()
if html == '':
    driver = webdriver.Chrome(executable_path=r"D:\Software\chromedriver_win32\chromedriver.exe",
                              options=driverOptions)
    # driver.get("https://www.baidu.com")
    # time.sleep(3)

    driver.get(site['url_torrents'])
    html = driver.page_source
    with open(local_file_name, 'w', encoding='utf-8') as f:
        f.write(html)

doc = pq(html, parser="html")
html2 = doc.__html__()
doc = pq(html2, parser="html")
table = doc(site['selector'])
# print(table)

# 获取种子列表
rows = table(site['selector'] + '> tbody > tr')
if rows.length == 0:
    # return 0
    exit(0)

# 返回结果
results = list()

# 获取表头
header = table(site['selector'] + '> thead > tr > th')
beginRowIndex = 0
if header.length == 0:
    beginRowIndex = 1
    header = rows.eq(0).find("th,td")
# print(header)

fieldIndex = {
    "title": -1,    # 标题
    "time": -1,		# 发布时间
    "size": -1,		# 大小
    "seeders": -1,    # 上传数量
    "leechers": -1,    # 下载数量
    "completed": -1,    # 完成数量
    "comments": -1,    # 评论数量
    "author": header.length - 1,    # 发布人
    "category": -1,    # 分类
    "progress": -1,    # 进度
    "status": -1,    # 状态
    "imdb_rate": -1,    # IMDB评分
    }
# print("header.length = ", header.length)

# 获取字段所在的列
for index in range(header.length):
    cell = header.eq(index)
    text = cell.text()

    # 分类
    if re.match(r'cat|类型|类别|類型|分类|分類|Тип', text):
        fieldIndex['category'] = index
        continue

    # 标题
    if re.match(r'标题|名称|標題', text):
        fieldIndex['title'] = index
        continue

    # 评论数
    if cell.find("img.comments").length:
        fieldIndex['comments'] = index
        continue
    elif re.match(r'评论', text):
        fieldIndex['comments'] = index
        continue

    # 发布时间
    if cell.find("img.time").length:
        fieldIndex['time'] = index
        continue
    elif re.match(r'添加于', text):
        fieldIndex['time'] = index
        continue

    # 大小
    if cell.find("img.size").length:
        fieldIndex['size'] = index
        continue
    elif re.match(r'大小', text):
        fieldIndex['size'] = index
        continue

    # 种子数
    if cell.find("img.seeders").length:
        fieldIndex['seeders'] = index
        continue

    # 下载数
    if cell.find("img.leechers").length:
        fieldIndex['leechers'] = index
        continue

    # 完成数
    if cell.find("img.snatched").length:
        fieldIndex['completed'] = index
        continue
    elif re.match(r'完成', text):
        fieldIndex['completed'] = index
        continue

    # 发布者
    if re.match(r'发布者|上传者', text):
        fieldIndex['author'] = index
        continue

    # 进度
    if re.match(r'进度', text):
        fieldIndex['progress'] = index
        continue

# print(fieldIndex['comments'])
# print(fieldIndex['author'])
# print(fieldIndex['size'])
# print(fieldIndex['category'])
# print(fieldIndex['completed'])
# print(fieldIndex['leechers'])
# print(fieldIndex['seeders'])
# print(fieldIndex['time'])
# print(fieldIndex['progress'])

count = 0
for index in range(beginRowIndex, rows.length):
    if index > DEGUG_RECORD_LIMIT:
        break
    row = rows.eq(index)
    # print(row)
    cells = row.children('td')
    if cells.size == 0:
        exit(1)
    for i in range(cells.size()):
        # print(i, cells.eq(i))
        pass
    # print(cells)

    # title = this.getTitle(row)
    pass

    data = {
        'category': getFieldValue(row, cells, fieldIndex, "category") or "",
        'title': getFieldValue(row, cells, fieldIndex, "title", True) or "",
        'comments': getFieldValue(row, cells, fieldIndex, "comments") or 0,
        'time': getFieldValue(row, cells, fieldIndex, "time"),
        'size': getFieldValue(row, cells, fieldIndex, "size") or 0,
        'seeders': getFieldValue(row, cells, fieldIndex, "seeders") or 0,
        'leechers': getFieldValue(row, cells, fieldIndex, "leechers") or 0,
        'completed': getFieldValue(row, cells, fieldIndex, "completed") or 0,
        'author': getFieldValue(row, cells, fieldIndex, "author") or "",
        'progress': getFieldValue(row, cells, fieldIndex, "progress"),
        'status': getFieldValue(row, cells, fieldIndex, "status") or "",
        'rate': getIMDBrate(cells.eq(fieldIndex["title"])) or "",
    }

    results.append(data)

# print(results)

# 获得指定分数以上的记录
MINI_RATEING = 7.9
records = list()
for record in results:
    if record['rate'] == '':
        continue

    if record['rate'] < MINI_RATEING:
        continue

    records.append(record)

print(len(records))
# print(records)

# 构造结果网页
construct_result_html(records, output_file_name)
exit(0)

# 打开结果网页
driver = webdriver.Chrome(executable_path=r"D:\Software\chromedriver_win32\chromedriver.exe", options=driverOptions)
# time.sleep(3)
driver.get(r'file://' + os.path.abspath(output_file_name))

