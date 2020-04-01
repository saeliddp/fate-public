from version2.models import *
responses = Response.objects.all()
users = Respondent.objects.all()

def toCSV(data):
    out = ""
    out += str(data[0])
    for d in data[1:]:
        out += "," + str(d)
    return out

def printResponses(start_ind=0, end_ind=len(responses)-1):
    print("user_id,chosen,unchosen,query,time_elapsed,date")
    for r in responses:
        print(toCSV([r.respondent.id, r.chosen_alg.name, r.unchosen_alg.name, r.query.query_name, r.time_elapsed, r.date]))
        
def printUsers(start_ind=0, end_ind=len(users)-1):
    print("user_id,ip_addr,browser,score,current_question,date")
    for u in users:
        print(toCSV([u.id, u.ip_addr, u.browser, u.score, u.curr_q, u.date]))