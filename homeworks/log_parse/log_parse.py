# -*- encoding: utf-8 -*-
import re
import math
import datetime
from collections import defaultdict


def parse(
        ignore_files=False,
        ignore_urls=[],
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
):
    urls_data = defaultdict(int)
    urls_time = defaultdict(int)

    result = []

    extreg = re.compile(r".*\.([a-zA-Z0-9]*)$")

    if not ignore_www:
        reg = r"^\[(.*)] \"([\S]*) (https?:\/\/)()([\S]*) ([\S]*)\" ([\S]*) ([\S]*)"
    else:
        reg = r"^\[(.*)] \"([\S]*) (https?:\/\/)(www\.)?([\S]*) ([\S]*)\" ([\S]*) ([\S]*)"

    reg = re.compile(reg)
    for line in (open('log.log')):
        match = re.match(reg, line)
        if not match:
            continue

        if start_at is not None or stop_at is not None:
            url_date = datetime.datetime.strptime(match.group(1), '%d/%b/%Y %H:%M:%S')

            if start_at is not None:
                if start_at > url_date:
                    continue
                else:
                    start_at = None

            if stop_at is not None:
                if stop_at < url_date:
                    break

        if len(ignore_urls) > 0 and match.group(5) in ignore_urls:
            continue

        if ignore_files and re.match(extreg, match.group(5)):
            continue

        if request_type is not None:
          if match.group(2) == request_type:
            urls_data[match.group(5)] += 1
        else:
            urls_data[match.group(5)] += 1

        if slow_queries:
            urls_time[match.group(5)] += int(match.group(8))


    if slow_queries:

        slowest = sorted(urls_data, key=lambda url: urls_time[url] / urls_data[url], reverse=True)[:5]
        result = [math.floor(urls_time[x] / urls_data[x]) for x in slowest]
    else:
        
        top = sorted(urls_data, key=lambda url: urls_data[url], reverse=True)[:5]
        result = [urls_data[x] for x in top]

    return result


def main():
    parse()


if __name__ == '__main__':
    main()