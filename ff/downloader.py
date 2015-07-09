#!/usr/bin/python

import sys, getopt
import pdfkit
from fiction import *

root = "http://www.fanfiction.net"

def get_chapters(url=None, storyid=None):
    if url is None:
        if storyid is None:
            print "Either url or storyid must be provided."
        else:
            url = root + "/s/%d" % storyid
    story = Story(url)
    chapter_gen = story.get_chapters()
    chapters = []
    for chapter in chapter_gen:
        chapters.append(chapter)
    return chapters

def get_total_story_html(chapter_list):
    html = ""
    for chapter in chapter_list:
        html += chapter.raw_text
        html += '\n'
    return html

def download_pdf(url, output):
    if output[-4:] != ".pdf":
        output += ".pdf"
    chapters = get_chapters(url)
    html = get_total_story_html(chapters)
    pdfkit.from_string(html, output)

def download_pdf_id(storyid, output):
    url = root + "/s/%d" % storyid
    download_pdf(url, output)

def main(argv):
    url = ''
    storyid = 0
    output = 'out.pdf'
    help_string = """
    downloader.py -h
    downloader.py -u [url] -o [output]
    downloader.py -s [storyid] -o [output]
    """
    try:
        opts, args = getopt.getopt(argv, "hu:o:s:", ["url=", "output=", "storyid="])
    except getopt.GetoptError:
        print "downloader.py -u <url> -o <outputfile>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print "downloader.py -u <url> -o <outputfile>"
            sys.exit(2)
        elif opt in ("-u", "--url"):
            url = arg
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-s", "--storyid"):
            storyid = int(arg)
    if len(url) > 0:
        print "Downloading fanfiction to %s" % output
        download_pdf(url, output)
    elif storyid != 0:
        print "Downloading fanfiction to %s" % output
        download_pdf_id(storyid, output)
    else:
        print "url or storyid not provided"
        print help_string

if __name__ == "__main__":
    main(sys.argv[1:])
