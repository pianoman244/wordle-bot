"""
All the code that actually plays Wordle is in here.
"""


import itertools
from enum import Enum
import math
import random
from typing import List
from tqdm import tqdm, tqdm_notebook

# wordle helper objects
from wordle_configs import result_configs
from wordle_information import Wordle_Information
from guess_info import Guess_Info
from wordle_game import Wordle_Game

'''
Select num random words from word_list. Words with repeated letters are removed from the return list
because of a bug that happens when I try to guess words with repeated letters.
'''
def select_words(word_list: List[str], num: int) -> List[str]:
    random.shuffle(word_list)
    sublist = []
    for word in word_list[:num]:
        repeat = False
        for letter in word:
            if word.count(letter) != 1:
                repeat = True
        
        if not repeat:
            sublist.append(word)
    return sublist

'''
Get the best guess based on given info.
info: Wordle_Information object
return: 5-letter word
'''
def best_guess(info: Wordle_Information, word_list: List[str], num_choices=50):
    best = [0, '']

    l = list(range(243))
    
    words = select_words(word_list, num_choices)
    #total_bar = tqdm(words, desc='Searching words', position=1)
    for word in tqdm(words):
        # bar = tqdm(l, desc=f"Analyzing {word.upper()}", position=0)
        # 243 combinations; progress one step per combination
        # this is necessary to prevent the bar from disappearing

        total_info = info.get_total_info(word)
        
        if total_info > best[0]:
            best[0] = total_info
            best[1] = word
        
        #total_bar.update()
    
    # bar.close()
    
    return best

'''
Solves the wordle represented by game object. Returns the number of guesses. 
If show_progress is marked as true, print progress along the way.
'''
def play_wordle(game: Wordle_Game, word_list: List[str], show_progress=False) -> int:
    info = Wordle_Information()

    guesses = 0

    word = "     "
    while not game.correct_word(word):
        num = min(50 * 4**guesses, 5757)
        if guesses == 0:
            word = random.choice(['arise', 'deals', 'crane', 'adieu', 'tares'])
        else:
            print("Choosing next guess:")
            word = best_guess(info, word_list, num)[1]

        if show_progress:
            print(f"Guessing {word}")
        guess_info = game.make_guess(word)
        guesses += 1
        info.add_info(guess_info)

        if show_progress:
            print(f"Result: {guess_info.info}")
            print(f"Possible words remaining: {info.count_possible_words()}\n")
        
        if info.count_possible_words() == 1:
            guesses += 1
            word = info.word_list[0]
            break
    
    if show_progress:
        print(f"Solved! Solution: {word}")
        print(f"Number of guesses: {guesses}")

    return guesses


info = Wordle_Information()
word_list = info.word_list
game = Wordle_Game("today")

play_wordle(game, word_list, show_progress=True)

# guess_info = Guess_Info("right", [])
# info.add_info(guess_info)

# guesses = {}

# for word in sublist:
#     info = Wordle_Information()
#     guess_info = game.make_guess("right")
#     info.add_info(guess_info)

#     guesses[word] = info.get_total_info(word)

# print(dict(sorted(guesses.items(), key=lambda item: item[1])))



# for word in sublist:
#     print(word, info.get_total_info(word))


