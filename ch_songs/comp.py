#!/usr/bin/env python
import os
import sys
from pprint import pprint
from datetime import datetime

import requests
import pandas as pd

#
# Download latest file
#
key =  '1AmYYhYd8iNhZG683LnOARKvCx9Anq3DeEKRmXss-Ync'
doc = f'https://docs.google.com/spreadsheet/ccc?key={key}&output=csv'

now = datetime.now()
day   = now.day   if now.day   >= 10 else f'0{now.day}'
month = now.month if now.month >= 10 else f'0{now.month}'
curr_file = f'song_list_{now.year}_{month}_{day}.csv'

resp = requests.get(doc)
resp.raise_for_status()
with open(curr_file, 'wb') as f:
    f.write(resp.content)

#
# Get previous file
#
try:
    prev_file = sys.argv[1]
except IndexError:
    prev_file = sorted([f for f in os.listdir('/home/james/git/misc/ch_songs') if f.startswith('song_list')])[-2]

#
# Do pandas things
#
cols = ['Artist', 'Song Name', 'Author of Custom (CLICK HERE TO FIND THE FILES)']

max_rows = 999
max_cols = 999

pd.options.display.max_rows = max_rows
pd.options.display.max_columns = max_cols

pd.options.display.max_colwidth = None
pd.options.display.expand_frame_repr = False

#try:
#    prev_file = sys.argv[1]
#    curr_file = sys.argv[2]
#except IndexError:
#    print("ERROR")
#    print("Usage: comp.py prev.csv curr.csv")
#    sys.exit(1)


prev = pd.read_csv(prev_file)
curr = pd.read_csv(curr_file)

m = curr.merge(prev, on=cols, how='left', indicator=True)

diff = m[m['_merge'] == 'left_only']

if len(diff) > max_rows:
    print('WARNING: not all rows will be displayed')
if len(diff.columns) > max_cols:
    print('WARNING: not all columns will be displayed')


if len(diff) > 0:
    print(f'\033[32m{len(diff)} new songs:\033[0m')
    print(diff[cols[:2]])
    #print(repr(diff[cols[:2]]))
else:
    print(f'\033[31mNo new songs.\033[0m')
