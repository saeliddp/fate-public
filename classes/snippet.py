'''
Created on Oct 5, 2018

@author: rg522
'''

class Snippet(object):
    def __init__(self, query=''):
        self.__rank = 0
        self.__title = ''
        self.__url = ''
        self.__desc = ''
#         self.__query = query

    def get_query(self):
        return self.__query

    def get_rank(self):
        return self.__rank

    def get_title(self):
        return self.__title
    
    def get_url(self):
        return self.__url

    def get_desc(self):
        return self.__desc

    def set_rank(self, value):
        self.__rank = value

    def set_title(self, value):
        self.__title = value

    def set_url(self, value):
        self.__url = value

    def set_desc(self, value):
        self.__desc = value
        
    def set_query(self, value):
        self.__query = value

    def __str__(self):
        return self.__title + '\n' + self.__url + '\n' + self.__desc
    
    def __hash__(self):
        return self.__rank
    
    def __eq__(self, other):
#         return self.__rank == other.__rank
        return self.__rank == other
    
class QuerySnippet(object):
    def __init__(self, q):
        self.query = q
        self.snippetList = []
        
    def add_snippet(self, s):
        self.snippetList.append(s)
    
    def __hash__(self):
        return self.query
    
    def __eq__(self, other):
#         return self.query == other.query
        return self.query == other
    
    