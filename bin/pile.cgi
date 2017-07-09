#!/usr/local/bin/python3

import sys
import json
from pile import Pile, Stack
from pathlib import Path
import os
import urllib.parse

# CGI WRAPPER ##################################################################

def cgi_write(s):
    sys.stdout.buffer.write((s + "\n").encode("utf-8"))

def cgi_qs():
    return dict(urllib.parse.parse_qsl(os.environ['QUERY_STRING']))

def cgi_method():
    return os.environ['REQUEST_METHOD']

# ACTION DISPATCHER ############################################################

_ACTIONS = {}

def action(action):
    def action_decorator(handler):
        _ACTIONS[action] = handler
        return handler
    return action_decorator

def action_dispatch():
    qs = cgi_qs()
    action = qs['ACTION']
    if not action:
        raise Error("No Action parameter provided")
    handler = _ACTIONS[action]
    if not handler:
        raise Error("No such action: " + action)
    qs.pop('ACTION')

    result = handler(**qs)

    cgi_write("Content-Type: Application/json; charset=utf-8")
    cgi_write("")
    cgi_write(json.dumps(result, default=lambda o: o.__dict__()))

## ACTIONS #####################################################################

@action("env")
def action_env():
    return dict(os.environ)

@action("args")
def action_args(**kwargs):
    return kwargs

@action("list")
def action_list():
    return list(Pile.from_folder("."))

@action("latest")
def action_latest():
    return Pile.from_folder(".").latest()

### STACK FUNCTIONS

@action("stack")
def action_stack(n=1):
    "return list of the latest added files"
    return Stack(".").top(int(n))

################################################################################

action_dispatch()
