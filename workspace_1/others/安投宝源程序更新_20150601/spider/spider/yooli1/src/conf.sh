DETAILPAGE1="http://www.yooli.com/currentProduct"
DETAILPAGE2="http://www.yooli.com/rest/currentProduct/selectCPInvestRecordByCPId"
POSTDATA1="currentProductId=\${BID}&currentPage=1&pageSize=10"
POSTDATA2="currentProductId=\${BID}&currentPage=\${i}&pageSize=10" 
COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
