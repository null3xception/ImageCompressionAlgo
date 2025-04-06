import heapq
import time
import math
from collections import defaultdict

# --------- Huffman Compression/Decompression ---------

class Node:
    def __init__(self, frequency, symbol, left=None, right=None):
        self.frequency = frequency
        self.symbol = symbol
        self.left = left
        self.right = right
        self.huffman_direction = ''

    def __lt__(self, nxt):
        return self.frequency < nxt.frequency

huffman_codes = {}

def calculate_huffman_codes(node, code=''):
    code += node.huffman_direction
    if node.left:
        calculate_huffman_codes(node.left, code)
    if node.right:
        calculate_huffman_codes(node.right, code)
    if not node.left and not node.right:
        huffman_codes[node.symbol] = code
    return huffman_codes

def get_merged_huffman_tree(byte_to_frequency):
    huffman_tree = []
    for byte, frequency in byte_to_frequency.items():
        heapq.heappush(huffman_tree, Node(frequency, byte))
    while len(huffman_tree) > 1:
        left = heapq.heappop(huffman_tree)
        right = heapq.heappop(huffman_tree)
        left.huffman_direction = "0"
        right.huffman_direction = "1"
        merged_node = Node(left.frequency + right.frequency, left.symbol + right.symbol, left, right)
        heapq.heappush(huffman_tree, merged_node)
    return huffman_tree[0]

def get_frequency(image_bit_string):
    byte_to_frequency = defaultdict(int)
    for i in range(0, len(image_bit_string), 8):
        byte = image_bit_string[i:i + 8]
        byte_to_frequency[byte] += 1
    return byte_to_frequency

def validate_bit_string(bit_string):
    if any(bit not in '01' for bit in bit_string):
        raise ValueError("The input bit string contains invalid characters. Only '0' and '1' are allowed.")
    return bit_string

def huffman_compress(bit_string):
    bit_string = validate_bit_string(bit_string)  # Validate input
    global huffman_codes
    byte_to_frequency = get_frequency(bit_string)
    merged_huffman_tree = get_merged_huffman_tree(byte_to_frequency)
    huffman_codes = calculate_huffman_codes(merged_huffman_tree)  # Store globally
    compressed_image_bit_string = ''.join(huffman_codes[bit_string[i:i + 8]] for i in range(0, len(bit_string), 8))
    
    # Save Huffman codes for later use in decompression
    with open("IO/Outputs/huffman_lz_codes.txt", "w") as f:
        f.write(str(huffman_codes))
    
    return compressed_image_bit_string

def huffman_decompress(compressed_bit_string):
    global huffman_codes
    # Load Huffman codes
    with open("IO/Outputs/huffman_lz_codes.txt", "r") as f:
        huffman_codes = eval(f.read())  # Convert stored string back to dictionary
    
    reversed_codes = {v: k for k, v in huffman_codes.items()}  # Reverse dictionary
    current_code = ""
    decompressed_bit_string = ""

    for bit in compressed_bit_string:
        current_code += bit
        if current_code in reversed_codes:
            decompressed_bit_string += reversed_codes[current_code]
            current_code = ""

    return decompressed_bit_string

# --------- LZW Compression/Decompression ---------

def lzw_compress(data):
    dictionary = {chr(i): i for i in range(256)}
    dict_size = 256
    result = []
    current_string = ""

    for symbol in data:
        current_string_plus_symbol = current_string + symbol
        if current_string_plus_symbol in dictionary:
            current_string = current_string_plus_symbol
        else:
            result.append(dictionary[current_string])
            dictionary[current_string_plus_symbol] = dict_size
            dict_size += 1
            current_string = symbol

    if current_string:
        result.append(dictionary[current_string])

    return result

def lzw_decompress(compressed_data):
    dictionary = {i: chr(i) for i in range(256)}
    dict_size = 256
    current_string = chr(compressed_data.pop(0))
    result = [current_string]

    for code in compressed_data:
        if code in dictionary:
            entry = dictionary[code]
        elif code == dict_size:
            entry = current_string + current_string[0]
        else:
            raise ValueError("Invalid compressed data")

        result.append(entry)
        dictionary[dict_size] = current_string + entry[0]
        dict_size += 1
        current_string = entry

    return ''.join(result)

# --------- Huffman-LZW Combined Compression ---------

def huffman_lzw_compress(image_bit_string):
    start_time = time.time()

    # Step 1: Apply LZW Compression
    lzw_compressed_data = lzw_compress(image_bit_string)

    # Convert LZW compressed output to a binary bit string (16-bit encoding per code)
    lzw_bit_string = ''.join(format(code, '016b') for code in lzw_compressed_data)

    # Step 2: Apply Huffman Compression on LZW output
    compressed_image_bit_stringHZ = huffman_compress(lzw_bit_string)

    end_time = time.time()
    compression_time = (end_time - start_time) * 1000

    original_size = len(image_bit_string) * 8
    compressed_size = len(compressed_image_bit_stringHZ)
    compression_percentage = (1 - (compressed_size / original_size)) * 100 if original_size > 0 else 0

    return compressed_image_bit_stringHZ, original_size, compressed_size, compression_percentage, compression_time

# --------- Huffman-LZW Combined Decompression ---------

def huffman_lzw_decompress(compressed_image_bit_string, original_bit_string):
    start_time = time.time()

    # Step 1: Apply Huffman Decompression
    decompressed_huffman_bit_string = huffman_decompress(compressed_image_bit_string)

    # Convert Huffman-decoded binary bit string back to LZW integer list (16-bit per code)
    lzw_compressed_data = [int(decompressed_huffman_bit_string[i:i + 16], 2) for i in range(0, len(decompressed_huffman_bit_string), 16)]

    # Step 2: Apply LZW Decompression
    decompressed_image_bit_string = lzw_decompress(lzw_compressed_data)

    end_time = time.time()
    decompression_time = (end_time - start_time) * 1000
    psnr = calculate_psnr(original_bit_string, decompressed_image_bit_string)

    return decompressed_image_bit_string, decompression_time, psnr

# --------- PSNR Calculation ---------

def calculate_psnr(original_bit_string, decompressed_bit_string):
    mse = sum(b1 != b2 for b1, b2 in zip(original_bit_string, decompressed_bit_string)) / len(original_bit_string)
    if mse == 0:
        return 100  # Perfect reconstruction
    max_pixel_value = 1
    psnr = 10 * math.log10((max_pixel_value ** 2) / mse)
    return psnr

