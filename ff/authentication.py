__author__ = 'Samson Danziger'

import yaml, re
import urllib2, cookielib, urllib
import subprocess
import getpass

root = 'https://www.fanfiction.net'
_CAPTCHA_REGEX = r"img_src:\s*'(\/cap\.jpg\?cid=(\w+)&a=(\w+))'"
_CAPTCHAID_REGEX = r"captcha_id:\s*'(\w+)'"


def _get_config(path=None):
    config = yaml.load(open('config.yaml', 'r').read())
    return config


def _solve_captcha(captcha_url):
    urllib.urlretrieve(captcha_url, 'captcha.jpg')
    cap_viewer = subprocess.Popen(['display', '-monochrome', 'captcha.jpg'])
    solution = raw_input('Solve CAPTCHA: ')
    cap_viewer.terminate()
    cap_viewer.kill()
    return solution


class FanfictionLogin(object):
    def __init__(self, config_file=None):
        config = _get_config(config_file)
        self.username = config['username']
        self.email = config['email']

        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(
            urllib2.HTTPRedirectHandler(),
            urllib2.HTTPHandler(debuglevel=0),
            urllib2.HTTPSHandler(debuglevel=0),
            urllib2.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [('User-agent',
                                   'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.1.4322)')]
        self.login()

    def login(self):  # Not working. Cannot get past login form.
        """
        Handle login
        :return: boolean, True is login was a success, otherwise False.
        """
        source = urllib2.urlopen("https://www.fanfiction.net/login.php").read()
        captcha_path = re.search(_CAPTCHA_REGEX, source).group(1).decode('utf-8')
        captcha_url = root + captcha_path
        captcha_id = re.search(_CAPTCHAID_REGEX, source).group(1).decode('utf-8')

        values = {
            'email': self.email,
            'password': getpass.unix_getpass('Enter fanfiction.net password: '),
            'captcha': _solve_captcha(captcha_url)
        }
        data = urllib.urlencode(values)
        response = self.opener.open("https://www.fanfiction.net/login.php", data)

        page = response.read()
        print page
