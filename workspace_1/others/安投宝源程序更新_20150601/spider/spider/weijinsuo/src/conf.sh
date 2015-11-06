HOST='http://www.weijinsuo.com'

GETPAGE="wget"

LOANTYPE=("Loan" "WXBLoan" "CommonLoan")
INDEXPAGE="${HOST}/callApi.do?callUrl=get\${LOANTYPE[\${t}]}List.do"
POSTDATA=("info=%7B'pageIndex'%3A'\${i}'%2C'pageSize'%3A'9'%7D&auth=%7B'source'%3A'7'%2C'vendor'%3A'100000'%2C'osver'%3A'1'%2C'appver'%3A'1'%2C'version'%3A22%2C'base64'%3A'1'%7D" "info=%7B'pageIndex'%3A'\${i}'%2C'pageSize'%3A'9'%7D&auth=%7B'source'%3A'7'%2C'vendor'%3A'100000'%2C'osver'%3A'1'%2C'appver'%3A'1'%2C'version'%3A22%2C'base64'%3A'1'%7D" "info=%7B'pageIndex'%3A'\${i}'%2C'pageSize'%3A'9'%2C'applyType'%3A'5'%7D&auth=%7B'source'%3A'7'%2C'vendor'%3A'100000'%2C'osver'%3A'1'%2C'appver'%3A'1'%2C'version'%3A21%2C'base64'%3A'1'%7D")

DETAILPAGE1=("${HOST}/callApi.do?callUrl=getLoanDetail.do" "${HOST}/callApi.do?callUrl=getPersistentLoanDetail.do" "${HOST}/callApi.do?callUrl=getLoanDetail.do")
DETAILPAGE2=("${HOST}/callApi.do?callUrl=getInvestmentLog.do" "${HOST}/callApi.do?callUrl=getPersistentLoanInvDetail.do" "${HOST}/callApi.do?callUrl=getInvestmentLog.do")



#DETAILPOST=("info=%7B'loanId'%3A'\${BID}'%7D&auth=%7B'source'%3A'7'%2C'vendor'%3A'100000'%2C'osver'%3A'1'%2C'appver'%3A'1'%2C'version'%3A20%2C'base64'%3A'1'%7D" "info=%7B'loanId'%3A'\${BID}'%7D&auth=%7B'source'%3A'7'%2C'vendor'%3A'100000'%2C'osver'%3A'1'%2C'appver'%3A'1'%2C'version'%3A21%2C'base64'%3A'1'%7D" "info=%7B'loanId'%3A'\${BID}'%7D&auth=%7B'source'%3A'7'%2C'vendor'%3A'100000'%2C'osver'%3A'1'%2C'appver'%3A'1'%2C'version'%3A20%2C'base64'%3A'1'%7D")
DETAILPOST=("info=%7B'loanId'%3A'\${BID}'%7D&auth=%7B'source'%3A'7'%2C'vendor'%3A'100000'%2C'osver'%3A'1'%2C'appver'%3A'1'%2C'version'%3A20%2C'base64'%3A'1'%7D" "info=%7B'loanId'%3A'\${BID}'%7D&auth=%7B'source'%3A'7'%2C'vendor'%3A'100000'%2C'osver'%3A'1'%2C'appver'%3A'1'%2C'version'%3A21%2C'base64'%3A'1'%7D" "info=%7B'loanId'%3A'\${BID}'%7D&auth=%7B'source'%3A'7'%2C'vendor'%3A'100000'%2C'osver'%3A'1'%2C'appver'%3A'1'%2C'version'%3A20%2C'base64'%3A'1'%7D")
