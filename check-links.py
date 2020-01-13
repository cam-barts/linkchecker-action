import markdown_link_extractor
import requests

import os
import os.path

import sys


exit_code = 0
def get_markdown(path):
    with open(path) as f:
        return f.read()

markdowns = {}

for dirpath, dirnames, filenames in os.walk("."):
    for filename in [f for f in filenames if f.endswith(".md")]:
        markdowns[os.path.join(dirpath, filename)] = markdown_link_extractor.getlinks(get_markdown(os.path.join(dirpath, filename)))


for file, links_list in markdowns.items():
    for link in links_list:
        try:
            resp = requests.get(link)
            if resp.status_code != 200:
                print(f'{link} got status code {resp.status_code} ({file})')
                exit_code = 1
        except requests.exceptions.MissingSchema:
            pass
        except:
            print(f'Error in url: {link} ({file})')
            exit_code = 1

sys.exit(exit_code)