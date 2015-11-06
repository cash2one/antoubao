HOST='http://www.minmindai.com'
INDEXPAGE="${HOST}/lend/index/p"
DETAILPAGE="${HOST}/Lend/detailpage/debtid"
PHPSESSID=`cat PHPSESSID`
GETPAGE="wget"
GETPAGE1="wget --no-cookies --header=\"Cookie: PHPSESSID=${PHPSESSID}; IESESSION=alive;\" --keep-session-cookie --no-check-certificate"

