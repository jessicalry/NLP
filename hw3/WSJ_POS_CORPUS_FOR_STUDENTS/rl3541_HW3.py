from os import linesep, truncate
import sys


def OOV_suffix_handler(word):
    probability = {}
    try:
        # if token contains number
        if any(char.isdigit() for char in word):
            probability["CD"] = 1.0
    except IndexError:
        pass

    try:
        # er could be noun or adjective comparative, assume 30:70
        if word[-2:] == "er":
            probability["NN"], probability["JJR"] = 0.3, 0.7
    except IndexError:
        pass

    try:
        # typical nouns
        if word[-2:] in ["ar", "or"] or \
           word[-3:] in ["acy", "age", "ism", "ist", "ity", "ion"] or \
           word[-4:] in ["ance", "ence", "ment", "ness", "sion", "tion", "hood", "ship"]:
            probability["NN"] = 1.0
    except IndexError:
        pass

    try:
        # typical adverbs / adjectives
        # ly could be adjective or adverb, assume 50:50
        if word[-2:] == "ly":
            probability["RB"] = 0.5
            probability["JJ"] = 0.5
    except IndexError:
        pass

    try:
        if word[-2:] in ["al", "ic"] or \
                word[-3:] in ["ful", "ish", "ate"] or \
                word[-4:] in ["able", "ible", "like"]:
            probability["JJ"] = 1.0
    except IndexError:
        pass

    try:
        # typical verb
        if word[-2:] == "en" or \
                word[-3:] in ["ify", "ize", "ise"]:
            probability["VB"] = 1.0
    except IndexError:
        pass

    try:
        # ate could be adjective or verb, assume 50:50
        if word[-3:] == "ate":
            probability["VB"] = 0.5
            probability["JJ"] = 0.5
    except IndexError:
        pass

    try:
        # Adjectives, comparative
        if word[-3:] == "ier":
            probability["JJR"] = 1.0
    except IndexError:
        pass

    try:
        # Adjectives, superlative
        if word[-3:] == "est":
            probability["JJS"] = 1.0
    except IndexError:
        pass

    # try:
    #     # adjectives with -
    #     if "-" in word:
    #         probability["JJ"] = 1.0
    # except IndexError:
    #     pass


# 95.0202 accuracy for oov above with score.py 

    # try:
    #     # VBD, VBN
    #     if word[-2:] == "ed":
    #         probability["VBD"] = .8
    #         probability["VBN"] = .2
    # except IndexError:
    #     pass

#95.0052 accuracy

    # try:
    #     # NNP, NNPS
    #     if word[0].isupper():
    #         if word[-1:] == "s":
    #             probability["NNPS"] = .9
    #             probability["NNP"] = .1
    # except IndexError:
    #     pass

#95.0050 accurary
    # try:
    #     # Farmers explicitly
    #     if word == "Farmers":
    #         probability["NNPS"] = 1.0
    # except IndexError:
    #     pass

    # try:
    #     # Adjectives, superlative
    #     if word[1].isupper():
    #         probability["NNP"] = 1.0
    #         if word[-1:]:
    #             probability["NNPS"] = .9
    #             probability["NNP"] = .1
    # except IndexError:
    #     pass

    return probability


''' likelihood '''


def likelihood_processing(infileName_training, likelihoodFreq, likelihood, wordSet, tagOccurrence, OOV_handler, MAX_FREQUENCY_BOUND):
    # read in the development .pos file
    with open(infileName_training, 'r') as instream:
        # loop through each line
        for line in instream:
            # data cleaning by removing the linesep and separator
            line = line.strip(linesep).split('\t')
            # disregard meaningless line without data
            if len(line) < 2:
                continue
            # unpack the value
            word, pos = line

            # quick update of wordSet
            wordSet.add(word)

            # if pos in likelihood
            if pos in likelihoodFreq:
                # in its value, increment the count for the corresponding word by 1
                likelihoodFreq[pos][word] = likelihoodFreq[pos].get(
                    word, 0.0) + 1
            # if pos is not in likelihood
            else:
                # initialize its value to a new dictionary with count 1 for the corresponding word
                likelihoodFreq[pos] = {word: 1}

        # loop through the likelihoodFreq
        for pos, wordDict in likelihoodFreq.items():
            # initialize the key to be empty dict
            likelihood[pos] = {}
            # quick summation of count of all words
            total = sum(count for count in wordDict.values())

            # add the total to tagOccurrence
            tagOccurrence[pos] = total

            # loop through the wordDict for current pos
            for word, count in wordDict.items():
                # populate likelihood for the current pos for each word's possibility
                likelihood[pos][word] = count / total
                # if the occurrence is less than the higher bound of low frequency words
                if count <= MAX_FREQUENCY_BOUND:
                    # add the tag to OOV_handler which stores all low frequency words
                    OOV_handler[pos] = OOV_handler.get(pos, 0.0) + 1

    ''' OOV handling '''
    # simple as is: OOV pos has probability of low word tag occurrence over tag total occurrence
    OOV_handler = {pos: occur / tagOccurrence[pos]
                   for pos, occur in OOV_handler.items()}

    return


''' transition '''


def transition_processing(infileName_training, beginSent, endSent, transitionFreq, transition):
    # read in the development .pos file, again
    with open(infileName_training, 'r') as instream:
        # previous line's pos, initialize to beginSent as begin of sentence
        prevPos = beginSent
        # loop through each line
        for line in instream:
            # data cleaning by removing the linesep and separator
            line = line.strip(linesep).split('\t')
            # unpack data
            # if blank line
            if len(line) < 2:
                # then it is the end/begin of sentence
                word, pos = endSent, endSent
            # if not blank line
            else:
                # then it is a real word + its pos
                word, pos = line

            # if prevPos is endSent, then change it to beginSent for the next sentence
            if prevPos == endSent:
                prevPos = beginSent
            # if prevPos in transitionFreq
            if prevPos in transitionFreq:
                # in its value, increment the count for the corresponding word by 1
                transitionFreq[prevPos][pos] = transitionFreq[prevPos].get(
                    pos, 0.0) + 1
            # if prevPos is not in transitionFreq
            else:
                # initialize its value to a new dictionary with count 1 for the corresponding pos
                transitionFreq[prevPos] = {pos: 1}

            # update prevPos before proceding to next iteration
            prevPos = pos

        # loop through the transitionFreq
        for pos, posDict in transitionFreq.items():
            # initialize the key to be empty dict
            transition[pos] = {}
            # quick summation of count of all words
            total = sum(count for count in posDict.values())
            # loop through the posDict for current pos
            for word, count in posDict.items():
                # populate transition for the current pos for each pos' possibility
                transition[pos][word] = count / total

    return


''' Transducer '''


def transducer_processing(infileName_testing, beginSent, endSent, wordSet, likelihood, transition, OOV_handler):
    # read in the testing file
    with open(infileName_testing, 'r') as instream:
        # initialize two Python Dictionaries and an index variable for:
        # dictionary contains scores for every tag at each index,
        # dictionary contains best previous tag for every tag at each index, and
        # index tracking of index within sentence boundary,
        # note that index starts at 1 because 0 is beginSent
        transducer = {}
        backpointer = {}
        index = 1
        # oov = set()

        # loop through each line
        for line in instream:
            # remove linesep
            word = line.strip(linesep)

            # no path found handling:
            # fatal error when there is no path found because transition sample is too small in scale
            bestTag = ''
            maxLikelihood = 0.0
            bestPrevTag = ''
            maxPrevLikelihood = 0.0
            bigramNotFound = True

            # if word is not empty, i.e. not beginSent or endSent
            if word != '':
                # loop through likelihood
                for tag, wordDict in likelihood.items():
                    # initialize for the first token within sentence boundary
                    if index == 1:
                        # initialize transducer and backpointer sub-dictionary for current token/index
                        transducer[index] = transducer.get(index, {})
                        backpointer[index] = backpointer.get(index, {})

                        # OOV handling
                        if word not in wordSet:
                            # oov.add(word) #see the list of OOVs
                            if tag is not beginSent and tag is not endSent:
                                try:
                                    wordDict[word] = OOV_suffix_handler(
                                        word).get(tag, (OOV_handler[tag]))
                                    #wordDict[word] = OOV_handler[tag]
                                except KeyError:
                                    wordDict[word] = wordDict.get(word, 1/1000)

                        # update transducer and backpointer accordingly
                        transducer[index][tag] = transition[beginSent].get(
                            tag, 0.0) * wordDict.get(word, 0.0)
                        backpointer[index][tag] = beginSent

                    # iterative computation for rest of tokens within sentence boundary
                    else:
                        # initialize transducer and backpointer sub-dictionary for current token/index
                        transducer[index] = transducer.get(index, {})
                        backpointer[index] = backpointer.get(index, {})
                        prevTransducer = transducer[index - 1]
                        transducer[index][tag] = 0

                        # OOV handling
                        if word not in wordSet:
                            # oov.add(word) #see the list of OOVs
                            if tag is not beginSent and tag is not endSent:
                                try:
                                    wordDict[word] = OOV_suffix_handler(
                                        word).get(tag, (OOV_handler[tag]))
                                    #wordDict[word] = OOV_handler[tag]
                                except KeyError:
                                    wordDict[word] = wordDict.get(word, 1/1000)

                        # get likelihood for the current word/token
                        tempProb = wordDict.get(word, 0)
                        # preperation for bigramNotFound
                        # get best current tag and max current likelihood
                        if tempProb > maxLikelihood:
                            bestTag = tag
                            maxLikelihood = tempProb

                        # loop through previous transducer
                        for prevTag, prevProb in prevTransducer.items():

                            if prevProb != 0:
                                # preperation for bigramNotFound
                                # get best previous tag and max previous likelihood
                                if prevProb > maxPrevLikelihood:
                                    bestPrevTag = prevTag
                                    maxPrevLikelihood = prevProb

                                # computation
                                tempProb = wordDict.get(word, 0)
                                tempProb *= transition[prevTag].get(
                                    tag, 0.0) * prevTransducer[prevTag]
                                # find max viterbi probability and best tag
                                # update transducer and backpointer accordingly
                                if tempProb > transducer[index][tag]:
                                    transducer[index][tag] = tempProb
                                    backpointer[index][tag] = prevTag
                                    # if there is valid bi-gram path(pair actually), then mark bigramNotFound as False
                                    bigramNotFound = False

                # if really no path has been found, then as we have prepepared above...
                if bigramNotFound:
                    # manually write transducer as max current likelihood
                    transducer[index][bestTag] = maxLikelihood
                    # manually write backpointer as best previous tag
                    backpointer[index][bestTag] = bestPrevTag

                # increment index by 1 as we move forward by one token
                index += 1

            # if it is beginSent or endSent
            else:
                # initialize transducer and backpointer sub-dictionary for current token/index
                transducer[index] = transducer.get(index, {})
                backpointer[index] = backpointer.get(index, {})
                prevTransducer = transducer[index - 1]
                transducer[index][endSent] = 0

                # probability for beginSent and endSent is predetermined as 1.0
                tempProb = 1.0
                for prevTag, prevProb in prevTransducer.items():
                    if prevProb != 0.0:
                        # computation
                        tempProb *= transition[prevTag].get(
                            endSent, 0.0) * prevTransducer[prevTag]
                        # find max viterbi probability and best tag
                        # update transducer and backpointer accordingly
                        if tempProb > transducer[index][endSent]:
                            transducer[index][endSent] = tempProb
                            backpointer[index][endSent] = prevTag

                # initialize bestPath for storing the best tag path
                bestPath = [endSent]
                # initialize curTag to be the last tag -> endSent
                curTag = endSent
                # loop through backpointer reversely
                for n in range(index, 0, -1):
                    # get best current tag
                    curTag = backpointer[n][curTag]
                    # append best current tag to bestPath
                    bestPath.append(curTag)

                # reverse the path so it starts from beginSent
                bestPath.reverse()

                # prepare a list storing valid tags for final output
                for tag in bestPath:
                    # ignore beginSent
                    if tag == beginSent:
                        continue
                    # ignore endSent but for newline purpose, treat it as empty string
                    if tag == endSent:
                        tag = ''
                    # evil yield generating a Python Generator
                    yield tag + '\n'

                # reinitialize when reaching sentence boundary
                transducer = {}
                backpointer = {}
                index = 1

                #write the oov set
                # with open("oov","w") as outs:
                #     for w in oov:
                #         outs.write(w+"\n")
                # outs.close()

    return


def write_out(infileName_testing, outfileName, tagGenerator):
    # open the testing file and output file
    with open(infileName_testing, 'r') as instream, open(outfileName, 'w') as outstream:
        # loop through each line in testing file
        for line in instream:
            # add '\t' and the corresponding POS tag for the current line
            line = line.strip(linesep)
            if line != '':
                line = line + '\t' + next(tagGenerator)
            else:
                line = next(tagGenerator)
            # write out the line
            outstream.write(line)


''' main function '''


def main():
    # file names
    # if there is input file names from command line
    inputLength = len(sys.argv)
    if inputLength == 4:
        infileName_training = sys.argv[1]
        infileName_testing = sys.argv[2]
        outfileName = sys.argv[3]
    # if there is no input file name from command line, do default
    elif inputLength == 1:
        infileName_training = "WSJ_02-21.pos"
        infileName_testing = "WSJ_24.words"
        outfileName = "submission.pos"
    # if there is invalid input file name from command line, raise warning to user
    else:
        error = "Please enter no file name for default run, or if you would like, \n\
                    enter three file names in order of training_file testing_file output_file."
        raise SystemError(error)

    # initialize four Python Dictionaries for:
    # temp dictionary contains frequency,
    # real dictionary used later contains possibility,
    # temp dictionary contains frequency, and
    # real dictionary used later contains possibility
    likelihoodFreq = {}
    likelihood = {}
    transitionFreq = {}
    transition = {}

    # initialize Python Set storing all word defined (i.e. the Vocabulary)
    wordSet = set()

    # initialize two variables for "Begin_Sent" and "End_Sent" strings
    beginSent = "Begin_Sent"
    endSent = "End_Sent"

    # initialize two Python Dictionaries and a variable for OOV handling:
    # temp dictionary contains pairs of {tag: total occurrence}
    # real dictionary stores pairs of {tag: (tag occurrence in low frequency words / total occurrence)} that wil be used later
    # the variable for the higher bound for word to be classified as low frequency word and thus store in OOV_handler
    tagOccurrence = {}
    OOV_handler = {}
    MAX_FREQUENCY_BOUND = 1

    # #  Training Stage  # #
    likelihood_processing(infileName_training, likelihoodFreq, likelihood,
                          wordSet, tagOccurrence, OOV_handler, MAX_FREQUENCY_BOUND)
    transition_processing(infileName_training, beginSent,
                          endSent, transitionFreq, transition)
    # #  Testing Stage  # #
    tagGenerator = transducer_processing(
        infileName_testing, beginSent, endSent, wordSet, likelihood, transition, OOV_handler)
    # #  Write Stage  # #
    write_out(infileName_testing, outfileName, tagGenerator)

    return


''' actual running (when not being imported) '''
# always a good practice
if __name__ == "__main__":
    main()
