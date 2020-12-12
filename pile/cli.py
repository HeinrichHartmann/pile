#!/usr/local/bin/python3

import sys
import click
import json
from pathlib import Path
from pile import Pile, tag2str, str2tag, kvtag2str
import unicodedata

def write(s):
    sys.stdout.buffer.write((s).encode("utf-8"))
def writeln(s):
    write(s + "\n")
def warn(s):
    sys.stderr.buffer.write((s + '\n').encode("utf-8"))

@click.group()
def main():
    pass

@click.command(help="List all valid documents in pile")
def ls():
    for doc in Pile.from_folder("."):
        writeln(doc.name())
main.add_command(ls)

@click.command(help="show left over documents")
def lt():
    for p in Pile.leftovers("."):
        writeln(p.name)
main.add_command(lt)

@click.command()
def totsv():
    fmt = "{}\t{}\t{}\t{}\t{}"
    writeln(fmt.format("date", "tags", "kvtags", "title", "ext"))
    for doc in Pile.from_folder("."):
        tags = ",".join(list(map(tag2str, doc.tags)))
        kvtags = ",".join([kvtag2str(k, v) for k,v in doc.kvtags.items()])
        # Normalize unicode strings before printing in order to keep alignment
        writeln(fmt.format(*map(lambda s : unicodedata.normalize('NFC', s),
                                [doc.date, tags, kvtags, doc.title, doc.ext[1:]])))
main.add_command(totsv)

@click.command()
def table():
    fmt = "{:10} {:20} {:20} {:50} {}"
    writeln(fmt.format("date", "tags", "kvtags", "title", "ext"))
    for doc in Pile.from_folder("."):
        tags = ",".join(list(map(tag2str, doc.tags)))
        kvtags = ",".join([kvtag2str(k, v) for k,v in doc.kvtags.items()])
        # Normalize unicode strings before printing in order to keep alignment
        writeln(fmt.format(*map(lambda s : unicodedata.normalize('NFC', s),
                                [doc.date, tags, kvtags, doc.title, doc.ext[1:]])))
main.add_command(table)

@click.command()
@click.option("--recurse","-r",help="Descend into subdirectories", is_flag=True)
def invoice_table(recurse):
    fmt = "{}\t{}\t{}\t{}\t{}"
    writeln(fmt.format("date", "title", "tags", "AMOUNT", "CUR"))
    for doc in Pile.from_folder(".", recurse=recurse):
        kvtags = doc.kvtags;
        if not "AMOUNT" in kvtags:
            warn("Skipping " + doc.path.name)
            continue
        amount = kvtags.pop("AMOUNT")
        cur    = kvtags.pop("CUR", "EUR")
        s_tags = ",".join(list(map(tag2str, doc.tags)) +
                          [kvtag2str(k, v) for k,v in doc.kvtags.items()])
        # Normalize unicode strings before printing in order to keep alignment
        writeln(fmt.format(*map(lambda s : unicodedata.normalize('NFC', s),
                                [doc.date, doc.title, s_tags, amount, cur])))
main.add_command(invoice_table)


@click.command(help="export documents as json")
def tojson():
    for doc in Pile.from_folder("."):
        writeln(json.dumps(doc.__dict__()))
main.add_command(tojson)

@click.command(help="normalize names of all file son the pile")
@click.option("--dry-run","-n",help="dry run", is_flag=True)
def normalize(dry_run):
    for doc in Pile.from_folder("."):
        if dry_run:
            if doc.name() != doc.text():
                write(doc.name())
                write(" -> ")
                write(doc.text())
                write("\n")
        else:
            doc.normalize()
main.add_command(normalize)

@click.command(help="List all tags")
def tags():
    for doc in Pile.from_folder("."):
        for tag in doc.tag_list():
            print(tag)
main.add_command(tags)

@click.command(help="extract tagged documents into a folder")
@click.argument('tag')
def extract(tag):
    Pile.from_folder(".").extract(str2tag(tag))
main.add_command(extract)

@click.command(help="Tag documents in subfolder with it's name, and move them to the pile.")
@click.argument('folder')
def fold(folder):
    pile = Pile.from_folder(folder)
    for doc in pile:
        doc.tag_add(str2tag(folder))
        doc.move_to_dir("./")
    Path(folder).rmdir() # remove if empty
main.add_command(fold)

@click.command()
def latest():
    pile = Pile.from_folder(".")
    print(pile.latest().name())
main.add_command(latest)
