#!/usr/bin/python

import sys, getopt
import pdfkit
from fiction import *

root = "https://www.fanfiction.net"


def get_chapters(story):
    chapter_gen = story.get_chapters()
    chapters = []
    for chapter in chapter_gen:
        chapters.append(chapter)
    return chapters


def get_total_story_html(chapter_list):
    html = ""
    for i in range(len(chapter_list)):
        html += '<h2>Chapter %s</h2>\n' % str(i + 1)  # couldn't use %d here for some reason
        html += chapter_list[i].raw_text
        html += '</br>' * 10  # new chapters after a break
    return html


def download_pdf(story, output):
    chapters = get_chapters(story)
    html = get_total_story_html(chapters)
    pdfkit.from_string(html, output)


def main(argv):
    url = ''
    storyid = 0
    output = ''
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
        story = Story(url=url)
    elif storyid != 0:
        story = Story(id=storyid)
    else:
        print "url or storyid not provided"
        print help_string
    if output == '':
        output = "%s_by_%s" % (story.title, story.author)
        output = output.replace(' ', '-')
        if output[-4:] != ".pdf":  # output should be a pdf file
            output += ".pdf"
    print "Downloading %s to %s" % (story.title, output)
    download_pdf(story, output)


if __name__ == "__main__":
    main(sys.argv[1:])
