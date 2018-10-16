# -*- encoding: utf-8 -*-
import re
import numpy
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

    if not ignore_www:
        reg = r"^\[(.*)] \"([\S]*) ()()([\S]*) ([\S]*)\" ([\S]*) ([\S]*)"
    else:
        reg = r"^\[(.*)] \"([\S]*) (https?://)(www\.)?([\S]*) ([\S]*)\" ([\S]*) ([\S]*)"

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

        if len(ignore_urls) > 0:
            if match.group(5) in ignore_urls:
                continue

        # TODO: Всегда добавлять в tuple
        if request_type is not None:
            if match.group(2) == request_type:
                urls_data.append(match.group(5))
        else:
            urls_data.append(match.group(5))

        # TODO: Во второй (1-й) элемент tuple записывать
        if slow_queries:
            urls_data.append(int(match.group(8)))

    # if len(ignore_urls) > 0:
    #     urls_data = list(filter(lambda x: x not in ignore_urls, urls_data))

    if slow_queries:
        slow_cnt = Counter(urls_data)

        print(sorted(urls_data))

        result = math.floor(numpy.mean(slow_cnt.most_common()[:-5:-1]))
    else:
        urls_cnt = Counter(urls_data)

        urls_list = urls_cnt.most_common(5)
        urls_list = [el[1] for el in urls_list]

        result = urls_list

    print(result)
    return result


def main():
    parse(slow_queries=True)


if __name__ == '__main__':
    main()