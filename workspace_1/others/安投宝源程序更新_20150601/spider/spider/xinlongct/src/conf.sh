HOST='http://www.xinlongct.com'
INDEXPAGE="${HOST}/invest/index.html?&status=1&page= ${HOST}/invest/index.html?&status=2&page= ${HOST}/invest/index.html?&status=10&page= ${HOST}/invest/index.html?&status=12&page="
DETAILPAGE="${HOST}/invest/detail.html?borrowid="
BRECPAGE="${HOST}/invest/detailTenderForJson.html"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie '--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'"
GETPAGE1="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie '--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36 --header='X-Requested-With:XMLHttpRequest' --header='Referer: http://www.xinlongct.com/invest/detail.html?borrowid=16199'"
