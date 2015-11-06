HOST='http://www.eweidai.com'
INDEXPAGE="${HOST}/invst/queryFrontProductListpd3.action?&currentPage="
DETAILPAGE="${HOST}/inv/"
INVESTORPAGE="${HOST}/invst/queryInvestPageInvestspd3.action?currentPage="
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
