#!/usr/bin/env python3
# Generate an HTML directory listing. Inspired by the lighttpd index
# module
#
# Requirements:
#   python3 >= 3.2 (html.escape)

import os
import stat
import mimetypes
import html
import datetime
from string import Template
from urllib.request import pathname2url
from argparse import ArgumentParser

class Node():
    def __init__(self, path, mime=False):
        self.path = path
        self.basename = os.path.basename(self.path)
        self.stat = os.stat(path)

        if self.is_directory():
            self.type_name = "Directory"
        else:
            type, _ = mimetypes.guess_type(self.basename)
            if mime and type:
                self.type_name = type
            else:
                self.type_name = "File"

    def is_file(self):
        return not stat.S_ISDIR(self.stat.st_mode)

    def is_directory(self):
        return stat.S_ISDIR(self.stat.st_mode)

class Directory():
    def __init__(self, path, mime=False):
        self.path = path
        self.contents = []

        for f in os.listdir(path):
            node = Node(os.path.join(path, f), mime)

            self.contents.append(node)

        self._sort_contents()

    def to_html(self, mime=False):
        output = "<table><tr><th>Name</th><th>Last Modified</th><th>Size</th><th>Type</th>"

        for n in self.contents:
            output += "<tr>"
            output += "<td><a href=\"{0}\">{1}</a>{2}</td>".format(pathname2url(n.path), html.escape(n.basename), "/" if n.is_directory() else "")
            output += "<td>{}</td>".format(format_time(int(n.stat.st_mtime)))
            output += "<td>{}</td>".format(readable_size(n.stat.st_size) if n.is_file() else "-")
            output += "<td>{}</td>".format(n.type_name)
            output += "</tr>"

        output += "</table>"

        return output

    def _sort_contents(self):
        files = []
        node_sort = lambda x: x.basename

        files = [n for n in self.contents if n.is_file()]
        self.contents = [x for x in self.contents if x not in set(files)]

        self.contents.sort(key=node_sort)
        files.sort(key=node_sort)

        self.contents.extend(files)

def token_replace(string, replacement):
    template = Template(string)

    return  template.safe_substitute(replacement)

def format_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%b-%d %H:%M:%S")

# Courtesy of http://stackoverflow.com/a/1094933/3397956
def readable_size(num):
    for x in ["","K","M"]:
        if num < 1024.0:
            return "{0:3.1f}{1}".format(num, x)

        num /= 1024.0
    return "{0:3.1f}{1}".format(num, "G")

if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument("directory", metavar="DIRECTORY", nargs="?", default=".", help="the directory for a listing should be produced")
    arg_parser.add_argument("-t", "--template", metavar="FILE", help="template file in which the listing is inserted")
    arg_parser.add_argument("-f", "--text-file", metavar="FILE", help="text file which is also incoporated in the final output (depending on the template)")
    arg_parser.add_argument("-m", "--mime", action="store_true", help="add MIME information to each file (based on extension)")
    arguments = arg_parser.parse_args()

    directory = Directory(arguments.directory, arguments.mime)
    listing = directory.to_html()

    replace = {}
    if not arguments.template:
        print(listing)
    else:
        with open(arguments.template, "r") as t:
            template = t.read()

            replace["PWD"] = html.escape(directory.path)
            replace["LISTING"] = listing

            if arguments.text_file:
                with open(arguments.text_file, "r") as text:
                    replace["TEXT"] = html.escape(text.read())

            print(token_replace(template, replace))
