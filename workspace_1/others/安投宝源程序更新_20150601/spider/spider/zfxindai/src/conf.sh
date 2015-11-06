HOST='http://www.zfxindai.cn'

#LOANTYPE=("/index/s/0" "/index4/s/4")
INDEXPAGE1="${HOST}/product/index4/s/4/p/"
INDEXPAGE2="${HOST}/product/index/s/0/p/"

DETAILPAGE=("${HOST}/invest/show/bid/" "${HOST}/product/show/id/")
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
