from django.shortcuts import render
from django.http import HttpResponse
from version2.extraction import *
from django.shortcuts import redirect
from version2.models import *
import csv, random, datetime
import pickle
from django.views.decorators.cache import cache_control

num_search_results = 10
# algorithms to be initially displayed on the left and right, respectively
left_alg = "05gfp"
right_alg = "09gfp"
# algorithms to be displayed on left and right after 10 turns
round_one_l = "05gfp"
round_one_r = "09gfp"
round_two_l = "0g"
round_two_r = "03gfp"

# maps algorithm names to lists of snippets
alg_to_snippets = {
    left_alg: extractFromFile(round_one_l + ".txt", num_search_results),
    right_alg: extractFromFile(round_one_r + ".txt", num_search_results),
    round_two_l: extractFromFile(round_two_l + ".txt", num_search_results),
    round_two_r: extractFromFile(round_two_r + ".txt", num_search_results)
}

# whether or not to swap the left and right algorithms on a given turn
with open('version2/swapvals.pickle', 'rb') as fr:
    swap = pickle.load(fr)

def get_ip_address(request):
    """ use requestobject to fetch client machine's IP Address """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', None)
    return ip


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def instructions(request):
    ip = get_ip_address(request)
    browser_info = request.user_agent.os.family + " " + request.user_agent.browser.family + " "
    if request.user_agent.is_pc:
            browser_info += "PC"
    else:
        browser_info += "Mobile"
    first_possible = list(range(49,97))
    second_possible = list(range(1, 49))
    f10 = ""
    s10 = ""
    for i in range(10):
        f10 += str(first_possible.pop(random.randint(0, len(first_possible) - 1))) + " "
        s10 += str(second_possible.pop(random.randint(0, len(second_possible) - 1))) + " "
    user = Respondent(
        ip_addr=ip,
        browser=browser_info,
        order=f10+s10[:-1])
    user.save()
    context = {
        'respondent_id': user.id
    }
    return render(request, 'version2/instructions.html', context)

#### BE CAREFUL WITH THIS METHOD
def getAlgs(id):
    if id >= 49 and not swap[id-1]:
        left_alg = round_one_l
        right_alg = round_one_r
    elif id >= 49:
        left_alg = round_one_r
        right_alg = round_one_l
    elif not swap[id-1]:
        left_alg = round_two_l
        right_alg = round_two_r
    else:
        left_alg = round_two_r
        right_alg = round_two_l
    
    return [left_alg, right_alg]
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def feedback(request, q_id, respondent_id, correct, current_score):
    if correct == 1:
        context = {"q_id": q_id, "respondent_id": respondent_id, "feedback": "CORRECT", "current_score": current_score}
    elif correct == 0:
        context = {"q_id": q_id, "respondent_id": respondent_id, "feedback": "INCORRECT", "current_score": current_score}
    else:
        context = {"q_id": q_id, "respondent_id": respondent_id, "feedback": "SKIPPED", "current_score": current_score}
    
    if (q_id - 1) % 5 == 0:
        context['is_five'] = 1
    else:
        context['is_five'] = 0
        
    return render(request, 'version2/basic_feedback.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def feedback_five(request, q_id, respondent_id, correct, current_score):
    if correct == 1:
        context = {"q_id": q_id, "respondent_id": respondent_id, "feedback": "CORRECT", "current_score": current_score}
    elif correct == 0:
        context = {"q_id": q_id, "respondent_id": respondent_id, "feedback": "INCORRECT", "current_score": current_score}
    else:
        context = {"q_id": q_id, "respondent_id": respondent_id, "feedback": "SKIPPED", "current_score": current_score}
        
    return render(request, 'version2/feedback.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def redir(request, q_id, respondent_id):
    user = Respondent.objects.filter(id=respondent_id)[0]
    id = user.curr_q
    
    if id < q_id:
        query_num = int(user.order.split(" ")[id - 1])
        choice = 'NO_CHOICE'
        not_choice = 'NO_CHOICE'
        if 'radio' in request.GET:
            left_alg = getAlgs(query_num)[0]
            right_alg = getAlgs(query_num)[1]
            if request.GET['radio'] == 'left':
                choice = left_alg
                not_choice = right_alg
            else:
                choice = right_alg
                not_choice = left_alg
        
        if 'time_elapsed' in request.GET:
            response = Response(respondent=user,
                                query=Query.objects.filter(query_id=query_num)[0], #gotta change thisssssssssss
                                chosen_alg=Algorithm.objects.filter(name=choice)[0],
                                unchosen_alg=Algorithm.objects.filter(name=not_choice)[0],
                                time_elapsed=int(request.GET['time_elapsed']))
            response.save()
            
            id += 1
            user.curr_q = id 
            correct = 0
            if choice == "0g" or choice == "05gfp":
                correct = 1
                user.score = user.score + 10 #- int(int(request.GET['time_elapsed']) / 6)
            elif choice == "03gfp" or choice == "09gfp":
                user.score = max(0, user.score - 5)
            else:
                correct = 2
            user.save()
            return redirect('version2-feedback', q_id=id, respondent_id=respondent_id, correct=correct, current_score=user.score)
        
        id += 1
        user.curr_q = id 
        user.save()

        
    return redirect('version2-home', q_id = id, respondent_id=respondent_id)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request, q_id, respondent_id):    
    user = Respondent.objects.filter(id=respondent_id)[0]
    
    if user.curr_q != q_id:
        return redirect('version2-redir', q_id=q_id, respondent_id=respondent_id)
        
    global left_alg
    global right_alg
    request.session.flush()
    font_size_title = "14px"
    font_size_body = "12px"
    title_height = "16px"
    body_height = "20px"
    if "Mobile" in user.browser:
        font_size_title = "20px"
        font_size_body = "18px"
        title_height = "22px"
        body_height = "32px"
    if q_id <= 20:
        query_num = int(user.order.split(" ")[user.curr_q - 1])

        left_alg = getAlgs(query_num)[0]
        right_alg = getAlgs(query_num)[1]
        context = {
            'left_snippets': alg_to_snippets[left_alg][query_num],
            'right_snippets': alg_to_snippets[right_alg][query_num],
            'query_name': alg_to_snippets[right_alg][query_num][0][0],
            'curr_qid': q_id + 1,
            'respondent_id': respondent_id,
            'font_size_title': font_size_title,
            'font_size_body': font_size_body,
            'body_height': body_height,
            'title_height': title_height
        }
        return render(request, 'version2/home.html', context)
    else:
        return redirect('version2-leaderboard', score=user.score)

def sortFirst(val):
    return val[0]
    
def leaderboard(request, score):
    topscores = TopScore.objects.all()
    min_topscore_val = 20000 # larger than the highest possible score
    min_topscore = None
    for ts in topscores:
        if ts.score < min_topscore_val:
            min_topscore_val = ts.score
            min_topscore = ts
    
    if score >= min_topscore_val and 'username' not in request.GET:
        t5_output = []
        topscores = TopScore.objects.all()
        for ts in topscores:
            t5_output.append((ts.score, ts.username))
        t5_output.sort(reverse=True)
        context = {'score': score, 'top_five': t5_output}
        return render(request, 'version2/username.html', context)
    elif 'username' in request.GET:
        min_topscore.score = score
        min_topscore.username = request.GET['username']
        min_topscore.save()
        
    t5_output = []
    topscores = TopScore.objects.all()
    for ts in topscores:
        t5_output.append((ts.score, ts.username))
    
    sdict = {}
    for u in Respondent.objects.all():
        if u.score not in sdict:
            sdict[u.score] = 0
        sdict[u.score] += 1
    freq_output = []
    for key in sdict:
        freq_output.append((key, sdict[key])) 
        
    freq_output.sort(reverse=True)  # remove if unnecessary   
    t5_output.sort(reverse=True)
    context = {
        "top_five": t5_output,
        "score_dict": freq_output,
        "score": score
    }
    return render(request, 'version2/leaderboard.html', context)


def exportUsers(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    writer.writerow(['id','ip_addr','email','browser','date'])
    for u in Respondent.objects.all().values_list('id', 'ip_addr', 'email', 'browser', 'date'):
        writer.writerow(u)
    today = datetime.date.today()
    filename = "users_" + today.strftime("%m_%d_%Y") + ".csv"
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    return response

def exportResponses(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    writer.writerow(['user_id','chosen','unchosen','query','time_elapsed','date'])
    for r in Response.objects.all():
        writer.writerow([r.respondent.id, r.chosen_alg.name, r.unchosen_alg.name, r.query.query_name, r.time_elapsed, r.date])
    today = datetime.date.today()
    filename = "responses_" + today.strftime("%m_%d_%Y") + ".csv"
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    return response