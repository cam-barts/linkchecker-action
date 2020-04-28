import markdown
import re
import requests
import os
import os.path
import sys
import aiohttp
import asyncio
import json
import datetime

EXCLUDE_FILES = os.environ.get("exclude_files")
INCLUDE_FILES = os.environ.get("include_files")

exit_code = 0


def get_include_exclude_files():
    """Parse file inclusions and exclusions from environmental variables"""
    if EXCLUDE_FILES and INCLUDE_FILES:
        print("Please only include an inclusion or an exclusion variable in the workflow")
        exit(2)
    elif EXCLUDE_FILES:
        return (EXCLUDE_FILES.split(','), [])
    elif INCLUDE_FILES:
        return ([], INCLUDE_FILES.split(','))
    else:
        return ([],[])


def get_exclusion_list():
    try:
        with open('.github/exclude_links.json') as infile:
            return json.load(infile)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {}

def get_links_from_markdown(string):
    """return a list with markdown links"""
    html = markdown.markdown(string, output_format='html')
    links = list(set(re.findall(r'href=[\'"]?([^\'" >]+)', html)))
    links = list(filter(lambda l: l[0] != "{", links))
    return links


def get_markdown_content(path):
    with open(path) as f:
        return f.read()

def get_markdown_files():
    e_files, i_files = get_include_exclude_files()
    markdowns = {}
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in [f for f in filenames if f.endswith(".md")]:
            if filename in i_files or filename not in e_files:
                markdowns[os.path.join(dirpath, filename)] = get_links_from_markdown(
                    get_markdown_content(os.path.join(dirpath, filename))
                )
    return markdowns

bad_links = []
timeout = aiohttp.ClientTimeout(total=10)

async def fetch_url(session, url):
    try:
        async with session.get(url, timeout=timeout) as response:
            return response.status
    except:
            return "Error (Likely 404)"

async def get_link_statuses():
    markdowns = get_markdown_files()
    exclusion_list = get_exclusion_list()
    async with aiohttp.ClientSession() as session:
        for filename, links_list in markdowns.items():
            for link in links_list:
                if link[0] != "#":
                    try:
                        if link not in exclusion_list[filename]:
                            code = await fetch_url(session, link)
                            if code != 200:
                                bad_links.append((filename, link, code))
                    except KeyError:
                        code = await fetch_url(session, link)
                        if code != 200:
                            bad_links.append((filename, link, code))

loop = asyncio.get_event_loop()
loop.run_until_complete(get_link_statuses())


def build_exclusion_list():
    el = get_exclusion_list()
    markdowns = get_markdown_files()
    new_items = []
    for link in bad_links:
        filename = link[0]
        url = link[1] 
        code = link[2]
        if not el.get(filename, 0):
            el[filename] = {}
        if not el[filename].get(url, 0):
            item = {
                "code" : code,
                "time": datetime.datetime.now().isoformat(),
                "reason": ""
            } 
            el[filename][url] = item
            new_items.append({url: item})
    with open('exclude_links.json', 'w') as outfile:
        json.dump(el, outfile)
    return new_items


new_items = build_exclusion_list()
if len(new_items):
    exit_code = 1 
    for item in new_items:
        print(item)

sys.exit(exit_code)