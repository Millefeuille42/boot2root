import sys
from itertools import permutations

def is_valid_input(numbers):
    return all(1 <= num <= 6 for num in numbers) and len(set(numbers)) == 6

def generate_valid_input():
    permutations_list = permutations(range(1, 7))
    for perm in permutations_list:
        if is_valid_input(perm):
            perm = ' '.join(map(str, perm))
            if perm.startswith('4'):
                print(perm)


def reverse_and_operation(desired_output):
    for i in range(100,256):  # Iterate through all printable alpha chars
        if (i & 15) == desired_output:
            return i

    return None

def encode_string(input_string):
    array_123 = 'isrveawhobpnutfg\xb0\x01'  # Corresponds to &array.123 in C code
    encoded_string = ""

    for char in input_string[:6]:
        encoded_char = array_123.index(char) & 15
        encoded_string += chr(reverse_and_operation(encoded_char))

    return encoded_string

def generate_numbers():
    numbers = [0] * 7
    numbers[1] = 1

    for index in range(1, 6):
        numbers[index + 1] = (index + 1) * numbers[index]

    return ' '.join(str(num) for num in numbers[1:])

if len(sys.argv) > 1:
    generate_valid_input()
else:
    print("Public speaking is very easy.")
    print(generate_numbers())
    print("1 b 214")
    print("9") # nth number of the fibonnaci suite (offset by one) + the secret password
    print(encode_string("giants"))
