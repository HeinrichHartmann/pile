#!/usr/local/bin/python3

import sys
import click
from docs import Pile

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
        write(doc.name())
        write(" -> ")
        if dry_run:
            write(doc.text())
        else:
            doc.normalize()
            write(doc.name())
        write("\n")
doc.add_command(normalize)

@click.command(help="show left over documents")
def left():
    for p in Pile.leftovers("."):
        writeln(p.name)
doc.add_command(left)


if __name__ == '__main__':
    doc()
