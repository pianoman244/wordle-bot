"""
This is the source of the Wordle bot's power. At its core, a Wordle_Information object stores all the
information gained so far in a game of Wordle. It can check if a word is possible given the current
information in valid_word() and seamlessly add information for new guesses in add_info. It can tell you 
how good a guess with the basics of information theory in get_total_info(). See comments and docstrings!
"""


import math
from enum import Enum
import random
from types import SimpleNamespace
from tqdm import tqdm, tqdm_notebook

from wordle_configs import result_configs
from guess_info import Guess_Info

class GuessNotPossibleException(Exception):
    """Exception raised when invalid guess info is supplied to add_info function.

    Attributes:
        guess_info -- the guess info that caused the error
        message -- explanation of the error
    """

    def __init__(self, guess_info, message="Guess supplied to add_info() creates impossible situation"):
        self.guess_info = guess_info
        self.message = message
        super().__init__(self.message)

NUM_LETTERS = 5

class Wordle_Information:
    def __init__(self):

        # New way of storing data (filled with example data)
        # 
        # green = [None, 'a', 'r', None, None]
        # yellow = {'s': {0, 3}, 'e': {0}}
        # gray = {'e, q, u, l'}
        #
        # 'green' stores the index of all the letters currently discovered
        # 'yellow' is a dictionary where the keys are letters and the values are sets of indices in the word that the letter is not at
        # 'gray' is a set of letters not in the word
        # 
        # This new configuration minimizes the amount of information stored and ensures direct access to all the necessary information
        self.green = [None] * NUM_LETTERS
        self.yellow = {}
        self.gray = set()
        
        # This will be used for some annoying edge cases. Example:
        #
        # Guess 1: areas
        # Result: yellow, green, green, yellow, gray
        #
        # Clearly, the only place the a could go after this is at the very end. We need some way to calculate that.
        # This deduction will happen in the add_info function when a letter is marked as yellow with this code:

        # NOTE NOTE NOTE NOTE: THIS IS NOT IMPLEMENTED YET!

        # if NUM_LETTERS - unknown_letters - len(self.yellow[letter]) == 1:
        #   self.green[idx] = letter
        #   unknown_letters -= 1
        #
        # This will also be used when checking if a word is possible. The valid_word function will count how many unique letters
        # have no existing information in the word and if it's greater than unknown_letters, the word will be marked as invalid.
        self.unknown_letters = NUM_LETTERS

        # Arbitrary constant that is used to denote letters that have been exhaustively specified (see long comment in add_info)
        self.SPECIAL = 69

        with open("words.txt") as f:
            self.word_list = f.read().splitlines()

        # Store temporary added information for adding info from individual guesses
        # Should be stored minimally but thoroughly for easy and quick reversal
        #
        # NOTE: This will need some updating when the implementation of stuff using unknown_letters is added!
        self.temp_changes_dict = {}

        # The only way for a guess to add green information is to change an unknown letter to a known letter. All that must be
        # stored is the indices of letters that were newly marked as green. They will be marked as None in reversal
        self.temp_changes_dict['green'] = []

        # Three ways for yellow information to be added:
        # 1. A letter with no yellow information gets new information in the guess
        #    Solution: mark that letter as None and remove info entirely within reversal
        #              iterate through the keys of temp_changes.yellow in reversal
        #
        # 2. New indices were added to yellow information for a letter
        #    Solution: store the added indices in a list here with the key as the letter and remove them from the info in reversal
        #
        # 3. Yellow info for letter was marked as self.SPECIAL because exhaustive info on letter found
        #    Solution: mark that letter as self.SPECIAL in the normal 'yellow' dictionary
        #              store original yellow information on all relevant letters in yellow_special and access them if self.SPECIAL marked
        #              if yellow_special info for a letter is None, delete the info on that letter from add_info
        #              this only needs to be done in that final step when letter is marked as self.SPECIAL; there will be no yellow instances
        #              of that letter elsewhere in the word in that case
        self.temp_changes_dict['yellow'] = {}
        self.temp_changes_dict['yellow_special'] = {}

        # The only way to add gray information is to add letters that are marked as gray. Store those letters and remove in reversal.
        self.temp_changes_dict['gray'] = set()

        # Nothing fancy here. This should store the amount of unknown letters before the guess.
        self.temp_changes_dict['unknown_letters'] = NUM_LETTERS

        # Allows accessing information from temp_changes_dict like temp_changes.green instead of temp_changes['green'] or something
        self.temp_changes = SimpleNamespace(**self.temp_changes_dict)

        self.result_configs = result_configs()


    '''
    Checks if the input word is possible given the information contained in self.
    If Guess_Info object is supplied with additional information, that will be taken into consideration.

    Things I need to check:
    1. All green letters occur in the same spot in the word
    2. All yellow letters occur in the word but not at the indices specified
    3. No gray letters occur in the word UNLESS yellow data for that letter is marked as self.SPECIAL

    NOTE: I think these are the only constraints I need to check, but I should revisit this later.
    '''
    def valid_word(self, word, guess_info=None):
        # shorthand/I might forget to call the longer version
        if guess_info:
            return self.valid_word_with_guess_info(word, guess_info)

        # verify that all yellow letters are in word somewhere
        for key in self.yellow.keys():
            if key not in word:
                return False

        for i in range(NUM_LETTERS):
            # verify that green letter exists at this index and then if it matches the character in word
            if self.green[i] and self.green[i] != word[i]:
                return False

            # verify that if this letter isn't green, it's not marked as special either
            # if a letter is marked as special, it's only in the word where it is marked as green
            # this should prevent treating yellow as a dictionary when it's actually self.SPECIAL
            if self.yellow.get(word[i]) == self.SPECIAL:
                if self.green[i] == word[i]:
                    continue
                else:
                    return False

            # before going further, check if there's yellow info on the letter
            if self.yellow.get(word[i]):

                # verify that the letter at this index is not marked as definitely not there in yellow[letter]
                if i in self.yellow[word[i]]:
                    return False

                # verify that there are available spots for the letter elsewhere in the word
                location_possible = False
                for j in range(NUM_LETTERS):
                    # check if current index is an open spot
                    # if it's open, check if it's been marked as not possible in yellow data
                    # if it's open and there's no yellow data, it's a legal spot
                    #
                    # NOTE: revisit this potentially. I'm almost positive that there's no way there could be
                    # significant conflicts or places where this marks words as valid that actually aren't,
                    # at least with 5-letter words
                    if self.green[j] == None and j not in self.yellow[word[i]]:
                        location_possible = True
                        break
                
                if not location_possible:
                    return False
            
            # verify that letter is not grayed out already
            if word[i] in self.gray:
                return False

            
        
        return True
    
    '''
    BLAH. This is the hardest part here. The crux of the program. If I can do this efficiently I'm golden.
    '''
    def valid_word_with_guess_info(self, word, guess_info):
        return True

    '''
    Removes all words from word_list that are not possible given the current information.
    '''
    def update_word_list(self):
        valid_words = []
        for word in self.word_list:
            if self.valid_word(word):
                valid_words.append(word)
        
        self.word_list = valid_words
    
    '''
    Reverse the effects of previous temporary call of add_info using the information stored in temp_changes.
    Four steps:
    1. Reverse green information
    Set self.green to None at the indices stored in self.temp_changes.green

    2. Reverse yellow information by iterating through keys in self.temp_changes.yellow. Cases:
    a. data stored is None
        Remove that key/value pair from self.yellow if it exists
    b. data stored is self.SPECIAL
        Set self.yellow information at that letter to data in self.temp_changes.yellow_special (remove key/value pair if this is None)
    c. data stored is a list of indices
        Remove those indices from existing yellow data

    3. Reverse gray information
    Remove all letters in self.temp_changes.gray from self.gray

    4. Reverse unknown_letters information
    Set self.unknown_letters to self.temp_changes.unknown_letters

    NOTE: This is unstable! Doesn't work the same every time. I'm pretty sure it has to do with the self.SPECIAL stuff. Will need more investigation.
    '''
    def remove_temporary_info(self):
        for idx in self.temp_changes.green:
            self.green[idx] = None

        for key in self.temp_changes.yellow.keys():
            if self.temp_changes.yellow[key] == None:
                self.yellow.pop(key)
            
            elif self.temp_changes.yellow[key] == self.SPECIAL:
                if self.temp_changes.yellow_special[key] == None:
                    self.yellow.pop(key)
                else:
                    self.yellow[key] = self.temp_changes.yellow_special[key]
            
            else:
                for idx in self.temp_changes.yellow[key]:
                    self.yellow[key].discard(idx)
        
        for letter in self.temp_changes.gray:
            self.gray.discard(letter)
        
        self.unknown_letters = self.temp_changes.unknown_letters

        self.update_word_list()

    '''
    Updates data to include the information supplied in guess_info.

    This will call update_word_list only if temporary==False. 

    If this info should only be added temporarily to check the results of a potential guess configuration,
    pass temporary=True. (Defaults to False.) Any call to reverse_temporary_info after this will reverse
    the effects of adding the info from this guess.

    IMPORTANT: this assumes guesses passed in are valid for efficiency purposes.

    NOTE: Efficiency could be gained here by returning False if no words are possible after this information is added (True otherwise).
    '''
    def add_info(self, guess_info, temporary=False):
        word = guess_info.word
        info = guess_info.info

        # Reset temporary buffer
        if temporary:
            self.temp_changes.green = []
            self.temp_changes.yellow = {}
            self.temp_changes.yellow_special = {}
            self.temp_changes.gray = set()
            self.temp_changes.unknown_letters = self.unknown_letters

        # Store all yellow and green letters in this iteration. If any green letters were also
        # eliminated from other places, we will mark the corresponding yellow letters entry to None.
        #
        # If a letter was correctly guessed somewhere in a word and incorrectly guessed elsewhere,
        # we can be certain that the letter only occurs at that one spot. This will be stored by
        # setting the misplaced_entry letter for that word to self.SPECIAL (arbitrary constant).
        # Until that point, it's impossible to know for certain if a letter exists in multiple places or not.
        #
        # Example: "tears" is guessed and the a is marked as yellow. yellow['a'] = [2]
        # "areas" is guessed next.
        #
        # Case 1:
        # The first a is green but the second a is yellow. green[0] = 'a', yellow['a'] = [2, 3]
        # Now we know there's an a at the beginning and not at index 2 or 3, but we don't know about 1 or 4 yet.
        # For all we know, there could be an a at both (if such a word exists) or neither
        #
        # Case 2 (example):
        # The first a is gray and the second a is yellow. We know for sure that there's only one a at the word and
        # it's at index 3. green[3] = 'a', yellow['a'] = self.SPECIAL
        gray_this_time = []
        yellow_this_time = []
        green_this_time = []

        for i in range(NUM_LETTERS):

            # letter not in word
            if info[i] == 0:

                # letter can't be gray and green at same spot; impossible info
                if self.green[i] == word[i]:
                    return False
                
                # if there's yellow info on this letter and it's not special, this letter can't be gray
                if self.yellow.get(word[i]) and self.yellow[word[i]] != self.SPECIAL:
                    return False

                if temporary:
                    # this is new gray information; add to temporary info
                    if word[i] not in self.gray:
                        self.temp_changes.gray.add(word[i])

                self.gray.add(word[i])
                gray_this_time.append(word[i])
            
            # letter is in word not at this location
            elif info[i] == 1:
                # letter can't be yellow and green at the same location
                if self.green[i] == word[i]:
                    return False
                
                # letter can't be yellow and gray at same location
                if word[i] in self.gray:
                    return False

                yellow_this_time.append(word[i])

                # letter was already yellow somewhere once
                if self.yellow.get(word[i]): 

                    # if letter is special, it can't be yellow; impossible info
                    if self.yellow[word[i]] == self.SPECIAL:
                        return False
                    else:
                        if temporary:
                            # new index that letter is not at; add to temporary info
                            if i not in self.yellow[word[i]]:
                                # add to existing temporary yellow info on this letter
                                if self.temp_changes.yellow.get(word[i]):
                                    self.temp_changes.yellow[word[i]].add(i)

                                # no temporary yellow info on this letter yet; create it
                                else:
                                    self.temp_changes.yellow[word[i]] = set([i])

                        self.yellow[word[i]].add(i)

                # first time misplacing letter; create yellow letter index set
                else:
                    # this is the first yellow info on this letter; mark temp_changes.yellow to None
                    if temporary:
                        self.temp_changes.yellow[word[i]] = None

                    self.yellow[word[i]] = set([i])
            
            # letter is at correct location
            elif info[i] == 2:
                
                # two letters can't both be correct in the same spot; impossible info
                if self.green[i] != None and self.green[i] != word[i]:
                    return False

                # there is yellow info on the letter already that says it's not at this location; impossible info
                if self.yellow.get(word[i]) and i in self.yellow[word[i]]:
                    return False

                if temporary:
                    # new green information; add to temporary green info
                    if self.green[i] == None:
                        self.temp_changes.green.append(i)

                self.green[i] = word[i]
                green_this_time.append(word[i])

                # one less unknown letter
                self.unknown_letters -= 1
        
        # potentially update yellow letters list
        for letter in green_this_time:
            if letter in gray_this_time:
                # same letter can't be green, yellow, and gray; impossible info
                if letter in yellow_this_time:
                    return False

                if temporary:
                    # save original yellow information in yellow_special; will be None if there was none (using get)
                    self.temp_changes.yellow[letter] = self.SPECIAL
                    self.temp_changes.yellow_special[letter] = self.yellow.get(letter)

                self.yellow[letter] = self.SPECIAL

        if not temporary:
            self.update_word_list()
        
        return True
    
    def get_possible_words(self):
        return self.word_list
    
    def count_possible_words(self):
        count = 0
        for word in self.word_list:
            if self.valid_word(word):
                count += 1
        
        return count
    
    '''
    Return the total amount of information given by the guess.
    Formula: 
    p = probability of configuration occuring (words possible after/words possible before)

    p * log_2(1/p) 
    '''
    def get_info(self, guess_info):
        if self.add_info(guess_info, temporary=True):
            before = len(self.word_list) # word_list is not updated in temporary call to add_info
            after = self.count_possible_words()
            if after > 0:
                p = after/before
                info = p * math.log2(1/p)
            else:
                info = None
        else:
            info = None

        self.remove_temporary_info()

        return info

    def get_total_info(self, word, progress_bar: tqdm=None):
        total_info = 0
        random.shuffle(result_configs())

        for config in self.result_configs:
            if progress_bar:
                progress_bar.update()

            guess_info = Guess_Info(word, config)
            
            info = self.get_info(guess_info)
            if info:
                total_info += info


        return total_info

    def __str__(self) -> str:
        ret = ""
        ret += "Green: " + str(self.green) + "\n"
        ret += "Yellow: " + str(self.yellow) + "\n"
        ret += "Gray: " + str(self.gray) + "\n"
        ret += "Possible words: " + str(self.count_possible_words()) + "\n"
        ret += "Words in word list: " + str(len(self.word_list)) + "\n"
        return ret