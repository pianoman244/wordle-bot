import itertools
from enum import Enum
import math

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
	for comb in itertools.combinations_with_replacement([0, 1, 2], 5):
		for perm in perm_unique(comb):
			yield perm

class Letter_Info(Enum):
	UNKNOWN = 0
	NO = 1
	YES = 2

class Wordle_Information:
	def __init__(self):
		# data stored as:
		# [ {'A': Letter_Info, 'B': Letter_Info, ... 'Z': Letter Info},
		#	{'A', Letter_Info ... },
		# 	{ ... },
		#	{ ... },
		#	{ ... },
		#
		#	{'A': Letter_Info, 'B': Letter_Info, ... 'Z': Letter_Info}
		# ]
		# data[0:4]: dictionaries storing given info about whether or not a letter is at that location
		# data[5]: dictionary storing booleans about whether or not a letter is contained in the word
		#          IMPORTANT: this will go from "YES" to "UNKNOWN" if the location of a letter is verified
		# 		   e.g. if you get a yellow S and find its location on the next guess, this will go to "UNKNOWN"
		#          if you get another yellow S in another location afterwards, this will go to "YES". gray goes to "NO
		#          this is to store information about duplicate letters if necessary
		self.data = []
		for i in range(6):
			self.data.append( {} )

			# initialize all data to unknown
			for ch in "abcdefghijklmnopqrstuvwxyz":
				self.data[i][ch] = Letter_Info.UNKNOWN
		
		
		with open("words.txt") as f:
			self.word_list = f.readlines()

	'''
	Determine if word is possible based on information contained in self.
	word: 5-letter word
	return: boolean
	'''
	def possible_word_helper(self, word):
		for i in range(5):
			ch = word[i]
			# check if current info about each letter conflicts with any letters in word
			if self.data[i][ch] == Letter_Info.NO:
				return False

			# check that all placed letters are in the word
			for letter in "abcdefghijklmnopqrstuvwxyz":
				if self.data[i][letter] == Letter_Info.YES and ch != letter:
					return False
			
		# check if all unplaced letters exist in the word
		for ch in "abcdefghijklmnopqrstuvwxyz":
			if self.data[5][ch] == Letter_Info.YES and ch not in word:
				return False


		# if no conflict, word is possible
		return True
	
	'''
	Determine if word is possible based on information in self combined with guess_info
	word: 5-letter word
	guess_info: Guess_Info object
	return: boolean
	'''
	def possible_word(self, word, guess_info=None):
		if guess_info:
			return self.possible_word_helper(word) and guess_info.possible_word(word)
		else:
			return self.possible_word_helper(word)

	'''
	Generate a list of all possible words based on information contained in self. 
	Store result in self.word_list.
	return: None
	'''
	def update_possible_words(self):
		possible_words = []

		for word in self.word_list:
			if self.possible_word(word):
				possible_words.append(word)

		self.word_list = possible_words

	'''
	Add the information given from guess_info to self.
	guess_info: Guess_Info object
	return: None
	'''
	def add_info(self, guess_info):
		# see else info[i] == 2 for info about this
		unknown_this_guess = {}
		for ch in "abcdefghijklmnopqrstuvwxyz":
			unknown_this_guess[ch] = False

		for i in range(5):
			ch = guess_info.word[i] # character currently checking
			info = guess_info.info[i] # info about character

			# letter is not at this location or anywhere in the word
			if info == 0:
				for j in range(6):
					self.data[j][ch] = Letter_Info.NO

			# letter is in the word but not at this location
			elif info == 1:
				self.data[5][ch] = Letter_Info.YES # letter is in the word
				self.data[i][ch] = Letter_Info.NO # not at this location
				unknown_this_guess[ch] = True

			# letter is in the word at this location
			elif info == 2:
				# if this letter was previously found as unknown earlier in the word on this guess,
				# this should stay marked as unknown (see comment in Wordle_Information.__init__)
				if not unknown_this_guess[ch]:
					self.data[i][ch] = Letter_Info.YES 
		
		self.update_possible_words()
	'''
	Generate total possible words after combining information in self with guess and related info.
	guess_info: Guess_Info object
	return: list of 5-letter words
	'''
	def possible_words(self, guess_info):
		words = []
		for word in self.word_list:
			if self.possible_word(word, guess_info):
				words.append(word)
		
		return words
	
	'''
	Count the total number of words possible after combining self with guess_info.
	guess_info: Guess_Info object
	return: int
	'''
	def count_possible_words(self, guess_info):
		words = 0
		
		for word in self.word_list:
			if self.possible_word(word, guess_info):
				words += 1

		return words
	
	'''
	Get total information given by making guess with info as the result from that guess.
	Total information is calculated by (# remaining possible words)/(# original possible words)
	If no words are possible with the information given by this guess, returns None.
	guess_info: Guess_Info object
	return: float or None
	'''
	def get_info(self, guess_info):
		if self.count_possible_words(guess_info) == 0:
			return None
		else:
			p = len(self.word_list)/self.count_possible_words(guess_info)
			return p

''' 
Container object for a guess and the information given by it.
'''
class Guess_Info:
	def __init__(self, word, info):
		self.word = word # word in the guess
		self.info = info # info given by it (5-integer tuple with 0, 1, or 2)

	
	'''
	Determine if word is possible based on information in guess_info alone
	word: 5-letter word
	guess_info: Guess_Info object
	return: boolean
	'''
	def possible_word(self, word):
		for i in range(5):
			word_ch = word[i]
			guess_ch = self.word[i]
			ch_info = self.info[i]
			
			# guessed character is not in word
			if ch_info == 0:
				if guess_ch in word:
					return False
			# guessed character is in word not at this location
			elif ch_info == 1:
				if guess_ch == word_ch or guess_ch not in word:
					return False
			# guessed character is correct at this location
			elif ch_info == 2:
				if guess_ch != word_ch:
					return False

		return True

class Wordle_Game:
	def __init__(self, word): 
		self.word = word

	'''
	Test the given word against the actual word and return information.
	word: 5-letter word
	return: Guess_Info object
	'''
	def make_guess(self, word):
		info = [-1]*5
		for i in range(5):
			if word[i] not in self.word:
				info[i] = 0
			elif word[i] in self.word and word[i] != self.word[i]:
				info[i] = 1
			elif word[i] == self.word[i]:
				info[i] = 2

		return Guess_Info(word, tuple(info))

	def correct_word(self, word):
		return self.word == word

'''
Get the best guess based on given info.
info: Wordle_Information object
return: 5-letter word
'''
def best_guess(info, configs):
	curr_best = None
	max_info = 0
	for word in info.word_list[:5]:
		total_info = 0
		good_configs = 0
		for config in configs:
			guess = Guess_Info(word, config)
			p = info.get_info(guess)
			if p != None:
				total_info += p*math.log(1/p, 2)
				good_configs += 1

		if total_info > max_info:
			curr_best = guess
	
	return guess.word


def play_wordle():
	info = Wordle_Information()
	configs = list(result_configs())

	guess1 = Guess_Info("arise", [0, 0, 0, 0, 2])
	guess2 = Guess_Info("touch", [0, 2, 0, 0, 0])
	guess3 = Guess_Info("bowel", [0, 2, 0, 1, 0])


	info.add_info(guess1)
	info.add_info(guess2)
	info.add_info(guess3)

	print(info.word_list)

	'''
	word = best_guess(info)
	guesses = 0
	while (!game.correct_word(word)):
		word = best_guess(info)
		guess_info = make_guess(word)
		info.add_info(guess_info)
		guesses += 1
	
	print("Total guesses needed: ", guesses)
	'''

play_wordle()
