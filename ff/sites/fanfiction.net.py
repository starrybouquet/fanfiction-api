ROOT = 'https://www.fanfiction.net'
LOGIN_EXT = '/login.php'
ACCOUNT_EXT = '/account/settings.php'

REGEX_DICT = {
    _STORYID: r"var\s+storyid\s*=\s*(\d+);",
    _CHAPTER: r"var\s+chapter\s*=\s*(\d+);",
    _CHAPTERS: r"Chapters:\s*(\d+)\s*",
    _WORDS: r"Words:\s*([\d,]+)\s*",
    _TITLE: r"var\s+title\s*=\s*'(.+)';",
    _DATEP: r"Published:\s*<span.+?='(\d+)'>",
    _DATEU: r"Updated:\s*<span.+?='(\d+)'>",

    # USER REGEX
    _USERID: r"var\s+userid\s*=\s*(\d+);",
    _AUTHOR: r"href='/u/\d+/(.+?)'",
    _USERID_URL: r".*/u/(\d+)",
    _USERNAME: r"<link rel=\"canonical\" href=\"//www.fanfiction.net/u/\d+/(.+)\">"
    _USER_STORY_COUNT: r"My Stories\s*<span class=badge>(\d+)<",
    _USER_FAVOURITE_COUNT: r"Favorite Stories\s*<span class=badge>(\d+)<",
    _USER_FAVOURITE_AUTHOR_COUNT: r"Favorite Authors\s*<span class=badge>(\d+)<",

    # Used to parse the attributes which aren't directly contained in the
    # JavaScript and hence need to be parsed manually
    _NON_JAVASCRIPT: r'Rated:(.+)',
    _HTML_TAG: r'<.*?>'
}

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
