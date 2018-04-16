import os
import re
import time
from nltk.parse import stanford
import nltk.data

########################1.读取动宾#################################
vo = [[]]

with open('top10.txt', 'r') as reader:
    for line in reader.readlines():
        vo.append(line.split())

################2.Python内调用Stanford parser###########
# 添加stanford环境变量,此处需要手动修改，jar包地址为绝对地址。
os.environ['STANFORD_PARSER'] = '/Users/wooden/Documents/jars/stanford-parser.jar'
os.environ['STANFORD_MODELS'] = '/Users/wooden/Documents/jars/stanford-parser-3.9.1-models.jar'

# 为JAVAHOME添加环境变量
java_path = "/Library/Java/JavaVirtualMachines/jdk1.8.0_161.jdk/Contents/Home/bin/java"
os.environ['JAVAHOME'] = java_path

# 句法标注
parser = stanford.StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

####################3.把wiki text划分为句子##########################
with open('/Volumes/Files/KnowledgeGraph/wiki_00.txt', 'r',encoding='UTF-8') as reader:
#with open(r'\\10.141.208.24\data\liujingping\wooden\output.txt', 'r',encoding='UTF-8') as reader:
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    line = reader.readline()
    j = 0
    cnt = 0
    dobj = 'dobj'
    nsubj = 'nsubj'
    while line:
        if cnt>300 :
            break
        j = j + 1
        print("processing text %d"%j)
        #print(line)
        json = eval(line)

        paragraphs = json['text']
        paragraphs = paragraphs.split('\n')  # 按段进行划分
        #i = 1
        #numpara = len(paragraphs)
        for paragraph in paragraphs:
            #print("processing text %d, paragraph %d"%(j,i))
            #i = i+1
            sentences = tokenizer.tokenize(paragraph)  # 按句子划分
            for sentence in sentences:
                if len(sentence)<80 and len(sentence)>10:  # 筛选长度在10到30之间的句子
                    for aPair in vo: #  a pair of verb and objects
                        tag = False   # tag : add a subjct: True   in this epoch not add a subject: false
                        if len(aPair) == 2:
                            verb, obj = aPair
                            if verb in sentence and obj in sentence:  #select the sentence with the two words
                                out = open('/Users/wooden/Documents/tmp_sentence.txt', 'w')
                                out.write(sentence)
                                out.close()
                                # RUN parser
                                os.system("cd /Users/wooden/Documents/stanford-parser-full-2018-02-27 && ./lexparser.sh /Users/wooden/Documents/tmp_sentence.txt > /Users/wooden/Documents/tmp_parserOutput.txt")
                                time.sleep(1)
                                # 可能会出现没有完全写入的情况，需要重新
                                while (not os.access("/Users/wooden/Documents/tmp_parserOutput.txt", os.R_OK)):
                                    time.sleep(1)
                                parserOutput = open("/Users/wooden/Documents/tmp_parserOutput.txt", 'r').read()
                                if not parserOutput: # 有时会有parser没有正常运行导致没有输出的现象出现
                                    continue
                                lines = parserOutput.split("\n\n")[1].split('\n')
                                sub = []
                                for line in lines:
                                    if verb in line: #包含这个动词（作为指向的节点）
                                        if nsubj in line:
                                            sub = re.findall('\ [^\s\-]*-',line)[0].strip().strip('-')  # 保存主语变量
                                        if dobj in line and sub and obj==re.findall('\ [^\s\-]*-',line)[0].strip().strip('-'):   # 是dobj成分，且正则匹配抽取的宾语和目标宾语一样。
                                           # 写入
                                            svoOut = open('/Users/wooden/Documents/svoOut.txt', 'a')
                                            svoOut.write("%s\t%s\t%s"%(sub, verb, obj))
                                            svoOut.close()
                                           # 更改状态：已经从该句中抽取了一个主语，不再考虑其他句子
                                            tag = True
                                            cnt = cnt + 1
                                            break
                                if tag:
                                    break
        line = reader.readline()