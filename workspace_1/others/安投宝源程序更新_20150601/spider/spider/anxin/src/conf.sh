HOST='http://www.anxin.com'
INDEXPAGE="${HOST}/invest/"
DETAILPAGE="${HOST}/invest/detail"

COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"

