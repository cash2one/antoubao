HOST='http://www.zfxindai.cn'

INDEXPAGE1="${HOST}/product/index1/s/1/p/"
INDEXPAGE2="${HOST}/product/index2/s/2/p/"

DETAILPAGE=("${HOST}/invest/show/bid/" "${HOST}/lab/show/bid/")
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
