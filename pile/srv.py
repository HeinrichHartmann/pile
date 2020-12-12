# -*- python -*-

import asyncio
from aiohttp import web
from urllib.parse import unquote
from pathlib import Path
import json
import argparse
import logging

logging.basicConfig(level=logging.DEBUG)

from pile import Pile, Stack

app = web.Application()
path_docs = Path("~/Documents").expanduser()
path_pile = Path("~/Pile").expanduser()
path_log = Path("~/var/log").expanduser()


def res(path):
    import pkg_resources

    return pkg_resources.resource_filename("pile", path)


async def handle_docs(request):
    return web.FileResponse(res("static/docs.html"))


async def handle_dfile(request):
    name = unquote(request.match_info.get("name", ""))
    return web.FileResponse(path_docs.joinpath(name))


async def handle_pile(request):
    return web.FileResponse(res("static/pile.html"))


async def handle_pfile(request):
    name = unquote(request.match_info.get("name", ""))
    return web.FileResponse(path_pile.joinpath(name))


async def handle_app_list(request):
    pile = Pile.from_folder(path_docs, recurse=True)
    return web.json_response(pile.list())


async def handle_app_last(request):
    stack = Stack(path_pile)
    if stack.is_empty():
        return web.json_response({})
    else:
        return web.json_response(stack.last().as_dict())


async def handle_app_refile(request):
    data = await request.json()
    source_filename = data["source"]
    target = data["target"]
    meta = data["meta"]
    stack = Stack(path_pile)
    assert not stack.is_empty()
    doc = stack.last()
    assert doc.name() == source_filename
    doc.update(meta)
    doc.normalize()
    doc.move_to_dir(target)
    return web.json_response({"path": doc.get_path()})


app.router.add_get("/", handle_docs)
app.router.add_get("/dfile/{name}", handle_dfile)

app.router.add_get("/pile", handle_pile)
app.router.add_get("/pfile/{name}", handle_pfile)

app.router.add_get("/app/list", handle_app_list)
app.router.add_get("/app/last", handle_app_last)
app.router.add_post("/app/refile", handle_app_refile)

app.router.add_static("/static", res("static"), show_index=True)
app.router.add_static("/js", res("static/js"), show_index=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default=33882, type=int)
    parser.add_argument("-d", "--daemon", default=False, action="store_true")
    args = parser.parse_args()
    if args.daemon:
        import sys

        sys.stderr = open(path_log.joinpath("piled.err"), "a")
        sys.stdout = open(path_log.joinpath("piled.out"), "a")
    print(args)
    print(path_docs, path_pile)
    web.run_app(app, port=args.port)
