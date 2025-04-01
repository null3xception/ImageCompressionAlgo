import numpy as np
from PIL import Image
import os

# LZW Compression
def lzw_compress(data):
    # Initialize dictionary with single characters (ASCII 0-255)
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
            if dict_size < 4096:  # Limit dictionary size to 4096 entries
                dictionary[current_string_plus_symbol] = dict_size
                dict_size += 1
            current_string = symbol

    if current_string:
        result.append(dictionary[current_string])
    return result

# Optimized LZW Decompression
def lzw_decompress(compressed_data):
    dictionary = {i: chr(i) for i in range(256)}  # Initialize dictionary with single characters
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

# Process Image (Convert to grayscale and reduce color depth if necessary)
def process_image_for_compression(img):
    img = img.quantize(colors=256)  # Limit to 256 colors
    pixel_data = list(img.getdata())  # Flatten pixel data into a list
    return pixel_data, img

# Load Image and Prepare for Compression
def load_uploaded_image(uploaded_image_path):
    img = Image.open(uploaded_image_path)
    pixel_data, img = process_image_for_compression(img)
    return pixel_data, img

# Save Decompressed Image
def save_decompressed_image(decompressed_image, output_path):
    decompressed_image.save(output_path)
    print(f"Decompressed image saved to {output_path}")

# Calculate PSNR between two images
def calculate_psnr(original_image, decompressed_image):
    # Ensure both images have the same dimensions and mode
    original_array = np.array(original_image)
    decompressed_array = np.array(decompressed_image)
    
    if original_array.shape != decompressed_array.shape:
        raise ValueError("Images must have the same dimensions for PSNR calculation.")
    
    mse = np.mean((original_array - decompressed_array) ** 2)
    
    if mse == 0:  # Identical images
        return 100
    
    max_pixel = 255.0
    psnr = 10 * np.log10((max_pixel ** 2) / mse)
    return psnr