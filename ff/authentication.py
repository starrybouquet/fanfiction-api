__author__ = 'Samson Danziger'

import yaml, bs4
import requests
import subprocess
import getpass
import shutil

root = 'https://www.fanfiction.net'
login_url = 'https://www.fanfiction.net/login.php'
settings_url = root + '/account/settings.php'
parser = 'lxml'

def _get_config(path=None):
    config = yaml.load(open('config.yaml', 'r').read())
    return config

def _solve_captcha(captcha_url):
    response = requests.get(captcha_url, stream=True)
    with open('captcha.jpg', 'wb') as out:
        shutil.copyfileobj(response.raw, out)
    del response
    cap_viewer = subprocess.Popen(['display', '-monochrome', 'captcha.jpg'])
    solution = raw_input('Solve CAPTCHA: ')
    cap_viewer.terminate()
    cap_viewer.kill()
    return solution

class FFLogin(object):

    def __init__(self, config_file=None):
        config = _get_config(config_file)
        self._setup_details(config)
        self.session = self.get_session()

    def _setup_details(self, config):
        if config['username'] == None:
            self.username = raw_input("Enter fanfiction.net username: ")
        else:
            self.username = config['username']
        if config['email'] == None:
            self.email = raw_input("Enter email used to register on fanfiction.net: ")
        else:
            self.email = config['email']
        if config['password'] == None:
            self.password = getpass.getpass("Enter fanfiction.net password: ")
        else:
            self.password = config['password']

    def get_session(self):
        """
        Handle login
        :returns session: requests.Session() that has logged in if login was successful, else false.
        """
        source = requests.get(login_url)
        soup = bs4.BeautifulSoup(source.text, parser)

        data = {}
        form = soup.find(id='login')
        inputs = form.find_all('input')
        captcha_tag = soup.find(id='xcaptcha')
        captcha_src = captcha_tag.get('src')

        for i in inputs:
            data[i.get('name')] = i.get('value')

        captcha = _solve_captcha(root + captcha_src)
        data['captcha'] = captcha

        data['email'] = self.email
        data['password'] = self.password

        with requests.Session() as r:
            r.get(login_url)
            p = r.post(login_url, data=data)
            if self.username in p.text:
                return r
            else:
                return False
