import requests
import re
import bs4
import os
from argparse import ArgumentParser
from directdownloader.direct_downloader import Download_Manager, logging

# Globals

FINAL_RECURRSION_LEVEL = 0

# TODO: Download Percentage needs to be displayed


def parse_arguments():
    """ Parse arguments at startup """

    parser = ArgumentParser(description='Scrub a directory.')
    parser.add_argument('url', metavar='url', type=str,
                        nargs='*', help='Automatically detect urls')

    parser.add_argument('--level', '-l', metavar='level',
                        type=int, nargs='?', help='Levels of recursion.')

    parser.add_argument('--threads', '-t', metavar='threads',
                        type=int, nargs='?', help='Number of threads to use.')

    parser.add_argument('--folder', '-f', metavar='folder',
                        type=str, nargs='?', help='Path of folder to download to.')

    parser.add_argument('--recursion', '-r', action='store_true',
                        help='Set recursion to all sub-directories')

    return parser.parse_args()


def get_url_html(url):
    """ Requests url and return it's contents """

    if re.search(r'^(\w+://)', url) is None:

        try:
            # If URL has no http:// in the beginning, add it.
            new_url = 'http://' + url
            site = requests.get(new_url)

            if site.status_code == 200:
                return site.text, new_url

            # If http:// failed, try https://
            new_url = 'https://' + url
            site = requests.get(new_url)

            if site.status_code == 200:
                return site.text, new_url

        except Exception as e:
            return None

    else:
        # If url has *:// at the beginning of the url, fetch html normally
        site = requests.get(url)

        if site.status_code == 200:
            return site.text, url
        else:
            return None, url


def purge_negative_links(list_of_urls: list, url: str):
    """ Removes links in a clean recursion ;) """

    illegal = ['','/','.','..','./','../','?C=D;O=A','?C=N;O=D','?C=S;O=A','?C=M;O=A']
    for iChar in illegal:
        if iChar is '':
            while url in list_of_urls:
                list_of_urls.remove(url)
        else:
            while url + iChar in list_of_urls:
                list_of_urls.remove(url + iChar)
    return list_of_urls

def return_file_and_folder_links(html, url):
    """ Parse HTML and return a list of urls to directories and file links """
    soup = bs4.BeautifulSoup(html, 'html.parser')
    all_links = soup.find_all('a', href=True)

    # Get all relative links
    relative_directories = []
    for link in all_links:
        if link['href'].endswith('/') and link.get('href')[:1] != '/':
            relative_directories.append(link.get('href'))

    relative_file_links = [
        link.get('href') for link in all_links if not link['href'].endswith('/')]

    # Get all absoulte links
    absoulute_file_links = [
        url + link if not re.match('^(https://|http://)', link) else url for link in relative_file_links]

    absolute_directories = []
    for link in relative_directories:

        if not re.match('^(https://|http://)', link) and link != url:
            absolute_directories.append(url + link)
        else:
            absolute_directories.append(url)

    absoulute_file_links = purge_negative_links(absoulute_file_links, url)
    absolute_directories = purge_negative_links(absolute_directories, url)

    return absolute_directories, absoulute_file_links


def download(url: str, path: str, current_level=0, threads=3):
    """
    url: url to parse and download
    path: path to download to
    final_level: final level of recursion to download to
    current_level: current level of recursion program is at
    """
    try:
        html, url = get_url_html(url)
        # If no HTML was given, assume could not connect.
        if html is None:
            logging.debug('Could not connect to: ' + url)
            return

        # If path to local device folder is not found, make it.
        if not os.path.exists(path):
            os.mkdir(path)

        # Change directory into the directory where the downloads should be
        os.chdir(path)
        logging.debug('Moved to: ' + path)

        absoulute_directories, absoulute_file_links = return_file_and_folder_links(
            html, url)

        # Send links to download Manager
        manager = Download_Manager(absoulute_file_links, threads, '.')
        manager.start()

        # Go to recursion level
        if current_level != FINAL_RECURRSION_LEVEL:
            for next_url in absoulute_directories:
                start = next_url.rfind('/', 0, len(next_url) - 1)
                download(next_url,
                         '.' +
                         next_url[start:],
                         current_level + 1,
                         threads)

        # Change to parent directory
        os.chdir('..')

    except Exception as e:
        logging.debug("Error downloading: " + str(e))


def main():
    """ Function that will be called when executing in CLI"""
    global FINAL_RECURRSION_LEVEL

    # Parse Arguments
    arguments = parse_arguments()

    # If no url, exit
    if len(arguments.url) == 0:
        exit(1)

    # If recursion level is defined within arguments, change global variable
    if arguments.level != None:
        FINAL_RECURRSION_LEVEL = arguments.level

    if arguments.recursion:
        FINAL_RECURRSION_LEVEL = 9**99

    # Check folder
    if arguments.folder is None:
        folder = './'
    elif arguments.folder[-1:] != '\\' and arguments.folder is not None:
        folder = arguments.folder + '/'
    else:
        folder = arguments.folder

    # If folder does not exists, make it
    if not os.path.exists(folder):
        os.mkdir(folder)

    # Change working directory to folder specified
    os.chdir(folder)

    # Number of download threads to use
    if arguments.threads is None:
        threads = 3
    else:
        threads = arguments.threads

    # Download all urls in arguments
    for url in arguments.url:
        download(url, folder, threads=threads)


if __name__ == '__main__':
    main()
