"""""
A Indirect & Direct Left Recursion algorithm by Ayush Chaudhari
Approach Used: Top Down Parsing of Symbols
Dated:21/April/2021
Logic & Terminalogies @  https://git.io/JOrnB
"""""

import os
import re
terminal_reg = "(?:[*+()@]|[a-z])"      #used in function "recursive_rm_Indirect_LR()" & "find_IdLR"



def encode(dictionary,nonTerminals):
    encode_dictionary={}
    mapping_list=[]

    symbol_ascii=64 #base symbol is considered as the ascii of(A)-1 which is 64
    
    for (index,nT) in enumerate(nonTerminals):
        if(index==0): #this means it is at the first place so this symbol is the starting symbol
            encode_dictionary['S']=dictionary[nT]
            mapping_list.append([nT,'S'])   #default_starting_symbol is 'S'
        else:
            if(symbol_ascii==83):
                symbol_ascii+=1
            encode_dictionary[chr(symbol_ascii)]=dictionary[nT]
            mapping_list.append([nT,chr(symbol_ascii)])

        symbol_ascii+=1
    #until this just the keys are being changed and the value i.e. list that are mapped with keys are not changed
    
    for nonTerminal in list(encode_dictionary):
        for (i,expression) in enumerate(encode_dictionary[nonTerminal]):
            for values in mapping_list: #values is a list having given default inputted nonTerminal value @ 0th index and changed nonTerminal value @ 1st index
                if expression[0]==values[0]:
                    encode_dictionary[nonTerminal][i]=expression.replace(values[0],values[1])
                    break
    
    return encode_dictionary,mapping_list



def new_char_generator(dictionary):
    total_keys=len(list(dictionary))
    if chr(64+total_keys)=='S':
        return chr(64+total_keys+1)
    return chr(64+total_keys)



def removeDLR(dictionary):
    Dict_removeDLR={}
    state=[0 for i in range(0,len(list(dictionary)))]
    for nonTerminal in dictionary:
        Dict_removeDLR[nonTerminal]=set()
    for (state_index,nonTerminal) in enumerate(dictionary):
        assign=""
        for (i,expression) in enumerate(dictionary[nonTerminal]):
            if(expression[0]=='@'):
                Dict_removeDLR[nonTerminal].add(assign)
            elif expression[0]==nonTerminal:  #if expression has the nonterminal at first index
                if state[state_index]==0:
                    assign=new_char_generator(Dict_removeDLR)
                    state[state_index]=1
                    Dict_removeDLR[assign]=set('@')
                
                # element=dictionary[nonTerminal][i][1:]+assign #it is deleting the non-terminal which is @ the start of the expression and add the new symbol at the last and adds it to the set of the new symbol assigned respectively
                Dict_removeDLR[assign].add(dictionary[nonTerminal][i][1:]+assign)
            else:
                # element=expression+assign #it is adding the new symbol at the last of the expression, the expression which is not starting with the current non-terminal and adding it to the same set belonging to that non-terminal respectively 
                Dict_removeDLR[nonTerminal].add(expression+assign)

    return Dict_removeDLR



def recursive_rm_Indirect_LR(rem_IdLR_dictionary,expression,current_NT,indirect_NT,arbNT_order):    
    set_replacing_particular_expression=set()
    
    remaining_expression=""

    if len(expression)> 1:
        remaining_expression=expression[1:]

    for exp in rem_IdLR_dictionary[indirect_NT]:
        if re.match(terminal_reg,exp[0]):
            continue

        if(exp[0]==current_NT):#exp[0]==currentNT means the indirectLR expression has reached to the end of its depth and now just we have to re found directly without any more idirect ways so directly add that exp at the place of the expression[0] and keep the remaining expression[1:] same             
            set_replacing_particular_expression.add(exp+remaining_expression)

        elif arbNT_order.index(exp[0]) > arbNT_order.index(current_NT): #this means that currentNt should always be less in Arbitrary order from the other nonTerminal which is found #less means currentNT comes first
            set_replacing_particular_expression.update(recursive_rm_Indirect_LR(rem_IdLR_dictionary,exp,current_NT,exp[0],arbNT_order))
            #temp_list just saves the set value in it temperorily for some operations
            temp_list=list(set_replacing_particular_expression)
            for i in range(len(temp_list)):
                temp_list[i]+=remaining_expression
            set_replacing_particular_expression=set(temp_list)

    return set_replacing_particular_expression



def find_IdLR(dictionary,arbNT_order):
    rem_IdLR_dictionary=dictionary.copy()
    for nonTerminal in dictionary:
        set_temp=set()
        for (i,expression) in enumerate(dictionary[nonTerminal]):
            if expression[0] in list(dictionary) and expression[0]!=nonTerminal and not re.match(terminal_reg,expression[0]):                
                set_replacing_expression=recursive_rm_Indirect_LR(rem_IdLR_dictionary,expression,nonTerminal,expression[0],arbNT_order)

#if set returned is empty no indirect LR found
#if set returned is not empty then it means it has indirect LR so delete that element from the rem_IdLR_dictionary and append the returned set in that existing set of productions, but I appended the whole set at the last when every expression of a current_nt is iterated so that there is no runtime error while iterating the list of expression for a particular nonTerminals' production                 
                if(set_replacing_expression!=set()):#means set is not empty
                    rem_IdLR_dictionary[nonTerminal]=rem_IdLR_dictionary[nonTerminal][:i]+rem_IdLR_dictionary[nonTerminal][i+1:] #that expression is removed
                    set_temp.update(set_replacing_expression) #set_temp saves the whole replacing set for a particular nonTerminal at an instance as it keeps updating itself for every expression

        rem_IdLR_dictionary[nonTerminal]+=set_temp #at last of every loop we append the replacing set to the list of expression of a particular nonTerminal at a instance

    return rem_IdLR_dictionary



def default_dict_former(dictionary):#convert the dictionary to default form such that every list of production has expression having DLR @ the 1st priority and kept at the starting index and then after that expression starting with either nonTerminals or terminals at the last.
    for nonTerminal in dictionary:
        front_list=[]
        rear_list=[]
        for expression in dictionary[nonTerminal]:
            if(expression[0]==nonTerminal):
                front_list.append(expression)
            else:
                rear_list.append(expression)
        front_list=sorted(front_list)
        rear_list=sorted(rear_list)
        dictionary[nonTerminal]=front_list+rear_list
    
    return dictionary



def left_recursion(dictionary,arbNT_order):
    Dict_removeLR={}
    state=[0 for i in range(0,len(list(dictionary)))]
    
    for nonTerminal in dictionary:
        Dict_removeLR[nonTerminal]=set()

    rem_IdLR_dictionary=find_IdLR(dictionary,arbNT_order)   #find_IdLR() function just normalizes the dictionary by finding indirectLR and calls recursive_rm_Indirect_LR which is a recursive function that converts indirectLR to directLR    
    rem_IdLR_dictionary=default_dict_former(rem_IdLR_dictionary)   #default_dict_former() function just convert the dictionary to default form i.e. for a nonTerminal its list is converted such that the expression @ first must have a expression in the list starting with that non terminal and if there is no such expression the sequence is just sorted alphabetically 
    
    return removeDLR(rem_IdLR_dictionary)



if __name__=="__main__":
    """path of current python file directory"""
    path=os.path.dirname(__file__) 

    with open(f'{path}\input.txt', 'r') as file:
        productions = [line.strip() for line in file]
    
    print("Input taken succesfully :",productions)
    
    # tokenizing
    print("Tokenizing:")
    dictionary={}
    inputWise_nonTerminals=[]
    
    for production in productions:
        nonTerminal,rhs=production.split('->')
        dictionary[nonTerminal]=rhs.split('|')
        inputWise_nonTerminals.append(nonTerminal)
        print(nonTerminal,":",dictionary[nonTerminal])

    encode_dictionary,mapping_list=encode(dictionary,inputWise_nonTerminals)
    print("Encoded Dictionary:\n",encode_dictionary)
    print("Considerations are as follows-")
    for mappings in mapping_list:
        print(mappings[0],"->",mappings[1])
    
    #Arbitrary Order is to be considered for indirectLR case
    #And I considered Arbitrary order as the nonTerminal defined first in dictionary as the first in the list also(highest athority of first) and nonterminal at the last is at the last of list(& has lowest authority)
    arbNT_order=[mappings[1] for mappings in mapping_list]  #arbitrary order starts always with S start symbol and goes on so 'S' in every order as per my algorithm has highest order. Order decreses as the Index of list increases
    
    Dict_removeLR=left_recursion(encode_dictionary,arbNT_order)
    print("Dictionary after removing Left recursion is-\n",Dict_removeLR)