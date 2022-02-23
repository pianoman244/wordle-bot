"""
A simple class to represent a game of Wordle. Used for simulations.
"""
from definitions import NUM_LETTERS

from guess_info import Guess_Info

class Wordle_Game:
	def __init__(self, word: str): 
		self.word = word

	'''
	Test the given word against the actual word and return information.
	word: 5-letter word
	return: Guess_Info object
	'''
	def make_guess(self, word: str) -> Guess_Info:
		info = [-1]*NUM_LETTERS
		for i in range(NUM_LETTERS):
			if word[i] not in self.word:
				info[i] = 0
			elif word[i] in self.word and word[i] != self.word[i]:
				info[i] = 1
			elif word[i] == self.word[i]:
				info[i] = 2

		return Guess_Info(word, tuple(info))

	def correct_word(self, word: str) -> bool:
		return self.word == word