import random

def gen(length):
  letters = {
    "vowel": {
      "single": ['a', 'e', 'i', 'o', 'u'],
      "double": ['oo', 'ee', 'ea', 'eu', 'io'],
    },
    "consonant": {
      "single": ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'x', 'y', 'z'],
      "double": ['st', 'th', 'gh', 'fl', 'ch']
    }
  }

  choices = ('vowel', 'consonant')
  types = ('single', 'double')

  # create starting
  letter_choice = random.choice(choices)
  letter_type = random.choice(types)

  name = random.choice(letters[letter_choice][letter_type])

  while len(name) < length:
    letter_choice = 'vowel' if letter_choice == 'consonant' else 'consonant'
    letter_type = 'single' if random.randint(0, 99) > 9 else 'double'

    name += random.choice(letters[letter_choice][letter_type])

  return name[:1].upper() + name[1:]

for i in range(100):
  length = random.randint(4, 6)
  print(gen(length))
