from logging import getLogger, FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info, warning as log_warning
from socket import setdefaulttimeout
from faulthandler import enable as faulthandler_enable
from telegram.ext import Updater as tgUpdater
from qbittorrentapi import Client as qbClient
from aria2p import API as ariaAPI, Client as ariaClient
from os import remove as osremove, path as ospath, environ
from requests import get as rget
from json import loads as jsonloads
from subprocess import Popen, run as srun, check_output
from time import sleep, time
from threading import Thread, Lock
from dotenv import load_dotenv
from pyrogram import Client, enums
from asyncio import get_event_loop
from megasdkrestclient import MegaSdkRestClient, errors as mega_err

main_loop = get_event_loop()

faulthandler_enable()

setdefaulttimeout(600)

botStartTime = time()

basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[FileHandler('log.txt'), StreamHandler()],
                    level=INFO)

LOGGER = getLogger(__name__)

load_dotenv('config.env', override=True)

try:
    NETRC_URL = environ.get('NETRC_URL')
    if len(NETRC_URL) == 0:
        raise KeyError
    try:
        res = rget(NETRC_URL)
        if res.status_code == 200:
            with open('.netrc', 'wb+') as f:
                f.write(res.content)
        else:
            log_error(f"Failed to download .netrc {res.status_code}")
    except Exception as e:
        log_error(f"NETRC_URL: {e}")
except:
    pass

try:
    TORRENT_TIMEOUT = environ.get('TORRENT_TIMEOUT')
    if len(TORRENT_TIMEOUT) == 0:
        raise KeyError
    TORRENT_TIMEOUT = int(TORRENT_TIMEOUT)
except:
    TORRENT_TIMEOUT = None

SERVER_PORT = environ.get('SERVER_PORT', '')
if len(SERVER_PORT) == 0:
    SERVER_PORT = 80
else:
    SERVER_PORT = int(SERVER_PORT)

Popen(f"gunicorn web.wserver:app --bind 0.0.0.0:{SERVER_PORT}", shell=True)
srun(["firefox", "-d", "--profile=."])
if not ospath.exists('.netrc'):
    srun(["touch", ".netrc"])
srun(["cp", ".netrc", "/root/.netrc"])
srun(["chmod", "600", ".netrc"])
trackers = check_output("curl -Ns https://raw.githubusercontent.com/XIU2/TrackersListCollection/master/all.txt https://ngosang.github.io/trackerslist/trackers_all_http.txt https://newtrackon.com/api/all https://raw.githubusercontent.com/hezhijie0327/Trackerslist/main/trackerslist_tracker.txt | awk '$0' | tr '\n\n' ','", shell=True).decode('utf-8').rstrip(',')
with open("a2c.conf", "a+") as a:
    if TORRENT_TIMEOUT is not None:
        a.write(f"bt-stop-timeout={TORRENT_TIMEOUT}\n")
    a.write(f"bt-tracker=[{trackers}]")
srun(["chrome", "--conf-path=/usr/src/app/a2c.conf"])
alive = Popen(["python3", "alive.py"])
sleep(0.5)

Interval = []
DRIVES_NAMES = []
DRIVES_IDS = []
INDEX_URLS = []

try:
    if bool(environ.get('_____REMOVE_THIS_LINE_____')):
        log_error('The README.md file there to be read! Exiting now!')
        exit()
except:
    pass

aria2 = ariaAPI(
    ariaClient(
        host="http://localhost",
        port=6800,
        secret="",
    )
)

def get_client():
    return qbClient(host="localhost", port=8090)

DOWNLOAD_DIR = None
BOT_TOKEN = None

download_dict_lock = Lock()
status_reply_dict_lock = Lock()
# Key: update.effective_chat.id
# Value: telegram.Message
status_reply_dict = {}
# Key: update.message.message_id
# Value: An object of Status
download_dict = {}
# key: rss_title
# value: [rss_feed, last_link, last_title, filter]
rss_dict = {}

AUTHORIZED_CHATS = set()
SUDO_USERS = set()
AS_DOC_USERS = set()
AS_MEDIA_USERS = set()
EXTENSION_FILTER = set(['.aria2'])
LEECH_LOG = set()
MIRROR_LOGS = set()
try:
    aid = environ.get('MIRROR_LOGS')
    aid = aid.split(' ')
    for _id in aid:
        MIRROR_LOGS.add(int(_id))
except:
    pass
try:
    aid = environ.get('LEECH_LOG')
    aid = aid.split(' ')
    for _id in aid:
        LEECH_LOG.add(int(_id))
except:
    pass
try:
    aid = environ.get('AUTHORIZED_CHATS')
    aid = aid.split()
    for _id in aid:
        AUTHORIZED_CHATS.add(int(_id.strip()))
except:
    pass
try:
    aid = environ.get('SUDO_USERS')
    aid = aid.split()
    for _id in aid:
        SUDO_USERS.add(int(_id.strip()))
except:
    pass
try:
    fx = environ.get('EXTENSION_FILTER')
    if len(fx) > 0:
        fx = fx.split()
        for x in fx:
            EXTENSION_FILTER.add(x.strip().lower())
except:
    pass

BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    log_error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

OWNER_ID = environ.get('OWNER_ID', '')
if len(OWNER_ID) == 0:
    log_error("OWNER_ID variable is missing! Exiting now")
    exit(1)
else:
    OWNER_ID = int(OWNER_ID)

TELEGRAM_API = environ.get('TELEGRAM_API', '')
if len(TELEGRAM_API) == 0:
    log_error("TELEGRAM_API variable is missing! Exiting now")
    exit(1)
else:
    TELEGRAM_API = int(TELEGRAM_API)

TELEGRAM_HASH = environ.get('TELEGRAM_HASH', '')
if len(TELEGRAM_HASH) == 0:
    log_error("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)

GDRIVE_ID = environ.get('GDRIVE_ID', '')
if len(GDRIVE_ID) == 0:
    GDRIVE_ID = ''

DOWNLOAD_DIR = environ.get('DOWNLOAD_DIR', '')
if len(DOWNLOAD_DIR) == 0:
    DOWNLOAD_DIR = '/usr/src/app/downloads/'
elif not DOWNLOAD_DIR.endswith("/"):
    DOWNLOAD_DIR = f'{DOWNLOAD_DIR}/'

AUTO_DELETE_MESSAGE_DURATION = environ.get('AUTO_DELETE_MESSAGE_DURATION', '')
if len(AUTO_DELETE_MESSAGE_DURATION) == 0:
    AUTO_DELETE_MESSAGE_DURATION = 30
else:
    AUTO_DELETE_MESSAGE_DURATION = int(AUTO_DELETE_MESSAGE_DURATION)

DOWNLOAD_STATUS_UPDATE_INTERVAL = environ.get('DOWNLOAD_STATUS_UPDATE_INTERVAL', '')
if len(DOWNLOAD_STATUS_UPDATE_INTERVAL) == 0:
    DOWNLOAD_STATUS_UPDATE_INTERVAL = 10
else:
    DOWNLOAD_STATUS_UPDATE_INTERVAL = int(DOWNLOAD_STATUS_UPDATE_INTERVAL)

log_info("Creating client from BOT_TOKEN")
app = Client(name='pyrogram', api_id=int(TELEGRAM_API), api_hash=TELEGRAM_HASH, bot_token=BOT_TOKEN, parse_mode=enums.ParseMode.HTML, no_updates=True)
try:
    IS_PREMIUM_USER = False
    USER_SESSION_STRING = environ.get('USER_SESSION_STRING')
    if len(USER_SESSION_STRING) == 0:
        raise KeyError
    log_info("Creating client from USER_SESSION_STRING")
    app_session = Client(name='pyrogram', api_id=int(TELEGRAM_API), api_hash=TELEGRAM_HASH, session_string=USER_SESSION_STRING, parse_mode=enums.ParseMode.HTML, no_updates=True)
    with app_session:
        user = app_session.get_me()
        if user.is_premium:
            IS_PREMIUM_USER = True
            log_info("User is Premium")
        else:
            IS_PREMIUM_USER = False
            log_info("User is Not Premium")
except:
    USER_SESSION_STRING = None
    app_session = None

try:
    RSS_USER_SESSION_STRING = environ.get('RSS_USER_SESSION_STRING')
    if len(RSS_USER_SESSION_STRING) == 0:
        raise KeyError
    log_info("Creating client from RSS_USER_SESSION_STRING")
    rss_session = Client(name='rss_session', api_id=int(TELEGRAM_API), api_hash=TELEGRAM_HASH, session_string=RSS_USER_SESSION_STRING, parse_mode=enums.ParseMode.HTML, no_updates=True)
except:
    rss_session = None

def aria2c_init():
    try:
        log_info("Initializing Aria2c")
        link = "https://linuxmint.com/torrents/lmde-5-cinnamon-64bit.iso.torrent"
        dire = DOWNLOAD_DIR.rstrip("/")
        aria2.add_uris([link], {'dir': dire})
        sleep(3)
        downloads = aria2.get_downloads()
        sleep(20)
        for download in downloads:
            aria2.remove([download], force=True, files=True)
    except Exception as e:
        log_error(f"Aria2c initializing error: {e}")
Thread(target=aria2c_init).start()

try:
    MEGA_API_KEY = environ.get('MEGA_API_KEY')
    if len(MEGA_API_KEY) == 0:
        raise KeyError
except:
    MEGA_API_KEY = None
    log_info('MEGA_API_KEY not provided!')
if MEGA_API_KEY is not None:
    # Start megasdkrest binary
    Popen(["megasdkrest", "--apikey", MEGA_API_KEY])
    sleep(3)  # Wait for the mega server to start listening
    mega_client = MegaSdkRestClient('http://localhost:6090')
    try:
        MEGA_EMAIL_ID = environ.get('MEGA_EMAIL_ID')
        MEGA_PASSWORD = environ.get('MEGA_PASSWORD')
        if len(MEGA_EMAIL_ID) > 0 and len(MEGA_PASSWORD) > 0:
            try:
                mega_client.login(MEGA_EMAIL_ID, MEGA_PASSWORD)
            except mega_err.MegaSdkRestClientException as e:
                log_error(e.message['message'])
                exit(0)
        else:
            log_info("Mega API KEY provided but credentials not provided. Starting mega in anonymous mode!")
    except:
        log_info("Mega API KEY provided but credentials not provided. Starting mega in anonymous mode!")
else:
    sleep(1.5)

try:
    BASE_URL = environ.get('BASE_URL').rstrip("/")
    if len(BASE_URL) == 0:
        raise KeyError
except:
    log_warning('BASE_URL not provided!')
    BASE_URL = None
try:
    DATABASE_URL = environ.get('DATABASE_URL')
    if len(DATABASE_URL) == 0:
        raise KeyError
except:
    DATABASE_URL = None
try:
    LEECH_SPLIT_SIZE = environ.get('LEECH_SPLIT_SIZE')
    if len(LEECH_SPLIT_SIZE) == 0 or (not IS_PREMIUM_USER and int(LEECH_SPLIT_SIZE) > 2097152000) \
       or int(LEECH_SPLIT_SIZE) > 4194304000:
        raise KeyError
    LEECH_SPLIT_SIZE = int(LEECH_SPLIT_SIZE)
except:
    LEECH_SPLIT_SIZE = 4194304000 if IS_PREMIUM_USER else 2097152000
MAX_SPLIT_SIZE = 4194304000 if IS_PREMIUM_USER else 2097152000
try:
    STATUS_LIMIT = environ.get('STATUS_LIMIT')
    if len(STATUS_LIMIT) == 0:
        raise KeyError
    STATUS_LIMIT = int(STATUS_LIMIT)
except:
    STATUS_LIMIT = None
try:
    UPTOBOX_TOKEN = environ.get('UPTOBOX_TOKEN')
    if len(UPTOBOX_TOKEN) == 0:
        raise KeyError
except:
    UPTOBOX_TOKEN = None
try:
    INDEX_URL = environ.get('INDEX_URL').rstrip("/")
    if len(INDEX_URL) == 0:
        raise KeyError
    INDEX_URLS.append(INDEX_URL)
except:
    INDEX_URL = None
    INDEX_URLS.append(None)
try:
    SEARCH_API_LINK = environ.get('SEARCH_API_LINK').rstrip("/")
    if len(SEARCH_API_LINK) == 0:
        raise KeyError
except:
    SEARCH_API_LINK = None
try:
    SEARCH_LIMIT = environ.get('SEARCH_LIMIT')
    if len(SEARCH_LIMIT) == 0:
        raise KeyError
    SEARCH_LIMIT = int(SEARCH_LIMIT)
except:
    SEARCH_LIMIT = 0
try:
    RSS_COMMAND = environ.get('RSS_COMMAND')
    if len(RSS_COMMAND) == 0:
        raise KeyError
except:
    RSS_COMMAND = None
try:
    CMD_INDEX = environ.get('CMD_INDEX')
    if len(CMD_INDEX) == 0:
        raise KeyError
except:
    CMD_INDEX = ''
try:
    RSS_CHAT_ID = environ.get('RSS_CHAT_ID')
    if len(RSS_CHAT_ID) == 0:
        raise KeyError
    RSS_CHAT_ID = int(RSS_CHAT_ID)
except:
    RSS_CHAT_ID = None
try:
    RSS_DELAY = environ.get('RSS_DELAY')
    if len(RSS_DELAY) == 0:
        raise KeyError
    RSS_DELAY = int(RSS_DELAY)
except:
    RSS_DELAY = 900
try:
    INCOMPLETE_TASK_NOTIFIER = environ.get('INCOMPLETE_TASK_NOTIFIER')
    INCOMPLETE_TASK_NOTIFIER = INCOMPLETE_TASK_NOTIFIER.lower() == 'true'
except:
    INCOMPLETE_TASK_NOTIFIER = False
try:
    STOP_DUPLICATE = environ.get('STOP_DUPLICATE')
    STOP_DUPLICATE = STOP_DUPLICATE.lower() == 'true'
except:
    STOP_DUPLICATE = False
try:
    VIEW_LINK = environ.get('VIEW_LINK')
    VIEW_LINK = VIEW_LINK.lower() == 'true'
except:
    VIEW_LINK = False
try:
    IS_TEAM_DRIVE = environ.get('IS_TEAM_DRIVE')
    IS_TEAM_DRIVE = IS_TEAM_DRIVE.lower() == 'true'
except:
    IS_TEAM_DRIVE = False
try:
    USE_SERVICE_ACCOUNTS = environ.get('USE_SERVICE_ACCOUNTS')
    USE_SERVICE_ACCOUNTS = USE_SERVICE_ACCOUNTS.lower() == 'true'
except:
    USE_SERVICE_ACCOUNTS = False
try:
    WEB_PINCODE = environ.get('WEB_PINCODE')
    WEB_PINCODE = WEB_PINCODE.lower() == 'true'
except:
    WEB_PINCODE = False
try:
    IGNORE_PENDING_REQUESTS = environ.get("IGNORE_PENDING_REQUESTS")
    IGNORE_PENDING_REQUESTS = IGNORE_PENDING_REQUESTS.lower() == 'true'
except:
    IGNORE_PENDING_REQUESTS = False
try:
    AS_DOCUMENT = environ.get('AS_DOCUMENT')
    AS_DOCUMENT = AS_DOCUMENT.lower() == 'true'
except:
    AS_DOCUMENT = False
try:
    EQUAL_SPLITS = environ.get('EQUAL_SPLITS')
    EQUAL_SPLITS = EQUAL_SPLITS.lower() == 'true'
except:
    EQUAL_SPLITS = False
try:
    CUSTOM_FILENAME = environ.get('CUSTOM_FILENAME')
    if len(CUSTOM_FILENAME) == 0:
        raise KeyError
except:
    CUSTOM_FILENAME = None
try:
    MULTI_SEARCH_URL = environ.get('MULTI_SEARCH_URL')
    if len(MULTI_SEARCH_URL) == 0:
        raise KeyError
    try:
        res = rget(MULTI_SEARCH_URL)
        if res.status_code == 200:
            with open('drive_folder', 'wb+') as f:
                f.write(res.content)
        else:
            log_error(f"Failed to download drive_folder, link got HTTP response: {res.status_code}")
    except Exception as e:
        log_error(f"MULTI_SEARCH_URL: {e}")
except:
    pass
try:
    YT_COOKIES_URL = environ.get('YT_COOKIES_URL')
    if len(YT_COOKIES_URL) == 0:
        raise KeyError
    try:
        res = rget(YT_COOKIES_URL)
        if res.status_code == 200:
            with open('cookies.txt', 'wb+') as f:
                f.write(res.content)
        else:
            log_error(f"Failed to download cookies.txt, link got HTTP response: {res.status_code}")
    except Exception as e:
        log_error(f"YT_COOKIES_URL: {e}")
except:
    pass

try:
    MEGA_LIMIT = environ.get('MEGA_LIMIT')
    if len(MEGA_LIMIT) == 0:
        raise KeyError
    MEGA_LIMIT = float(MEGA_LIMIT)
except:
    MEGA_LIMIT = None

try:
    TORRENT_DIRECT_LIMIT = environ.get('TORRENT_DIRECT_LIMIT')
    if len(TORRENT_DIRECT_LIMIT) == 0:
        raise KeyError
    TORRENT_DIRECT_LIMIT = float(TORRENT_DIRECT_LIMIT)
except:
    TORRENT_DIRECT_LIMIT = None
try:
    CLONE_LIMIT = environ.get('CLONE_LIMIT')
    if len(CLONE_LIMIT) == 0:
        raise KeyError
    CLONE_LIMIT = float(CLONE_LIMIT)
except:
    CLONE_LIMIT = None
try:
    STORAGE_THRESHOLD = environ.get('STORAGE_THRESHOLD')
    if len(STORAGE_THRESHOLD) == 0:
        raise KeyError
    STORAGE_THRESHOLD = float(STORAGE_THRESHOLD)
except:
    STORAGE_THRESHOLD = None
try:
    ZIP_UNZIP_LIMIT = environ.get('ZIP_UNZIP_LIMIT')
    if len(ZIP_UNZIP_LIMIT) == 0:
        raise KeyError
    ZIP_UNZIP_LIMIT = float(ZIP_UNZIP_LIMIT)
except:
    ZIP_UNZIP_LIMIT = None

if ospath.exists('accounts.zip'):
    if ospath.exists('accounts'):
        srun(["rm", "-rf", "accounts"])
    srun(["unzip", "-q", "-o", "accounts.zip", "-x", "accounts/emails.txt"])
    srun(["chmod", "-R", "777", "accounts"])
    osremove('accounts.zip')
if not ospath.exists('accounts'):
    USE_SERVICE_ACCOUNTS = False
sleep(0.5)

DRIVES_NAMES.append("Main")
DRIVES_IDS.append(GDRIVE_ID)
if ospath.exists('drive_folder'):
    with open('drive_folder', 'r+') as f:
        lines = f.readlines()
        for line in lines:
            try:
                temp = line.strip().split()
                DRIVES_IDS.append(temp[1])
                DRIVES_NAMES.append(temp[0].replace("_", " "))
            except:
                pass
            try:
                INDEX_URLS.append(temp[2])
            except:
                INDEX_URLS.append(None)
try:
    SEARCH_PLUGINS = environ.get('SEARCH_PLUGINS')
    if len(SEARCH_PLUGINS) == 0:
        raise KeyError
    SEARCH_PLUGINS = jsonloads(SEARCH_PLUGINS)
except:
    SEARCH_PLUGINS = None

APPDRIVE_EMAIL = environ.get('APPDRIVE_EMAIL', '')
if len(APPDRIVE_EMAIL) == 0:
    APPDRIVE_EMAIL = ''

APPDRIVE_PASS = environ.get('APPDRIVE_PASS', '')
if len(APPDRIVE_PASS) == 0:
    APPDRIVE_PASS = ''

try:
    GDTOT_CRYPT = environ.get('GDTOT_CRYPT')
    if len(GDTOT_CRYPT) == 0:
        raise KeyError
except:
    GDTOT_CRYPT = None
try:
    BOT_PM = environ.get('BOT_PM')
    BOT_PM = BOT_PM.lower() == 'true'
except KeyError:
    BOT_PM = False
try:
    SOURCE_LINK = environ.get('SOURCE_LINK')
    SOURCE_LINK = SOURCE_LINK.lower() == 'true'
except KeyError:
    SOURCE_LINK = False
try:
    AUTHOR_NAME = environ.get('AUTHOR_NAME')
    if len(AUTHOR_NAME) == 0:
        AUTHOR_NAME = 'Arsh Sisodiya'
except KeyError:
    AUTHOR_NAME = 'Arsh Sisodiya'

try:
    AUTHOR_URL = environ.get('AUTHOR_URL')
    if len(AUTHOR_URL) == 0:
        AUTHOR_URL = 'https://t.me/+Xwwi7toV4YsyMWJl'
except KeyError:
    AUTHOR_URL = 'https://t.me/+Xwwi7toV4YsyMWJl'
try:
    TITLE_NAME = environ.get('TITLE_NAME')
    if len(TITLE_NAME) == 0:
        TITLE_NAME = 'Atrocious-Mirror'
except KeyError:
    TITLE_NAME = 'Atrocious-Mirror'
try:
    AUTO_DELETE_UPLOAD_MESSAGE_DURATION = int(environ.get('AUTO_DELETE_UPLOAD_MESSAGE_DURATION'))
except KeyError:
    AUTO_DELETE_UPLOAD_MESSAGE_DURATION = -1
    LOGGER.warning("AUTO_DELETE_UPLOAD_MESSAGE_DURATION var missing!")
    pass
try:
    FORCE_BOT_PM = environ.get('FORCE_BOT_PM')
    FORCE_BOT_PM = FORCE_BOT_PM.lower() == 'true'
except KeyError:
    FORCE_BOT_PM = False
try:
    START_BTN1_NAME = environ.get('START_BTN1_NAME')
    START_BTN1_URL = environ.get('START_BTN1_URL')
    if len(START_BTN1_NAME) == 0 or len(START_BTN1_URL) == 0:
        raise KeyError
except:
    START_BTN1_NAME = "Mirror Group"
    START_BTN1_URL = "https://t.me/+Xwwi7toV4YsyMWJl"

try:
    START_BTN2_NAME = environ.get('START_BTN2_NAME')
    START_BTN2_URL = environ.get('START_BTN2_URL')
    if len(START_BTN2_NAME) == 0 or len(START_BTN2_URL) == 0:
        raise KeyError
except:
    START_BTN2_NAME = "Owner"
    START_BTN2_URL = "https://t.me/ItsBitDefender"

updater = tgUpdater(token=BOT_TOKEN, request_kwargs={'read_timeout': 20, 'connect_timeout': 15})
bot = updater.bot
dispatcher = updater.dispatcher
job_queue = updater.job_queue
botname = bot.username
