HOST="http://www.xinhe99.com"
INDEXPAGE="${HOST}/invest/index"
DETAILPAGE="${HOST}/invest/"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
