#!/usr/bin/env python
# _*_ coding:utf-8 _*_
#!/usr/bin/python
import string
import re
with open('lagou_backup.json', 'rb') as old_file:
    with open('lagou.json', 'br+') as new_file:
        for x in old_file:
            t = []
            term = ['python', '算法', '深度学习', '机器学习', '数据挖掘', 'R语言']
#            if "大数据" in x.decode('utf-8') or "java" in x.decode('utf-8'):
            if any(t in x.decode('utf-8') for t in term):
                line = x.replace(b'[', b'').replace(b']', b'').replace(b'/', b'').replace(b'""', b'"None"').replace(b' ', b'')
                new_file.write(line)
                continue

#            new_file.close()

