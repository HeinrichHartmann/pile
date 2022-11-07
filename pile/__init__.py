# coding: utf-8

import re
from pathlib import Path
import os
import os.path
import datetime
import shutil

# MacOSX insists in filenames being utf8, with NFD normalized
# This means umlauts are represented as two unicode points : (1) LATIN SMALL LETTER ? (2) WITH COMBINING DIAERESIS
# We explicitly include the latter unicode point
# See, e.g. https://tex.stackexchange.com/questions/94418/os-x-umlauts-in-utf8-nfd-yield-package-inputenc-error-unicode-char-u8̈-not

W = "[A-Za-z0-9,._\u0308\u006B]"
RE_YEAR = re.compile("\d\d\d\d")
RE_DATE = re.compile("(\d\d\d\d-\d\d-\d\d)(.*)")
RE_EXT = re.compile(".*?[.]([a-zA-Z]{1,3})")
RE_KVTAG = re.compile("[#]({w}+)=({w}+)".format(w=W))
RE_TAG = re.compile("[#]{w}+".format(w=W))


def tag2str(tag):
    return "#" + tag


def str2tag(s):
    return s.lstrip("#")


def kvtag2str(k, v):
    return "#" + k + "=" + v


def _move(src: Path, tar: Path):
    """Move file past device boundaries"""
    try:
        src.rename(tar)
    except OSError:
        shutil.copy(src, tar)
        src.unlink()


class Document:
    "A managed document"

    def __init__(self, date, tags, kvtags, title, ext, path):
        self.date = date
        self.tags = tags
        self.kvtags = kvtags
        self.ext = ext
        self.title = title
        self.path = path

    def as_dict(self):
        return {
            "date": self.date,
            "tags": self.tag_list(),
            "kvtags": self.kvtags,
            "title": self.title,
            "extension": self.ext,
            "filename": self.path.name,
            "path": self.path.resolve().as_posix(),
        }

    def update(self, data):
        print("update", self, data)
        for key in ["date", "tags", "kvtags", "title", "ext"]:
            if key in data:
                setattr(self, key, data[key])

    @staticmethod
    def parse_path(path):
        "Returns document with parsed out valid semantic field from filename"

        # Apparently python3 pathlib paths are unicode strings, and not bytes (as in UNIX)
        # http://beets.io/blog/paths.html
        name = path.name

        # Split off extension
        rest, ext = os.path.splitext(name)

        # Split off date
        match = RE_DATE.match(rest)
        date = None
        if match:
            date = match.group(1)
            rest = match.group(2)

        # Extract kv-tags
        kvtags = dict(RE_KVTAG.findall(rest))
        rest = RE_KVTAG.sub("", rest)

        # Extract tags
        tags = [str2tag(tag_str) for tag_str in RE_TAG.findall(rest)]
        tags = list(set(tags))
        tags.sort()
        rest = RE_TAG.sub("", rest)

        # Fetch remaining bits as title
        rest = re.sub("[_,|:]", " ", rest)
        rest = re.sub("  +", " ", rest)
        rest = rest.strip(" ")
        title = rest
        return Document(date, tags, kvtags, title, ext, path)

    @staticmethod
    def create_from_path(path):
        "Create document from correctly formatted file-name"

        if not path.is_file():
            raise ValueError("Path not a file")

        if path.name.startswith("."):
            raise ValueError("Hidden files are not allowed: " + path.name)

        doc = Document.parse_path(path)

        if not doc.date:
            raise ValueError(f"Date field not found: {path.name}")
        return doc

    def inferr_from_path(path):
        "Infer as much information as possible from the file"
        doc = Document.parse_path(path)
        if not doc.date:
            doc.date = datetime.datetime.fromtimestamp(path.stat().st_ctime).strftime(
                "%Y-%m-%d"
            )
        return doc

    def text(self):
        tags = "".join([tag2str(t) + " " for t in sorted(self.tags)])
        kvtags = "".join(
            [kvtag2str(k, self.kvtags[k]) + " " for k in sorted(self.kvtags)]
        )
        return "{} {}{}{}{}".format(self.date, tags, kvtags, self.title, self.ext)

    def normalize(self):
        q = self.path.with_name(self.text())
        self.path.rename(q)
        self.path = q

    def move_to_dir(self, target):
        q = Path(target).expanduser() / self.path.name
        _move(self.path, q)
        self.path = q

    def name(self):
        return self.path.name

    def has_tag(self, tag):
        return tag in self.tags

    def tag_list(self):
        return self.tags

    def tag_add(self, tag):
        "Add tag to tags list"
        if not tag in self.tags:
            self.tags += [tag]
            self.tags.sort()
            self.normalize()

    def tag_rm(self, tag):
        "remove tag from internal tag list. Need to normalize() to change file name"
        if tag in self.tags:
            self.tags = [t for t in self.tags if t != tag]
            self.normalize()

    def get_path(self):
        print(self.path.as_posix())
        return self.path.as_posix()

    def punt(self):
        """
        Kicks a dockument back to the end of the Pile.

        Hack: As Pile is ordered by mtime, we achieve this by modifying the mtime to -1 year
        """
        stat = self.path.stat()
        print("PUNT atime, mtime = ", stat.st_atime, stat.st_mtime)
        delta = 60 * 60 * 24 * 365  # on year
        os.utime(self.path.as_posix(), (stat.st_atime - delta, stat.st_mtime - delta))
        return self.get_path()


class Pile:
    "A pile of managed documents"

    def __init__(self, backing_dir):
        self.docs = []
        self.backing_dir = Path(backing_dir)
        assert self.backing_dir.is_dir()

    def __iter__(self):
        "iterate over documents within the pile"
        return iter(self.docs)

    def add(self, doc):
        "Throw a doc to onto the pile"
        self.docs.append(doc)

    @staticmethod
    def from_folder(dirpath, recurse=False):
        pile = Pile(dirpath)

        def _rec(dirpath, tags):
            for p in Path(dirpath).iterdir():
                if recurse and p.is_dir():
                    if RE_YEAR.match(p.name):
                        _rec(p, tags)
                    elif RE_TAG.match(p.name):
                        _rec(p, tags + [p.name])
                    else:
                        print(f"Skipping directory {p.name}")
                else:
                    try:
                        d = Document.create_from_path(p)
                        d.tags += tags
                        pile.add(d)
                    except ValueError as e:
                        print(e)
                        pass

        _rec(dirpath, [])
        return pile

    @staticmethod
    def leftovers(path):
        "returns all paths that are not valid documents"
        pile = Pile(path)
        for p in Path(path).iterdir():
            try:
                pile.add(Document.create_from_path(p))
            except ValueError as e:
                yield p

    def extract(self, tag):
        "moves all documents tagged with $tag into a subfolder"
        tagdir = self.backing_dir / tag2str(tag)
        if not tagdir.exists():
            tagdir.mkdir()

        for doc in self:
            if doc.has_tag(tag):
                doc.move_to_dir(tagdir)
                doc.tag_rm(tag)

    def latest(self):
        self.docs.sort(key=lambda doc: doc.date)
        return self.docs[-1]

    def list(self):
        self.docs.sort(key=lambda doc: doc.date, reverse=True)

        def _render(doc):
            out = doc.as_dict()
            out["path"] = doc.path.relative_to(self.backing_dir).as_posix()
            return out

        return [_render(doc) for doc in self.docs]


class Stack:
    "A stack of not yet managed documents"

    def __init__(self, backing_dir):
        self.backing_dir = Path(backing_dir)
        assert self.backing_dir.is_dir()

    def top(self, n):
        content = list(self.backing_dir.iterdir())
        content = filter(lambda p: not p.name.startswith("."), content)
        # sort by creation time
        # https://stackoverflow.com/a/168435/1209380
        content = [
            x[0]
            for x in sorted(
                [(fn, os.stat(fn)) for fn in content],
                reverse=True,
                key=lambda x: x[1].st_mtime,
            )
        ]
        content = content[:n]
        content = map(Document.inferr_from_path, content)
        return list(content)

    def is_empty(self):
        content = list(self.backing_dir.iterdir())
        content = filter(lambda p: not p.name.startswith("."), content)
        if next(content, None) == None:
            return True
        return False

    def last(self):
        return self.top(1)[0]
