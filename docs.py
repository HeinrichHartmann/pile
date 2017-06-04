#
# Document Manager
#

import sys
import re
from pathlib import Path
import json
import os
import os.path
import click

re_date = re.compile("(\d\d\d\d-\d\d-\d\d)(.*)")
re_ext = re.compile(".*?[.]([a-zA-Z]{1,3})")
re_tag = re.compile("[#][A-Za-z0-9]+")
re_scan_tag = re.compile("S[0-9]+")

class Document:
    "A managed document"
    
    def __init__(self, date, tags, title, ext, path):
        self.date = date
        self.tags = tags
        self.ext = ext
        self.title = title
        self.path = path

    @staticmethod
    def from_path(path):
        if path.name.startswith("."):
            raise ValueError("Hidden files are not allowed: " + path.name)

        name = path.name

        # Split off extension
        base, ext = os.path.splitext(name)

        # Split off date
        match = re_date.match(base)
        rest = None
        date = None
        if match:
            date = match.group(1)
            rest = match.group(2)
        else:
            raise ValueError("No date field found " + name)

        # Filename seems ok.
        # Causes IO(?) Check last
        if not path.is_file():
            raise ValueError("Path not a file")

        # Extract tags
        tags = list(map(lambda x: x.lstrip('#'), re_tag.findall(rest)))
        rest = re_tag.sub("", rest)

        # Scan tags
        tags.extend(re_scan_tag.findall(rest))
        rest = re_scan_tag.sub("", rest)

        # Cleanup title
        rest = rest.strip("_")
        rest = re.sub("__", "", rest)
        title = re.sub("_", " ", rest)
        return Document(date, tags, title, ext, path)
        
    def text(self):
        tags = ",".join(map(lambda x: "#" + x, self.tags))
        return '{}|{}|{}{}'.format(self.date, tags, self.title, self.ext)

import sqlite3
class Pile():
    "A pile of managed documents"

    def __init__(self, backing_dir):
        self.docs = []
        self.backing_dir = backing_dir

    def add(self, doc):
        "Throw a doc to onto the pile"
        self.docs.append(doc)
        
    @staticmethod
    def from_folder(path):
        pile = Pile(path)
        for p in Path(path).iterdir():
            try:
                pile.add(Document.from_path(p))
            except ValueError as e:
                pass
        return pile

    def __iter__(self):
        "iterate over documents within the pile"
        return iter(self.docs)
