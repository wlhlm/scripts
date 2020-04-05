#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse

import natsort

import eyed3
import eyed3.mp3
import eyed3.mp3.headers
import eyed3.id3

def merge_mp3_ffmpeg(file_output, mp3s):
    """Merge a list of MP3 files into one using ffmpeg.

    This method relies on the multimedia swiss army knife ffmpeg to do the heavy
    lifting.
    """
    paths = []
    file_input = "concat:"

    for mp3 in mp3s:
        paths.append(mp3.path)

    # This function relies on ffmpeg's concat protocol [1] which just appends all
    # files into one big blob. This requires building a specific input file
    # string beginning with "concat:" followed by a list of files separated by
    # "|":
    #
    # concat:file1.mp3|file2.mp3|file3.mp3|...
    #
    # [1]: https://trac.ffmpeg.org/wiki/Concatenate#protocol
    file_input += "|".join(paths)
    # After concatenating we just copy the resulting file to the output without
    # reencoding it using "-c copy".

    ffmpeg_cmdline = ["ffmpeg", "-i", file_input, "-y", "-c", "copy", file_output]
    ret = subprocess.run(ffmpeg_cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ret.returncode != 0:
        # Print cmdline for feedback
        print(" ".join(ffmpeg_cmdline))
        print(ret.stdout, file=sys.stderr)
        return None
    else:
        return file_output


def merge_mp3_custom(file_output, mp3s):
    """Merge a list of MP3 files into one using custom handling functionality
    instead of relying on external tools.

    This function leverages eyed3 to strip all metadata from the file allowing
    us to just append it to the output file.
    """
    with open(file_output, "wb") as output:
        for mp3 in mp3s:
            with open(mp3.path, "rb") as input:
                size = os.fstat(input.fileno()).st_size
                tag1 = eyed3.id3.Tag()
                tag2 = eyed3.id3.Tag()
                if tag1.parse(input, version=eyed3.id3.ID3_V1):
                    size -= 128
                input.seek(0)
                if tag2.parse(input, version=eyed3.id3.ID3_V2):
                    size -= tag2.file_info.tag_size
                    input.seek(tag2.file_info.tag_size)

                output.write(input.read(size))

    return file_output


def get_merged_mp3_name(path):
    """Determines the of the output MP3 file."""

    absolutepath = os.path.abspath(path)
    if os.path.isfile(absolutepath):
        dirpath = os.path.dirname(absolutepath)
    else:
        dirpath = absolutepath

    # Use the name of the Directory which includes our MP3 files.
    return os.path.basename(dirpath) + ".mp3"


def get_mp3_files(path):
    """Compile a list of all valid MP3 files in the given path."""
    mp3_files = []

    for file_name in natsort.natsorted(os.listdir(path)):
        f = os.path.join(path, file_name)
        if os.path.isfile(f):
            mp3_file = eyed3.load(f)
            # Filter out files that are not detected as MP3 files.
            if isinstance(mp3_file, eyed3.mp3.Mp3AudioFile):
                mp3_files.append(mp3_file)

    return mp3_files


class Chapter:
    """A simple chapter.

    While the ID3v2 chapter specification allows for more fields like URL and
    image, we only support a simple name and length.
    """

    def __init__(self, name="", length=""):
        self._name = name
        self._length = length

    @property
    def name(self):
        return self._name

    @property
    def length(self):
        return self._length

    @staticmethod
    def write_chapters(path, chapters):
        """Add chapter information to file in path

        This write chapters according to the ID3v2 specification [1].

        [1]: http://id3.org/id3v2-chapters-1.0
        """
        tag = eyed3.id3.Tag()
        tag.version = eyed3.id3.ID3_V2_3
        tag.clear()

        # Accordings to the specification, chapter frames have to be organized
        # in a "table of contents", so create one here.
        toc = tag.table_of_contents.set(
            "toc".encode(), toplevel=True, description="Table of contents"
        )

        # current_length keeps track of our current position (time) within the
        # merged mp3 file. This is necessary since our chapter lengths all start
        # from zero.
        current_length = 0
        for chapter in chapters:
            # The first argument is an identifier and has to be unique within
            # the ID3 tag. The chapter name should be sufficient here. The
            # seconds argument is a tuple of the start and end time of the
            # chapter to be added.
            tag.chapters.set(
                chapter.name.encode(), (current_length, current_length + chapter.length)
            )
            # To give the chapter an actual name that is displayed in the
            # player, we first have to get the specific chapter frame and then
            # add a title to it.
            chapter_frame = tag.chapters.get(chapter.name.encode())
            chapter_frame.title = chapter.name

            # Associate the chapter frame with the table of contents.
            toc.child_ids.append(chapter_frame.element_id)

            current_length += chapter.length + 1

        tag.save(path)

    @staticmethod
    def get_chapters(mp3s):
        """Compile a list of chapters for the merged MP3 file.

        Each Chapter gets a length in milliseconds derived from the individual
        MP3 file to be merged later on. In Addition a chapter name is extracted
        from the title tag.
        """
        chapters = []

        for mp3 in mp3s:
            length = mp3.info.time_secs
            name = mp3.tag.title

            chapters.append(
                Chapter(
                    # Chapter lengths have to be given in milliseconds, so
                    # convert from floating point seconds to integer
                    # milliseconds.
                    length=int(length * 1000),
                    name=name,
                )
            )

        return chapters


if __name__ == "__main__":
    # Rely on python's nifty ArgumentParser to do the heavy lifitng for us.
    arg_parser = argparse.ArgumentParser(usage="%(prog)s [options] DIRECTORY")
    arg_parser.add_argument(
        "directory",
        type=str,
        metavar="DIRECTORY",
        help="directory with MP3 files for merging",
    )
    arg_parser.add_argument(
        "-o", "--output", type=str, metavar="MP3", help="name of the output file"
    )
    arg_parser.add_argument(
        "--ffmpeg", action="store_true", help="use ffmpeg for concatenating MP3 files"
    )
    arguments = arg_parser.parse_args()

    # Main application flow:
    # 1. Determine output file name
    if arguments.output:
        output_file = arguments.output
    else:
        output_file = get_merged_mp3_name(arguments.directory)
    # 2. Retrieve a list of MP3 files to be merged.
    files = get_mp3_files(arguments.directory)
    # 3. Load chapter information
    chapters = Chapter.get_chapters(files)
    # 4. Merge MP3 files into one
    if arguments.ffmpeg:
        merged_mp3 = merge_mp3_ffmpeg(output_file, files)
    else:
        merged_mp3 = merge_mp3_custom(output_file, files)
    # 5. Write Chapter information
    Chapter.write_chapters(merged_mp3, chapters)
    # 6. Done!
