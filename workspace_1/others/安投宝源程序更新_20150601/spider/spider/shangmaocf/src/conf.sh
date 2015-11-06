HOST='http://www.shangmaocf.com'
INDEXPAGE="${HOST}/invest/index"
INVESTORPAGE="${HOST}/invest/a"
DETAILPAGE="${HOST}/invest/a"

COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"

