__author__ = 'Samson Danziger'

from weasyprint import HTML
from ebooklib import epub
import tempfile
import os, shutil
import codecs

root = "https://www.fanfiction.net"

def _get_download_name(story):
    s = "%s_by_%s" % (story.title, story.author)
    s = s.replace(' ', '-')
    return s


def _add_extension(name, ext):
    if not name.endswith('.%s' % (ext)):
        name += '.%s' % (ext)
    return name



def download_pdf(story, output='', message=True):
    """ Download a story to pdf.
    :type message: bool
    """
    if output == '':
        output = _get_download_name(story)
    output = _add_extension(output, 'pdf')
    if message:
        print 'Downloading \'%s\' to %s...' % (story.title, output)
    html = ''
    for chapter in story.get_chapters():
        if message:
            print 'Adding %s...' % (chapter.title)
        html += '<h2>Chapter %d: %s</h2>' % (chapter.number, chapter.title)
        html += chapter.raw_text
        html += '</br>' * 10
    if message:
        print 'Compiling PDF...'

    # This turned out not to work on the command line as it needed an X interface.
    #pdfkit.from_string(html, output)
    # Instead trying with weasyprint
    content = unicode(html.strip(codecs.BOM_UTF8), 'utf-8')
    h = HTML(content)
    h.write_pdf(output)
    

def download_epub(story, output='', message=True):
    """ Download a story to ePub.
    :type message: bool
    """
    if output == '':
        output = _get_download_name(story)
    output = _add_extension(output, 'epub')
    if message:
        print 'Downloading \'%s\' to %s...' % (story.title, output)
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
    spine = ['nav']
    for chapter in story.get_chapters():
        if message:
            print 'Adding Chapter %d: %s' % (chapter.number, chapter.title)
        # add chapters
        c = epub.EpubHtml(title=chapter.title, file_name='chapter_%d.xhtml'%(chapter.number), lang='en')
        #c.add_link(href='style/default.css', rel='stylesheet', type='text/css')
        c.content = chapter.raw_text

        book.add_item(c)
        spine.append(c) # no idea what this does
        toc.append(c) # add the chapter to the table of contents

    book.toc = toc
    book.add_item(epub.EpubNcx()) # add some other stuff
    book.add_item(epub.EpubNav())
    book.spine = spine

    if message:
        print 'Compiling ePub...'
    # write epub
    epub.write_epub(output, book)

def download_mobi(story, output='', message=True):
    if output == '':
        output = _get_download_name(story)
    output = _add_extension(output, 'mobi')
    temp_storage = tempfile.gettempdir()
    current = os.system('pwd')
    download_epub(story, '%s/temp.epub' % (temp_storage), message)
    if message:
        print 'Converting to mobi...'
    os.system('kindlegen %s/temp.epub -c2 -o convert.mobi' % (temp_storage))
    if message:
        print 'Moving to %s...' % (output)
    shutil.move('%s/convert.mobi' % (temp_storage), '%s' % (output))

def download_txt(story, output='', message=True):
    if output == '':
        output = _get_download_name(story)
    output = _add_extension(output, 'txt')
    text = ''
    for chapter in story.get_chapters():
        if message:
            print 'Adding %s...' % (chapter.title)
        text += 'Chapter %d: %s\n' % (chapter.number, chapter.title)
        text += chapter.text
        text += '\n' * 10
    if message:
        print 'Writing to file...'
    f = open(output, 'wb')
    f.write(text)
    f.close()
    if message:
        print 'Done!'


def download(story, output='', message=True, ext=''):
    try:
        ext = ext.lower()
        output = '%s.%s' % (output, ext)
        if ext == 'pdf':
            download_pdf(story, output, message)
        elif ext == 'epub':
            download_epub(story, output, message)
        elif ext == 'mobi':
            download_mobi(story, output, message)
        elif ext == 'txt' or ext == 'text':
            download_txt(story, output, message)
        else:
            print 'That functionality does not yet exist.'
    except KeyboardInterrupt:
        print 'Stopping download.'
