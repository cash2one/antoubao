HOST="http://www.yijiedai.com"
INDEXPAGE="${HOST}/invest?page="
DETAILPAGE="${HOST}/invest/view/"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
