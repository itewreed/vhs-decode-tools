#!/usr/bin/env python3

import sys

line_bytes = 1135 * 2
field_lines = 313
field_range = range(6, 22)


with open(sys.argv[1], 'rb') as infile:
    with open(sys.argv[2], 'wb') as outfile:
        while True:
            for l in range(field_lines):
                if l in field_range:
                    b = infile.read(line_bytes)
                    if len(b) < line_bytes:
                        exit(0)
                    outfile.write(b)
                else:
                    infile.seek(line_bytes, 1)
