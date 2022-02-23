"""
All the code that actually plays Wordle is in here.
"""

import json
import random
from typing import List
from tqdm import tqdm, tqdm_notebook

# wordle helper objects
from wordle_information import Wordle_Information
from guess_info import Guess_Info
from wordle_game import Wordle_Game
from definitions import WORD_LIST, NUM_LETTERS

'''
Helper method to determine if a word has repeated letters.
'''
def repeated_letters(word: str) -> bool:
    for letter in word:
        if word.count(letter) != 1:
            return True
        
    return False

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
Find the best guess(es) given some Wordle_Information objects and optionally a word list.

infos: Wordle_Information or List[Wordle_Information] - the information to analyze
word_list: List[str]=WORD_LIST - the words to analyze. Defaults to global WORD_LIST from words.txt
num_choices: int=1 - the number of possible guesses to return (in decreasing order); default only 1
num_to_analyze: int=50 - the number of words from word_list to analyze (default 50)
shuffle_words: bool=True - whether or not to randomly select words from the word list (default yes)

return: List[str, float] or List[List[str, float]] - guesses with accompanying information in a 2-item list
    Returns a list of 2-item list if num_choices > 1
'''
def best_guess(infos, word_list: List[str]=WORD_LIST, num_choices=1, num_to_analyze=50, shuffle_words=True):
    # validate that infos is the correct type
    if type(infos) == Wordle_Information:
        infos = [infos]
    elif not type(infos) == List[Wordle_Information]:
        raise TypeError("infos should be a single Wordle_Information object or a list of them")
    
    # initialize best words list
    best = []
    min_info = 0

    # select words from word list    
    if shuffle_words:
        words = select_words(word_list, num_to_analyze)
    else:
        words = word_list[:num_to_analyze]

    # iterate through words (with progress bar)
    for word in tqdm(words):

        # add up total information word would give when guessing against all Wordle_Information objects in infos
        total_info = 0
        for info in infos:
            total_info += info.get_total_info(word)
        
        # insert into list of best words
        if total_info > min_info:
            insert_idx = 0
            for data in best:
                if total_info < data[1]:
                    insert_idx += 1
            
            best.insert(insert_idx, [word, total_info])

            if len(best) > num_choices:
                best.pop()
            
            # update min_info to the info of the lowest word in the list
            min_info = best[-1][1]
    
    # return single 2-item list if num_choices=1
    if num_choices == 1:
        return best[0]
    else:
        return best

'''
Helper function to play_wordle. Checks if user gave readable input for the guess_info portion.
info: str - user input for guess info
return: bool (good or bad input)
'''
def valid_guess_info_input(info: str) -> bool:
    # check if they entered NUM_LETTERS tokens
    spl = info.split(' ')
    if len(spl) != NUM_LETTERS:
        return False

    # make sure all tokens are 0, 1, or 2
    for n in spl:
        if n not in ['0', '1', '2']:
            return False
    
    return True

'''
Returns a list of the top words (along with their information) in a dictionary from first_words.py.
num: int - number of words to get
return: dict - dictionary with keys of words, values of information from words
'''
def get_best_first_words(num = 5) -> dict:
    # read words from first_words.json into dict
    with open ("first_words.json", 'r') as f:
        first_words = json.load(f)['words']

    # sort by info
    sorted_first_words = dict(sorted(first_words.items(), key=lambda item: item[1]).__reversed__())

    # get first num words
    words = []
    for idx, word in enumerate(sorted_first_words.keys()):
        words.append([word, first_words[word]])
        if idx+1 >= num:
            break
    
    return words

'''
Plays a game of Wordle through the terminal. Word list to use can be optionally specified.
'''
def play_wordle(word_list: List[str] = WORD_LIST):

    info = Wordle_Information()
    guesses = 0
    
    # input loop
    while True:

        # prompt guess
        if guesses == 0:
            # if first guess, get options from stored list (too much to compute)
            print("What word would you like to start with?")
            print("Good options:")
            for word in random.sample(get_best_first_words(20), 5):
                print(f"  {word[0]} (info {word[1]:.3f})")

        else:
            # if not first guess, analyze words with best_guess

            # get valid input for how many words to analyze
            n = input("How many words would you like to analyze? ")
            while not (n.isnumeric() and 0 <= int(n) <= len(word_list)):
                n = input(f"Please input an integer between 10 and {len(word_list)}.")

            n = int(n)
            if 0 < n:
                print(" Analyzing good options ".center(40, "#")) 
                best_words = best_guess(info, word_list=word_list, num_choices=5, num_to_analyze=n) # analyze the words

                print("Good options:")
                for word in best_words:
                    print(f"  {word[0]} (info {word[1]})") # print them

            print("What word would you like to guess?")
        
        # get guess
        choice = input().lower()
        while True:
            if repeated_letters(choice) or len(choice) != NUM_LETTERS:
                choice = input(f"Please enter a {NUM_LETTERS}-letter word with no repeated letters: ").lower()
                continue

            if choice not in word_list:
                yn = input("This word is not in the word list. Continue anyway? (Y/y/N/n): ")
                while yn not in ['Y', 'y', 'N', 'n']:
                    yn = input("Enter Y/y/N/n: ")

                if yn in "Nn":
                    choice = input("Please enter a 5-letter word with no repeated letters: ").lower()
                    continue
                else:
                    break
            else:
                break

        guesses += 1

        yn = input("Was your guess correct? (Y/y/N/n) ")
        while yn not in ['Y', 'y', 'N', 'n']:
            yn = input("Enter Y/y/N/n: ")
        
        if yn.lower() == "y":
            print(f"Congratulations! You took {guesses} guesses.")
            yn = True
            break
        
        # get input for info about guess
        result = input("Enter the result of your guess, separated by single spaces (0 is gray, 1 is yellow, 2 is green): ").strip()
        while True:
            # first check if input is valid
            if not valid_guess_info_input(result):
                result = input("Bad input. Try again: ").strip()
                continue
        
            # next check if this causes any immediate conflicts
            guess_info = Guess_Info(choice, [int(n) for n in result.split(' ')])
            if not info.add_info(guess_info, temporary=True):
                result = input("This conflicts with previous information. Input again: ")
                info.remove_temporary_info()
                continue
            
            # next check if this leaves any possible words
            if info.count_possible_words() == 0:
                result = input("This information leaves no possible valid words. Input again: ")
                info.remove_temporary_info()
                continue

            # for some reason the user said they didn't get it right earlier
            if guess_info.info == [2] * NUM_LETTERS:
                print(f"Congratulations! You took {guesses} guesses.")
                return

            # valid info. Reset temporary info used for input checking and add info permanently
            info.remove_temporary_info()
            info.add_info(guess_info)
            break
        
        # print remaining possible words
        if info.count_possible_words() > 15:
            print(f"There are {info.count_possible_words()} possible words remaining.")
        elif info.count_possible_words() == 1:
            print(f"Congratulations! You have eliminated all but one word. The word is: {info.get_possible_words()[0]}")
            print(f"You took {guesses} guesses.")
        else:
            print("Remaining possible words:")
            for word in info.get_possible_words():
                if repeated_letters(word):
                    print(f"  {word} (no info available)")
                else:
                    print(f"  {word} (info {info.get_total_info(word):.3f})")
        
'''
Solves the wordle represented by game object. Returns the number of guesses. 
If show_progress is marked as true, print progress along the way.
Returns number of guesses the bot took. If the bot can't find the word, returns None.
'''
def play_wordle_simulated(game: Wordle_Game, word_list: List[str]=WORD_LIST, show_progress=False) -> int:
    
    info = Wordle_Information()
    guesses = 0
    word = " "*NUM_LETTERS # blank string NUM_LETTERS long

    # keep guessing till the word is right
    while not game.correct_word(word):
        # NOTE: change this to match the specified amount of time for analyzing later
        num = min(50 * 4**guesses, len(word_list))

        # choose next guess
        if guesses == 0:
            word = random.choice(['arise', 'deals', 'crane', 'adieu', 'tares'])
        else:
            if show_progress:
                print("Choosing next guess:")
            word = best_guess(info, num_to_analyze=num)[0]

        if show_progress:
            print(f"Guessing {word}")
        
        # guess word and add info
        guess_info = game.make_guess(word)
        guesses += 1
        info.add_info(guess_info)

        if show_progress:
            print(f"Result: {guess_info.info}")
            print(f"Possible words remaining: {info.count_possible_words()}\n")
        
        # word is correct; break
        if info.count_possible_words() == 1:
            guesses += 1
            word = info.word_list[0]
            if not game.correct_word(word):
                if show_progress:
                    print("Correct word not in word list.")
                
                return None # error
    
    if show_progress:
        print(f"Solved! Solution: {word}")
        print(f"Number of guesses: {guesses}")

    return guesses

def main():
    play_wordle()

if __name__ == "__main__":
    main()