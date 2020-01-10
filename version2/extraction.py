from classes.snippet import *
import pickle

# splits the DOCUMENT# by the middle '00' to get qid and r
def splitByDoubleZeros(doc_num):
    # finds index of last zero, not including any trailing zeroes
    num_trailing = 0
    temp_ind = len(doc_num) - 1
    while doc_num[temp_ind] == str(0):
        num_trailing += 1
        temp_ind -= 1
    
    last_zero_ind = doc_num[:len(doc_num) - num_trailing].rindex('0')
    
    # [qid, r]
    return [doc_num[:last_zero_ind - 1], doc_num[last_zero_ind + 1:]]
    

# finds the index of a Snippet with the given original rank in a list of Snippets
# returns None if the desired Snippet is not found
def binarySnippetSearch(low_index, high_index, og_rank, snippet_list):
    median = int((low_index + high_index) / 2)
    median_rank = int(snippet_list[median].get_rank())
    #print("low: " + str(low_index) + " high: " + str(high_index) + " high rank: " + snippet_list[high_index].get_rank())
    if median_rank == og_rank:
        return snippet_list[median]
    elif low_index == high_index:
        print("couldn't find snippet with og_rank" + str(og_rank))
        return None
    elif low_index == high_index - 1:
        return binarySnippetSearch(high_index, high_index, og_rank, snippet_list)
    elif median_rank < og_rank:
        return binarySnippetSearch(median, high_index, og_rank, snippet_list)
    else:
        return binarySnippetSearch(low_index, median, og_rank, snippet_list)

"""
returns snippet data in the format:
    {
        qid1: [[query_name, snippet1title, snippet1url, snippet1desc], [query_name, snippet2title...]],
        qid2: [...]
    }

for each qid, snippet1 corresponds to the first snippet in the reranked list
"""
# query 82 is nonexistent
def extractFromFile(file_name, num_snippets):
    file = open("./version2/txtdata/version2/" + file_name, "r")
    lines = file.readlines()
    file.close()
    
    with open("./version2/snippet.pickle", 'rb') as fr:
        query_snippet_list = pickle.load(fr)
        
    results = {}
    
    # there are 10 results for a given query, but we only want to
    # inspect a certain number
    
    # the number of snippets added to the current qid in results
    snippets_added = 0
    curr_qid = -1
    for line in lines:
        tokens = line.split(' ')
        q_and_r = splitByDoubleZeros(tokens[2])
        qid = int(q_and_r[0])
        
        # once a new qid is reached, set curr_qid equal to it,
        # set snippets_added equal to zero, and add an empty list at
        # results[currQid]
        if curr_qid != qid:
            curr_qid = qid
            snippets_added = 0
            results[curr_qid] = []
           
        if snippets_added < num_snippets:
            og_rank = int(q_and_r[1])
            new_rank = int(tokens[3]) # corresponds to RANK
            
            query_snippet = query_snippet_list[qid - 1]
            snippet_list = query_snippet.snippetList            
            curr_snippet = binarySnippetSearch(0, len(snippet_list) - 1, og_rank, snippet_list)
            if curr_snippet is None:
                print(curr_qid)
            #if og_rank != int(curr_snippet.get_rank()):
                #print("Current Snippet's original rank is unequal to the 'r' field in the .txt file.")
                
            # [query_name, title, url, description]
            # replaces double quotes with single quotes
            results[qid].append([query_snippet.query.replace('"', "'"), curr_snippet.get_title().replace('"', "'"), 
                                curr_snippet.get_url().replace('"', "'"), curr_snippet.get_desc().replace('"', "'")])
                                
            snippets_added += 1
            
    
    return results

    
    


