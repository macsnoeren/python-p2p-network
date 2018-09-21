#######################################################################################################################
# AVANS - BLOCKCHAIN - MINOR MAD                                                                                      #
#                                                                                                                     #
# Author: Maurice Snoeren                                                                                             #
# Version: 0.1 beta (use at your own risk)                                                                            #
#                                                                                                                     #
# Example python script to show the working principle of simple encryption                                            #
#######################################################################################################################

def remove_spaces (input):
    return input.replace(" ", "")

def get_char_number(chars, char):
    for i in range(len(chars)):
        if char == chars[i]:
            return i

    print("Character not found '%s'" % char)
    return 0;

def shift_cypher_encrypt (input, chars, k):
    input = remove_spaces(input)
    cypher = list(input)

    for x in range(len(input)):
        p = get_char_number(chars, input[x])
        y = (p + k) % len(chars) # Shift cypher
        cypher[x] = chars[y]

    return "".join(cypher)

def shift_cypher_decrypt (input, chars, k):
    cypher = list(input)

    for x in range(len(input)):
        p = get_char_number(chars, input[x])
        y = (p - k) % len(chars) # Shift cypher
        cypher[x] = chars[y]

    return "".join(cypher)

def affine_cypher_encrypt (input, chars, a, b):
    input = remove_spaces(input)
    cypher = list(input)

    for x in range(len(input)):
        p = get_char_number(chars, input[x])
        y = (a*p + b) % len(chars) # Affine cypher
        cypher[x] = chars[y]

    return "".join(cypher)

def affine_cypher_decrypt (input, chars, a, b):
    cypher = list(input)

    for x in range(len(input)):
        p = get_char_number(chars, input[x])
        y = (a*p - b) % len(chars) # Shift cypher
        cypher[x] = chars[y]

    return "".join(cypher)

def vigenere_cypher_encrypt (input, chars, key):
    input = remove_spaces(input)
    cypher = list(input)
    key    = list(key)

    for x in range(len(input)):
        p = get_char_number(chars, input[x])

        k = get_char_number( chars, key[x % len(key)] )
        y = (p + k) % len(chars)  # Shift cypher
        cypher[x] = chars[y]

    return "".join(cypher)

def vigenere_cypher_decrypt (input, chars, key):
    cypher = list(input)
    key    = list(key)

    for x in range(len(input)):
        p = get_char_number(chars, input[x])

        k = get_char_number( chars, key[x % len(key)] )
        y = (p - k) % len(chars)  # Shift cypher
        cypher[x] = chars[y]

    return "".join(cypher)


chars = "abcdefghijklmnopqrstuvwxyz"
total = len(chars)

print("Total character in the chypher: %d" % total)

input_text = "blockchain is cool"
print("Input text             : " + input_text)
print("Shift  cypher(3) encrypt: " + shift_cypher_encrypt(input_text, chars, 3))
print("Shift  cypher(3) decrypt: " + shift_cypher_decrypt(shift_cypher_encrypt(input_text, chars, 3), chars, 3))

# y = 9x + 2 => x = 1/9(y - 2) => inverse of 9 mod 26 is 3 (gcd(9, 26) = 1, 9 * 3 = 1 (mod 26)=> x = 3(y - 2) => x = 3y - 6
print("Affine cypher(9, 2) encrypt: " + affine_cypher_encrypt(input_text, chars, 9, 2))
print("Affine cypher(3, 6) decrypt: " + affine_cypher_decrypt(affine_cypher_encrypt(input_text, chars, 9, 2), chars, 3, 6))

print("Vigenere cypher('key') encrypt: " + vigenere_cypher_encrypt(input_text, chars, "key"))
print("Vigenere cypher('key') decrypt: " + vigenere_cypher_decrypt(vigenere_cypher_encrypt(input_text, chars, "key"), chars, "key"))





