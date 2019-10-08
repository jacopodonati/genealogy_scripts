from lxml import html
from urllib.parse import urljoin
from urllib.request import urlopen
import os, requests, sys, urllib

url = 'http://www.antenati.san.beniculturali.it/v/Archivio+di+Stato+di+Forli/Stato+civile+italiano/Forliprovincia+di+Forli-Cesena/Matrimoni/1876/10/100546507_00301.jpg.html?g2_imageViewsIndex=0'
inverse_order = False
full_resolution = False
test_run = False


def write_link():
    file_name = 'link.URL'
##    link = open('.' + city + registry + year + registry_nr + prefix + file_name, 'wb', encoding='utf-8')
##    link.write('[InternetShortcut]\nURL=' + full_url)
##    link.close

def extract_info():
    global url, tail, base, padding, last, registry_nr, year, registry, city, archive_type, archive, root, full_url
    url = url[:url.rfind('?')]
    url_filename = url[url.rfind('/'):]
    tail = url_filename[url_filename.find('.'):]
    base = url_filename[:url_filename.find('_') + 1]
    last_file = url_filename[url_filename.find('_') + 1 :url_filename.find('.')]
    padding = len(last_file)
    last = int(last_file.lstrip('0'))
    url = url[:url.rfind('/')]
    full_url = url
    registry_nr = url[url.rfind('/'):]
    url = url[:url.rfind('/')]
    year = url[url.rfind('/'):]
    url = url[:url.rfind('/')]
    registry = url[url.rfind('/'):]
    url = url[:url.rfind('/')]
    city = url[url.rfind('/'):-25]
    url = url[:url.rfind('/')]
    archive_type = url[url.rfind('/'):]
    url = url[:url.rfind('/')]
    archive = url[url.rfind('/'):]
    url = url[:url.rfind('/')]
    root = url[:url.rfind('/')]

def setup():
    global headers, prefix, step, first
    extract_info()
    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11' }
    prefix = '/'
    step = 1
    first = 1
    if thumbnails is True:
        prefix = '/thumb_'
    if inverse_order is True:
        first, last = last, first
        step = -1
    print('Downloading %s from %s(%s)' % (registry[1:], year[1:], registry_nr[1:]))

setup()
if thumbnails is True:
    write_link()

for i in range(first, last + 1, step):
    current_url = full_url + base + str(i).zfill(padding) + tail
    current_file = '.' + city + registry + year + registry_nr + prefix + str(i).zfill(len(str(last))) + '.jpg'
    try:
        page = requests.get(current_url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    tree = html.fromstring(page.content)
    if full_resolution is True:
        img = tree.xpath('//a[contains(@class, "cloud-zoom")]/@href')
        img_url = img[-1]
    else:
        img = tree.xpath('//a[contains(@class, "cloud-zoom")]/img/@src')
        img_url = urljoin(root, img[-1])
    print("Downloading %s/%s" % (str(i).zfill(len(str(last))), last), end='\n')
    img_file = urlopen(img_url)
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
