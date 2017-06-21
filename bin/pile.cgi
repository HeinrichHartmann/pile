#!/usr/local/bin/python3

import sys
from pile import Pile

def write(s):
    sys.stdout.buffer.write((s + "\n").encode("utf-8"))

def cgi():
   write("Content-Type: text/plain; charset=utf-8\n")
   for doc in Pile.from_folder("."):
       write(doc.text())

cgi()
