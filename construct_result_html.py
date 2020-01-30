# !/usr/bin/env python
# coding:utf-8

import os
from pyquery import PyQuery as pq


def construct_result_html(records, output_file_name):
    html = '''
    <html><body><table></table></body></html>
    '''
    tr = '<tr></tr>'
    td = '<td></td>'
    a = '<a></a>'

    doc = pq(html, parser="html")

    doc('body').addClass('myclass')
    doc('table').attr('ss', 'dd')
    # print(doc)

    # 构建表头
    count_record = 0
    doc('table').append(tr)
    for key in ['category', 'title', 'rate', 'time', 'size', 'seeders', 'leechers', 'completed', 'author', 'progress']:
        doc('tr:last').append(td)
        doc('td:last').append(key)

    for record in records:
        count_record += 1
        if count_record > 10000:
            break
        # print(count_record, line)

        doc('table').append(tr)
        count_item = 0
        for key in ['category', 'title', 'rate', 'time', 'size', 'seeders', 'leechers', 'completed', 'author', 'progress']:
            count_item += 1
            # print(record[key])
            # 记录的值可能是含<td>标签的html代码，因此需要用table包含
            table = pq('<table><tbody><tr><td></td></tr></tbody></table>', parser='html')
            table('td:last').append(str(record[key]))
            test = doc('table>tr:last')
            doc('table>tr:last').append(td).append(table)
            '''if count_item == 9:
                doc('td:last').append(a)
                doc('a:last').append(record[key])
            else:
                doc('td:last').append('<span></span>')
                doc('span:last').append(str(record[key]))
            '''
        # doc('a:last').attr('href', line[9])
        # doc('a:last').attr('target', '_blank')
        # print(doc.html())

        if not (count_record % 100):
            print(count_record)

    with open(output_file_name, 'w', encoding='utf-8-sig') as f:
        f.write(doc.html())

