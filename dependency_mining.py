from itertools import combinations  
import pandas as pd
import numpy as np
import operator
import time
import sys

'''
final
'''

class Literal:
    '''
    the strcture of one literal
    '''
    attributeLabel = -1 
    def __init__(self,identity,variable,attribute,value,isEqual,eqVari,eqAttri,equalClass,entityType):
        self.identity = identity
        self.variable = variable
        self.attribute = attribute
        self.value = value
        self.isEqual = isEqual
        self.eqVari = eqVari
        self.eqAttri = eqAttri
        self.equalClass = equalClass
        self.entityType = entityType

    def getValue(self):
        if self.isEqual:
            return "%s.%s=%s.%s" % (self.eqVari[0],self.eqAttri[0],self.eqVari[1],self.eqAttri[1])
        else:
            return "%s.%s=%s" % (self.variable,self.attribute,self.value)

    def __repr__(self):
        if self.isEqual:
            return "%s.%s=%s.%s" % (self.eqVari[0],self.eqAttri[0],self.eqVari[1],self.eqAttri[1])
        else:
            return "%s.%s=%s" % (self.variable,self.attribute,self.value)

class Block:
    '''
    the strcture of one block of each lattice level
    '''
    def __init__(self,attributeLabels,literalsSet):
        self.attributeLabels = attributeLabels
        self.literalsSet = literalsSet
    def __repr__(self):
        return str(self.attributeLabels)

'''
param: attribute: the values of a variable attribute in dataTable
return: the partition of the values of a variable attribute
'''
def create_Attribute_Paritition(attrValues):
    tmpl = attrValues.to_dict()
    ini_dict = tmpl
    flipped = {}
    for key, value in ini_dict.items():
        if value not in flipped.keys():
            flipped[value] = [key]
        else:
            flipped[value].append(key)
    return flipped

'''
return: the set of all literals in dataTable, the number of attributes
'''
def generLiterals(readFile,attriNumberLimit):
    filename = readFile
    df = pd.read_csv(filename,delimiter=";;",engine='python')
    # constrain the number of attributes
    if attriNumberLimit!=-1:
        df = df.iloc[0:len(df.index),0:attriNumberLimit]

    literals = []
    temp1 = 0
    # execute literal situation a
    for colName  in df.columns:
        partiton = create_Attribute_Paritition(df[colName])
        #print(partiton)
        variable = colName.split(".")[0].split(":")[1].split(")")[0]
        attribute = colName.split(".")[1]
        entityType = colName.split(".")[0].split(":")[0].split("(")[1]
        if attribute!="id": 
            for value in partiton.keys():
                # value is not null
                if value==value and value!="N":
                    equalClass = tuple(partiton[value])
                    literals.append(Literal(temp1,variable,attribute,value,False,None,None,equalClass,entityType))
                    temp1 += 1
    # print(literals)
    # execute literal situation b&c
    # situationBdic: {1: {y0:[name,id,genre],y1:[id,name,genre,year]}}
    situationBdic = {}
    for colName in df.columns:
        variable = colName.split(".")[0].split(":")[1].split(")")[0]
        attribute = colName.split(".")[1]
        entityType = colName.split(".")[0].split(":")[0].split("(")[1]
        if entityType not in situationBdic.keys():
            situationBdic[entityType] = {}
        if variable in situationBdic[entityType].keys():
            situationBdic[entityType][variable].append(attribute)
        else:
            situationBdic[entityType][variable] = [attribute]
    situations = []
    for entityType in situationBdic.keys():
        for ent1Name, ent2Name in combinations(situationBdic[entityType].keys(),2):
            ent1Attris = situationBdic[entityType][ent1Name]
            ent2Attris = situationBdic[entityType][ent2Name]
            for attriName in ent1Attris:
                if attriName in ent2Attris:
                    literalB = ent1Name+"."+attriName+"="+ent2Name+"."+attriName
                    situations.append([entityType,literalB])
    #print(situations)
    for situation in situations:
        entityType = situation[0]
        vari1 = situation[1].split("=")[0].split(".")[0]
        attri1 = situation[1].split("=")[0].split(".")[1]
        vari2 = situation[1].split("=")[1].split(".")[0]
        attri2 = situation[1].split("=")[1].split(".")[1]
        se = pd.Series(df["("+entityType+":"+vari1+")"+"."+attri1]==df["("+entityType+":"+vari2+")"+"."+attri2])
        equalClass = tuple(se[se].index)
        literals.append(Literal(temp1,"None",attri1,None,True,(vari1,vari2),(attri1,attri2),equalClass,entityType))
        temp1 += 1
    # generate the attributeLabel for each literal
    attriLabelSet = set()
    for literal in literals:
        attriLabel = str(literal.entityType)+"."+literal.attribute
        attriLabelSet.add(attriLabel)
    attriLabelSet = list(attriLabelSet)
    attriLabelSet.sort()
    print(attriLabelSet)
    dicting1 = {}
    attributeLabel = 0
    for attriLabel in attriLabelSet:
        dicting1[attriLabel] = attributeLabel
        attributeLabel+=1
    for literal in literals:
        literal.attributeLabel = dicting1[str(literal.entityType)+"."+literal.attribute]
    return literals,len(attriLabelSet)

'''
output: the dependencies of one level
'''
def compute_dependencies_and_prune(levelSet,dependency_set,level0Set):
    reBlocks = []
    for block in levelSet:
        # each surplus attribute should be selected as the rhs
        lhsLabelSet = block.attributeLabels
        rhsLiteralSet = []
        for level0_block in level0Set:
            if not(level0_block.attributeLabels[0] in lhsLabelSet):
                for literals in level0_block.literalsSet:
                    rhsLiteralSet.append(literals[0])
        reLiteralsSet = []
        for literals in block.literalsSet:
            lhsSet = literals
            literals_reRank = 0
            for rhs in rhsLiteralSet:
                rhsMatches = rhs.equalClass
                lhsMatches = lhsSet[0].equalClass
                lhsValueSet = []
                rhsValue = rhs.getValue()
                for literal in lhsSet:
                    lhsMatches = tuple(set(lhsMatches).intersection(literal.equalClass))
                    lhsValueSet.append(literal.getValue())
                # if the intersection of the partitions is empty
                # judge whether the intersection is empty first
                if (len(set(lhsMatches).intersection(rhsMatches))==0):
                    literals_reRank += 1
                # if the lhs matches are the subset of rhs matches
                elif (set(lhsMatches).issubset(set(rhsMatches))):
                    isUseful = False
                    isRedundant = False
                    tmp = rhs.variable
                    for literal in lhsSet:
                        if tmp!=literal.variable or tmp=="None" or literal.variable=="None":
                            # more than one literal in dependency
                            isUseful = True
                            break
                    for dependency in dependency_set:
                        d_lhsValueSet = dependency.split("->")[0].split(";;")
                        d_rhsValue = dependency.split("->")[1]
                        if (set(d_lhsValueSet).issubset(set(lhsValueSet)) and d_rhsValue==rhsValue):
                            isRedundant = True
                            break
                    
                    if (isUseful and not(isRedundant)):
                        #dependency = "{"
                        dependency = ""
                        for i in range(len(lhsSet)):
                            if (i==len(lhsSet)-1):
                                #dependency += lhsSet[i].getValue()+"}"
                                dependency += lhsSet[i].getValue()
                            else:
                                dependency += lhsSet[i].getValue()+";;"        
                        dependency += "->"
                        dependency += rhs.getValue()
                        dependency_set.append(dependency)
                        print(dependency)
                        # fileout.write(dependency+"\n")
                    literals_reRank += 1
            if (literals_reRank==len(rhsLiteralSet)):
                reLiteralsSet.append(literals)
        for reliterals in reLiteralsSet:
            # prune
            block.literalsSet.remove(reliterals)
        if (len(block.literalsSet)==0):
            reBlocks.append(block)
    for reBlock in reBlocks:
        # prune
        levelSet.remove(reBlock)

'''
main method
'''
def mainMethod(readFile,dependency_set,information,attriNumberLimit):
    literals,attriNumber = generLiterals(readFile,attriNumberLimit)
    information.append("literalNumber "+str(len(literals))+" attriNumber "+str(attriNumber))
    # the initialization of lattice
    level = 0
    lattice = []
    level0Set = []
    L = []
    for i in range(attriNumber):
        L.append((i,))
    for attriLabels in L:
        # print(attriLabels[0])
        literalsSet = []
        for literal in literals:
            if literal.attributeLabel==attriLabels[0]:
                literalsSet.append([literal])
                # print(literal)
        level0Set.append(Block([attriLabels[0]],literalsSet))
    lattice.append(level0Set)
    compute_dependencies_and_prune(level0Set,dependency_set,level0Set)
    # lattice generation
    for i in range(1,attriNumber+1):
        levelSet = []
        print("level ",i)
        for block1Index, block2Index in combinations([j for j in range(len(lattice[i-1]))], 2):
            block1 = lattice[i-1][block1Index]
            block2 = lattice[i-1][block2Index]
            if (len(block1.literalsSet)!=0 and len(block1.literalsSet)!=0):
                literalsSet = []
                attributeLabels = set()
                for attriLabel in block1.attributeLabels:
                    attributeLabels.add(attriLabel)
                for attriLabel in block2.attributeLabels:
                    attributeLabels.add(attriLabel)
                attributeLabels = list(attributeLabels)
                attributeLabels.sort()
                for literals1 in block1.literalsSet:
                    literals1Id = []
                    length = len(literals1)
                    for j in range(0,length-1):
                        literals1Id.append(literals1[j].identity)
                    for literals2 in block2.literalsSet:
                        literals2Id = []
                        for j in range(0,length-1):
                            literals2Id.append(literals2[j].identity)
                        # only the set which the prefixs are same can be combined to generate a new set in the next level
                        if (operator.eq(literals1Id,literals2Id)):
                            literalSet = []
                            for j in range(0,length-1):
                                literalSet.append(literals1[j])
                            if literals1[length-1].attributeLabel < literals2[length-1].attributeLabel:
                                literalSet.append(literals1[length-1]);literalSet.append(literals2[length-1])
                            else:
                                literalSet.append(literals2[length-1]);literalSet.append(literals1[length-1])
                            literalsSet.append(literalSet)      
                if (len(literalsSet)>0):
                    levelSet.append(Block(attributeLabels,literalsSet))
        level += 1
        compute_dependencies_and_prune(levelSet,dependency_set,level0Set)
        lattice[i-1] = []
        lattice.append(levelSet)
    print("literals number",len(literals))
    print("attribute number",attriNumber)

def clean_redundant(dependency_set,fileout,information):
    res_dict = {}
    rel_dict = {}
    for dependency in dependency_set:
        s = dependency.split('->')
        s1 = s[0]
        # s1 = s1.replace('{', '')
        # s1 = s1.replace('}', '')
        s2 = s[-1]
        # s2 = s2.replace("\n", '')
        if s1 in rel_dict.keys():
            tem = rel_dict[s1]
            tem.append(s2)
            rel_dict[s1] = tem.copy()
            res_dict[s1] = tem.copy()
        else:
            lists = [s2]
            rel_dict[s1] = lists.copy()
            res_dict[s1] = lists.copy()
    
    vaildNumber = 0
    for item in rel_dict.items():
        key = item[0]
        value = item[1]
        sli = key.split(';;')
        validSet = value.copy()
        for single_value in value:
            if len(sli) == 2:
                # A,B->C, A,C->B
                for i in range(0, 2):
                    new_str1 = sli[i] + ';;' + single_value
                    new_str2 = single_value + ';;' + sli[i]
                    new_value1 = []
                    new_value2 = []
                    if new_str1 in res_dict.keys():
                        new_value1 = res_dict[new_str1]
                    if new_str2 in res_dict.keys():
                        new_value2 = res_dict[new_str2]
                    if sli[1 - i] in new_value1 or sli[i-1] in new_value2:
                        if single_value in validSet:
                            validSet.remove(single_value)
            # A->[B,C],B->[C]
            if single_value in rel_dict.keys():
                two_lev = res_dict[single_value]
                for three_lev in two_lev:
                    if three_lev in value:
                        if three_lev in validSet:
                            validSet.remove(three_lev)
            
        res_dict[key] = validSet.copy()
        for rhs in validSet:
            fileout.write("{"+key+'} -> '+rhs+"\n")
            vaildNumber += 1

    fileout.write("\n"+information[0]+"\n")
    fileout.write("before: dependency number "+str(len(dependency_set))+"\n")
    fileout.write("after: dependency number "+str(vaildNumber)+"\n")

if __name__=="__main__":
    pyMiningFile_path = sys.argv[1]
    tableId = sys.argv[2]
    start_time = time.time()
    filePath = pyMiningFile_path+"/result/dependency/dependency_result"+tableId+'.txt'
    fileout = open(filePath,'w',encoding='utf-8')
    readFile = pyMiningFile_path+"/test/process_3_producer/proTable_meaning/"+"produce_Table"+tableId+".txt"
    dependency_set = []
    information = []
    attriNumberLimit = int(sys.argv[3])
    mainMethod(readFile,dependency_set,information,attriNumberLimit)
    clean_redundant(dependency_set,fileout,information)
    fileout.close()
    end_time = time.time()
    print("start_time:", start_time)
    print("end_time:", end_time)
    print("time cost:", end_time - start_time, "s")