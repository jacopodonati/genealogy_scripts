from lxml import html
from urllib.parse import urljoin
from urllib.request import urlopen
import argparse, errno, logging, os, requests, sys, urllib

def extract_info(args):
    logging.info('Extracting info from URL.')
    # URL example:
    # http://www.antenati.san.beniculturali.it/v/Archivio+di+Stato+di+Forli/Stato+civile+italiano/Forliprovincia+di+Forli-Cesena/Matrimoni/1876/10/100546507_00301.jpg.html?g2_imageViewsIndex=0
    url = args.URL
    protocol = 'http://'
    logging.debug('Protocol used is {}.'.format(protocol))

    # Anything after '?' is useless to us
    if '?' in url:
        url = url[:url.rfind('?')]

    # Splitting our URL by '/'
    split_url = url.split('/')

    # How every filename will start and end
    filename_head = split_url[-1][:split_url[-1].find('_') + 1]
    filename_tail = split_url[-1][split_url[-1].find('.'):]

    # Get the last page number, get how many zeros and trim them
    last_file = split_url[-1][split_url[-1].find('_') + 1 : split_url[-1].find('.')]
    padding = len(last_file)
    last = int(last_file.lstrip('0'))

    # Base URL of every page
    base_url = protocol + '/'.join(split_url[2:10])

    # Then a list of self-explanatory variables
    registry_nr = split_url[9]
    year = split_url[8]
    registry_type = split_url[7]
    city = split_url[6]
    archive_type = split_url[5]
    archive_city = split_url[4]
    root = protocol + '/'.join(split_url[2:3])

    return {
        'url': url,
        'filename_head': filename_head,
        'filename_tail': filename_tail,
        'last': last,
        'padding': padding,
        'base_url': base_url,
        'registry_nr': registry_nr,
        'year': year,
        'registry_type': registry_type,
        'city': city,
        'archive_type': archive_type,
        'archive_city': archive_city,
        'root': root
    }

def setup_args():
    parser = argparse.ArgumentParser(description='Download archives')
    parser.add_argument('-t', '--test-run', action='store_true')
    parser.add_argument('-f', '--full-resolution', action='store_true')
    parser.add_argument('-i', '--inverse-order', action='store_true')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('URL')
    return parser.parse_args()

def setup_download(args):
    url_info = extract_info(args)
    logging.info('Setting up parameters.')
    parameters = dict()
    parameters['headers'] = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11' }
    logging.debug('User-Agent is {}.'.format(parameters['headers']))

    if args.full_resolution is True:
        parameters['prefix'] = '/'
    else:
        parameters['prefix'] = '/thumb_'
    logging.debug('File prefix is {}.'.format(parameters['prefix']))

    if args.inverse_order is True:
        parametersons['step'] = -1
        parameters['first'] = url_info['last']
        parameters['last'] = 1
    else:
        parameters['step'] = 1
        parameters['first'] = 1
        parameters['last'] = url_info['last']
    logging.debug('First to download is record no. {}.  Last to download is record no. {}.'.format(parameters['first'], parameters['last']))

    return {**url_info, **parameters}

def setup_logging(args):
    level = logging.WARNING
    print(args.verbose)
    if args.verbose > 0:
        level = logging.DEBUG
        if args.verbose > 1:
            level = logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=level)

def write_link(download_parameters):
    logging.info('Writing link file.')
    file_name = 'link.URL'
    # link = open('./' + '/'.join([download_parameters['city'], download_parameters['registry_type'], download_parameters['year'], download_parameters['registry_type']]), file_name, 'wb', encoding='utf-8')
    # link.write('[InternetShortcut]\nURL=' + download_parameters['base_url'])
    # link.close

def main():
    args = setup_args()
    setup_logging(args)        
    logging.info('Setting up.')
    download_parameters = setup_download(args)
    print('Downloading %s from %s(%s)' % (download_parameters['registry_type'], download_parameters['year'], download_parameters['registry_nr']))

    if args.full_resolution is False:
        write_link(download_parameters)

    for i in range(download_parameters['first'], download_parameters['last'] + 1, download_parameters['step']):
        logging.info('Record no. {}.'.format(i))
        current_url = '/'.join([download_parameters['base_url'], download_parameters['filename_head'] + str(i).zfill(download_parameters['padding']) + download_parameters['filename_tail']])
        current_file = './' + '/'.join([download_parameters['city'], download_parameters['registry_type'], download_parameters['year'], download_parameters['registry_nr'], download_parameters['prefix'] + str(i).zfill(len(str(download_parameters['last']))) + '.jpg'])
        logging.debug('Current URL: {}\nCurrent filename: {}.'.format(current_url, current_file))
        try:
            logging.info('Downloading the page.')
            page = requests.get(current_url, headers=download_parameters['headers'])
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        logging.info('Parsing the page.')
        tree = html.fromstring(page.content)
        if args.full_resolution is True:
            img = tree.xpath('//a[contains(@class, "cloud-zoom")]/@href')
            img_url = img[-1]
        else:
            img = tree.xpath('//a[contains(@class, "cloud-zoom")]/img/@src')
            img_url = urljoin(download_parameters['root'], img[-1])
        logging.debug('Image URL is {}.'.format(img_url))
        print("Downloading %s/%s" % (str(i).zfill(len(str(download_parameters['last']))), download_parameters['last']), end='\n')
        
        logging.info('Downloading the image.')
        img_file = urlopen(img_url)
        if args.test_run is False:
            logging.info('Writing the image on disk')
            if not os.path.exists(os.path.dirname(current_file)):
                try:
                    os.makedirs(os.path.dirname(current_file))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            output = open(current_file, "wb")
            output.write(img_file.read())
            output.close()

    print("Done.")

if __name__ == "__main__":
    main()