import requests
import re
import bs4
import os
from argparse import ArgumentParser
from direct_downloader.direct_downloader import Download_Manager, logging


FINAL_RECURRSION_LEVEL = 0

# TODO: Logger - Possibily 3 different files "Skipped.txt", "Failed.txt"
# TODO: Download Percentage needs to be displayed


def parse_arguments():
    parser = ArgumentParser(description='Scrub a directory.')
    parser.add_argument('url', metavar='url', type=str,
                        nargs='*', help='Automatically detect urls')

    parser.add_argument('--level', '-l', metavar='level',
                        type=int, nargs='?', help='Levels of recursion.')

    parser.add_argument('--threads', '-t', metavar='threads',
                        type=int, nargs='?', help='Number of threads to use.')

    parser.add_argument('--folder', '-f', metavar='folder',
                        type=str, nargs='?', help='Path of folder to download to.')

    return parser.parse_args()


def return_main_site_text(url):
    site = requests.get(url)
    if site.status_code == 200:
        return site.text
    else:
        return None


def purge_negative_links(list_of_urls: list, url: str):
    # Take out parent link and url
    while url in list_of_urls:
        list_of_urls.remove(url)

    while url + '/' in list_of_urls:
        list_of_urls.remove(url + '/')

    while url + '.' in list_of_urls:
        list_of_urls.remove(url + '.')

    while url + '..' in list_of_urls:
        list_of_urls.remove(url + '..')

    while url + './' in list_of_urls:
        list_of_urls.remove(url + './')

    while url + '../' in list_of_urls:
        list_of_urls.remove(url + '../')

    # Appache Parent Redirects
    while url + '?C=D;O=A' in list_of_urls:
        list_of_urls.remove(url + '?C=D;O=A')

    while url + '?C=N;O=D' in list_of_urls:
        list_of_urls.remove(url + '?C=N;O=D')

    while url + '?C=S;O=A' in list_of_urls:
        list_of_urls.remove(url + '?C=S;O=A')

    while url + '?C=M;O=A' in list_of_urls:
        list_of_urls.remove(url + '?C=M;O=A')

    return list_of_urls


def return_file_and_folder_links(html, url):
    """ Parse HTML and return a list of urls to directories and file links """
    soup = bs4.BeautifulSoup(html, 'html.parser')
    all_links = soup.find_all('a', href=True)

    # Get all relative links
    # relative_directories = [link.get('href') for link in all_links if link['href'].endswith(
    #    '/') and not link['href'].startswith('/')]

    relative_directories = []
    for link in all_links:
        if link['href'].endswith('/') and link.get('href')[:1] != '/':
            relative_directories.append(link.get('href'))

    relative_file_links = [
        link.get('href') for link in all_links if not link['href'].endswith('/')]

    # Get all absoulte links

    absoulute_file_links = [
        url + link if not re.match('^(https://|http://)', link) else url for link in relative_file_links]

    # absolute_directories = [
    #    url + link if not re.match('^(https://|http://)', link) else url for link in relative_directories]

    absolute_directories = []
    for link in relative_directories:
        #print('LINK:', link)
        #print('URL:', url)
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
        html = return_main_site_text(url)

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

        # Send to download Manager
        manager = Download_Manager(absoulute_file_links, threads, '.')
        manager.start()

        # Go to recursion level
        #print('Level:', current_level)
        #print('Final Level:', FINAL_RECURRSION_LEVEL)
        if current_level != FINAL_RECURRSION_LEVEL:
            for next_url in absoulute_directories:
                #print('----------next url:', next_url)
                start = next_url.rfind('/', 0, len(next_url) - 1)
                download(next_url,
                         '.' + next_url[start:],
                         current_level + 1,
                         threads)
                logging.info('URL: %s, CL: %d, FL: %d, T: %d' % (
                    next_url, current_level + 1, FINAL_RECURRSION_LEVEL, threads))
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

    if not os.path.exists(folder):
        os.mkdir(folder)

    if arguments.threads is None:
        threads = 3
    else:
        threads = arguments.threads

    os.chdir(folder)

    # If no url, exit
    if len(arguments.url) == 0:
        exit(1)

    # Download all urls in arguments
    for url in arguments.url:
        download(url, folder, threads=threads)


if __name__ == '__main__':
    main()
