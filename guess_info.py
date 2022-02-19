''' 
Simple object to store a guess and the information contained in it.
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