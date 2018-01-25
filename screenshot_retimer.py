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
import argparse
from shutil import which

start_time = timeit.default_timer()

parser = argparse.ArgumentParser(description='Correct the file creation and modified time on FFXIV screenshots exported from the PS4.')
parser.add_argument('directory', help='Path to the directory containing the images.')
parser.add_argument('-e', '--execute', action='store_true', help='Modifiy the files.')
parser.add_argument('-r', '--rename', action='store_true', help='Rename the files to First Last YYYYMMDD_HHMMSS.')
parser.add_argument('-v', '--verbose', action='store_true', help='Display additional logging.')
parser.add_argument('-c', '--creation_time', action='store_true', help='Use the macOS SetFile command to also set file creation time. It\'s slow!!')

args = parser.parse_args()



def correct_file_time(filename, datetime_string):
    time_struct = time.strptime(datetime_string, '%m/%d/%Y %H:%M:%S')
    seconds_since = int(time.mktime(time_struct))

    full_file_path = path + filename

    os.utime(full_file_path, (seconds_since, seconds_since))

def correct_file_time_setfile(filename, datetime_string):
    full_file_path = path + filename

    os.system('SetFile -dm "{}" {}'.format(datetime_string, full_file_path.replace(' ', '\\ ')))



if args.creation_time:
    if not which('SetFile'):
        print('SetFile flag was used, but SetFile command cannot be found.')
        print('Install Xcode command line tools from https://developer.apple.com')
        exit(1)
    elif args.verbose:
        print('SetFile command found:',which('SetFile'))

path = os.path.expanduser(args.directory)
if args.verbose:
    print('Checking directory {}'.format(path))

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

# invalid_files = []
# for f in files:
#     filename = f[-1]
#     if len(f) != 10:
#         print('Invalid filename: {}'.format(filename))
#         invalid_files.append(filename)
#     elif filename[-3:] not in ['jpg', 'png']:
#         print('Invalid extension: {}'.format(filename))
#         invalid_files.append(filename)
#     else:
#         images.append(f)


# filter out movies or other files
images = [f for f in files if f[8] in ['jpg', 'png']]

# if args.verbose:
#     # print(set([image[9] for image in images]))
#     excluded_files = list(set(dir_list) - set([image[9] for image in images]))
#     if len(excluded_files) > 0:
#         print('The following files were excluded:')
#         for ex in excluded_files:
#             print('--- {}'.format(ex))


if args.verbose:
    print('Adjusting file creation/modification times.')

for i in images:
    [first, last, month, day, year, hours, minutes, seconds, extension, original_filename] = i

    time_string = '{}/{}/{} {}:{}:{}'.format(month, day, year, hours, minutes, seconds)
    time_string_sane = '{}/{}/{} {}:{}:{}'.format(year, month, day, hours, minutes, seconds)
    new_filename = '{} {} {}{}{}_{}{}{}.{}'.format(first, last, year, month, day, hours, minutes, seconds, extension)
    
    if args.verbose:
        print('\'{}\''.format(original_filename))
        print('\tRetiming to {}{}'.format(time_string_sane, '\n' if not args.rename else ''))
    
    if args.execute:
        if args.creation_time:
            correct_file_time_setfile(original_filename, time_string)
        else:
            correct_file_time(original_filename, time_string)

    if args.rename:
        if args.verbose:
            print('\tRenaming to \'{}\'\n'.format(new_filename))
        if args.execute:
            os.rename(path + original_filename, path + new_filename)

end_time = timeit.default_timer()
print('Completed in {0} seconds.\n'.format(round(end_time-start_time,2)))
print('{} files {} {}{}.'.format(len(images), 'were' if args.execute else 'will be', 'renamed and retimed' if args.rename else 'retimed', ' using SetFile' if args.creation_time else ''))

if not args.execute:
    print('DRY RUN COMPLETE. No files were modified. Run command with -e flag to execute.')
