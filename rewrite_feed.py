#!/usr/bin/env python3
"""Fetch the MainBranch Extended platform RSS and rewrite it with the
iTunes tags Apple Podcasts Connect requires (author, owner, category),
which the platform feed does not emit. Output: feed.xml for GitHub Pages."""
import re, sys, urllib.request
import xml.etree.ElementTree as ET

SOURCE = "https://muse.ai/podcasts/feed/1311603018703153/788213e2-188d-41de-a1c3-17dd14d9129e"
OUT = sys.argv[1] if len(sys.argv) > 1 else "feed.xml"
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
ET.register_namespace("itunes", ITUNES_NS)
ET.register_namespace("", "")

AUTHOR = "Andrea Griffiths"
OWNER_EMAIL = "mainbranchextended@gmail.com"
CATEGORY = "Technology"

def q(tag):
    return f"{{{ITUNES_NS}}}{tag}"

req = urllib.request.Request(SOURCE, headers={"User-Agent": "MainBranchFeedProxy/1.0"})
raw = urllib.request.urlopen(req, timeout=60).read()
root = ET.fromstring(raw)
channel = root.find("channel")
assert channel is not None, "no channel in feed"

def get_text(tag):
    el = channel.find(q(tag))
    return el.text if el is not None else None

def set_text(tag, text):
    el = channel.find(q(tag))
    if el is None:
        el = ET.SubElement(channel, q(tag))
    el.text = text

# author / type / summary / owner / category -- inserted right after
# <description> so channel metadata precedes all <item> elements
def insert_after_description(tag, text=None, attrs=None):
    el = channel.find(q(tag))
    if el is None:
        el = ET.Element(q(tag))
        if text is not None:
            el.text = text
        for k, v in (attrs or {}).items():
            el.set(k, v)
        desc_el = channel.find("description")
        idx = list(channel).index(desc_el) + 1 if desc_el is not None else 0
        channel.insert(idx, el)
    return el

desc_text = channel.findtext("description")
insert_after_description("author", AUTHOR)
insert_after_description("type", "episodic")
if desc_text and not get_text("summary"):
    insert_after_description("summary", desc_text)
owner = insert_after_description("owner")
name = owner.find(q("name"))
if name is None:
    name = ET.SubElement(owner, q("name"))
name.text = AUTHOR
email = owner.find(q("email"))
if email is None:
    email = ET.SubElement(owner, q("email"))
email.text = OWNER_EMAIL
if channel.find(q("category")) is None:
    cat = ET.Element(q("category"))
    cat.set("text", CATEGORY)
    desc_el = channel.find("description")
    idx = list(channel).index(desc_el) + 1 if desc_el is not None else 0
    # place category right after owner for tidy metadata grouping
    owner_el = channel.find(q("owner"))
    idx = list(channel).index(owner_el) + 1 if owner_el is not None else idx
    channel.insert(idx, cat)

# normalize explicit: Apple wants yes/no/clean, feed has "false"
exp = channel.find(q("explicit"))
if exp is not None and (exp.text or "").strip().lower() in ("false", "0"):
    exp.text = "no"

tree = ET.ElementTree(root)
tree.write(OUT, encoding="utf-8", xml_declaration=True)

# sanity: report item count and injected tags
check = open(OUT, encoding="utf-8").read()
items = len(re.findall(r"<item>", check))
tags = {t: f"<itunes:{t}>" in check or f"<itunes:{t} " in check for t in ["author", "owner", "category", "type", "summary"]}
print(f"items={items} tags={tags}")
