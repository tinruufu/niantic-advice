import csv
import json
import os
import random
import re
import subprocess
from tempfile import mkstemp, mkdtemp
from time import sleep
from urllib.parse import quote

from PIL import Image
from selenium.webdriver import PhantomJS

try:
    from secrets import mapbox_style, mapbox_access_token
except ImportError:
    mapbox = None
else:
    mapbox = True


HERE = os.path.dirname(os.path.realpath(__file__))
W, H = (2000, 1000)


def get_city_latlng():
    with open(os.path.join(HERE, 'cities.tsv')) as cities_file:
        tsv = csv.reader(cities_file, csv.excel_tab)
        raw_latlon = random.choice([
            r[0:2] for r in
            list(tsv)[1:]  # ignore attribution comment
        ])

    for dimension in raw_latlon:
        major, minor, direction = re.match(
            r'(\d+)°(\d+)′([NESW])', dimension
        ).groups()

        absolute = int(major) + (int(minor)/60)

        if direction not in 'NE':
            yield -absolute
        else:
            yield absolute


def get_map_url():
    lat, lon = get_city_latlng()

    return (
        'https://api.mapbox.com/styles/v1/{style}/static/'
        '{lon},{lat},{zoom},{bearing},{pitch}/'
        '{w}x{h}@2x?'
        'access_token={access_token}'
        .format(
            style=mapbox_style,
            lon=lon,
            lat=lat,
            zoom=17,
            bearing=random.random()*360,
            pitch=45,
            w=1280,
            h=1280 // (W // H),
            access_token=mapbox_access_token,
        )
    )


def generate_image(advice):
    image_path = os.path.join(mkdtemp(), 'pogo.png')
    html_path = os.path.join(HERE, 'index.html')
    url = 'file://{}#{}'.format(html_path, quote(advice, safe=''))
    driver = PhantomJS(service_log_path=mkstemp()[1])
    driver.set_window_size(W, H)
    driver.get(url)

    if mapbox:
        map_url = get_map_url()
        driver.execute_script('setBackground({});'.format(json.dumps(map_url)))
        for attempt in range(10):
            if driver.execute_script('return mapElement.complete;'):
                break
            sleep(1)
        else:
            raise ValueError('image failed to load:\n{}'.format(map_url))

    driver.save_screenshot(image_path)

    # twitter's gonna make our beautiful screenshot a jpeg unless we make it
    # think that we're using transparency for a reason, so,,
    img = Image.open(image_path)
    origin = img.getpixel((0, 0))
    new_origin = origin[:3] + (254,)
    img.putpixel((0, 0), new_origin)
    img.save(image_path)

    subprocess.check_call(['optipng', '-quiet', image_path])

    return image_path


if __name__ == '__main__':
    from advice import get_advice
    print(generate_image(get_advice()))
