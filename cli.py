#!/usr/local/bin/python3

import click
from docs import Pile

@click.group()
def doc():
    pass
    
@click.command(help="List all documents in table")
def ls():
    for doc in Pile.from_folder("."):
        print(doc.text())
    
doc.add_command(ls)

if __name__ == '__main__':
    doc()
