HOST='http://www.dai36.com'
INDEXPAGE="${HOST}/invest.htm"
DETAILPAGE="${HOST}/borrowinfo.htm?jid="
INVESTORPAGE="${HOST}/borrowinfo.htm?cmd=listBidsDetail"
JSESSIONID=`cat JSESSIONID`
GETPAGE="wget"
GETPAGE1="wget --header=\"Cookie: JSESSIONID=${JSESSIONID}; IESESSION=alive;\""
