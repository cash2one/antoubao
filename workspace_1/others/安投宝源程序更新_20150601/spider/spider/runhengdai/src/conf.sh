HOST='http://www.runhengdai.com'
INDEXPAGE="https://member.runhengdai.com/invest-pageid_"
DETAILPAGE="https://member.runhengdai.com/invest/detail-bid_"
#INVESTORPAGE="${HOST}/invest/investRecord?"
COOKIE=`cat COOKIE`  
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
