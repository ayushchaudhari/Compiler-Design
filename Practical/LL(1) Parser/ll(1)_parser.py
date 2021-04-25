"""""
A LL(1) Parse Table Generation algorithm by Ayush Chaudhari
Dated:23/April/2021
---------------------------------------------------------------------------------------------
Variables and Terminalogies:

Variables: 
language_statements -> List comprising of all the productions
dictionary: dictionary containing key as non terminal and its value as the list of production
nonTerminal: List of the keys of dictionary (basically comprising of Non Terminal or variable)
dictOf_first -> dictionary containing key as non terminal and its value as list of firsts
dictOf_follow -> dictionary containing key as non terminal and its value as list of follow
set_of_first -> set of all the first of a particular non-terminal
set_of_follow -> set of all the follow of a particular non-terminal

Terminalogies:
Letter,key -> letter,key is used for the non terminals(capital letters[A-Z])
definition -> definition is used for produce of the non-terminals {example:If S->Aab is production so definition is "Aab" which is produce of non-terminal->'S'}
expression -> expression is used for particular produce in all the produces of non-terminals {example:If S->Aab|@ then there are 2 expression->['Aab','@']} 

Default Consideration:
@ as Є
S as default Start Symbol

Rules for first:
1: First(terminal) -> terminal
2: First(Є) -> Є   OR   First(@)->@ as @ is considered as ε
3: If X->Y1 Y2 Y3 ... Yn is a production,
   First(X) = First(Y1)
   If First(Y1) contains Є then First(X) = { First(Y1) – Є } U { First(Y2) }
   If First (Yi) contains Є for all i = 1 to n, then add Є to First(X)
    For example:
    X->AAb , A->a|@
    First(X)->First(A)->{'a','@'} then as it considered @ so find the First(next symbol of expression){find the first of next symbol++ recursively till the first has '@' and till the end of expression} 
    like First(A) again ->{a,'@'} so again '@' then find first(b)->b 
    Then final set of {'a','b','@'}

Rules for Follow:
1: FOLLOW(S) = {$}   // where S is the starting Non-Terminal
2: If A -> pBq is a production, where p, B and q are any grammar symbols,
   then everything in FIRST(q)  except Є is in FOLLOW(B).
3: If A->pB is a production, then everything in FOLLOW(A) is in FOLLOW(B).
4: If A->pBq is a production and FIRST(q) contains Є, 
   then FOLLOW(B) contains { FIRST(q) – Є } U FOLLOW(A)

Requirements-
pip install ordered-set
pip install prettytable
"""""

from ordered_set import OrderedSet
from prettytable import PrettyTable
import re

regex = "(?:[*+()@]|[a-z])"
keywords = "(id)|(int)|(char)"


def calc_setOf_first(letter,dictionary,dictOf_first,i):
    set_of_first = OrderedSet()

    for expression in dictionary[letter]:
        if re.match(keywords,expression):
            set_of_first.add(expression)   
        elif re.match(regex,expression[i]):
            set_of_first.add(expression[i])
        else:    
            set_temp = OrderedSet()
            set_temp.update(dictOf_first[expression[i]])
            i+=1
            
            if '@' in set_temp and i<len(expression):
                set_temp.update(calc_setOf_first(letter,dictionary,dictOf_first,i)) 
                
            set_of_first.update(set_temp)
            
    return set_of_first


#this function calls function named cal_setOf_first
def first(nonTerminals,dictionary):
    dictOf_first = {}

    for letter in reversed(nonTerminals):
        set_of_first = calc_setOf_first(letter,dictionary,dictOf_first,0) #list of all the first of letter by letter 
        dictOf_first[letter] = set_of_first

    return dictOf_first
#----------------------------------this is end of first---------------------------------------# 


#this function returns the set of follow for a particular non-Terminal
def recursive_follow(key,dictionary,dictOf_first,dictOf_follow):
    if key in dictOf_follow:
        return dictOf_follow[key]
        
    for key_temp in dictionary:
        for expression in dictionary[key_temp]:
            if key in expression:# finding its first occurence in right hand side of all the keys
                if expression.index(key) < len(expression)-1: #coming in between somewhere or at the start of the expression
                    if re.match(regex,expression[expression.index(key)+1]):
                        return OrderedSet(expression[expression.index(key)+1])
                    else:
                        if '@' in dictOf_first[expression[expression.index(key)+1]]:
                            set_temp=OrderedSet(dictOf_first[expression[expression.index(key)+1]])
                            set_temp.remove('@')
                            set_temp.update(recursive_follow(expression[expression.index(key)+1],dictionary,dictOf_first,dictOf_follow))                                    
                        else:
                            set_temp=OrderedSet(dictOf_first[expression[expression.index(key)+1]])
                        return(set_temp)
                else: # this is if the terminal is found @ end of string
                    set_temp=OrderedSet()
                    set_temp.update(recursive_follow(key_temp,dictionary,dictOf_first,dictOf_follow))
                    return set_temp
    
    return OrderedSet()


#this function calls another function named recursive_follow
def follow(dictionary,dictOf_first):
    dictOf_follow={}
    # default start symbol S
    for key in dictionary:
        dictOf_follow[key] = recursive_follow(key,dictionary,dictOf_first,dictOf_follow)
        if key=='S':
            dictOf_follow[key].add('$')
        
    return dictOf_follow
#----------------------------------------follow ends here--------------------------------------#

def find_terminals(dictionary):
    terminal_reg = "(?:[*+()]|(id)|[a-z])"
    keywords_reg="((id)|(int)|(char))"
    terminals=OrderedSet()
    # terminals=[expression[0] for nT,expression in dictionary.items() if re.match(terminal_reg, expression[0])]
    for nT in dictionary:
        for expression in dictionary[nT]:
            if re.match(keywords_reg,expression):
                terminals.append(expression)
                continue
            for (i,alphabet) in enumerate(expression):
                if re.match(terminal_reg,alphabet):
                    terminals.append(alphabet)
    return terminals


#------------------------------------------parse-table-------------------------------------#
def first_of_exp(dictionary,expression,i,dictOf_first): #this function calculates the first for a expression i.e. for a single production of a Non Terminal in list of all the production present
    set_of_first=OrderedSet()

    if re.match(keywords,expression):
        set_of_first.add(expression)
    elif re.match(regex,expression[i]):
        set_of_first.add(expression[i])
    else:    
        return_set = dictOf_first[expression[i]]
        i+=1

        if '@' in return_set and i < len(expression):
            return_set.update(first_of_exp(dictionary,expression,i,dictOf_first))

        set_of_first.update(return_set)

    return set_of_first


def LL1_parser(dictionary,dictOf_first,dictOf_follow,terminals,nonTerminals): #this function makes the LL(1) Parse table
    parse_table = PrettyTable(['NT/t']+terminals)

    for nT in nonTerminals:
        temp_list = [nT]+[list() for term in enumerate(terminals)]  #temp_list is a list having expression @ the index of all its first
        for exp in dictionary[nT]:
            set_of_first = first_of_exp(dictionary, exp, 0, dictOf_first)   #set_of_first is a OrderedSet having first with respect to a certain expression
            if '@' in set_of_first:
                set_of_first.remove('@')
                set_of_first.update(dictOf_follow[nT])
            for item in set_of_first:
                temp_list[terminals.index(item)+1].append(nT+"->"+exp)
        
        parse_table.add_row(temp_list)

    return parse_table
#--------------------------------------------------------------------------------------------#


if __name__=="__main__":
    import os
    #os is imported to get the path of current running py file
    # path=os.path.dirname(__file__)
    
    # with open(f'{path}\input.txt', 'r') as file:
    #     language_statements = [line.strip() for line in file]

    grammer="S->TR,R->+TR|@,T->FY,Y->*FY|@,F->id|(S)"
    
    language_statements=grammer.split(',')


    print("\nInput taken succesfully :",language_statements)
    
    # tokenizing
    print("\nTokenizing:")
    dictionary={}
    for statement in language_statements:
        letter,definition=statement.split('->')
        dictionary[letter]=definition.split('|')
        print(letter,":",definition.split('|'))
   
    nonTerminals=list(dictionary) #this is the list of the keys comprising of Non Terminal letter

    #------------------------------calculation of first-------------------------------------#
    print("\nThe first for the given grammer-")
    dictOf_first=first(nonTerminals,dictionary)
    for letter in nonTerminals:
        print(letter,":",dictOf_first[letter])

    #------------------------------calculation of follow-------------------------------------#
    print("\nThe follow for the given grammer:")
    dictOf_follow=follow(dictionary,dictOf_first)
    for letter in nonTerminals:
        print(letter,":",dictOf_follow[letter])

    #-------------------------------------Parse Table-----------------------------------------#
    terminals_list = list(find_terminals(dictionary))
    terminals_list.append('$') #since parse table also has a coloumn of $ for special case i.e. 'Є' as in case of first->Є we see the follow of its parent nonTerminal from where it is derived and the follow might contain '$'
    #non terminals list is we already have in nonTerminals
    parse_table = LL1_parser(dictionary,dictOf_first,dictOf_follow,terminals_list,nonTerminals)
    print("\nThe LL(1) Parse Table is as follow:")
    print(parse_table)
    #-----------------------------------------------------------------------------------------#