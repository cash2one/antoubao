HOST='https://www.zzwms.com/'
INDEXPAGE="${HOST}/loan/all/p/"
DETAILPAGE="${HOST}/loan/blist/id/"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"


