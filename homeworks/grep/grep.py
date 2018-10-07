import argparse
import sys
import re


def output(line):
    print(line)


def grep(lines, params):
    outLines = []

    for i, line in enumerate(lines):
        pattern_buf = params.pattern
        line_buf = line.rstrip()

        
        if params.ignore_case == True:
            pattern_buf = pattern_buf.lower()
            line_buf = line_buf.lower()

        # a.sd*asd? -> a\.sd.*asd.
        pattern_buf = pattern_buf.replace('.', '\.')
        pattern_buf = pattern_buf.replace('?','.')
        pattern_buf = pattern_buf.replace('*', '.*')
        if re.search(pattern_buf, line_buf):
            outLines.append(i)

    
    N = params.context
    B = N
    A = N

    if params.before_context > 0:
        B = params.before_context
    if params.after_context > 0:
        A = params.after_context
    temp = []                
    for i in outLines:
        for j in range(i - B, i + A + 1):
            if j >= 0 and j < len(lines) and (len(temp) == 0 or j > temp[-1]):
                temp.append(j)

    originLines = outLines
    outLines = temp

    if params.invert == True:
        outLines = [i for i in range(0, len(lines)) if i not in outLines]

    if params.count == True:
        output(str(len(outLines)))
    else:
        for i in outLines:
            if params.line_number == True:
                if i in originLines:
                    output(str(i+1)+':'+lines[i])
                else:
                    output(str(i+1)+'-'+lines[i])
            else:
                output(lines[i])




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