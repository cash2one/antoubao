HOST="http://www.dfjr580.com"
INDEXPAGE="${HOST}/borrow/list_"
DETAILPAGE="${HOST}/borrow/"
COOKIE=`cat COOKIE`  
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
