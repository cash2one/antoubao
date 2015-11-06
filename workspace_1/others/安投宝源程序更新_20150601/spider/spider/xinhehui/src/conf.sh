HOST="https://www.xinhehui.com"
TYPE=("2" "3" "4" "6")
INDEXPAGE="${HOST}/Financing/Invest/ajaxplist?c=\${TYPE[\${t}]}&p="
DETAILPAGE1="${HOST}/Financing/Invest/view?id="
DETAILPAGE2="${HOST}/Financing/Invest/fastCash?id="
DETAILPAGE="${HOST}/Financing/Invest/ajaxBuyLog?id=\${BID}&p="
DETAILPAGE_1="${HOST}/Financing/Invest/ajaxBuyLog?id=\${BID}&p=1"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
