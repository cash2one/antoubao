HOST='http://www.winwindai.com'
INDEXPAGE1="${HOST}/finance.do?pageSize=10&title=&type=&m=&deadline=&isDayThe="
INDEXPAGE2="${HOST}/financeCyb.do?pageSize=10&title=&type=&m=&deadline=&isDayThe="
DETAILPAGE1="${HOST}/financeDetail.do?id="
DETAILPAGE2="${HOST}/currentInvestInit.do?id="
INVESTORPAGE="${HOST}/getInvestList.do"
JSESSIONID=`cat JSESSIONID`
GETPAGE="wget --no-cookies --header=\"Cookie: JSESSIONID=${JSESSIONID}; IESESSION=alive;\" --keep-session-cookie --no-check-certificate"

