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
from colorama import Fore, Back, Style

EXCLUDE_FILES = os.environ.get("exclude_files")
INCLUDE_FILES = os.environ.get("include_files")

exit_code = 0


def get_include_exclude_files():
    """Parse file inclusions and exclusions from environmental variables"""
    if EXCLUDE_FILES and INCLUDE_FILES:
        print(f"{Back.RED}{Fore.WHITE}Please only include an inclusion or an exclusion variable in the workflow{Style.RESET_ALL}")
        exit(2)
    elif EXCLUDE_FILES:
        print(f"{Back.BLACK}{Fore.RED}Excluding the following files:{Style.RESET_ALL}")
        for filename in EXCLUDE_FILES.split(","):
            print(filename)
        return (EXCLUDE_FILES.split(","), [])
    elif INCLUDE_FILES:
        print(f"{Back.BLACK}{Fore.RED}Including only the following files:{Style.RESET_ALL}")
        for filename in INCLUDE_FILES.split(","):
            print(filename)
        return ([], INCLUDE_FILES.split(","))
    else:
        return ([], [])


e_files, i_files = get_include_exclude_files()


def get_exclusion_list():
    """If there is a link exclusion list present, import it"""
    try:
        with open(".github/exclude_links.json") as infile:
            config = json.load(infile)
            print(f"{Back.CYAN}Recived the following Link Exclusion List:{Style.RESET_ALL}")
            print(config)
            return config
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        print(f"{Back.CYAN}{Fore.RED}Link Exclusion List not set{Style.RESET_ALL}")
        return {}

exclusion_list = get_exclusion_list()

def get_markdown_links_from_path(path):
    with open(path) as f:
        content = f.read()
    html = markdown.markdown(content, output_format="html")
    links = list(set(re.findall(r'href=[\'"]?([^\'" >]+)', html)))
    links = list(filter(lambda l: l[0] != "{", links))
    return links



def get_markdown_files():
    """Gets dictionary with keys being markdown files and values being a list of links in that markdown file"""
    markdowns = {}
    for dirpath, dirnames, filenames in os.walk("."):
        if len(i_files):
            files_to_check = [f for f in filenames if f in i_files]
        else:
            files_to_check = [f for f in filenames if f.endswith(".md")]

        for filename in files_to_check:
            if filename not in e_files:
                path = os.path.join(dirpath, filename)
                markdowns[path] = get_markdown_links_from_path(path)

    return markdowns


bad_links = []

async def fetch_url(session, url, timeout=10):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            return response.status
    except:
        return str(sys.exc_info()[0])


async def get_link_statuses():
    markdowns = get_markdown_files()
    async with aiohttp.ClientSession() as session:
        for filename, links_list in markdowns.items():
            for link in links_list:
                if link[0] != "#":
                    try:
                        if link not in exclusion_list[filename]:
                            code = await shield(fetch_url(session, link))
                            if code != 200:
                                print(f"{Back.RED}{Fore.WHITE}{link} returned status code: {code}{Style.RESET_ALL}")
                                bad_links.append((filename, link, code))
                    except KeyError:
                        code = await fetch_url(session, link)
                        if code != 200:
                            print(f"{Back.RED}{Fore.WHITE}{link} returned status code: {code}{Style.RESET_ALL}")
                            bad_links.append((filename, link, code))



loop = asyncio.get_event_loop()
loop.run_until_complete(get_link_statuses())


def build_exclusion_list():
    markdowns = get_markdown_files()
    new_items = []
    for link in bad_links:
        filename = link[0]
        url = link[1]
        code = link[2]
        if not exclusion_list.get(filename, 0):
            exclusion_list[filename] = {}
        if not exclusion_list[filename].get(url, 0):
            item = {
                "code": code,
                "time": datetime.datetime.now().isoformat(),
                "reason": "",
            }
            exclusion_list[filename][url] = item
            new_items.append({url: item})
    with open("exclude_links.json", "w") as outfile:
        json.dump(exclusion_list, outfile)
    return new_items


new_items = build_exclusion_list()
if len(new_items):
    exit_code = 1
    for item in new_items:
        print(item)

# sys.exit(exit_code)
os.environ["EXIT_CODE"] = str(exit_code)
