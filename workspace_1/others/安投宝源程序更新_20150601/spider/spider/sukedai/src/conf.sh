HOST="https://www.sukedai.com"
INDEXPAGE="${HOST}/investing/index"
DETAILPAGE="${HOST}/invest/a"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"

