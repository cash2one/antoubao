HOST='http://www.baikaiqi.com'
INDEXPAGE="${HOST}/invest/index_"
DETAILPAGE="${HOST}/invest/"
INVESTORPAGE="${HOST}/?log=post&desc=invest_record&id=\${ID}&page="
PHPSESSID=`cat PHPSESSID`
GETPAGE="wget --header=\"Cookie: PHPSESSID=${PHPSESSID}\""
