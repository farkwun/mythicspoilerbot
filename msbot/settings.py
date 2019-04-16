from os import environ

VERIFY_TOKEN = environ.get('MSBOT_VERIFY_TOKEN')
PAGE_ACCESS_TOKEN = environ.get('MSBOT_PAGE_ACCESS_TOKEN')
API_KEY = environ.get('MSBOT_API_KEY')

DB_LOCATION = 'db/msbot_tables.db'
TEST_DB_LOCATION = 'db/test_msbot_tables.db'

DEV_SAFELIST = {
}
