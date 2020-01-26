from django.shortcuts import render
from django.http import HttpResponse
from version2.extraction import *
from django.shortcuts import redirect
from version2.models import *
import random
from django.views.decorators.cache import cache_control

num_search_results = 10
# algorithms to be initially displayed on the left and right, respectively
left_alg = "0g"
right_alg = "03gfp"
# algorithms to be displayed on left and right after 10 turns
round_one_l = "0g"
round_one_r = "03gfp"
round_two_l = "05gfp"
round_two_r = "09gfp"

# maps algorithm names to lists of snippets
alg_to_snippets = {
    left_alg: extractFromFile(round_one_l + ".txt", num_search_results),
    right_alg: extractFromFile(round_one_r + ".txt", num_search_results),
    round_two_l: extractFromFile(round_two_l + ".txt", num_search_results),
    round_two_r: extractFromFile(round_two_r + ".txt", num_search_results)
}

# whether or not to swap the left and right algorithms on a given turn
swap = [False, True, True, False, True, True, True, False, False, False, False, False, True, True, False, False, True, False, True, True, False]

def get_ip_address(request):
    """ use requestobject to fetch client machine's IP Address """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', None)
    return ip
    
def consent(request):
    return render(request, 'version2/consent.html')
    
def email(request):
    """
    if 'email' in request.GET:
        if len(Respondent.objects.filter(email=request.GET['email'])) > 0:
            context = {'prompt': "Someone has already used that email to play! Please enter a valid email:"}
            return render(request, 'version2/email.html', context)
        ip = get_ip_address(request)
        browser_info = request.user_agent.os.family + " " + request.user_agent.browser.family + " "
        if request.user_agent.is_pc:
            browser_info += "PC"
        else:
            browser_info += "Mobile"
            
        respondent = Respondent(
            ip_addr=ip,
            email=request.GET['email'],
            browser=browser_info)
        respondent.save()
        return redirect('version2-instructions', respondent_id=respondent.id)
    else:
        context = {'prompt': "Please enter your email below:"}
        return render(request, 'version2/email.html', context)
    """
    ip = get_ip_address(request)
    browser_info = request.user_agent.os.family + " " + request.user_agent.browser.family + " "
    if request.user_agent.is_pc:
            browser_info += "PC"
    else:
        browser_info += "Mobile"
            
    respondent = Respondent(
        ip_addr=ip,
        browser=browser_info)
    respondent.save()
    return redirect('version2-instructions', respondent_id=respondent.id)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def instructions(request, respondent_id):
    user = Respondent.objects.filter(id=respondent_id)[0]
    if user.curr_q != 0:
        return redirect('version2-redir', q_id=1, respondent_id=respondent_id)
    else:
        context = {
            'respondent_id': respondent_id
        }
        return render(request, 'version2/instructions.html', context)

def getAlgs(id):
    if id < 11 and not swap[id-1]:
        left_alg = round_one_l
        right_alg = round_one_r
    elif id < 11:
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
def feedback(request, q_id, respondent_id, correct):
    if correct == 1:
        context = {"q_id": q_id, "respondent_id": respondent_id, "feedback": "CORRECT"}
    elif correct == 0:
        context = {"q_id": q_id, "respondent_id": respondent_id, "feedback": "INCORRECT"}
    else:
        return redirect("version2-home", q_id=q_id, respondent_id=respondent_id)
    return render(request, 'version2/feedback.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def redir(request, q_id, respondent_id):
    user = Respondent.objects.filter(id=respondent_id)[0]
    id = user.curr_q
    
    if id < q_id:
        choice = 'NO_CHOICE'
        not_choice = 'NO_CHOICE'
        if 'radio' in request.GET:
            left_alg = getAlgs(id)[0]
            right_alg = getAlgs(id)[1]
            if request.GET['radio'] == 'left':
                choice = left_alg
                not_choice = right_alg
            else:
                choice = right_alg
                not_choice = left_alg
        
        if 'time_elapsed' in request.GET:
            response = Response(respondent=user,
                                query=Query.objects.filter(query_id=id)[0],
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
            return redirect('version2-feedback', q_id=id, respondent_id=respondent_id, correct=correct)
        
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
        
    left_alg = getAlgs(q_id)[0]
    right_alg = getAlgs(q_id)[1]
    request.session.flush()
    if q_id <= 20:
        context = {
            'left_snippets': alg_to_snippets[left_alg][q_id],
            'right_snippets': alg_to_snippets[right_alg][q_id],
            'query_name': alg_to_snippets[right_alg][q_id][0][0],
            'curr_qid': q_id + 1,
            'respondent_id': respondent_id
        }
        return render(request, 'version2/home.html', context)
    else:
        return redirect('version2-leaderboard', score=user.score)

def sortFirst(val):
    return val[0]
    
def leaderboard(request, score):
    users = Respondent.objects.all()
    output = {}
    for u in users:
        if u.score not in output:
            output[u.score] = 0
        output[u.score] += 1
    a_output = []
    for key in output:
        a_output.append((key, output[key]))
    context = {
        "score_dict": a_output,
        "score": score
    }
    return render(request, 'version2/leaderboard.html', context)
    
