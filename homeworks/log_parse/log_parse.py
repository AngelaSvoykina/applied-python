# -*- encoding: utf-8 -*-
import re
import math
import datetime
from collections import Counter


def parse(
        ignore_files=False,
        ignore_urls=[],
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
):
    urls_data = []

    if start_at:
        start_at = datetime.datetime.strptime(start_at, '%d/%b/%Y %H:%M:%S')

    if stop_at:
        stop_at = datetime.datetime.strptime(stop_at, '%d/%b/%Y %H:%M:%S')

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

        if start_at is not None:
            url_date = datetime.datetime.strptime(match.group(1), '%d/%b/%Y %H:%M:%S')

            if start_at > url_date:
                continue
            else:
                start_at = None

        if stop_at is not None:
            url_date = datetime.datetime.strptime(match.group(1), '%d/%b/%Y %H:%M:%S')

            if stop_at < url_date:
                break

        if len(ignore_urls) > 0 and match.group(5) in ignore_urls:
            continue

        if ignore_files and re.match(extreg, match.group(5)):
            continue

        if request_type is not None and match.group(2) == request_type:
            urls_data.append([match.group(5)])
        else:
            urls_data.append([match.group(5)])

        if slow_queries:
            urls_data[-1].append(int(match.group(8)))

    if slow_queries:
        slowest = sorted(urls_data, key=lambda x: x[1], reverse=True)[:5]
        slowest = [[slow_el[0], sum(el[1] for el in urls_data if el[0] == slow_el[0])] for slow_el in slowest]
        urls_cnt = Counter(el[0] for el in urls_data)

        slowest = [math.floor(el[1]/urls_cnt[el[0]]) for el in slowest]
        result = sorted(slowest, reverse=True)
    else:
        urls_cnt = Counter(el[0] for el in urls_data)

        urls_list = urls_cnt.most_common(5)
        urls_list = [el[1] for el in urls_list]

        result = urls_list

    return result


def main():
    parse(slow_queries=True)


if __name__ == '__main__':
    main()