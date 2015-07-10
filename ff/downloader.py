__author__ = 'Samson Danziger'

import pdfkit

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


def download_pdf(story, output, message=True):
    """
    :type message: bool
    """
    if output == '':
        output = "%s_by_%s" % (story.title, story.author)
        output = output.replace(' ', '-')
    if output[-4:] != ".pdf":  # output should be a pdf file
        output += ".pdf"
    if message:
        print 'Downloading \'%s\' to %s' % (story.title, output)
    chapters = get_chapters(story)
    html = get_total_story_html(chapters)
    pdfkit.from_string(html, output)
