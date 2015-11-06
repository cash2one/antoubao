HOST='https://www.ddgbank.com'
INDEXPAGE="${HOST}/Plan/index/p"
DETAILPAGE="${HOST}/plan"
INVESTPAGE="${HOST}/plan/getInvestments.html?pid="
PHPSESSID=`cat PHPSESSID`
GETPAGE="wget"
GETPAGE1="wget --no-cookies --header=\"Cookie: PHPSESSID=${PHPSESSID}; PHPSESSID_NS_Sig=oenCV6mfyjki71O7; ddg_home_3e7e22b67764ffd727da564826610ecb=1;\" --keep-session-cookie --no-check-certificate"
