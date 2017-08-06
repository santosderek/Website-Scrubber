import requests
import re
import bs4
import os

from Downloader import Download_Manager


def return_main_site_text(url):
    site = requests.get(url)
    if site.status_code == 200:
        return site.text
    else:
        return None


def main(url, directory_name):

    html = return_main_site_text(url)

    if html is None:
        print('Could not connect to:', url)
        return

    if not os.path.exists(directory_name):
        os.mkdir(directory_name)

    soup = bs4.BeautifulSoup(html, 'html.parser')
    list_of_website_urls = [
        url + link.get('href') for link in soup.find_all('a')]

    manager = Download_Manager(list_of_website_urls, 3, directory_name)
    manager.start()


if __name__ == '__main__':
    url = ''
    directory_name = ''
    main(url, directory_name)
