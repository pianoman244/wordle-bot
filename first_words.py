from wordle_information import Wordle_Information
from play_wordle import best_guess
from definitions import WORD_LIST
import json

'''
Searches for the best first words in word_list picking up where it left off.
Reads and stores data in first_words.json:
- words: dictionary where keys are words and values are info amounts.
- next_index: the index of the next word in word_list that hasn't been analyzed yet

step: number of words to analyze in one batch before re-writing to file

Only analyzes words that don't repeat letters.
'''
def search_for_first_words(step=10, word_list=WORD_LIST):
    # used to analyze words
    info = Wordle_Information()

    # load first words file
    with open("first_words.json", 'r') as f:
        first_words = json.load(f)
    start = first_words['next_index'] # pick up where you left off; index of first word to analyze stored from last time
    print(f"Starting at index {start}")

    # keep analyzing words until break or program is stopped
    for i in iter.count():

        # start and index of slice of words to analyze from
        idx1 = start + i*step
        idx2 = min(start + (i+1)*step, len(word_list)) # stop at the end of the list

        # analyze slice
        print("Analyzing words:")
        print(word_list[idx1:idx2])
        guess = best_guess([info], word_list[idx1:idx2], num_to_analyze=step) 
        print(guess)

        # insert best word from slice s
        first_words['words'][guess[0]] = guess[1]
        print(f"Best word: {guess[0]} (info {guess[1]})")
        first_words['next_index'] = idx2

        # write every time so I can break the loop if I want to
        with open("first_words.json", 'w') as f:
            json.dump(first_words, f)
        
        # reached the end of the list
        if idx2 == len(word_list):
            break

'''
Print the top num words from first_words.json. Defaults to 5.
'''
def print_best_first_words(num = 5):
    # read in words
    with open("first_words.json", 'r') as f:
        first_words = json.load(f)['words']
    
    # sort words by info amount
    sorted_first_words = dict(sorted(first_words.items(), key=lambda item: item[1]).__reversed__())

    # print words
    for idx, word in enumerate(sorted_first_words.keys()):
        print(f"{idx + 1}: {word} (info: {sorted_first_words[word]})")
        if idx+1 >= num:
            break

'''
Return a dictionary with words as keys and info as values of top num words from first_words.json. Defaults to 5.
'''
def get_best_first_words(num = 5) -> dict:
    # read words from file
    with open("first_words.json", 'r') as f:
        first_words = json.load(f)['words']
    
    # sort by info amount
    sorted_first_words = dict(sorted(first_words.items(), key=lambda item: item[1]).__reversed__())

    # add to list and return
    words = []
    for idx, word in enumerate(sorted_first_words.keys()):
        words.append([word, first_words[word]])
        if idx+1 >= num:
            break
    
    return words

def main():
    search_for_first_words()

if __name__ == "__main__":
    main()