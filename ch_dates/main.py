#!/usr/bin/env python

# Outputs information parsed from Clone Hero screenshot filenames.
#
# A clone hero "session" is defined as the length of time between the ends of
# the first and last songs played on a given day. This has some implications:
# - A session requires at least 2 songs
# - A user who played clone hero more than once in a day (say in the morning
#   and later the evening) will notice higher than expected session times.
# - The length of the first song is not included in session time.

import os
import re
import operator
from functools import reduce
from datetime import datetime

screenshot_dir = '/home/james/.config/Clone Hero Launcher/gameFiles/Screenshots'

# format that clonehero uses when it saves screenshots
filename_date_fmt = '%Y%m%d%H%M%S'

# will be used to populate a dictionary's keys
day_fmt = '%Y%m%d'

# month strings
ms = {1: 'Jan', 2: 'Feb', 3: 'Mar',
      4: 'Apr', 5: 'May', 6: 'Jun',
      7: 'Jul', 8: 'Aug', 9: 'Sep',
      10: 'Oct', 11: 'Nov', 12: 'Dec'}


# Parses @filename and adds data to @results
def process(filename, results):
    date_str = re.search(r'[0-9]+.png', filename)[0].rstrip('.png')
    date = datetime.strptime(date_str, filename_date_fmt)

    # Convert date+timestamp to just year+month+day for use as a key
    day_obj = datetime.strptime(date.strftime(day_fmt), day_fmt)

    try:
        results[day_obj].append(date)
    except KeyError:
        results[day_obj] = [date]


# Returns a subset of the input results (basically "filter" for dicts)
def segment(results, fn):
    return {k:v for k,v in results.items() if fn(k)}


def get_years(results):
    return sorted(list({k.year for k in results}))


def get_months(results):
    return sorted(list({(k.year, k.month) for k in results}))


def analyze(results, title):
    lengths = []
    song_counts = []

    for day, times in results.items():
        if len(times) <= 1: # can't determine session length with only 1 timestamp
            continue

        times = sorted(times) # earliest time at front, latest at back

        length = times[-1] - times[0]
        assert type(length) != int
        num_songs = len(times)

        lengths.append(length)
        song_counts.append(num_songs)

    total_time = reduce(operator.add, lengths)
    avg_len = total_time/len(lengths)
    avg_count = round(sum(song_counts)/len(song_counts), 2)

    print(f'\033[35m{title}\033[0m ({len(lengths)} sessions)')
    print(f'Total hours played: \033[32m{int(total_time.total_seconds()/3600)}\033[0m')
    print(f'Avg session length: \033[32m{avg_len}\033[0m')
    print(f'Avg # songs:        \033[32m{avg_count}\033[0m')
    print()


def main():
    # keys will be datetime objects, values will be list of datetime objects
    results = {}

    #
    # Get dates and times from all files
    #
    for loc, _, files in os.walk(screenshot_dir):
        if loc != screenshot_dir:
            continue # no recursive search

        for filename in files:
            process(filename, results)

    #
    # Analyze results
    #
    print('-' * 40)
    analyze(results, 'Overall')
    
    print('-' * 40)
    for year in get_years(results):
        analyze(segment(results, lambda x: x.year == year), str(year))

    print('-' * 40)
    for year, month in get_months(results):
        title = f'{ms[month]} {year}'
        analyze(segment(results, lambda x: x.year == year and x.month == month), title)


if __name__ == '__main__':
    main()
