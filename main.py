from cookielib import CookieJar
import urllib2
import re
import collections
import math
import hunt

# to make sure twitter doesn't know we're a robot
# add 'human-like' headers. Using Mozilla browser
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

# twitter search link is globally declared to I can access across fxns
# instantiate comparison dictionary to store data
# instantiate hashtag dicts to compare subjects later
# common words array ignores 100 most common words in the english language
startingLink = 'https://twitter.com/search?f=realtime&q='

# temp = open('sourceCode', 'w')
compDict = {}
hash1 = []
hash2 = []
subLib1 = []
subLib2 = []
commonWords = []

GUI = hunt.GUI()

def main():
    global GUI

    loadCommonWords()

    GUI.launchGUI(dual_func)

def compare(subject1, subject2):

    subject1 = stringClean(subject1)
    subject2 = stringClean(subject2)

    compDict['freq1'] = tweetParser(subject1, 1)
    compDict['freq2'] = tweetParser(subject2, 2)

    tweetCollision()


# cut up the source code and get hash tags, tweet text and frequency
def tweetParser(subject1, which):# change this to just subject and subject number
    global compDict
    try:
        sourceCode = opener.open(startingLink+subject1+'&src=hash').read()
        sourceCode = re.sub(r'<span class="Icon Icon--small Icon--top"></span>.*?</p>', '', sourceCode)
        tweets = re.findall(r'<p class="js-tweet-text tweet-text" lang="en" data-aria-label-part="0">.*?</p>', sourceCode)
        findHashTags(sourceCode, which)
        frequency = re.findall(r'data-long-form="true" aria-hidden="true">(.*?)</span>', sourceCode)

        for item in tweets:
            if item in 'Top news story':
                continue
            cleanedTweet = re.sub(r'data-expanded-url=(.*?)<span class="tco-ellipsis"></span>', '', item)
            cleanedTweet = re.sub(r'<.*?>', '', cleanedTweet)

            if cleanedTweet.find("&#") != -1:
                cleanedTweet = re.sub(r'&#.*?;', '\'', cleanedTweet)
            storeTweet(cleanedTweet.lower(), which)
        return analyzeFrequency(frequency)

    except Exception, e:
        print str(e)
        print 'Damn'

# look at the time since the tweet, find the average
def analyzeFrequency(frequencyArray):
    sum = 0.0
    if len(frequencyArray) == 0:
        return 0
    for item in frequencyArray:
        time = re.findall(r'\d{0,3}', item)
        unit = re.findall(r'[a-z]', item)
        if unit[0] == 's':
            sum += (float(time[0])/60.0)
        if unit[0] == 'm':
            sum += float(time[0])
        if unit[0] == 'h':
            sum += float(time[0])*60
    avg = sum / (len(frequencyArray))
    return avg


# get hashtags for each subject
def findHashTags(tweets, which):
    tags = re.findall(r'<a href="/hashtag/(.*?)\?src=hash', tweets)
    if which is 1:
        global hash1
        for item in tags:
            hash1.append(item)
    if which is 2:
        global hash2
        for item in tags:
            hash2.append(item)

# twitter has a protocol for search strings with whitespace
def stringClean(query):
    newString = ''

    if ' ' in query:
        cut = query.split()
        for item in cut:
            newString += '%20' + item
        return newString
    else:
        return query

# get turn the tweets into words, cross reference words with CommonWords dictionary
def storeTweet(tweet, which):
    words = re.findall(r'\b[a-z]+\b', tweet) # get the words from the tweet
    temp = set(commonWords)

    if which is 1:
        global subLib1
        subLib1 += [item for item in words if item not in temp]
    if which is 2:
        global subLib2
        subLib2 += [item for item in words if item not in temp]


# load the common word dictionary
def loadCommonWords():
    global commonWords
    wordFile = open('CommonWords.txt', 'r')
    for line in wordFile:
        commonWords.append(line.strip())
    wordFile.close()

# look for word collisions and for hash tag collisions
def tweetCollision():
    counter1 = collections.Counter(subLib1)
    counter2 = collections.Counter(subLib2)
# change lists to set, more efficient and easier to check for collisions
    terms = set(counter1).union(counter2)
    dotprod = sum(counter1.get(k, 0) * counter2.get(k, 0) for k in terms)
    magA = math.sqrt(sum(float(counter1.get(k, 0))**2 for k in terms))
    magB = math.sqrt(sum(float(counter2.get(k, 0))**2 for k in terms))
    compDict['similarity Index'] = dotprod / (magA * magB)

# combine both tweet dictionaries together, adding values between keys
# look for intersection between groups and get max 3 collisions
    maxCollision = counter1 + counter2
    intersection = set(counter1.keys()) & set(counter2.keys())
    i = 1
    compDict['number of common words'] = len(intersection)
    compDict['number of words'] = len(list(maxCollision))
    while intersection and i < 4:
        max = getMaxWords(maxCollision, intersection)
        compDict['common word '+str(i)] = max
        if len(intersection) > 0:
            intersection.remove(max)
        i += 1
    checkHashTags()


# get the next max word from array of common words
def getMaxWords(allColl, intersection):
    max = 0
    maxWord = ''
    for item in intersection:
        temp = allColl[item]
        if temp > max:
            max = temp
            maxWord = item
    return maxWord

def checkHashTags():
    counter1 = collections.Counter(hash1)
    counter2 = collections.Counter(hash2)
    intersection = set(counter1.keys()) & set(counter2.keys())
    compDict['hashTags'] = len(list(intersection))
    allTags = counter1 + counter2
    i = 1
    while intersection and i < 4:
        max = getMaxWords(allTags, intersection)
        print max
        compDict['hash tag '+str(i)] = max
        if len(intersection) > 0:
            intersection.remove(max)
        i += 1


def publishResults():
    global GUI
    percentSimilar = crunchNumbs()
    final = []

    final.append('____________________________________________\n')
    final.append("Similarity index between provided subjects:")
    final.append('          '+ str(percentSimilar)+'%\n\n')
    final.append("Number of common hash tags: "+str(compDict['hashTags']))
    if 'hash tag 1' in compDict:
        final.append("Most common hash tag: "+ str(compDict['hash tag 1']))
        if 'hash tag 2' in compDict:
            final.append("2nd most common hash tag: "+str(compDict['hash tag 2']))
            if 'hash tag 3' in compDict:
                final.append("3rd most common hash tag: "+str(compDict['hash tag 3']))
    final.append("Number of non trivial common words: "+str(compDict['number of common words']))
    final.append("Total number of non trivial words: "+str(compDict['number of words']))
    if 'common word 1' in compDict:
        final.append("Most common word: "+ str(compDict['common word 1']))
        if 'common word 2' in compDict:
            final.append("2nd most common word: "+str(compDict['common word 2']))
            if 'common word 3' in compDict:
                final.append("3rd most common word: "+str(compDict['common word 3']))
    final.append('____________________________________________')
    GUI.results(final)


# frequency= 10%, simIndex= 35%, hash tags= 40%, 10% buffer
def crunchNumbs():
    x=1
    totFreq = abs(compDict['freq2'] + compDict['freq1'])
    freqWeight = abs(compDict['freq2'] - compDict['freq1']) / totFreq
    freqWeight = 10 - freqWeight*10

    commWord = (compDict['number of common words'] / compDict['number of words']) * 5
    simIndex = 0
    while x == 1:
        if compDict['similarity Index'] > .85 :
            simIndex = 30
            x = 0
            continue
        if compDict['similarity Index'] > .65 :
            simIndex = 28
            x = 0
            continue
        if compDict['similarity Index'] > .50 :
            simIndex = 26
            x = 0
            continue
        if compDict['similarity Index'] > .30 :
            simIndex = 24
            x = 0
            continue
        if compDict['similarity Index'] > .1 :
            simIndex = 22
            x = 0
            continue
        if compDict['similarity Index'] > .0750 :
            simIndex = 17
            x = 0
            continue
        if compDict['similarity Index'] > .050 :
            simIndex = 13
            x = 0
            continue
        if compDict['similarity Index']>.025 :
            simIndex = 5
            x = 0
            continue
        if compDict['similarity Index']>.010 :
            simIndex = 3
            x = 0
            continue
        x=0
    simIndex += commWord
    tags = 0
    while x == 0:
        if compDict['hashTags']> 4 :
            tags = 40
            x = 1
        if compDict['hashTags'] == 3 :
            tags = 35
            x = 1
        if compDict['hashTags'] == 2 :
            tags = 28
            x = 1
        if compDict['hashTags'] == 1 :
            tags = 20
            x = 1
        x = 1
    return simIndex+10+tags+freqWeight

def dual_func(str1, str2):
    compare(str1, str2)
    publishResults()

main()
