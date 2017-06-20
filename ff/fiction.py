import re, requests, bs4, unicodedata
from datetime import timedelta, date
from time import time
import ff
# Constants
root = 'https://www.fanfiction.net'

# REGEX MATCHES

# STORY REGEX
_STORYID_REGEX = r"var\s+storyid\s*=\s*(\d+);"
_CHAPTER_REGEX = r"var\s+chapter\s*=\s*(\d+);"
_CHAPTERS_REGEX = r"Chapters:\s*(\d+)\s*"
_WORDS_REGEX = r"Words:\s*([\d,]+)\s*"
_TITLE_REGEX = r"var\s+title\s*=\s*'(.+)';"
_DATEP_REGEX = r"Published:\s*<span.+?='(\d+)'>"
_DATEU_REGEX = r"Updated:\s*<span.+?='(\d+)'>"

# USER REGEX
_USERID_REGEX = r"var\s+userid\s*=\s*(\d+);"
_AUTHOR_REGEX = r"href='/u/\d+/(.+?)'"
_USERID_URL_EXTRACT = r".*/u/(\d+)"
_USERNAME_REGEX = r"<link rel=\"canonical\" href=\"//www.fanfiction.net/u/\d+/(.+)\">"
_USER_STORY_COUNT_REGEX = r"My Stories\s*<span class=badge>(\d+)<"
_USER_FAVOURITE_COUNT_REGEX = r"Favorite Stories\s*<span class=badge>(\d+)<"
_USER_FAVOURITE_AUTHOR_COUNT_REGEX = r"Favorite Authors\s*<span class=badge>(\d+)<"

# Useful for generating a review URL later on
_STORYTEXTID_REGEX = r"var\s+storytextid\s*=\s*storytextid=(\d+);"

# REGEX that used to parse reviews page
_REVIEW_COMPLETE_INFO_REGEX = r"img class=.*?</div"
_REVIEW_USER_NAME_REGEX = r"> *([^< ][^<]*)<"
_REVIEW_CHAPTER_REGEX = r"<small style=[^>]*>([^<]*)<"
_REVIEW_TIME_REGEX = r"<span data[^>]*>([^<]*)<"
_REVIEW_TEXT_REGEX = r"<div[^>]*>([^<]*)<"

# Used to parse the attributes which aren't directly contained in the
# JavaScript and hence need to be parsed manually
_NON_JAVASCRIPT_REGEX = r'Rated:(.+)'
_HTML_TAG_REGEX = r'<.*?>'

# Needed to properly decide if a token contains a genre or a character name
# while manually parsing data that isn't directly contained in the JavaScript
_GENRES = [
    'General', 'Romance', 'Humor', 'Drama', 'Poetry', 'Adventure', 'Mystery',
    'Horror', 'Parody', 'Angst', 'Supernatural', 'Suspense', 'Sci-Fi',
    'Fantasy', 'Spiritual', 'Tragedy', 'Western', 'Crime', 'Family', 'Hurt',
    'Comfort', 'Friendship'
]

# TEMPLATES
_STORY_URL_TEMPLATE = 'https://www.fanfiction.net/s/%d'
_CHAPTER_URL_TEMPLATE = 'https://www.fanfiction.net/s/%d/%d'
_USERID_URL_TEMPLATE = 'https://www.fanfiction.net/u/%d'

_DATE_COMPARISON = date(1970, 1, 1)


def _parse_string(regex, source):
    """Returns first group of matched regular expression as string."""
    return re.search(regex, source).group(1)


def _parse_integer(regex, source):
    """Returns first group of matched regular expression as integer."""
    match = re.search(regex, source).group(1)
    match = match.replace(',', '')
    return int(match)


def _parse_date(regex, source):
    xutime = _parse_integer(regex, source)
    delta = timedelta(seconds=xutime)
    return _DATE_COMPARISON + delta


def _unescape_javascript_string(string_):
    """Removes JavaScript-specific string escaping characters."""
    return string_.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')


def _visible_filter(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    element = unicodedata.normalize('NFKD', element).encode('ascii', 'ignore')
    if re.match(r'<!--.*-->', str(element)):
        return False
    return True


class Story(object):
    def __init__(self, url=None, id=None):
        """ A story on fanfiction.net

        If both url, and id are provided, url is used.

        :type id: int
        :param url: The url of the story.
        :param id: The story id of the story.

        Attributes:
            id  (int):              The story id.
            timestamp:              The timestamp of moment when data was consistent with site
            chapter_count (int);    The number of chapters.
            word_count (int):       The number of words.
            author_id (int):        The user id of the author.
            title (str):            The title of the story.
            date_published (date):  The date the story was published.
            date_updated (date):    The date of the most recent update.
            author (str):           The name of the author.
            rated (str):            The story rating.
            language (str):         The story language.
            genre [str]:            The genre(s) of the story.
            characters [str]:       The character(s) of the story.
            reviews (int):          The number of reviews of the story.
            favs (int):             The number of user which has this story in favorite list
            followers (int):        The number of users who follow the story
            complete (bool):        True if the story is complete, else False.
        """
        self.id = id
        if id is None:
            if url is None:
                raise ValueError("There must be a url or an id.")
            else:
                self.id = _parse_integer(_STORYID_REGEX, source)

    def _init_int_value_from_token(self, tokens, prefix):
        for token in tokens:
            if token.startswith(prefix):
                # Replace comma in case the number is greater than 9999
                return int(token.split()[1].replace(',', ''))
        # value wasn't found 
        return 0


    def download_data(self):
        self.timestamp = time()
        url = _STORY_URL_TEMPLATE % int(self.id)
        source = requests.get(url)
        source = source.text
        # Easily parsable and directly contained in the JavaScript, lets hope
        # that doesn't change or it turns into something like below
        try:
            # if there is only 1 chapter
            self.date_updated = _parse_date(_DATEU_REGEX, source)
            self.chapter_count = _parse_integer(_CHAPTERS_REGEX, source)
        except AttributeError:
            self.chapter_count = 1
            self.date_updated = None

        self.word_count = _parse_integer(_WORDS_REGEX, source)
        self.author_id = _parse_integer(_USERID_REGEX, source)
        self.title = _unescape_javascript_string(_parse_string(_TITLE_REGEX, source).replace('+', ' '))
        self.date_published = _parse_date(_DATEP_REGEX, source)
        self.author = _unescape_javascript_string(_parse_string(_AUTHOR_REGEX, source))

        if self.date_updated is None:
            self.date_updated = self.date_published

        # Tokens of information that aren't directly contained in the
        # JavaScript, need to manually parse and filter those
        tokens = [token.strip() for token in
                  re.sub(_HTML_TAG_REGEX, '', _parse_string(_NON_JAVASCRIPT_REGEX, source)).split('-')]

        # Both tokens are constant and always available
        self.rated = tokens[0].replace('Fiction', '').strip()
        self.language = tokens[1]

        # After those the remaining tokens are uninteresting and looking for
        # either character or genre tokens is useless
        token_terminators = ['Chapters: ', 'Words: ', 'Reviews: ', 'Favs: ', 'Follows: ', 'Updated: ', 'Published: ', 'id: ']

        # Check if tokens[2] contains the genre
        if tokens[2] in _GENRES or '/' in tokens[2] and all(token in _GENRES for token in tokens[2].split('/')):
            self.genre = tokens[2].split('/')
            # tokens[2] contained the genre, check if next token contains the
            # characters
            if not any(tokens[3].startswith(terminator) for terminator in token_terminators):
                self.characters = tokens[3].split(',')
            else:
                # No characters token
                self.characters = []
        elif any(tokens[2].startswith(terminator) for terminator in token_terminators):
            # No genre and/or character was specified
            self.genre = []
            self.characters = []
            # tokens[2] must contain the characters since it wasn't a genre
            # (check first clause) but isn't either of "Reviews: ", "Updated: "
            # or "Published: " (check previous clause)
        else:
            self.characters = tokens[2].split(',')

        self.reviews = self._init_int_value_from_token(tokens, 'Reviews: ')
        self.favs = self._init_int_value_from_token(tokens, 'Favs: ')
        self.followers = self._init_int_value_from_token(tokens, 'Follows: ')

        # complete is directly contained in the tokens as a single-string
        if 'Status: Complete' in tokens:
            self.complete = True
        else:
            # FanFiction.Net calls it "In-Progress", I'll just go with that
            self.complete = False

    def get_chapters(self):
        """
        A generator for all chapters in the story.
        :return: A generator to fetch chapter objects.
        """
        try:
            for number in range(1, self.chapter_count + 1):
                yield Chapter(story_id=self.id, chapter=number)
        except KeyboardInterrupt:
            print("!-- Stopped fetching chapters")

    def get_user(self):
        """
        :return: The user object of the author of the story.
        """
        return User(id=self.author_id)

    def print_info(self, attrs=['title', 'id', 'author', 'author_id', 'chapter_count', 'word_count', 'date_published',
                                'date_updated', 'rated', 'complete', 'language', 'genre', 'characters', 'reviews', 'favs', 'followers']):
        """
        Print information held about the story.
        :param attrs: A list of attribute names to print information for.
        :return: void
        """
        for attr in attrs:
            print("%12s\t%s" % (attr, getattr(self, attr)))

    def get_reviews(self):
        """
        A generator for all reviews in the story.
        :return: A generator to fetch reviews.
        """
        return ReviewsGenerator(self.id)



    def download(self, output='', message=True, ext=''):
        ff.download(self, output=output, message=message, ext=ext)

    # Method alias which allows the user to treat the get_chapters method like
    # a normal property if no manual opener is to be specified.
    chapters = property(get_chapters)

class ReviewsGenerator(object):
    """
    Class that generates review in chronological order
    Attributes:
        base_url            (int):      storys review url without specified page number
        page_number         (int):      number of current review page
        reviews_cache       List(str):  list of already downloaded  (and partially processed) reviews 
        skip_reviews_number (int):      length of already processed review from review_cache
    """
    def __init__(self, story_id, chapter=0):
        """
        If chapter unspecified then generator generates review for all chapters
        """
        self.story_id = story_id
        self.base_url = root + '/r/' + str(story_id) + '/' + str(chapter) + '/'

    def __iter__(self):
        self.page_number = 0
        self.reviews_cache = []
        self.skip_reviews_number = 0
        return self

    def __next__(self):
        self.skip_reviews_number += 1
        if len(self.reviews_cache) >= self.skip_reviews_number:
            return Review(self.story_id, self.reviews_cache[self.skip_reviews_number - 1])

        self.page_number += 1
        page = self._downloadReviewPage(self.page_number)
        self.reviews_cache = re.findall(_REVIEW_COMPLETE_INFO_REGEX, page, re.DOTALL)

        if len(self.reviews_cache) == 0:
            raise StopIteration

        self.skip_reviews_number = 1
        return Review(self.story_id, self.reviews_cache[0])

    def _downloadReviewPage(self, page_number):
        url = self.base_url + str(page_number) + '/'
        return requests.get(url).text



class Review(object):
    """
    A single review of fanfiction story, on fanfiction.net
    Attributes:
        story_id    (int):  story ID
        user_id     (int):  ID of user who submited review (may be None if review is anonymous)
        user_name   (str):  user name (or pseudonym for anonymous review)
        chapter     (str):  chapter name
        time_ago    (str):  how much time passed since review submit (format may be inconsistent with what you see in browser just because fanfiction.net sends different pages depend on do you download page from browser or from console/that library
        text        (str):  review text
    """
    def __init__(self, story_id, unparsed_info):
        """
        That method should not be invoked outside of Story and Chapter classes
        :param story_id         (int):  story ID
        :param unparsed_info    (int):  string that contain the rest info
        """
        self.story_id = story_id
        self.user_name = _parse_string(_REVIEW_USER_NAME_REGEX, unparsed_info)
        self.chapter = _parse_string(_REVIEW_CHAPTER_REGEX, unparsed_info)
        self.text = _parse_string(_REVIEW_TEXT_REGEX, unparsed_info)

        self.time_ago = _parse_string(_REVIEW_TIME_REGEX, unparsed_info)

        # fanfiction.net provide strange format, instead of '8 hours ago' it show '8h'
        # so let's add ' ago' suffix if review submitted hours or minutes ago
        if self.time_ago[-1] == 'h' or self.time_ago[-1] == 'm':
            self.time_ago += ' ago'

        if re.search(_USERID_URL_EXTRACT, unparsed_info) == None:
            self.user_id = None
        else:
            self.user_id = _parse_integer(_USERID_URL_EXTRACT, unparsed_info)


class Chapter(object):
    def __init__(self, url=None, story_id=None, chapter=None):
        """ A single chapter in a fanfiction story, on fanfiction.net

        :param url: The url of the chapter.
        :param story_id: The story id of the story of the chapter.
        :param chapter: The chapter number of the story.

        Attributes:
            story_id    (int):  Story ID
            number      (int):  Chapter number
            story_text_id (int):    ?
            title       (str):  Title of the chapter, or title of the story.
            raw_text    (str):  The raw HTML of the story.
            text_list   List(str):  List of unicode strings for each paragraph.
            text        (str):  Visible text of the story.
        """

        if url is None:
            if story_id is None:
                print('A URL or story id must be entered.')
            elif chapter is None:
                print('Both a stroy id and chapter number must be provided')
            elif story_id and chapter:
                url = _CHAPTER_URL_TEMPLATE % (story_id, chapter)

        source = requests.get(url)
        source = source.text
        self.story_id = _parse_integer(_STORYID_REGEX, source)
        self.number = _parse_integer(_CHAPTER_REGEX, source)
        self.story_text_id = _parse_integer(_STORYTEXTID_REGEX, source)

        soup = bs4.BeautifulSoup(source, 'html5lib')
        select = soup.find('select', {'name': 'chapter'})
        if select:
            # There are multiple chapters available, use chapter's title
            self.title = select.find('option', selected=True).string.split(None, 1)[1]
        else:
            # No multiple chapters, one-shot or only a single chapter released
            # until now; for the lack of a proper chapter title use the story's
            self.title = _unescape_javascript_string(_parse_string(_TITLE_REGEX, source)).decode()
        soup = soup.find('div', id='storytext')
        # Try to remove AddToAny share buttons
        try:
            soup.find('div', {'class': lambda class_: class_ and 'a2a_kit' in class_}).extract()
        except AttributeError:
            pass
        # Normalize HTML tag attributes
        for hr in soup('hr'):
            del hr['size']
            del hr['noshade']

        self.raw_text = soup.decode()

        texts = soup.findAll(text=True)
        self.text_list = list(filter(_visible_filter, texts))
        self.text = '\n'.join(self.text_list)

    def get_reviews(self):
        """
        A generator for all reviews for that chapter
        :return: A generator to fetch reviews.
        """
        return ReviewsGenerator(self.story_id, self.number)

class User(object):
    def __init__(self, url=None, id=None):
        if url is None:
            if id is None:
                raise ValueError("Either url or id must be specified.")
            else:
                self.id = id
        else:
            self.id = _parse_integer(_USERID_URL_EXTRACT, url)

    def download_data(self):
        self.timestamp = time()
        url = _USERID_URL_TEMPLATE % self.id
        source = requests.get(url)
        source = source.text
        self._soup = bs4.BeautifulSoup(source, 'html5lib')
        self.url = url
        self.username = _parse_string(_USERNAME_REGEX, source)
        self.story_count = _parse_integer(_USER_STORY_COUNT_REGEX, source)
        self.favourite_count = _parse_integer(_USER_FAVOURITE_COUNT_REGEX, source)
        try:
            self.favourite_author_count = _parse_integer(_USER_FAVOURITE_AUTHOR_COUNT_REGEX, source)
        except AttributeError:
            self.favourite_author_count = None

    def get_stories(self):
        """
        Get the stories written by this author.
        :return: A generator for stories by this author.
        """
        xml_page_source = requests.get(root + '/atom/u/%d/' % self.id)
        xml_page_source = xml_page_source.text
        xml_soup = bs4.BeautifulSoup(xml_page_source)
        entries = xml_soup.findAll('link', attrs={'rel': 'alternate'})
        for entry in entries:
            story_url = entry.get('href')
            yield Story(story_url)

    def get_favourite_stories(self):
        """
        Get the favourite stories of this author.
        :return: A Story generator for the favourite stories for this author.
        """
        favourite_stories = self._soup.findAll('div', {'class': 'favstories'})
        for story in favourite_stories:
            link = story.find('a', {'class': 'stitle'}).get('href')
            link = root + link
            yield Story(link)

    def get_favourite_authors(self):
        """
        :return: User generator for the favourite authors of this user.
        """
        tables = self._soup.findAll('table')
        table = tables[-1]
        author_tags = table.findAll('a', href=re.compile(r".*/u/(\d+)/.*"))
        for author_tag in author_tags:
            author_url = author_tag.get('href')
            author_url = root + author_url
            yield User(author_url)
