HOST='https://www.hzjr.com'
INDEXPAGE="${HOST}/invest/index/s/0-0-0-0-0/p/"
DETAILPAGE="${HOST}/invest/detail/id/"
INVESTORPAGE="${HOST}/invest/getrecord/id/"
PHPSESSID=`cat PHPSESSID`
GETPAGE="wget --header=\"Cookie: PHPSESSID=${PHPSESSID}\""
