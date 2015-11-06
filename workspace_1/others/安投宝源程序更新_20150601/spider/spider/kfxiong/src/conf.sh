HOST='http://www.kfxiong.com'
INDEXPAGE="${HOST}/invest/index.html?page="
DETAILPAGE="${HOST}/invest/a"
#INVESTORPAGE="${HOST}/invest/getrecord/id/"
COOKIE=`cat COOKIE`
GETPAGE="wget --header=\"Cookie: ${COOKIE}\""
