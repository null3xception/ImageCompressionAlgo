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
    with open("IO/Outputs/modified_codes.txt", "w") as f:
        f.write(str(huffman_codes))
    
    # Ensure padding to byte boundary
    while len(compressed_image_bit_string) % 8 != 0:
        compressed_image_bit_string += '0'  # Pad with zeros

    return compressed_image_bit_string

def huffman_decompress(compressed_bit_string):
    global huffman_codes
    # Load Huffman codes
    with open("IO/Outputs/modified_codes.txt", "r") as f:
        huffman_codes = eval(f.read())  # Convert stored string back to dictionary
    
    reversed_codes = {v: k for k, v in huffman_codes.items()}  # Reverse dictionary
    current_code = ""
    decompressed_bit_string = ""

    for bit in compressed_bit_string:
        current_code += bit
        if current_code in reversed_codes:
            decompressed_bit_string += reversed_codes[current_code]
            current_code = ""

    # Strip padding bits that were added during compression
    decompressed_bit_string = decompressed_bit_string.rstrip('0')

    return decompressed_bit_string

# --------- LZW Compression/Decompression ---------

def lzw_encode(input_string, table_max_size):
    table = {chr(i): i for i in range(256)}
    dict_size = 256
    output = []
    current_string = ""
    
    for symbol in input_string:
        current_string_plus_symbol = current_string + symbol
        if current_string_plus_symbol in table:
            current_string = current_string_plus_symbol
        else:
            output.append(table[current_string])
            if len(table) < table_max_size:
                table[current_string_plus_symbol] = dict_size
                dict_size += 1
            current_string = symbol
    
    if current_string:
        output.append(table[current_string])
    
    return output

def lzw_decode(compressed_data, table_max_size):
    table = {i: chr(i) for i in range(256)}
    dict_size = 256
    current_code = compressed_data.pop(0)
    current_string = table[current_code]
    result = [current_string]
    
    for code in compressed_data:
        if code in table:
            entry = table[code]
        elif code == dict_size:
            entry = current_string + current_string[0]
        else:
            raise ValueError("Invalid compressed data")
        
        result.append(entry)
        if len(table) < table_max_size:
            table[dict_size] = current_string + entry[0]
            dict_size += 1
        current_string = entry
    
    return ''.join(result)

# --------- Huffman-LZW Modified Compression ---------

def modified_compress(image_bit_string):
    start_time = time.time()

    # Step 1: Apply LZW Compression
    table_max_size = 2**12  # Example: 12-bit table size
    lzw_compressed_data = lzw_encode(image_bit_string, table_max_size)

    # Convert LZW compressed output to a binary bit string (16-bit encoding per code)
    lzw_bit_string = ''.join(format(code, '016b') for code in lzw_compressed_data)

    # Step 2: Apply Huffman Compression on LZW output
    compressed_image_bit_stringM = huffman_compress(lzw_bit_string)

    end_time = time.time()
    compression_time = (end_time - start_time) * 1000

    original_size = len(image_bit_string) * 8
    compressed_size = len(compressed_image_bit_stringM)
    compression_percentage = (1 - (compressed_size / original_size)) * 100 if original_size > 0 else 0

    return compressed_image_bit_stringM, original_size, compressed_size, compression_percentage, compression_time

# --------- Huffman-LZW Modified Decompression ---------

def modified_decompress(compressed_image_bit_string, original_bit_string):
    start_time = time.time()

    # Step 1: Apply Huffman Decompression
    decompressed_huffman_bit_string = huffman_decompress(compressed_image_bit_string)

    # Convert Huffman-decoded binary bit string back to LZW integer list (16-bit per code)
    lzw_compressed_data = [int(decompressed_huffman_bit_string[i:i + 16], 2) for i in range(0, len(decompressed_huffman_bit_string), 16)]

    # Step 2: Apply LZW Decompression
    table_max_size = 2**12  # Example: 12-bit table size
    decompressed_image_bit_string = lzw_decode(lzw_compressed_data, table_max_size)

    end_time = time.time()
    decompression_time = (end_time - start_time) * 1000
    psnr = calculate_psnr(original_bit_string, decompressed_image_bit_string)

    return decompressed_image_bit_string, decompression_time, psnr

def calculate_psnr(original_bit_string, decompressed_bit_string):
    mse = sum(b1 != b2 for b1, b2 in zip(original_bit_string, decompressed_bit_string)) / len(original_bit_string)
    if mse == 0:
        return 100  # Perfect reconstruction
    max_pixel_value = 1
    psnr = 10 * math.log10((max_pixel_value ** 2) / mse)
    return psnr