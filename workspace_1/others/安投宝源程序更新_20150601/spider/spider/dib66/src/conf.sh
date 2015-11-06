HOST="http://www.dib66.com"
INDEXPAGE="${HOST}/investList.do?pageSize=10&deadline=-1&paymentMode=-1&curPage="
DETAILPAGE="${HOST}/borrow-"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"

