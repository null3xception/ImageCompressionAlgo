import heapq
import time
import math

import file_handling


class node:

    def __init__(self, frequency, symbol, left=None, right=None):
        self.frequency = frequency
        self.symbol = symbol
        self.left = left
        self.right = right
        self.huffman_direction = ''

    def __lt__(self, nxt):
        return self.frequency < nxt.frequency


huffman_codes = {}


def get_compressed_image(image_bit_string):
    compressed_image_bit_string = ""
    for i in range(0, len(image_bit_string), 8):
        byte = image_bit_string[i:i + 8]
        compressed_image_bit_string += huffman_codes[byte]
    return compressed_image_bit_string


def calculate_huffman_codes(node, code=''):
    code += node.huffman_direction
    if (node.left):
        calculate_huffman_codes(node.left, code)
    if (node.right):
        calculate_huffman_codes(node.right, code)
    if (not node.left and not node.right):
        huffman_codes[node.symbol] = code
    return huffman_codes


def get_merged_huffman_tree(byte_to_frequency):
    huffman_tree = []
    for byte, frequency in byte_to_frequency.items():
        heapq.heappush(huffman_tree, node(frequency, byte))
    while len(huffman_tree) > 1:
        left = heapq.heappop(huffman_tree)
        right = heapq.heappop(huffman_tree)
        left.huffman_direction = "0"
        right.huffman_direction = "1"
        merged_node = node(left.frequency + right.frequency,
                           left.symbol + right.symbol, left, right)
        heapq.heappush(huffman_tree, merged_node)
    return huffman_tree[0]


def get_frequency(image_bit_string):
    byte_to_frequency = {}
    for i in range(0, len(image_bit_string), 8):
        byte = image_bit_string[i:i + 8]
        if byte not in byte_to_frequency:
            byte_to_frequency[byte] = 0
        byte_to_frequency[byte] += 1
    return byte_to_frequency


def compress(image_bit_string):
    start_time = time.time()  # Start measuring time

    # Step 1: Get frequency of bytes
    byte_to_frequency = get_frequency(image_bit_string)

    # Step 2: Build Huffman Tree
    merged_huffman_tree = get_merged_huffman_tree(byte_to_frequency)

    # Step 3: Generate Huffman Codes
    calculate_huffman_codes(merged_huffman_tree)

    # Step 4: Write Huffman codes to a file
    file_handling.write_dictionary_file(huffman_codes, "./IO/Outputs/huffman_codes.txt")

    # Step 5: Compress the image bit string
    compressed_image_bit_string = get_compressed_image(image_bit_string)

    end_time = time.time()  # End measuring time
    compression_time = (end_time - start_time) * 1000

    # Step 6: Compute size details
    original_size = len(image_bit_string)  # in bits
    compressed_size = len(compressed_image_bit_string)  # in bits
    compression_ratio = (compressed_size / original_size) * 100 if original_size > 0 else 0

    # Return everything including the compressed image
    return compressed_image_bit_string, original_size, compressed_size, compression_ratio, compression_time

def calculate_psnr(original_bit_string, decompressed_bit_string):
    """Calculate PSNR between original and decompressed bit strings."""
    mse = sum(b1 != b2 for b1, b2 in zip(original_bit_string, decompressed_bit_string)) / len(original_bit_string)
    
    if mse == 0:
        return 100  # Instead of 'inf', return 100 dB for perfect reconstruction
    
    max_pixel_value = 1  # Since it's a binary bit string (0 or 1)
    psnr = 10 * math.log10((max_pixel_value ** 2) / mse)
    return psnr

def decompress(compressed_image_bit_string, original_bit_string):
    start_time = time.time()  # Start measuring time
    decompressed_image_bit_string = ""
    current_code = ""
    for bit in compressed_image_bit_string:
        current_code += bit
        for byte, code in huffman_codes.items():
            if current_code == code:
                decompressed_image_bit_string += byte
                current_code = ""
    
    end_time = time.time()  # End measuring time
    decompression_time = (end_time - start_time) * 1000
    psnr = calculate_psnr(original_bit_string, decompressed_image_bit_string)

    return decompressed_image_bit_string, decompression_time, psnr