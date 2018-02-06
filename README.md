# PS4/FFXIV Screenshot Retimer

I play a lot of FFXIV on the PS4, and take a lot of screenshots when doing so (over 5000 by the end of 4.0!). A few times a year I'll transfer these off my PS4 to save space and help me look at them, but while the datetime stamps are recorded in the file name¹, they aren't stored in the file metadata, instead just being whenever files were moved to a flash drive. This means the screenshots don't sort correctly and it drives me crazy. How can I relive my adventure through Eorzea when the screenshots are out of order? This fixes the metadata using the datetime stored in the filename.

Example usage: `python screenshot_retimer.py ~/Desktop/PS4/FFXIV/Screenshots/ -e`

I settled on using the `-e` flag to actually execute, but that might be a little overly cautious. There are a couple of other optional parameters you can read about using the `-h` flag (`python screenshot_retimer.py -h`).

There are two ways it assigns times, a fast method which works most of the time but doesn't assign file creation times on macOS² for some edge cases, and a slow method that does but requires the installation of macOS Developer Tools. Chances are these are already installed for most targets of this script.

¹ 'Stored' in a non-sortable way using the stupid US MM-DD-YYYY notation.

² I guess most UNIX systems don't care about file creation time, on access and modified times. The file creation time will be set if the modified time is before present.

TODO
* Make it work with videos. For some unknown reason, there are at least 3 different formats of video file names over the years. Shouldn't be hard, but need to add flags and test.
