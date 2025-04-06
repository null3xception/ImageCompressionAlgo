import os
# A Function That Reads an Image as Binary Data and Returns a String of bits
def read_image_bit_string(path):
    with open(path, 'rb') as image:
        bit_string = ""
        byte = image.read(1)
        while (len(byte) > 0):
            byte = ord(byte)
            bits = bin(byte)[2:].rjust(8, '0')
            bit_string += bits
            byte = image.read(1)
    return bit_string


def write_image(bit_string, path):
    with open(path, 'wb') as image:
        for i in range(0, len(bit_string), 8):
            byte = bit_string[i:i + 8]
            image.write(bytes([int(byte, 2)]))


def write_dictionary_file(dictionary, path):
    with open(path, 'w') as f:
        for key, value in dictionary.items():
            f.write('%s:%s\n' % (key, value))


def convert_bit_string_to_bytes(bit_string):
    """Convert a bit string (binary) to a byte array, ensuring valid 8-bit sequences."""
    byte_array = bytearray()
    
    # Ensure the bit string length is a multiple of 8
    if len(bit_string) % 8 != 0:
        print("Warning: Bit string length is not a multiple of 8. Padding may be required.")
        bit_string = bit_string.ljust(len(bit_string) + (8 - len(bit_string) % 8), '0')  # Pad with 0s

    for i in range(0, len(bit_string), 8):
        byte = bit_string[i:i + 8]

        if len(byte) != 8 or any(b not in '01' for b in byte):  # Extra validation
            print(f"Invalid byte found and skipped: {byte}")  
            continue  

        byte_array.append(int(byte, 2))

    return bytes(byte_array)

def write_imageHL(bit_string, output_path):
    """Writes a bit string to a binary file safely."""
    try:
        byte_array = bytearray()
        for i in range(0, len(bit_string), 8):
            byte = bit_string[i:i + 8]
            if len(byte) == 8:
                byte_array.append(int(byte, 2))  # Convert to integer and add to byte array
        with open(output_path, 'wb') as file:
            file.write(byte_array)
    except Exception as e:
        print(f"ERROR: Unable to write image file: {e}")


def read_image_bit_stringHL(path):
    """Reads an image file safely as a binary bit string."""
    try:
        with open(path, 'rb') as image:
            binary_data = image.read()
            bit_string = ''.join(f'{byte:08b}' for byte in binary_data)  # Convert each byte to 8-bit string
        return bit_string
    except Exception as e:
        print(f"ERROR: Unable to read image: {e}")
        return None
    

def read_image_bit_stringM(path):
    """Reads an image file safely as a binary bit string."""
    try:
        with open(path, 'rb') as image:
            binary_data = image.read()
            # Convert each byte to an 8-bit binary string
            bit_string = ''.join(f'{byte:08b}' for byte in binary_data)
            
            # Handle padding during reading
            if len(bit_string) % 8 != 0:
                print(f"Warning: Bit string length is not a multiple of 8 bits. Padding may have been added.")
                
        return bit_string
    except Exception as e:
        print(f"ERROR: Unable to read image: {e}")
        return None

# Function to save decompressed image
def save_decompressed_image_with_write_image(bit_string, path):
    try:
        with open(path, "wb") as f:
            f.write(convert_bit_string_to_bytes(bit_string))
            f.flush()  # Force write to disk
            os.fsync(f.fileno())  # Ensure file is fully written
    except Exception as e:
        print(f"Error writing decompressed image: {e}")


def convert_bit_string_to_bytesM(bit_string):
    """Convert a bit string (binary) to a byte array, ensuring valid 8-bit sequences."""
    byte_array = bytearray()

    # Remove any non-binary characters and log invalid ones
    cleaned_bit_string = ""
    for char in bit_string:
        if char in '01':
            cleaned_bit_string += char
        else:
            print(f"Invalid character '{char}' removed from bit string.")

    # Ensure the bit string length is a multiple of 8
    if len(cleaned_bit_string) % 8 != 0:
        print("Warning: Bit string length is not a multiple of 8. Padding may be required.")
        cleaned_bit_string = cleaned_bit_string.ljust(len(cleaned_bit_string) + (8 - len(cleaned_bit_string) % 8), '0')  # Pad with 0s

    for i in range(0, len(cleaned_bit_string), 8):
        byte = cleaned_bit_string[i:i + 8]
        byte_array.append(int(byte, 2))

    return bytes(byte_array)

def write_imageM(bit_string, output_path):
    """Writes a bit string to a binary file safely with padding."""
    try:
        # Pad bit string to be a multiple of 8 bits
        padded_bit_string = bit_string.ljust(len(bit_string) + (8 - len(bit_string) % 8), '0') if len(bit_string) % 8 != 0 else bit_string
        
        byte_array = bytearray()
        for i in range(0, len(padded_bit_string), 8):
            byte = padded_bit_string[i:i + 8]
            byte_array.append(int(byte, 2))  # Convert to integer and add to byte array

        with open(output_path, 'wb') as file:
            file.write(byte_array)
    except Exception as e:
        print(f"ERROR: Unable to write image file: {e}")

def save_decompressed_image_with_write_imageM(bit_string, path):
    try:
        with open(path, "wb") as f:
            f.write(convert_bit_string_to_bytesM(bit_string))
            f.flush()  # Force write to disk
            os.fsync(f.fileno())  # Ensure file is fully written
    except Exception as e:
        print(f"Error writing decompressed image: {e}")

