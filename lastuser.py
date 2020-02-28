from version2.models import *

def main():
    me = Respondent.objects.last()

    for r in Response.objects.filter(respondent=me):
        print(r)