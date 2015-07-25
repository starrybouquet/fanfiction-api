__author__ = 'Samson Danziger'

import pdfkit
from ebooklib import epub

root = "https://www.fanfiction.net"

def _get_total_story_html(story):
    """ Concatenate story text html, with chapter numbers as headings.Chapter headings are incremental.
    :param chapter_list: A list of chapters to concatenate.
    :return:
    """
    html = ""
    for i, chapter in enumerate(story.get_chapters()):
        html += '<h2>Chapter %s</h2>\n' % str(chapter.number)  # couldn't use %d here for some reason
        html += chapter.raw_text
        html += '</br>' * 10  # new chapters after a break
    return html


def download_pdf(story, output='', message=True):
    """ Download a story to pdf.
    :type message: bool
    """
    if output == '':
        output = "%s_by_%s" % (story.title, story.author)
        output = output.replace(' ', '-')
    if output[-4:].lower() != ".pdf":  # output should be a pdf file
        output += ".pdf"
    if message:
        print 'Downloading \'%s\' to %s' % (story.title, output)
    html = _get_total_story_html(story)
    pdfkit.from_string(html, output)

def download_epub(story, output='', message=True):
    """ Download a story to ePub.
    :type message: bool
    """
    if output == '':
        output = "%s_by_%s" % (story.title, story.author)
        output = output.replace(' ', '-')
    if output[-5:].lower() != ".epub":  # output should be a pdf file
        output += ".epub"
    if message:
        print 'Downloading \'%s\' to %s' % (story.title, output)
    # actual book build
    book = epub.EpubBook()
    # set metadata
    book.set_identifier(str(story.id))
    book.set_title(story.title)
    book.set_language('en')
    book.add_author(story.author)
    # create chapters
    toc = []
    section = []
    spine = ['cover', 'nav']
    for chapter in story.get_chapters():
        # add chapters
        c = epub.EpubHtml(title=chapter.title, file_name='chapter_%d.xhtml'%(chapter.number), lang='en')
        #c.add_link(href='style/default.css', rel='stylesheet', type='text/css')
        c.content = chapter.raw_text

        if message:
            print 'Adding Chapter %d: %s' % (chapter.number, chapter.title)

        book.add_item(c)
        spine.append(c)
        toc.append(c)
    
    book.toc = toc
    print toc
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = spine

    # write epub
    epub.write_epub(output, book)
