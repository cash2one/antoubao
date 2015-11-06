HOST='http://www.jimubox.com'
INDEXPAGE="${HOST}/Project/List?rate=&guarantee=&range=&category=&status=&page="
DETAILPAGE="${HOST}/Project/Index/"
BRECPAGE='${HOST}/Project/GetInvestsPaging?id=${ID}&skip=${SKIP}&take=20&once=$((`date +%s%N`/1000000))'
GETPAGE="wget"

