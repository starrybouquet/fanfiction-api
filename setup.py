from setuptools import setup

setup(name='fanfiction-api',
      version='1.2',
      description='Simple API to fanfiction.net',
      download_url='https://github.com/MarsCapone/fanfiction-api',
      url='https://marscapone.github.io/fanfiction-api',
      author='Samson Danziger & Roman Karpichev',
      author_email='samson.danziger@gmail.com',
      packages=['ff'],
      install_requires=[
          'beautifulsoup4',
          'requests',
      ])
