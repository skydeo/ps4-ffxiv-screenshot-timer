'''
['Xander', 'Barabroda', '06', '18', '2017', '13', '37', '51', 'jpg']
0 = First name
1 = Last name
2 = Month
3 = Day
4 = Year
5 = Hour
6 = Minute
7 = Second
8 = extension
'''

import os
import re
import time
import timeit

start_time = timeit.default_timer()

verbose = True

def correct_file_time(filename, time_string):
    time_struct = time.strptime(time_string, '%Y %m %d %H %M %S')
    seconds_since = int(time.mktime(time_struct))

    full_file_path = path + filename

    os.utime(full_file_path, (seconds_since, seconds_since))

path = '~/Desktop/PS4/SHARE/Screenshots/FINAL FANTASY XIV/'

path = os.path.expanduser(path)

dir_list = os.scandir(path)

files = []
for item in dir_list:
    if item.is_file() and not item.name.startswith('.'):
        files.append(re.split(' |_|\.',item.name) + [item.name])

invalid_files = False
for f in files:
    if len(f) != 10:
        if not invalid_files:
            print('Filename pattern changed. Code needs correcting. Exiting without modifying files.')
            print('Filenames should be in format: \'First Last MM_DD_YYYY HH_MM_SS.jpg\'.')
            invalid_files = True
        print('Invalid filename: {}'.format(f[-1]))

if invalid_files:
    exit(1)

# filter out movies or other files
images = [f for f in files if (f[8] == 'jpg' or f[8] == 'png')]

for i in images:
    time_string = i[4] + ' ' + i[2] + ' ' + i[3] + ' ' + i[5] + ' ' + i[6] + ' ' + i[7]
    filename = i[-1]

    correct_file_time(filename, time_string)

    # new_filename = i[0] + ' ' + i[1] + ' ' + time_string.replace(' ','') + '.' + i[8]

    # os.rename(path + filename, path + new_filename)

end_time = timeit.default_timer()
print('Completed in {0} seconds.'.format(round(end_time-start_time,2)))
