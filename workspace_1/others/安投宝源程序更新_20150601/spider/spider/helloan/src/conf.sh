HOST="http://www.helloan.cn/process"
INDEXPAGE="${HOST}/lend/bids?pageNow="
DETAILPAGE1="${HOST}/public/bid/detail/"
DETAILPAGE2="${HOST}/public/bid/detail/submittions?bidId=\${ID}&isBiddingType=false&pageNow="
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
