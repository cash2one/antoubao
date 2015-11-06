HOST="http://www.yooli.com"
INDEXPAGE="${HOST}/dingcunbao"
POSTDATA_INDEX="PAGE_NO_KEY=\${i}&PAGE_COUNT_KEY=\${pagecount}&PAGE_SIZE_KEY=\${pagesize}&PAGE_RECORDCOUNT_KEY=\${recordcount}&sortingField=&isDesc=true"
DETAILPAGE1="${HOST}/dingcunbao/detail/"
DETAILPAGE2="${HOST}/rest/financePlan/getFinancePlanInvestorByPlanId"
POSTDATA2="financePlanId=\${VID}&pageSize=\${PSIZE}&currentPage=" 
#COOKIE=`cat COOKIE`
#GETPAGE="wget --no-cookies --header=\"Cookie: ${COOKIE}\" --header=\"User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36\" --keep-session-cookie"
GETPAGE="wget --no-cookies --header=\"Accept-Language:zh-CN,zh;q=0.8,en;q=0.6\" --keep-session-cookie"
