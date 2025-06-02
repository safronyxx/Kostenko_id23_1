import heapq
from collections import Counter, namedtuple
from typing import Dict
import base64

# ЛОГИКА ДЛЯ ШИФР И ДЕШИФР

class Node(namedtuple("Node", ["char", "freq"])):
    def __lt__(self, other):
        return self.freq < other.freq

# ХАФФМАН
def build_huffman_tree(text):
    frequency = Counter(text)
    heap = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(left.char + right.char, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0] if heap else None

def generate_huffman_codes(node, prefix="", codebook=None):
    if codebook is None:
        codebook = {}
    if not hasattr(node, "left") and not hasattr(node, "right"):
        codebook[node.char] = prefix
    else:
        generate_huffman_codes(node.left, prefix + "0", codebook)
        generate_huffman_codes(node.right, prefix + "1", codebook)
    return codebook

# XOR
def xor_encrypt(binary_string, key):
    key_bin = ''.join(f"{ord(c):08b}" for c in key)
    result = ""
    for i in range(len(binary_string)):
        result += str(int(binary_string[i]) ^ int(key_bin[i % len(key_bin)]))
    return result

def pad_binary_string(binary_string):
    padding = 8 - len(binary_string) % 8 if len(binary_string) % 8 != 0 else 0
    return binary_string + "0" * padding, padding

def unpad_binary_string(binary_string, padding):
    return binary_string[:-padding] if padding > 0 else binary_string

def binary_to_base64(binary_string):
    byte_array = bytearray(int(binary_string[i:i+8], 2) for i in range(0, len(binary_string), 8))
    return base64.b64encode(byte_array).decode("utf-8")

def base64_to_binary(encoded_str):
    byte_array = base64.b64decode(encoded_str)
    return ''.join(f"{byte:08b}" for byte in byte_array)

def reverse_huffman_codes(huffman_codes):
    return {v: k for k, v in huffman_codes.items()}


# ШИФРОВАНИЕ
def encode_text(text, key):
    tree = build_huffman_tree(text)
    huffman_codes = generate_huffman_codes(tree)

    encoded_binary = ''.join(huffman_codes[char] for char in text)
    padded_binary, padding = pad_binary_string(encoded_binary)
    encrypted_binary = xor_encrypt(padded_binary, key)
    encoded_data = binary_to_base64(encrypted_binary)

    return {
        "encoded_data": encoded_data,
        "key": key,
        "huffman_codes": huffman_codes,
        "padding": padding
    }


# ДЕШИФРОВАНИЕ
def decode_text(encoded_data, key, huffman_codes, padding):
    encrypted_binary = base64_to_binary(encoded_data)
    decrypted_binary = xor_encrypt(encrypted_binary, key)
    unpadded_binary = unpad_binary_string(decrypted_binary, padding)

    reversed_codes = reverse_huffman_codes(huffman_codes)
    current = ""
    decoded_text = ""
    for bit in unpadded_binary:
        current += bit
        if current in reversed_codes:
            decoded_text += reversed_codes[current]
            current = ""

    return {"decoded_text": decoded_text}
