from distutils.core import setup

setup(name='fanfiction-api',
      version='1.0',
      description='Simple API to fanfiction.net',
      download_url='https://github.com/MarsCapone/fanfiction-api',
      url='https://marscapone.github.io/fanfiction-api',
      author='Samson Danziger',
      author_email='samson.danziger@gmail.com',
      packages=['ff'],
      install_requires=[
          'PyYAML',
          'pdfkit',
          'beautifulsoup4'
      ])
