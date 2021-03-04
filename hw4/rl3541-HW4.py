import ssl
import math
import nltk
import stop_list
import string
import time
#download nltk packages
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer



# import time
# start_time = time.time()


def main():
    #stemming
    ps = PorterStemmer()

    #some global variables
    TFIDF_dict_q = {}
    TFIDF_dict_a = {}
    all_q = {}
    all_ab = {}


    #instream query 
    with open("cran.qry", "r") as instream_query:
        #change all IDs from 1-365 to 1-225
        ID_list = []
        i=0

        query = []

        TF = 0
        TF_dict = {}

        IDF = 0
        IDF_dict = {}

        TFIDF = 0

        flag = True

        for line in instream_query:
            word = word_tokenize(line)

            if word[0] == ".I": #if we get a line starting with I
                i+=1 #increment the ID convertor from 365 to 225
                flag = False
                if i!=0:
                    all_q[i] = query #append the query into all-query list for query with ID i
                
                #start a new query
                query=[]
                #collect ID
                # i = word[1]
                ID_list.append(i)

            elif word[0] == ".W": #if the line starts with W, start recording the query
                flag = True
                continue

            else:
                if flag == True:
                    query+=word #recording the query
                query = [ps.stem(word) for word in query if word not in stop_list.closed_class_stop_words and\
                     word not in string.punctuation and not word.isdigit()] #handling stopwords

            all_q[i] = query #add the last query into query list
        # print(all_q)

        #to calculate the tf score
        cc = 0
        for Id in all_q:
            if Id!=0:
                TF_list = []
                for p,term in enumerate(all_q[Id]):
                    cc=1
                    for rest_terms in all_q[Id][p+1:]:
                        if term == rest_terms:
                            cc+=1
                            #print(cc)
                    # TF_list.append(math.log(cc/len(all_q[Id])))
                    if cc!=0:
                        TF_list.append(1)
                    else:
                        TF_list.append(0)
                TF_dict[Id] = TF_list
        # print(TF_dict)
                
        #to calculate the idf score: log(doc_nums/doc_num_containing_term)
        doc_nums = len(all_q)
        doc_dict = {}
        doc_containing = 0
        for ID in ID_list:
            word_index = 0
            IDF_list = []
            j = ID+1
            for word in all_q[ID]:
                doc_containing=1
                for ID2 in ID_list[j:]:
                    if word in all_q[ID2]:
                        doc_containing+=1 #get the number of docs containing word
                    j+=1
                real_num = doc_nums/doc_containing
                IDF = math.log(doc_nums/doc_containing)
                IDF_list.append(IDF)
            IDF_dict[ID] = IDF_list

        #to calculate the TFIDF score: tf * idf
        for ID in ID_list:
            TFIDF_list = []
            for i in range(len(TF_dict[ID])):
                TFIDF = TF_dict[ID][i] * IDF_dict[ID][i]
                TFIDF_list.append(TFIDF)
                TFIDF_dict_q[ID] = TFIDF_list

        # print(TFIDF_dict_q)



    #instream abstract
    with open("cran.all.1400", "r") as instream_abstract:
        ID_a = 0
        ID_list = []

        abstract = []
        all_ab = {}

        TF = 0
        TF_dict = {}

        IDF = 0
        IDF_dict = {}

        TFIDF = 0

        flag = True

        for line in instream_abstract:
            word = word_tokenize(line)

            if word[0] == ".I":
                flag = False
                if ID_a!=0:
                    all_ab[ID_a] = abstract
                
                #start a new abstract
                abstract=[]
                #collect ID
                ID_a = int(word[1])
                ID_list.append(ID_a)

            elif word[0] == ".T" or word[0] == ".A" or word[0] == ".B":
                continue
            
            elif word[0] == ".W":
                flag = True
                continue

            else:
                if flag == True:
                    abstract+=word
                abstract = [ps.stem(word) for word in abstract if word not in stop_list.closed_class_stop_words and\
                     word not in string.punctuation and not word.isdigit()]#handling stopwords

            all_ab[ID_a] = abstract #add the last abstract into abstract list
            #ID_list.append(ID_a) #collect the last ID

        #to calculate the tf score
        cc = 0
        for Id in all_ab:
            if Id!=0:
                TF_list = []
                for p,term in enumerate(all_ab[Id]):
                    cc=1
                    for rest_terms in all_ab[Id][p+1:]:
                        if term == rest_terms:
                            cc+=1
                            #print(cc)
                    # TF_list.append(math.log(cc/len(all_ab[Id])))
                    if cc!=0:
                        TF_list.append(1)
                    else:
                        TF_list.append(0)
                TF_dict[Id] = TF_list
                
        #to calculate the idf score: log(doc_nums/doc_num_containing_term)
        doc_nums = len(all_ab)
        doc_dict = {}
        doc_containing = 0
        j = 0
        for ID in ID_list:
            j = ID+1
            word_index = 0
            IDF_list = []
            for word in all_ab[ID]:
                doc_containing=1
                for ID2 in ID_list[j:]:
                    if word in all_ab[ID2]:
                        doc_containing+=1 #get the number of docs containing word
                    j+=1
                real_num = doc_nums/doc_containing
                IDF = math.log(doc_nums/doc_containing)
                IDF_list.append(IDF)
            IDF_dict[ID] = IDF_list
        #print(IDF_dict)

        #print(TF_dict)
        #print(IDF_dict)
        #get TFIDF scores
        for ID in ID_list:
            TFIDF_list = []
            for i in range(len(TF_dict[ID])):
                TFIDF = TF_dict[ID][i] * IDF_dict[ID][i]
                TFIDF_list.append(TFIDF)
                TFIDF_dict_a[ID] = TFIDF_list
        # print(TFIDF_dict_a)


    start_time = time.time() #for my own purpose to record running time

    #get a new query to compute the cosine similarity
    outwrite = open("output.txt","w") 
    i=0
    score = 0
    # out = [[0 for i in range(3)]for j in range(len(all_ab))]
    # out = [[0]*3]*len(all_ab) #init an out list composed of query idx, abstract idx, and cosine score
    for q,query in all_q.items(): #loop thru all queries
        # print(query)
        out = [[0 for i in range(3)]for j in range(len(all_ab))]
        # print(out)

        for a,abst in all_ab.items(): #loop thru all abstracts
            a_idx = int(a)-1 #index of each word in abstract
            # print(a_idx)
            new_vec = [0]*len(query) #init a new vector for each query to store the scores for each abstract
            idx_list = [word for word in query if word in abst] #find a list of words in both query and abstract
            # print(idx_list)

            #if there isn't any matching word in abstract, move on to next abstract?
            # if len(idx_list) == 0:
            #     continue

            for w in idx_list: #find the idx in the abstract and in query for each word in idx_list 
                idx_ab = abst.index(w) 
                idx_q = query.index(w)
                new_vec[idx_q] = TFIDF_dict_a[a][idx_ab] #get the TFIDF score according to the idx in the abstract
            # print(new_vec)

            score = cos_sim(TFIDF_dict_q[q], new_vec) #calculate the score for this particular abstract 
            # print(score)
            out[a_idx][0] = q
            out[a_idx][1] = a
            out[a_idx][2] = score

        #sort for each query 
        sorted_out = sorted(out,key=lambda l:l[2],reverse=True)
        # print(sorted_out)

        #outwrite for each query
        for line in sorted_out:
            for idx in line:
                outwrite.write(str(idx))
                outwrite.write(" ")
            outwrite.write('\n')

        i+=1 #go to the next query
    # print("--- %s seconds ---" % (time.time() - start_time))
    # print(TFIDF_dict_q)
    # print(query_idconvertor)

    #For each query, create a feature vector representing the words in the query. completed
    #Each word should be represented by a TFIDF score,  completed
    #Same for the abstract collections completed
    #Use cosine similarity to determine the order of abstracts bugs exist
    #Output format: query id, abstract id, cosine score



def cos_sim(l1,l2):
    numerator = sum([a * b for a, b in zip(l1,l2)])
    sumA = 0
    sumB = 0
    for num in l1:
        sumA+=num**2
    for numm in l2:
        sumB+=numm**2
    denom = math.sqrt(sumA*sumB)
    if denom == 0:
        return 0
    #print(numerator/denom)
    return numerator/denom
    

main()