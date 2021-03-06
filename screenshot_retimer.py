import os
import re
import time
import timeit
import shutil
from pathlib import Path
from gooey import Gooey, GooeyParser



def retime_ps4_screenshots(input_dir, execute=False, rename=False, setfile=False, verbose=True):
  start_time = timeit.default_timer()
  input_dir = Path(input_dir)


  def create_dir_list(input_dir):
    p = Path(input_dir).iterdir()
    dir_list = [entry for entry in p 
                if entry.is_file()
                and not entry.name.startswith('.')]
    return dir_list


  def correct_file_time(filename, datetime_string):
    time_struct = time.strptime(datetime_string, '%m/%d/%Y %H:%M:%S')
    seconds_since = int(time.mktime(time_struct))
    os.utime(filename, (seconds_since, seconds_since))


  def correct_file_time_setfile(filename, datetime_string):
    os.system('SetFile -dm "{}" {}'.format(datetime_string, filename.replace(' ', '\\ ')))


  if setfile:
    if not shutil.which('SetFile'):
      print('Creation time flag (-c) was used, but SetFile command cannot be found.')
      print('Install Xcode command line tools from https://developer.apple.com')
      exit(1)
    elif verbose:
      print(f'SetFile command found: {shutil.which("SetFile")}')

  # path = os.path.expanduser(input_dir)
  if verbose:
    print(f'Checking directory {input_dir}')
  dir_list = create_dir_list(input_dir)

  files = []
  videos = []
  for item in dir_list:
    if item.suffix.lower() in ['.jpg', '.png']:
      files.append(re.split(r' |_|\.',item.name) + [item])
    elif item.suffix.lower() == '.mp4':
      videos.append(re.split(r' |_|\.',item.name) + [item])
  

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

  # Validate the files to build images and invalid files lists.
  images = []
  invalid_files = []

  if verbose:
    print('Checking files for invalid file names and extensions.')
  for f in files:
    dir_entry = f[-1]
    if len(f) != 10:
      invalid_files.append(dir_entry)
      if verbose:
        print('Invalid filename: \'{}\''.format(dir_entry))
    elif dir_entry.suffix not in ['.jpg', '.png', '.mp4']:
      invalid_files.append(dir_entry)
      if verbose:
        print('Invalid extension: \'{}\''.format(dir_entry.name))
    else:
      images.append(f)
  if verbose:
    if not len(invalid_files):
      print('None found.')
    else:
      print()

  if verbose:
    print('Retiming images.')


  for i in images:
    [first, last, month, day, year, hours, minutes, seconds, extension, original_filename] = i

    time_string = f'{month}/{day}/{year} {hours}:{minutes}:{seconds}'
    time_string_sane = f'{year}/{month}/{day} {hours}:{minutes}:{seconds}'
    new_filename = input_dir / f'{first} {last} {year}{month}{day}_{hours}{minutes}{seconds}.{extension}'

    if verbose == 2:
      print('\'{}\''.format(original_filename))
      print('\tRetiming to {}{}'.format(time_string_sane, '\n' if not rename else ''))

    if execute:
      if setfile:
        correct_file_time_setfile(original_filename, time_string)
      correct_file_time(original_filename, time_string)

    if rename:
      if verbose == 2:
        print('\tRenaming to \'{}\'\n'.format(new_filename))
      if execute:
        os.rename(original_filename, new_filename)

  end_time = timeit.default_timer()
  print('Completed in {0} seconds.'.format(round(end_time-start_time,2)))
  print('{} files {} {}{}.'.format(len(images), 'were' if execute else 'will be', 'renamed and retimed' if rename else 'retimed', ' using SetFile' if setfile else ''))

  if len(invalid_files) > 0:
    print('\nThe following {} {} {} processed. {}.'.format(len(invalid_files),'files' if len(invalid_files) != 1 else 'file','weren\'t' if execute else 'won\'t be', 'See above' if verbose else 'Run with the -v flag for more details'))
    for invalid_file in invalid_files:
      print('\t\'{}\''.format(invalid_file))
    print()

  if not execute:
    print('DRY RUN COMPLETE. No files were modified. Run with -e flag to execute.')


@Gooey()
def main():
  parser = GooeyParser(description='Correct the file creation and modified time on FFXIV screenshots exported from the PS4.')
  parser.add_argument('directory', metavar='Screenshot Folder', widget='DirChooser', help='Path to the directory containing the images.')
  parser.add_argument('-e', '--execute', action='store_true', help='Modifiy the files.')
  parser.add_argument('-r', '--rename', action='store_true', help='Rename the files to \'First Last YYYYMMDD_HHMMSS.xyz\'')
  parser.add_argument('-c', '--creation_time', action='store_true', help='Use the macOS SetFile command to also set file creation time. It\'s much slower!')
  group = parser.add_mutually_exclusive_group()
  group.add_argument('-v', '--verbose', action='store_true', help='Display additional logging.')
  group.add_argument('-n', '--noisy', action='store_true', help='Display a huge amount of logging.')

  args = parser.parse_args()

  if args.noisy:
    args.verbose = True

  retime_ps4_screenshots(
    args.directory,
    execute=args.execute,
    rename=args.rename,
    setfile=args.creation_time,
    verbose=args.verbose
    )


if __name__ == '__main__':
  main()
