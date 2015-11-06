HOST='https://www.shuangfudai.com'
INDEXPAGE="${HOST}/invest/index.html?search=select&status=0&search_type=1&order=-5&pageNum=10&page="
DETAILPAGE="${HOST}/invest/detail.html?borrowid="
BRECPAGE='${HOST}/invest/detailTenderForJson.html?randID=`date "+%a%%20%b%%20%d%%20%Y%%20%H%%3A%M%%3A%S%%20GMT+0800%%20%%28%%u4E2D%%u56FD%%u6807%%u51C6%%u65F6%%u95F4%%29"`&borrowid=${ID}&page='
JSESSIONID=`cat JSESSIONID`
GETPAGE="wget --no-cookies --header=\"Cookie: JSESSIONID=${JSESSIONID}; IESESSION=alive;\" --keep-session-cookie --no-check-certificate"

