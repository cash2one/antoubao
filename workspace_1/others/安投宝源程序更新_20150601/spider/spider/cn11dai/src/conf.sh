HOST="http://www.cn11dai.com"
INDEXPAGE="${HOST}/invest/index.html?page="
DETAILPAGE1="${HOST}/invest/detail.html?borrowid="
DETAILPAGE2="${HOST}/invest/detailTenderForJson.html?borrowid=\${ID}&page="
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
