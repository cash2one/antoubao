HOST='https://www.bao.cn'
INDEXPAGE="${HOST}/product/ruyibao/index/page-"
DETAILPAGE="${HOST}/product/ruyibao/inves/"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"


