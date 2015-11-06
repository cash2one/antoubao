HOST='http://www.huyibank.com'
INDEXPAGE="${HOST}/invest/index.html?search=select&status=14&keywords=&use=&type=&succtime1=&succtime2=&order=-7&search=&time_limit=&time_limit_day=&pageNum=10&page="
DETAILPAGE="${HOST}/invest/detail.html?borrowid="
BRECPAGE='${HOST}/invest/detailTenderForJson.html?randID=`date "+%a%%20%b%%20%d%%20%Y%%20%H%%3A%M%%3A%S%%20GMT+0800%%20%%28%%u4E2D%%u56FD%%u6807%%u51C6%%u65F6%%u95F4%%29"`&borrowid=${ID}&page=${j}'
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie --header=\"User-Agent:Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36\""

