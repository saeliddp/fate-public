from version2.models import *
import ipinfo

access_token = 'b85753035711db'
handler = ipinfo.getHandler(access_token)
rpds = Respondent.objects.all()

def country_frequency():
    cfdict = {}
    for r in rpds:
        details = handler.getDetails(r.ip_addr)
        if details.country not in cfdict:
            cfdict[details.country] = 0
        cfdict[details.country] += 1
    return cfdict
    