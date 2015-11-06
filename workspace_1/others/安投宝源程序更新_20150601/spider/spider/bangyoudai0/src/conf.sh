HOST="http://www.bangyoudai.com"
INDEXPAGE="${HOST}/plan-plan_list/p-"
DETAILPAGE="${HOST}/plan/id-"
COOKIE=`cat COOKIE`
GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --keep-session-cookie"
