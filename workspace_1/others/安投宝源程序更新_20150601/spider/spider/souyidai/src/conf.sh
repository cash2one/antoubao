HOST="https://www.souyidai.com"
LOANTYPE=("onlinelist" "fulllist")
INDEXPAGE="${HOST}/invest/\${LOANTYPE[\${t}]}"
POSTDATA1_0="pageNo=\${i}&isTransfer=0&isFresh=-1&isSmall=0&loanType=-1&repayMode=-1&guar=-1&sort=openTime&sortD=0"
POSTDATA1_1="pageNo=\${i}&isTransfer=0&isFresh=-1&isSmall=0"
POSTDATA2_0="pageNo=\${i}&isTransfer=0&isFresh=-1&isSmall=1&loanType=-1&repayMode=-1&guar=-1&sort=openTime&sortD=0"
POSTDATA2_1="pageNo=\${i}&isTransfer=0&isFresh=-1&isSmall=1"
DETAILPAGE="${HOST}/bid/detail/"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
