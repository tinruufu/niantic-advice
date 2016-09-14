import subprocess
import os
from urllib.parse import quote
from tempfile import mkstemp, mkdtemp

from PIL import Image
from selenium.webdriver import PhantomJS


def generate_image(advice):
    image_path = os.path.join(mkdtemp(), 'pogo.png')
    html_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'index.html',
    )
    url = 'file://{}#{}'.format(html_path, quote(advice, safe=''))
    driver = PhantomJS(service_log_path=mkstemp()[1])
    driver.set_window_size(2000, 1000)
    driver.get(url)

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
