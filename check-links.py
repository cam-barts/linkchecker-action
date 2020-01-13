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
bad_links = []

for dirpath, dirnames, filenames in os.walk("."):
    for filename in [f for f in filenames if f.endswith(".md")]:
        markdowns[os.path.join(dirpath, filename)] = markdown_link_extractor.getlinks(get_markdown(os.path.join(dirpath, filename)))

for file, links_list in markdowns.items():
    for link in links_list:
        try:
            resp = requests.get(link)
            if resp.status_code != 200:
                bad_links.append((link, file))
        except requests.exceptions.MissingSchema:
            pass
        except:
            bad_links.append((link, file))

for item in bad_links:
    link = item[0]
    file = item[1]
    try:
        resp = requests.get(link)
        if resp.status_code != 200:
            print(f"{link} in {file} received status code {resp.status_code}")
    except Exception as e:
        print(f"{link} in {file} received the following exception: {e}")
sys.exit(exit_code)