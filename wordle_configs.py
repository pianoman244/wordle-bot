"""
There is no need for this file. It's an overly complicated way of generating the 
3^5 possible combinations of greens, yellows, and grays after guessing a word. 
result_configs() is called in the initializer for Wordle_Information.
"""


import itertools

class unique_element:
    def __init__(self,value,occurrences):
        self.value = value
        self.occurrences = occurrences

# unique permutations of elements
def perm_unique(elements):
    eset=set(elements)
    listunique = [unique_element(i,elements.count(i)) for i in eset]
    u=len(elements)
    return perm_unique_helper(listunique,[0]*u,u-1)

def perm_unique_helper(listunique,result_list,d):
    if d < 0:
        yield tuple(result_list)
    else:
        for i in listunique:
            if i.occurrences > 0:
                result_list[d]=i.value
                i.occurrences-=1
                for g in  perm_unique_helper(listunique,result_list,d-1):
                    yield g
                i.occurrences+=1

# all possible information outputs from a given guess
def result_configs():
    configs = []
    for comb in itertools.combinations_with_replacement([0, 1, 2], 5):
        for perm in perm_unique(comb):
            configs.append(perm) 
    
    return configs