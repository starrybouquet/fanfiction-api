__author__ = 'Samson Danziger'

import authentication, downloader, fiction

# Provide access to methods and classes from ff
Story = fiction.Story
User = fiction.User
Chapter = fiction.Chapter

download_pdf = downloader.download_pdf

FFLogin = authentication.FFLogin