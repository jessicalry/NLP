def main(f1, f2):
    f1_data = {}
    count=0
    with open(f1,"r") as f1:
        for line in f1:
            word = line.strip("\n").split("\t")
            if len(word)!=1:
                w = word[0]
                pos = word[1]
                f1_data[w] = pos

    with open(f2,"r") as f2:
        for line in f2:
            count+=1
            word = line.strip("\n").split("\t")
            if len(word)!=1:
                if f1_data[word[0]]!=word[1]:
                    print("error in line "+str(count))
                    print("word: "+word[0])
                    print("24: "+f1_data[word[0]])
                    print("submission: "+word[1])
    return

if __name__ == "__main__":
    main("WSJ_24.pos","submission.pos")