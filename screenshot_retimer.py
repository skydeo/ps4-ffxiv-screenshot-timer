import os
import re
import time
import timeit
import shutil
from pathlib import Path
from gooey import Gooey, GooeyParser

class Screenshot:
  ''' An object to hold a screenshot (or video) that should be renamed or retimed '''

  def __init__(self, file_path):
    self.original_filename = file_path.name
    self.file_path = file_path

    parts = re.split(r' |_|\.', self.file_path.name)
    if len(parts) == 9:
      [first, last, month, day, year, hours, minutes, seconds, _] = parts
      name = f'{first} {last}'
    elif len(parts) == 8:
      [first, month, day, year, hours, minutes, seconds, _] = parts
      name = first

    self.timestamp = f'{year}{month}{day}_{hours}{minutes}{seconds}'
    self.new_filename = f'{name} {self.timestamp}{self.file_path.suffix}'
    self.setfile_timestamp = f'{month}/{day}/{year} {hours}:{minutes}:{seconds}'

    if self.file_path.suffix.lower() in ['.jpg', '.png']:
      self.type = 'image'
    elif self.file_path.suffix.lower() in ['.mp4']:
      self.type = 'video'
    else:
      self.type = 'unknown'
  
  def correct_file_time(self):
    time_struct = time.strptime(self.timestamp, '%Y%m%d_%H%M%S')
    seconds_since = int(time.mktime(time_struct))
    os.utime(self.file_path, (seconds_since, seconds_since))
  
  def correct_file_time_setfile(self):
    os.system('SetFile -dm "{}" {}'.format(self.setfile_timestamp, self.file_path.replace(' ', '\\ ')))
  
  def rename_file(self):
    os.rename(self.file_path.parents[0] / self.original_filename, self.file_path.parents[0] / self.new_filename)


def retime_ps4_screenshots(input_dir, execute=False, rename=False, setfile=False, verbose=True):
  start_time = timeit.default_timer()
  input_dir = Path(input_dir)


  if setfile:
    if not shutil.which('SetFile'):
      print('Creation time flag (-c) was used, but SetFile command cannot be found.')
      print('Install Xcode command line tools from https://developer.apple.com')
      exit(1)
    elif verbose:
      print(f'SetFile command found: {shutil.which("SetFile")}')


  def create_dir_list(input_dir):
    p = Path(input_dir).iterdir()
    dir_list = [entry for entry in p 
                if entry.is_file()
                and not entry.name.startswith('.')]
    return dir_list


  if verbose:
    print(f'Checking directory {input_dir}')
  dir_list = create_dir_list(input_dir)

  files = []
  for item in dir_list:
    if item.is_file():
      files.append(Screenshot(item))

  # Validate the files to build images and invalid files lists.
  if verbose:
    print('Checking files for invalid file names and extensions.')

  images = [f for f in files if f.type == 'image']
  videos = [f for f in files if f.type == 'video']
  unknowns = [f for f in files if f.type == 'unknown']

  if verbose:
    print(f'Found {len(images)} screenshots, {len(videos)} videos, and {len(unknowns)} unknown file types.')
    print('Retiming images.')

  for image in images:
    # if verbose == 2:
    if verbose:
      print(f"'{image.original_filename}\'")
      print('\tRetiming to {}{}'.format(image.setfile_timestamp, '\n' if not rename else ''))

    if execute:
      if setfile:
        image.correct_file_time_setfile()
      image.correct_file_time()

    if rename:
      # if verbose == 2:
      if verbose:
        print(f"\tRenaming to '{image.new_filename}'\n")
      if execute:
        image.rename_file()

  end_time = timeit.default_timer()
  print('Completed in {0} seconds.'.format(round(end_time-start_time,2)))
  print('{} files {} {}{}.'.format(len(images), 'were' if execute else 'will be', 'renamed and retimed' if rename else 'retimed', ' using SetFile' if setfile else ''))

  if len(unknowns) > 0:
    print('\nThe following {} {} {} processed. {}.'.format(len(unknowns),'files' if len(unknowns) != 1 else 'file','weren\'t' if execute else 'won\'t be', 'See above' if verbose else 'Run with the -v flag for more details'))
    for unknown in unknowns:
      print(f"\t'{unknown.name}'")
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
