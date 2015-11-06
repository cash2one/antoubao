HOST='https://www.zrcaifu.com'
INDEXPAGE="${HOST}/invest?page="
DETAILPAGE="${HOST}/invest/detail?id="
INVESTORPAGE="${HOST}/invest/history?page="
COOKIE=`cat COOKIE`
GETPAGE="wget --header=\"Cookie: ${COOKIE}\""
