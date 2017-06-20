#!/usr/local/bin/python3

import sys
import click
from pathlib import Path
from docs import Pile, Tag

def write(s):
    sys.stdout.buffer.write((s).encode("utf-8"))
def writeln(s):
    write(s + "\n")

@click.group()
def doc():
    pass
    
@click.command(help="List all valid documents in pile")
def ls():
    for doc in Pile.from_folder("."):
        writeln(doc.name())
doc.add_command(ls)

@click.command(help="show left over documents")
def lt():
    for p in Pile.leftovers("."):
        writeln(p.name)
doc.add_command(lt)

@click.command()
def table():
    fmt = "{:10} {:20} {} {}"
    writeln(fmt.format("date", "tags", "title", "ext"))
    for doc in Pile.from_folder("."):
        writeln(fmt.format(doc.date, ",".join(doc.tags), doc.title, doc.ext[1:]))
doc.add_command(table)

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
doc.add_command(normalize)

@click.command(help="List all tags")
def tags():
    for doc in Pile.from_folder("."):
        for tag in doc.tag_list():
            print(tag)
doc.add_command(tags)

@click.command(help="extract tagged documents into a folder")
@click.argument('tag')
def extract(tag):
    Pile.from_folder(".").extract(tag)
doc.add_command(extract)

@click.command(help="Tag documents in sub directory with it's name, and move them to the pile.")
@click.argument('directory')
def fold(directory):
    pile = Pile.from_folder(directory)
    for doc in pile:
        doc.tag_add(Tag.from_str(directory))
        doc.move_to_dir("./")
doc.add_command(fold)

if __name__ == '__main__':
    doc()
