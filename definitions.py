NUM_LETTERS = 5

WORD_LIST = []
# read words from words.txt
with open("words.txt") as f:
    for line in f.readlines():
        WORD_LIST.append(line.strip())
    f.close()

'''
Returns a list of possible configurations of green, yellow, and gray, represented by 2, 1, and 0.
Defaults to words of size NUM_LETTERS.
'''
def result_configs(configs = [[]], num_left=NUM_LETTERS):
    if num_left == 0:
        return configs
    else:
        new_configs = []
        for i in [0, 1, 2]:
            for config in configs:
                new_configs.append(config + [i])
        
        return result_configs(new_configs, num_left - 1)