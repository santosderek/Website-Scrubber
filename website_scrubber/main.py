import requests
import re
import bs4
import os
from argparse import ArgumentParser
from direct_downloader.direct_downloader import Download_Manager

FINAL_RECURRSION_LEVEL = 0


def parse_arguments():
    parser = ArgumentParser(description='Scrub a directory.')
    parser.add_argument('url', metavar='url', type=str,
                        nargs='*', help='Automatically detect urls')
    parser.add_argument('--level', '-l', metavar='level',
                        type=int, nargs='?', help='Levels of recursion.')
    parser.add_argument('--folder', '-f', metavar='folder',
                        type=str, nargs='?', help='Path of folder to download to.')

    return parser.parse_args()


def return_main_site_text(url):
    site = requests.get(url)
    if site.status_code == 200:
        return site.text
    else:
        return None


def return_file_and_folder_links(html, url):
    """ Parse HTML and return a list of urls to directories and file links """
    soup = bs4.BeautifulSoup(html, 'html.parser')
    all_links = soup.find_all('a', href=True)

    # Get all relative links
    relative_directories = [link.get('href')
                            for link in all_links if link['href'].endswith('/')]

    relative_file_links = [
        link.get('href') for link in all_links if not link['href'].endswith('/')]

    # Get all absoulte links
    absoulute_file_links = [
        url + link if not re.match('^(https://|http://)', link) else url for link in relative_file_links]

    absolute_directories = [
        url + link if not re.match('^(https://|http://)', link) else url for link in relative_directories]

    # Take out parent link and url
    # ... File links
    while url in absoulute_file_links:
        absoulute_file_links.remove(url)

    while url + '../' in absoulute_file_links:
        absoulute_file_links.remove(url + '../')

    # ... Directories
    while url in absolute_directories:
        absolute_directories.remove(url)

    while url + '../' in absolute_directories:
        absolute_directories.remove(url + '../')

    return absolute_directories, absoulute_file_links


def download(url: str, path: str, current_level=0, threads=3):
    """
    url: url to parse and download
    path: path to download to
    final_level: final level of recursion to download to
    current_level: current level of recursion program is at
    """
    try:
        html = return_main_site_text(url)

        if html is None:
            print('Could not connect to:', url)
            return

        # If path to local device folder is not found, make it.
        if not os.path.exists(path):
            os.mkdir(path)

        # Change directory into the directory where the downloads should be
        os.chdir(path)

        absoulute_directories, absoulute_file_links = return_file_and_folder_links(
            html, url)

        # Send to download Manager
        print('Moved to:', path)
        manager = Download_Manager(absoulute_file_links, threads, '.')
        manager.start()

        # Go to recursion level
        #print('Level:', current_level)
        #print('Final Level:', FINAL_RECURRSION_LEVEL)
        if current_level != FINAL_RECURRSION_LEVEL:
            for next_url in absoulute_directories:
                start = next_url.rfind('/', 0, len(next_url) - 1)
                download(next_url,
                         '.' + next_url[start:],
                         current_level + 1,
                         threads)
        os.chdir('..')

    except Exception as e:
        print(e)


def main():
    """ Function that will be called when executing in CLI"""
    global FINAL_RECURRSION_LEVEL

    # Parse Arguments
    arguments = parse_arguments()

    # If recursion level is defined within arguments, change global variable
    if arguments.level != None:
        FINAL_RECURRSION_LEVEL = arguments.level

    # Check folder
    if arguments.folder is None:
        folder = './'
    elif arguments.folder[-1:] != '\\' and arguments.folder is not None:
        folder = arguments.folder + '/'
    else:
        folder = arguments.folder

    os.chdir(folder)

    # If no url, exit
    if len(arguments.url) == 0:
        exit(1)

    # Download all urls in arguments
    for url in arguments.url:
        download(url, folder)


if __name__ == '__main__':
    main()
