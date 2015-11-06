HOST='https://www.qian88.com.cn'
INDEXPAGE="${HOST}/queryInvestmentInit.html?paramMap.jbuezz=ss&paramMap.pageNo="
DETAILPAGE="${HOST}/queryInvestmentDetail.html?paramMap.id="
INVESTORPAGE="${HOST}/queryInvesmentUserInfo.html?"
COOKIE=`cat COOKIE`  
POSTDATA="paramMap.borrowId=\${ID}"
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"

