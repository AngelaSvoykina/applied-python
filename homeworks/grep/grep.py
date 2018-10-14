import argparse
import sys
from collections import deque
import re


def output(line):
    print(line)


def grep(lines, params):
    N = params.context
    B = N
    A = N

    if params.before_context > 0:
        B = params.before_context
    if params.after_context > 0:
        A = params.after_context

    pattern_buf = params.pattern

    if params.ignore_case:
        pattern_buf = pattern_buf.lower()

    # a.sd*asd? -> a\.sd.*asd.
    pattern_buf = pattern_buf.replace('.', '\.')
    pattern_buf = pattern_buf.replace('?', '.')
    pattern_buf = pattern_buf.replace('*', '.*')

    pattern_buf = re.compile(pattern_buf)

    # Deque размера B
    out_lines = deque(maxlen=B)

    num_lines = 0
    print_until_line = 0
    last_printed_line = -1

    for i, line in enumerate(lines):

        line_buf = line.rstrip()

        if params.ignore_case:
            line_buf = line_buf.lower()

        is_match = pattern_buf.search(line_buf)

        if params.invert:
            is_match = not is_match

        if is_match:
            num_lines += 1

            if not params.count:
                if B != 0:
                    if (i - last_printed_line - 1) == 0:
                        deque_i = B
                    elif (i - last_printed_line - 1) >= B:
                        deque_i = 0
                    else:
                        deque_i = i - last_printed_line - 1

                    # Ouput lines from deck correspondingly to already printed
                    for k in range(deque_i, B):
                        num_lines += 1

                        if params.line_number:
                            output(str(i - B + k + 1) + '-' + out_lines[k])
                        else:
                            output(out_lines[k])

                if params.line_number:
                    output(str(i + 1) + ':' + line)
                else:
                    output(line)

                # update printed lines
                print_until_line = i + A + 1
                last_printed_line = i

        elif i < print_until_line:
            num_lines += 1

            if not params.count:
                if params.line_number:
                    output(str(i + 1) + '-' + line)
                else:
                    output(line)

            last_printed_line = i

        out_lines.append(line)

    if params.count:
        output(str(num_lines))


def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v',
        action="store_true",
        dest="invert",
        default=False,
        help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
