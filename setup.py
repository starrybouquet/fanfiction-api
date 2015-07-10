from setuptools import setup, find_packages

setup(name='fanfiction-api',
      version='1.0',
      description='Simple API to fanfiction.net',
      url='https://github.com/MarsCapone/fanfiction-api',
      author='Samson Danziger',
      author_email='samson.danziger@gmail.com',
      packages=find_packages(),
      install_requires=[
          'PyYAML',
          'pdfkit',
          'beautifulsoup4'
      ],
      zip_safe=False)
