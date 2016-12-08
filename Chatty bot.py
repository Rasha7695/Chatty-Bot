#!/bin/python
import sys
import re
import operator
import random
import signal
#======================initialization=====================
#check if we have the right number of arguments
if len(sys.argv)<=1:
	print "Error Wrong number of arguments"
	exit(-1)

#build a bad characters table to use in the clean method
bad_characters=[]
for c in range(0,255):
	if not (((c>=ord('a') and c<=ord('z')) or (c>=ord('A') and c<=ord('Z')) or c==ord('-') or c==ord('.')) or c==ord('?') or c==ord('!')):
		bad_characters.append(chr(c))
#handle ctrl-c gracefully
def signal_handler(signal, frame):
        print('\nYou pressed Ctrl+C, terminating!')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
#========================================================

#A method to clean strings from bad characters
def clean(s,bads):
	for c in bads:
		s=s.replace(c,"")
	return s

#dictionary to hold the parsed data
#structure of the data is {key=word1,value={word2,freq}}
data={}
#a list to hold sentences parsed in each text
sentences=[]
#dicionary to store the stop pairs
#structure of end pairs is key=(word1,word2)
end_pairs=[]
def parse(path):
	#open the file
	try:
		f=open(path,"r")
	except IOError:
		print "Error cannot locate one of the input file(s)"
		exit(-1)
	#clear the variables
	sentence=[]
	sentences=[]
	#scan every line in the file
	for line in f:
		# split on space
		for word in line.split():
			# convert to lower and remove punctuation or bad characters
			p=clean(word.lower(),bad_characters)
			# split on hyphens
			for w in p.split('-'):
				#avoid empty strings
				if(w==""):
					continue
				#we got a stoping word, we should flush the pairs and end the sentence
				#add the word the the collected data then do the flushing
				if(w[-1]=='.' or w[-1]=='?' or w[-1]=='!'):
					#remove the ending characters
					w=clean(w,['.','?','!'])
					#add the word to the sentence
					sentence.append(w)
					#flush the sentence into the data
					addData(sentence)
					#memorize this sentence
					sentences.append(sentence)
					sentence=[]
				#we only need to add the word to the sentence here
				else:
					sentence.append(w)
	#connect the words in the end of sentences
	for i in range(len(sentences)-1):
		#get the last word in the first sentence
		l=sentences[i][-1]
		#get the first word in the last sentence
		f=sentences[i+1][0]
		#connect them
		if data.has_key(l):
			if data[l].has_key(f):
				data[l][f]+=1
			else:
				data[l][f]=1
		else:
			data[l]={f:1}

				


def addData(words):
	#no valid words in the file
	if(len(words)==0):
		exit(-1)
	#build pairs from any two consecutive words
	for i in range(len(words)-1):
		k1=words[i]
		k2=words[i+1]
		#put the key-value pair in the dictionary
		if data.has_key(k1):
			if data[k1].has_key(k2):
				data[k1][k2]+=1
			else:
				data[k1][k2]=1
		else:
			data[k1]={k2:1}
		#if we are accessing the last pair in the data
		#then we have an end pair
		if i==len(words)-2:
			end_pairs.append(tuple([words[i],words[i+1]]))
		

#randomly generate a word that follows "w", this depends on the frequency
#of the word pairs in the data gathered from the files
def generate(w):
	#a variable to hold the possible values
	list_of_possible_words=[]
	#if we don't have words that might follow w
	#we just return None
	if not data.has_key(w):
		return None

	#otherwise we get all possible word repeated by their frequency
	#which is more fun and it make the word generation non-deterministic
	for d in data[w].items():
		#add d[1] possibilty of d[0]
		for _ in range(d[1]):
			list_of_possible_words.append(d[0])

	#no possible words, return None
	if len(list_of_possible_words)==0:
		return None
	#return a random word from the list
	else:
		return random.sample(list_of_possible_words,1)[0]
		#return list_of_possible_words[0]
	
def main():
	#parse all the input files
	cf=1
	while cf<len(sys.argv):
		parse(sys.argv[cf])
		cf+=1
	print end_pairs
	#start the chat loop
	while(1):
		#display the send prompt for the user
		print "Send: ",
		last_word=raw_input()
		if(last_word==""):
			print "please enter a non empty sentence!"
			continue
		last_word=clean(last_word.split()[-1].lower(),bad_characters+['.','?','!'])
		
	
		#try to generate a sentece until we hit a stop pair
		print "Receive:",
		#counter to count the number of times we have generated a word
		cnt=0
		#the resulting sentence
		res=[]
		#boolean flag so we dont stop at first iteration
		first=1
		#while we still can generate more words
		while(cnt<=20):
			#generate a new word
			next_word=generate(last_word)
			#if such word don't exist, break
			if(next_word==None):
				#start with a random word
				if(cnt!=0):
					break
				else:
					next_word=random.sample(data.keys(),1)[0]
			#if it's the first word, capitalize the first letter
			if(cnt==0):
				if  len(next_word)>1:
					res.append(next_word[0].upper()+next_word[1:])
				else:
					res.append(next_word[0].upper())
			else:
				res.append(next_word)
			#if we got a stoping pair, Halt !
			if first==0 and tuple([last_word,next_word]) in end_pairs:
				break
			last_word=next_word
			cnt+=1
			first=0
		#end the sentence with a dot
		print " ".join(res)+"."
		

main()		
