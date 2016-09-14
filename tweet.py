from __future__ import unicode_literals

import tweepy

from advice import get_advice
from image import generate_image
from secrets import app_key, app_secret, token_key, token_secret


auth = tweepy.OAuthHandler(app_key, app_secret)
auth.set_access_token(token_key, token_secret)
api = tweepy.API(auth)


def tweet():
    advice = get_advice()
    image = generate_image(advice)
    api.update_with_media(image, status=advice)


if __name__ == '__main__':
    tweet()
