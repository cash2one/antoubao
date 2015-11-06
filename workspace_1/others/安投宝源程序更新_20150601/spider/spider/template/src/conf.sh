HOST='https://www.example.com'
INDEXPAGE="${HOST}/invest/index.html?status=1&order=-1"
DETAILPAGE="${HOST}/invest/detail.html"
BRECPAGE="${HOST}/invest/detailTenderForJson.html"
JSESSIONID=`cat JSESSIONID`
GETPAGE="wget --no-cookies --header=\"Cookie: JSESSIONID=${JSESSIONID}; IESESSION=alive;\" --keep-session-cookie"

