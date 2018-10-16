# -*- encoding: utf-8 -*-


def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
   import re
   import numpy
   import collections
   from collections import Counter
   slow_queries = True
   urls = []
   slow = []
   reg = r"^\[(.*)] \"([\S]*) ([\S]*) ([\S]*)\" ([\S]*) ([\S]*)"
   reg = re.compile(reg)
   for line in (open('777.txt')):
     for match in re.finditer(reg, line):
         if match.group not in ignore_urls:
           urls.append(match.group(3))
         if slow_queries == True:
           slow.append(int(match.group(6)))
          
   cnt = Counter(urls)
   urls1 = cnt.most_common(5)
   numpy.mean(slow.most_common()[:-5:-1])




   print(urls1)
   #print(slow)
   return urls1
   return slow

def main():
    parse()

if name == '__main__':
    main()