from .common import * # noqa
from .common import env
from .common import BASE_DIR

SECRET_KEY = env('SECRET_KEY')

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': '',
        'CACHE': True,
        'STATS_FILE': BASE_DIR / 'client/webpack-stats-prod.json',
    }
}
COMPRESS_OFFLINE = True
