HOST='https://www.zhaoshangdai.com'
INDEXPAGE1="${HOST}/invest/index.html?order=-1"
INDEXPAGE2="${HOST}/invest/index.html?status=10&order=-5"
DETAILPAGE="${HOST}/invest/detail.html"
BRECPAGE="${HOST}/invest/detailTenderForJson.html"
JSESSIONID=`cat JSESSIONID`

GETPAGE="wget --no-cookies --header=\"Cookie: JSESSIONID=${JSESSIONID}; IESESSION=alive;\" --keep-session-cookie"

