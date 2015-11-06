HOST="https://www.julend.com"
INDEXPAGE="${HOST}/front/invest/investHome?&currPage="
DETAILPAGE1="${HOST}/front/invest/invest?bidId="
DETAILPAGE2="${HOST}/front/invest/viewBidInvestRecords"
POSTDATA2="pageSize=10&bidIdSign=\${BID}&pageNum="
#COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
GETPAGE="wget"
