import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageFile, ImageTk
from tkinter import filedialog
import os
import file_handling
import huffman_coding
import time
import tkinter.messagebox as messagebox
from lzw_coding import lzw_compress, lzw_decompress, calculate_psnr, load_uploaded_image, save_decompressed_image
import huffman_lzw_coding   
import threading
import modified
import sys
import subprocess

ctk.set_appearance_mode("light")  
ctk.set_default_color_theme("dark-blue")  

compressed_image_bit_string = None
image_bit_string = None
image_holder = None

#region ------- Algorithms Functions ---------------------
def huffmanCompress(progress_callback):
    global compressed_image_bit_string, image_bit_string

    for i in range(100):
        progress_callback(i * 1, "Huffman")  # Update progress (10% increments) with Huffman label
        time.sleep(0.2)  # Simulate work

    image_path = uploadedImagePath
    image_bit_string = file_handling.read_image_bit_string(image_path)
    
    # Compress the image
    compressed_image_bit_string, original_size, compressed_size, compression_ratio, compression_time = huffman_coding.compress(image_bit_string)
    file_handling.write_image(compressed_image_bit_string, "IO/Outputs/huffman_compressed_image.bin")
    
    compressed_size = len(compressed_image_bit_string) / 8 / 1024  # KB
    compression_ratio = len(image_bit_string) / len(compressed_image_bit_string)
    
    # Update UI labels
    huffmanSizeLabel.configure(text=f"{compressed_size:.2f} KB")
    huffmanRatioLabel.configure(text=f"{compression_ratio:.4f}%")
    huffmanTimeLabel.configure(text=f"{compression_time:.2f} ms")
    
    
def huffmanDecompress(progress_callback):
    global compressed_image_bit_string, image_bit_string

    for i in range(100):
        progress_callback(i * 1, "Huffman")  # Update progress (10% increments) with Huffman label
        time.sleep(0.2)  # Simulate work
    
    decompressed_image_bit_string, decompression_time, psnr = huffman_coding.decompress(compressed_image_bit_string, image_bit_string)
    file_handling.write_image(decompressed_image_bit_string, "IO/Outputs/huffman_decompressed_image.jpg")
    
    # Load decompressed image
    huffmanDecompressedImage = ctk.CTkImage(
        light_image=Image.open("IO/Outputs/huffman_decompressed_image.jpg"),
        dark_image=Image.open("IO/Outputs/huffman_decompressed_image.jpg"),
        size=(250, 250)
    )
    
    img_label1.configure(image=huffmanDecompressedImage)  # Update image
    img_label1.image = huffmanDecompressedImage
    
    # Update UI labels
    huffmanDecompressedTimeLabel.configure(text=f"{decompression_time:.2f} ms")  # Display decompression time
    huffmanPSNRLabel.configure(text=f"{psnr:.2f} dB")  # Display PSNR value
    btn1.place_forget()

def huffmanDecompressNoCallBack():
    global compressed_image_bit_string, image_bit_string

    decompressed_image_bit_string, decompression_time, psnr = huffman_coding.decompress(compressed_image_bit_string, image_bit_string)
    file_handling.write_image(decompressed_image_bit_string, "IO/Outputs/huffman_decompressed_image.jpg")
    
    # Load decompressed image
    huffmanDecompressedImage = ctk.CTkImage(
        light_image=Image.open("IO/Outputs/huffman_decompressed_image.jpg"),
        dark_image=Image.open("IO/Outputs/huffman_decompressed_image.jpg"),
        size=(250, 250)
    )
    
    img_label1.configure(image=huffmanDecompressedImage)  # Update image
    img_label1.image = huffmanDecompressedImage
    
    # Update UI labels
    huffmanDecompressedTimeLabel.configure(text=f"{decompression_time:.2f} ms")  # Display decompression time
    huffmanPSNRLabel.configure(text=f"{psnr:.2f} dB")  # Display PSNR value
    btn1.place_forget()
    

def lzwCompress(progress_callback):
    global uploadedImagePath
    for i in range(100):
        progress_callback(i * 1, "LZW")  # Update progress (5% increments) with LZW label
        time.sleep(0.2)  # Simulate work

    image_path = uploadedImagePath
    image_data, original_image = load_uploaded_image(image_path)

    # Compress the image using LZW
    start_time = time.time()
    compressed_data = lzw_compress([chr(pixel) for pixel in image_data])

    # Write compressed data to file
    with open("IO/Outputs/lzw_compressed_image.bin", "wb") as f:
        for code in compressed_data:
            f.write(code.to_bytes(2, byteorder="big"))  # Write each code as 2 bytes

    # Calculate compressed size
    compression_time = time.time() - start_time
    compressed_size_bytes = len(compressed_data) * 2  # Assuming each entry takes 2 bytes
    compressed_size = f"{compressed_size_bytes} Bytes" if compressed_size_bytes < 1024 else \
                    f"{compressed_size_bytes / 1024:.2f} KB" if compressed_size_bytes < 1024**2 else \
                    f"{compressed_size_bytes / (1024 ** 2):.2f} MB"

    # Update UI Labels
    lzwSizeLabel.configure(text=f"{compressed_size}")
    lzwRatioLabel.configure(text=f"{len(compressed_data) / len(image_data):.4f}%")
    lzwTimeLabel.configure(text=f"{compression_time:.2f} ms")

    return compressed_data, original_image

def lzwCompressNoCallBack():
    global uploadedImagePath
    
    image_path = uploadedImagePath
    image_data, original_image = load_uploaded_image(image_path)

    # Compress the image using LZW
    start_time = time.time()
    compressed_data = lzw_compress([chr(pixel) for pixel in image_data])

    # Write compressed data to file
    with open("IO/Outputs/lzw_compressed_image.bin", "wb") as f:
        for code in compressed_data:
            f.write(code.to_bytes(2, byteorder="big"))  # Write each code as 2 bytes

    # Calculate compressed size
    compression_time = time.time() - start_time
    compressed_size_bytes = len(compressed_data) * 2  # Assuming each entry takes 2 bytes
    compressed_size = f"{compressed_size_bytes} Bytes" if compressed_size_bytes < 1024 else \
                    f"{compressed_size_bytes / 1024:.2f} KB" if compressed_size_bytes < 1024**2 else \
                    f"{compressed_size_bytes / (1024 ** 2):.2f} MB"

    # Update UI Labels
    lzwSizeLabel.configure(text=f"{compressed_size}")
    lzwRatioLabel.configure(text=f"{len(compressed_data) / len(image_data):.4f}%")
    lzwTimeLabel.configure(text=f"{compression_time:.2f} ms")

    return compressed_data, original_image

def lzwDecompress(progress_callback):
    compressed_data, original_image = lzwCompressNoCallBack()

    for i in range(100):
        progress_callback(i * 1, "LZW")  # Update progress (5% increments) with LZW label
        time.sleep(0.2)  # Simulate work
    
    start_time = time.time()
    decompressed_data = lzw_decompress(compressed_data)
    decompressed_image = Image.new('L', original_image.size)
    decompressed_image.putdata([ord(c) for c in decompressed_data])
    decompression_time = time.time() - start_time
    
    #print(f"Decompression time: {decompression_time:.2f} seconds")
    
    # Calculate PSNR
    psnr = calculate_psnr(original_image, decompressed_image)
    #print(f"PSNR: {psnr:.2f} dB")

    lzwDecompressedTimeLabel.configure(text=f"{decompression_time:.2f} ms")
    lzwPSNRLabel.configure(text=f"{psnr:.2f} dB")

    
    # Save the decompressed image
    output_path = "IO/Outputs/lzw_decompressed_image.jpg"  # Define the output path for the decompressed image
    save_decompressed_image(decompressed_image, output_path)

    lzwDecompressedImage = ctk.CTkImage(
        light_image=Image.open("IO/Outputs/lzw_decompressed_image.jpg"),
        dark_image=Image.open("IO/Outputs/lzw_decompressed_image.jpg"),
        size=(250, 250)
    )
    
    img_label2.configure(image=lzwDecompressedImage)  # Update image
    img_label2.image = lzwDecompressedImage
    btn2.place_forget()
    
    return decompressed_image

def lzwDecompressNoCallBack():
    compressed_data, original_image = lzwCompressNoCallBack()

    
    start_time = time.time()
    decompressed_data = lzw_decompress(compressed_data)
    decompressed_image = Image.new('L', original_image.size)
    decompressed_image.putdata([ord(c) for c in decompressed_data])
    decompression_time = time.time() - start_time
    
    #print(f"Decompression time: {decompression_time:.2f} seconds")
    
    # Calculate PSNR
    psnr = calculate_psnr(original_image, decompressed_image)
    #print(f"PSNR: {psnr:.2f} dB")

    lzwDecompressedTimeLabel.configure(text=f"{decompression_time:.2f} ms")
    lzwPSNRLabel.configure(text=f"{psnr:.2f} dB")

    
    # Save the decompressed image
    output_path = "IO/Outputs/lzw_decompressed_image.jpg"  # Define the output path for the decompressed image
    save_decompressed_image(decompressed_image, output_path)

    lzwDecompressedImage = ctk.CTkImage(
        light_image=Image.open("IO/Outputs/lzw_decompressed_image.jpg"),
        dark_image=Image.open("IO/Outputs/lzw_decompressed_image.jpg"),
        size=(250, 250)
    )
    
    img_label2.configure(image=lzwDecompressedImage)  # Update image
    img_label2.image = lzwDecompressedImage
    btn2.place_forget()
    
    return decompressed_image

def huffmanLZWCompress(progress_callback):
    global image_bit_string

    for i in range(100):  # First half progress for Huffman
        progress_callback(i * 1, "Huffman-LZW")
        time.sleep(0.2)  # Simulating work

    # Step 1: Read image safely
    image_path = uploadedImagePath
    image_bit_string = file_handling.read_image_bit_string(image_path)

    if not image_bit_string:
        print("ERROR: Image bit string is empty or corrupted!")
        return

    # Step 2: Apply Huffman-LZW Compression
    compressed_image_bit_stringHL, original_size, compressed_size, compression_ratio, compression_time = huffman_lzw_coding.huffman_lzw_compress(image_bit_string)

    # Step 3: Save compressed file safely
    file_handling.write_imageHL(compressed_image_bit_stringHL, "IO/Outputs/huffman_lzw_compressed_image.bin")

    # Step 4: Calculate compression stats
    compressed_size_kb = compressed_size / 8 / 1024
    
    compression_percentage = (1 - (compressed_size / original_size)) 

    # Step 5: Update UI labels
    huffmanLzwSizeLabel.configure(text=f"{compressed_size_kb:.2f} KB")
    huffmanLzwRatioLabel.configure(text=f"{compression_percentage:.4f}%")
    huffmanLzwTimeLabel.configure(text=f"{compression_time:.2f} ms")

def huffmanLZWDecompress(progress_callback):
    global decompressed_image_bit_string

    # Simulate progress update for the Huffman-LZW decompression
    for i in range(100):  # First half progress for Huffman
        progress_callback(i * 1, "Huffman-LZW")
        time.sleep(0.2)  # Simulating work
    
    try:
        # Read the compressed image bit string from file
        compressed_image_path = "IO/Outputs/huffman_lzw_compressed_image.bin"
        compressed_image_bit_stringHL = file_handling.read_image_bit_stringHL(compressed_image_path)

        # Read the original bit string from the uploaded image
        original_bit_string = file_handling.read_image_bit_stringHL(uploadedImagePath)

        # Step 2: Apply Huffman-LZW Decompression
        decompressed_image_bit_string, decompression_time, psnr = huffman_lzw_coding.huffman_lzw_decompress(
            compressed_image_bit_stringHL, original_bit_string
        )

        # Step 3: Save decompressed image
        output_path = "IO/Outputs/huffman_lzw_decompressed_image.jpg"
        file_handling.save_decompressed_image_with_write_image(decompressed_image_bit_string, output_path)

        # Step 4: Update UI Labels with decompression time and PSNR
        huffmanLzwDecompressedTimeLabel.configure(text=f"{decompression_time:.2f} ms")
        huffmanLzwPSNRLabel.configure(text=f"{psnr:.2f} dB")

        # Step 5: Load the decompressed image with PIL and handle truncated images
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        decompressed_image = Image.open(output_path)

        # Step 6: Create CTkImage and update the UI label
        huffmanlzwDecompressedImage = ctk.CTkImage(
            light_image=decompressed_image,
            dark_image=decompressed_image,
            size=(250, 250)
        )
        
        # Update the label with the decompressed image
        img_label3.configure(image=huffmanlzwDecompressedImage)
        img_label3.image = huffmanlzwDecompressedImage  # Keep a reference to avoid garbage collection
        btn3.place_forget()

    except Exception as e:
        # Handle any exceptions, such as file not found or decompression failure
        print(f"Error during Huffman-LZW decompression: {e}")
        huffmanLzwDecompressedTimeLabel.configure(text="Error")
        huffmanLzwPSNRLabel.configure(text="Error")

def huffmanLZWDecompressNoCallBack():
    global decompressed_image_bit_string

    try:
        # Read the compressed image bit string from file
        compressed_image_path = "IO/Outputs/huffman_lzw_compressed_image.bin"
        compressed_image_bit_stringHL = file_handling.read_image_bit_stringHL(compressed_image_path)

        # Read the original bit string from the uploaded image
        original_bit_string = file_handling.read_image_bit_stringHL(uploadedImagePath)

        # Step 2: Apply Huffman-LZW Decompression
        decompressed_image_bit_string, decompression_time, psnr = huffman_lzw_coding.huffman_lzw_decompress(
            compressed_image_bit_stringHL, original_bit_string
        )

        # Step 3: Save decompressed image
        output_path = "IO/Outputs/huffman_lzw_decompressed_image.jpg"
        file_handling.save_decompressed_image_with_write_image(decompressed_image_bit_string, output_path)

        # Step 4: Update UI Labels with decompression time and PSNR
        huffmanLzwDecompressedTimeLabel.configure(text=f"{decompression_time:.2f} ms")
        huffmanLzwPSNRLabel.configure(text=f"{psnr:.2f} dB")

        # Step 5: Load the decompressed image with PIL and handle truncated images
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        decompressed_image = Image.open(output_path)

        # Step 6: Create CTkImage and update the UI label
        huffmanlzwDecompressedImage = ctk.CTkImage(
            light_image=decompressed_image,
            dark_image=decompressed_image,
            size=(250, 250)
        )
        
        # Update the label with the decompressed image
        img_label3.configure(image=huffmanlzwDecompressedImage)
        img_label3.image = huffmanlzwDecompressedImage  # Keep a reference to avoid garbage collection
        btn3.place_forget()

    except Exception as e:
        # Handle any exceptions, such as file not found or decompression failure
        print(f"Error during Huffman-LZW decompression: {e}")
        huffmanLzwDecompressedTimeLabel.configure(text="Error")
        huffmanLzwPSNRLabel.configure(text="Error")

def modifiedCompress(progress_callback):
    global image_bit_string

    # Simulate progress update for the Modified compression
    for i in range(100):  # Update progress for Modified compression
        progress_callback(i * 1, "Modified")
        time.sleep(0.2)  # Simulating work

    try:
        # Step 1: Read image safely
        image_path = uploadedImagePath
        image_bit_string = file_handling.read_image_bit_stringM(image_path)

        if not image_bit_string:
            print("ERROR: Image bit string is empty or corrupted!")
            return

        # Step 2: Apply Modified Compression
        compressed_image_bit_stringM, original_size, compressed_size, compression_ratio, compression_time = modified.modified_compress(image_bit_string)

        # Step 3: Save compressed file safely
        file_handling.write_imageM(compressed_image_bit_stringM, "IO/Outputs/modified_compressed_image.bin")

        # Step 4: Calculate compression stats
        compressed_size_kb = compressed_size / 8 / 1024
        compression_percentage = (1 - (compressed_size / original_size))

        # Step 5: Update UI labels with compression stats
        modifiedSizeLabel.configure(text=f"{compressed_size_kb:.2f} KB")
        modifiedRatioLabel.configure(text=f"{compression_percentage:.4f}%")
        modifiedTimeLabel.configure(text=f"{compression_time:.2f} ms")

    except Exception as e:
        print(f"Error during Modified compression: {e}")
        modifiedSizeLabel.configure(text="Error")
        modifiedRatioLabel.configure(text="Error")
        modifiedTimeLabel.configure(text="Error")

def modifiedDecompress(progress_callback):
    global decompressed_image_bit_string

    # Simulate progress update for the modified decompression
    for i in range(100):  # Update progress for Modified Decompression
        progress_callback(i * 1, "Modified")
        time.sleep(0.2)  # Simulating work
    
    try:
        # Step 1: Read the compressed image bit string from file
        compressed_image_path = "IO/Outputs/modified_compressed_image.bin"
        compressed_image_bit_stringM = file_handling.read_image_bit_stringM(compressed_image_path)

        # Step 2: Read the original bit string from the uploaded image
        original_bit_string = file_handling.read_image_bit_stringM(uploadedImagePath)

        # Step 3: Apply Modified Decompression
        decompressed_image_bit_string, decompression_time, psnr = modified.modified_decompress(
            compressed_image_bit_stringM, original_bit_string
        )

        # Step 4: Save decompressed image
        output_path = "IO/Outputs/modified_decompressed_image.jpg"
        file_handling.save_decompressed_image_with_write_imageM(decompressed_image_bit_string, output_path)

        # Step 5: Update UI Labels with decompression time and PSNR
        modifiedDecompressedTimeLabel.configure(text=f"{decompression_time:.2f} ms")
        modifiedPSNRLabel.configure(text=f"{psnr:.2f} dB")

        # Step 6: Load the decompressed image with PIL and handle truncated images
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        decompressed_image = Image.open(output_path)

        # Step 7: Create CTkImage and update the UI label
        modifiedDecompressedImage = ctk.CTkImage(
            light_image=decompressed_image,
            dark_image=decompressed_image,
            size=(250, 250)
        )
        
        # Update the label with the decompressed image
        img_label4.configure(image=modifiedDecompressedImage)
        img_label4.image = modifiedDecompressedImage  # Keep a reference to avoid garbage collection
        btn4.place_forget()

    except Exception as e:
        # Handle any exceptions, such as file not found or decompression failure
        print(f"Error during Modified decompression: {e}")
        huffmanLzwDecompressedTimeLabel.configure(text="Error")
        huffmanLzwPSNRLabel.configure(text="Error")
        # Optionally show an error message on the image label
        img_label4.configure(text="Decompression failed")

def modifiedDecompressNoCallBack():
    global decompressed_image_bit_string

    try:
        # Step 1: Read the compressed image bit string from file
        compressed_image_path = "IO/Outputs/modified_compressed_image.bin"
        compressed_image_bit_stringM = file_handling.read_image_bit_stringM(compressed_image_path)

        # Step 2: Read the original bit string from the uploaded image
        original_bit_string = file_handling.read_image_bit_stringM(uploadedImagePath)

        # Step 3: Apply Modified Decompression
        decompressed_image_bit_string, decompression_time, psnr = modified.modified_decompress(
            compressed_image_bit_stringM, original_bit_string
        )

        # Step 4: Save decompressed image
        output_path = "IO/Outputs/modified_decompressed_image.jpg"
        file_handling.save_decompressed_image_with_write_imageM(decompressed_image_bit_string, output_path)

        # Step 5: Update UI Labels with decompression time and PSNR
        modifiedDecompressedTimeLabel.configure(text=f"{decompression_time:.2f} ms")
        modifiedPSNRLabel.configure(text=f"{psnr:.2f} dB")

        # Step 6: Load the decompressed image with PIL and handle truncated images
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        decompressed_image = Image.open(output_path)

        # Step 7: Create CTkImage and update the UI label
        modifiedDecompressedImage = ctk.CTkImage(
            light_image=decompressed_image,
            dark_image=decompressed_image,
            size=(250, 250)
        )
        
        # Update the label with the decompressed image
        img_label4.configure(image=modifiedDecompressedImage)
        img_label4.image = modifiedDecompressedImage  # Keep a reference to avoid garbage collection
        btn4.place_forget()

    except Exception as e:
        # Handle any exceptions, such as file not found or decompression failure
        print(f"Error during Modified decompression: {e}")
        huffmanLzwDecompressedTimeLabel.configure(text="Error")
        huffmanLzwPSNRLabel.configure(text="Error")
        # Optionally show an error message on the image label
        img_label4.configure(text="Decompression failed")

#endregion


#region ----------- Functions -------------------------

def updateCompressButtonState():
    if image_holder:  # If there is an image in the holder
        compressButton.configure(state="normal")  # Enable the button
    else:
        compressButton.configure(state="disabled")  # Disable the button

def updateDecompressButtonState():
    if image_holder:  # If there is an image in the holder
        decompressButton.configure(state="normal")  # Enable the button
    else:
        decompressButton.configure(state="disabled")  # Disable the button

def modalDecompress():
    # Create a new top-level window to act as a modal
    modal_window = ctk.CTkToplevel(app)
    modal_window.geometry("400x150")
    modal_window.title("Decompress")

    # Center the modal window
    window_width = 400
    window_height = 150
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_left = int(screen_width / 2 - window_width / 2)
    modal_window.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

    # Disable the main window to mimic modal behavior
    app.withdraw()

    # Add a label with the question
    label = ctk.CTkLabel(modal_window, text="Do you want to manually decompress the images?")
    label.pack(pady=20)

    # Button frame for Yes and No
    button_frame = ctk.CTkFrame(modal_window)
    button_frame.pack(pady=10)

    def on_yes():
        # Overlay buttons centered on the image labels
        decompressButton.configure(state="disabled")
        btn1.place(x=50, y=150)
        btn2.place(x=310, y=150)
        btn3.place(x=560, y=150)
        btn4.place(x=810, y=150)
        modal_window.destroy()
        app.deiconify()

    def on_no():
        decompressImage(app)  # Replace with your default/no-path logic
        modal_window.destroy()
        app.deiconify()

    # Yes and No buttons
    yes_button = ctk.CTkButton(button_frame, text="Yes", command=on_yes)
    no_button = ctk.CTkButton(button_frame, text="No", command=on_no)

    yes_button.pack(side="left", padx=10)
    no_button.pack(side="right", padx=10)

def upload_image():
    global uploadedImagePath
    global image_holder

    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])

    if file_path:  # Check if a file is selected
        uploadedImagePath = file_path
        image_holder = uploadedImagePath
        img = Image.open(file_path)
        updateCompressButtonState()

        # Now, create the CTkImage with the grayscale image
        new_image = ctk.CTkImage(light_image=img, dark_image=img, size=(250, 250))

        # Update the image holder with the new image
        mainImageHolderWidget.configure(image=new_image)
        mainImageHolderWidget.image = new_image  

        # Get file size
        file_size_bytes = os.path.getsize(file_path)
        if file_size_bytes < 1024:
            file_size = f"{file_size_bytes} Bytes"
        elif file_size_bytes < 1024 ** 2:
            file_size = f"{file_size_bytes / 1024:.2f} KB"
        elif file_size_bytes < 1024 ** 3:
            file_size = f"{file_size_bytes / (1024 ** 2):.2f} MB"
        else:
            file_size = f"{file_size_bytes / (1024 ** 3):.2f} GB"

        # Extract image details
        image_info = f"File: {os.path.basename(file_path)}\nSize: {img.size[0]}x{img.size[1]}\nFormat: {img.format}\nFile Size: {file_size}"

        # Update textbox with image details
        mainImageHolderTextBox.configure(state="normal")  # Enable editing
        mainImageHolderTextBox.delete("1.0", "end")  # Clear previous text
        mainImageHolderTextBox.insert("1.0", image_info)  # Insert new info
        mainImageHolderTextBox.configure(state="disabled")  # Make read-only again


def upload_huffman_bin():
    def updateProgress(value, algorithm):
        # Update progress bar and percentage label
        progress.set(value)
        percentage_label.configure(text=f"{value}% - {algorithm}")
        app.update_idletasks()  # Ensure the UI updates


    # Start the process of file upload and decompression
    file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])

    if file_path:
        file_name = os.path.basename(file_path)

        expected_file_name = "huffman_compressed_image.bin"

        if file_name == expected_file_name:
            # Update the file label with the valid file name
            file_label1.configure(text=f"{file_name}", text_color="black")

            modal_window = ctk.CTkToplevel(app)
            modal_window.geometry("400x100")
            modal_window.title("Decompression Progress")

            # Center the modal window on the screen
            window_width = 400
            window_height = 100
            screen_width = app.winfo_screenwidth()
            screen_height = app.winfo_screenheight()

            # Calculate the position to center the modal window
            position_top = int(screen_height / 2 - window_height / 2)
            position_left = int(screen_width / 2 - window_width / 2)

            # Set the position of the modal window
            modal_window.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

            # Make sure modal window stays on top and grabs focus
            modal_window.grab_set()  # Grabs all events for the modal window
            modal_window.lift()      # Brings the modal window to the front
            modal_window.focus_set() # Ensures modal has focus

            # Create a label for loading status
            label = ctk.CTkLabel(modal_window, text="Decompressing, please wait...")
            label.pack(pady=10)

            # Create a Progressbar widget using CustomTkinter
            progress = ctk.CTkProgressBar(modal_window, width=300, mode="determinate")
            progress.pack(pady=10)

            # Create a label to show the percentage of progress and the current algorithm
            percentage_label = ctk.CTkLabel(modal_window, text="0% - Huffman")
            percentage_label.pack(pady=5)

            # Disable the main window (to mimic modal behavior)
            app.attributes("-disabled", True)

            # Simulate decompression and update progress (replace with actual decompression logic)
            def simulate_decompression():
                # Only call huffmanDecompress when the file is successfully uploaded
                    # Only call huffmanDecompress when the file is successfully uploaded
                for i in range(101):
                    updateProgress(i * 1, "Huffman")  # Update progress during simulation
                    time.sleep(0.2)  # Simulate work

                # Call huffmanDecompress only after simulation loop finishes, no redundant progress update
                huffmanDecompressNoCallBack()

                # Show the completion message and close the modal
                messagebox.showinfo("Decompression Complete", "The image has been successfully decompressed!")
                modal_window.destroy()
                updateDecompressButtonState()

            # Start the decompression process in a separate thread to avoid freezing the GUI
            threading.Thread(target=simulate_decompression, daemon=True).start()
        else:
            # Show an error message if the file name doesn't match
            file_label1.configure(text=f"Wrong file! Please upload '{expected_file_name}'.", text_color="red")
            modal_window.destroy()  # Close the modal window immediately

    # Enable the main window again once process completes
    app.attributes("-disabled", False)

def upload_lzw_bin():
    def updateProgress(value, algorithm):
        # Update progress bar and percentage label
        progress.set(value)
        percentage_label.configure(text=f"{value}% - {algorithm}")
        app.update_idletasks()  # Ensure the UI updates


    # Start the process of file upload and decompression
    file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])

    if file_path:
        file_name = os.path.basename(file_path)

        expected_file_name = "lzw_compressed_image.bin"

        if file_name == expected_file_name:
            # Update the file label with the valid file name
            file_label2.configure(text=f"{file_name}", text_color="black")

            modal_window = ctk.CTkToplevel(app)
            modal_window.geometry("400x100")
            modal_window.title("Decompression Progress")

            # Center the modal window on the screen
            window_width = 400
            window_height = 100
            screen_width = app.winfo_screenwidth()
            screen_height = app.winfo_screenheight()

            # Calculate the position to center the modal window
            position_top = int(screen_height / 2 - window_height / 2)
            position_left = int(screen_width / 2 - window_width / 2)

            # Set the position of the modal window
            modal_window.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

            # Make sure modal window stays on top and grabs focus
            modal_window.grab_set()  # Grabs all events for the modal window
            modal_window.lift()      # Brings the modal window to the front
            modal_window.focus_set() # Ensures modal has focus

            # Create a label for loading status
            label = ctk.CTkLabel(modal_window, text="Decompressing, please wait...")
            label.pack(pady=10)

            # Create a Progressbar widget using CustomTkinter
            progress = ctk.CTkProgressBar(modal_window, width=300, mode="determinate")
            progress.pack(pady=10)

            # Create a label to show the percentage of progress and the current algorithm
            percentage_label = ctk.CTkLabel(modal_window, text="0% - LZW")
            percentage_label.pack(pady=5)

            # Disable the main window (to mimic modal behavior)
            app.attributes("-disabled", True)

            # Simulate decompression and update progress (replace with actual decompression logic)
            def simulate_decompression():
                for i in range(101):
                    updateProgress(i * 1, "LZW")  # Update progress during simulation
                    time.sleep(0.2)  # Simulate work

                lzwDecompressNoCallBack()

                # Show the completion message and close the modal
                messagebox.showinfo("Decompression Complete", "The image has been successfully decompressed!")
                modal_window.destroy()
                updateDecompressButtonState()

            # Start the decompression process in a separate thread to avoid freezing the GUI
            threading.Thread(target=simulate_decompression, daemon=True).start()
        else:
            # Show an error message if the file name doesn't match
            file_label2.configure(text=f"Wrong file! Please upload '{expected_file_name}'.", text_color="red")
            modal_window.destroy()  # Close the modal window immediately

    # Enable the main window again once process completes
    app.attributes("-disabled", False)

def upload_huffmanlzw_bin():
    def updateProgress(value, algorithm):
        # Update progress bar and percentage label
        progress.set(value)
        percentage_label.configure(text=f"{value}% - {algorithm}")
        app.update_idletasks()  # Ensure the UI updates


    # Start the process of file upload and decompression
    file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])

    if file_path:
        file_name = os.path.basename(file_path)

        expected_file_name = "huffman_lzw_compressed_image.bin"

        if file_name == expected_file_name:
            # Update the file label with the valid file name
            file_label3.configure(text=f"{file_name}", text_color="black")

            modal_window = ctk.CTkToplevel(app)
            modal_window.geometry("400x100")
            modal_window.title("Decompression Progress")

            # Center the modal window on the screen
            window_width = 400
            window_height = 100
            screen_width = app.winfo_screenwidth()
            screen_height = app.winfo_screenheight()

            # Calculate the position to center the modal window
            position_top = int(screen_height / 2 - window_height / 2)
            position_left = int(screen_width / 2 - window_width / 2)

            # Set the position of the modal window
            modal_window.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

            # Make sure modal window stays on top and grabs focus
            modal_window.grab_set()  # Grabs all events for the modal window
            modal_window.lift()      # Brings the modal window to the front
            modal_window.focus_set() # Ensures modal has focus

            # Create a label for loading status
            label = ctk.CTkLabel(modal_window, text="Decompressing, please wait...")
            label.pack(pady=10)

            # Create a Progressbar widget using CustomTkinter
            progress = ctk.CTkProgressBar(modal_window, width=300, mode="determinate")
            progress.pack(pady=10)

            # Create a label to show the percentage of progress and the current algorithm
            percentage_label = ctk.CTkLabel(modal_window, text="0% - Huffman-LZW")
            percentage_label.pack(pady=5)

            # Disable the main window (to mimic modal behavior)
            app.attributes("-disabled", True)

            # Simulate decompression and update progress (replace with actual decompression logic)
            def simulate_decompression():
                # Only call huffmanDecompress when the file is successfully uploaded
                    # Only call huffmanDecompress when the file is successfully uploaded
                for i in range(101):
                    updateProgress(i * 1, "Huffman-LZW")  # Update progress during simulation
                    time.sleep(0.2)  # Simulate work

                # Call huffmanDecompress only after simulation loop finishes, no redundant progress update
                huffmanLZWDecompressNoCallBack()

                # Show the completion message and close the modal
                messagebox.showinfo("Decompression Complete", "The image has been successfully decompressed!")
                modal_window.destroy()
                updateDecompressButtonState()

            # Start the decompression process in a separate thread to avoid freezing the GUI
            threading.Thread(target=simulate_decompression, daemon=True).start()
        else:
            # Show an error message if the file name doesn't match
            file_label3.configure(text=f"Wrong file! Please upload '{expected_file_name}'.", text_color="red")
            modal_window.destroy()  # Close the modal window immediately

    # Enable the main window again once process completes
    app.attributes("-disabled", False)

def upload_modified_bin():
    def updateProgress(value, algorithm):
        # Update progress bar and percentage label
        progress.set(value)
        percentage_label.configure(text=f"{value}% - {algorithm}")
        app.update_idletasks()  # Ensure the UI updates


    # Start the process of file upload and decompression
    file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])

    if file_path:
        file_name = os.path.basename(file_path)

        expected_file_name = "modified_compressed_image.bin"

        if file_name == expected_file_name:
            # Update the file label with the valid file name
            file_label4.configure(text=f"{file_name}", text_color="black")

            modal_window = ctk.CTkToplevel(app)
            modal_window.geometry("400x100")
            modal_window.title("Decompression Progress")

            # Center the modal window on the screen
            window_width = 400
            window_height = 100
            screen_width = app.winfo_screenwidth()
            screen_height = app.winfo_screenheight()

            # Calculate the position to center the modal window
            position_top = int(screen_height / 2 - window_height / 2)
            position_left = int(screen_width / 2 - window_width / 2)

            # Set the position of the modal window
            modal_window.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

            # Make sure modal window stays on top and grabs focus
            modal_window.grab_set()  # Grabs all events for the modal window
            modal_window.lift()      # Brings the modal window to the front
            modal_window.focus_set() # Ensures modal has focus

            # Create a label for loading status
            label = ctk.CTkLabel(modal_window, text="Decompressing, please wait...")
            label.pack(pady=10)

            # Create a Progressbar widget using CustomTkinter
            progress = ctk.CTkProgressBar(modal_window, width=300, mode="determinate")
            progress.pack(pady=10)

            # Create a label to show the percentage of progress and the current algorithm
            percentage_label = ctk.CTkLabel(modal_window, text="0% - Modified")
            percentage_label.pack(pady=5)

            # Disable the main window (to mimic modal behavior)
            app.attributes("-disabled", True)

            # Simulate decompression and update progress (replace with actual decompression logic)
            def simulate_decompression():
                # Only call huffmanDecompress when the file is successfully uploaded
                    # Only call huffmanDecompress when the file is successfully uploaded
                for i in range(101):
                    updateProgress(i * 1, "Modified")  # Update progress during simulation
                    time.sleep(0.2)  # Simulate work

                # Call huffmanDecompress only after simulation loop finishes, no redundant progress update
                modifiedDecompressNoCallBack()

                # Show the completion message and close the modal
                messagebox.showinfo("Decompression Complete", "The image has been successfully decompressed!")
                modal_window.destroy()
                updateDecompressButtonState()

            # Start the decompression process in a separate thread to avoid freezing the GUI
            threading.Thread(target=simulate_decompression, daemon=True).start()
        else:
            # Show an error message if the file name doesn't match
            file_label4.configure(text=f"Wrong file! Please upload '{expected_file_name}'.", text_color="red")
            modal_window.destroy()  # Close the modal window immediately

    # Enable the main window again once process completes
    app.attributes("-disabled", False)
    
   
def compressImage(app):
    def updateProgress(value, algorithm):
        progress.set(value)  # Set the value of the progress bar
        percentage_label.configure(text=f"{value}% - {algorithm}")  # Update the percentage label to show the algorithm
        app.update_idletasks()

    # Create a new top-level window to act as a modal
    modal_window = ctk.CTkToplevel(app)
    modal_window.geometry("400x100")
    modal_window.title("Compression Progress")

    # Center the modal window on the screen
    window_width = 400
    window_height = 100
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()

    # Calculate the position to center the modal window
    position_top = int(screen_height / 2 - window_height / 2)
    position_left = int(screen_width / 2 - window_width / 2)

    # Set the position of the modal window
    modal_window.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

    # Create a label for loading status
    label = ctk.CTkLabel(modal_window, text="Compressing, please wait...")
    label.pack(pady=10)

    # Create a Progressbar widget using CustomTkinter
    progress = ctk.CTkProgressBar(modal_window, width=300, mode="determinate")
    progress.pack(pady=10)

    # Create a label to show the percentage of progress and the current algorithm
    percentage_label = ctk.CTkLabel(modal_window, text="0% - Huffman")
    percentage_label.pack(pady=5)

    # Disable the main window (to mimic modal behavior)
    app.attributes("-disabled", True)

    # Function to run the compression in a separate thread
    def compress():
        huffmanCompress(updateProgress)
        lzwCompress(updateProgress)
        huffmanLZWCompress(updateProgress)
        modifiedCompress(updateProgress)
        
        # Once done, show a message and close the modal
        messagebox.showinfo("Compression Complete", "The image has been successfully compressed!")
        modal_window.destroy()
        updateDecompressButtonState()
        
        # Enable the main window again
        app.attributes("-disabled", False)

    # Start the compression in a separate thread
    threading.Thread(target=compress, daemon=True).start()

def decompressImage(app):
    def updateProgress(value, algorithm):
        progress.set(value)  # Set the value of the progress bar
        percentage_label.configure(text=f"{value}% - {algorithm}")  # Update the percentage label to show the algorithm
        app.update_idletasks()

    # Create a new top-level window to act as a modal
    modal_window = ctk.CTkToplevel(app)
    modal_window.geometry("400x100")
    modal_window.title("Decompression Progress")

    # Center the modal window on the screen
    window_width = 400
    window_height = 100
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()

    # Calculate the position to center the modal window
    position_top = int(screen_height / 2 - window_height / 2)
    position_left = int(screen_width / 2 - window_width / 2)

    # Set the position of the modal window
    modal_window.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

    # Create a label for loading status
    label = ctk.CTkLabel(modal_window, text="Decompressing, please wait...")
    label.pack(pady=10)

    # Create a Progressbar widget using CustomTkinter
    progress = ctk.CTkProgressBar(modal_window, width=300, mode="determinate")
    progress.pack(pady=10)

    # Create a label to show the percentage of progress and the current algorithm
    percentage_label = ctk.CTkLabel(modal_window, text="0% - Huffman")
    percentage_label.pack(pady=5)

    # Disable the main window (to mimic modal behavior)
    app.attributes("-disabled", True)

    # Function to run the compression in a separate thread
    def decompress():
        huffmanDecompress(updateProgress)
        lzwDecompress(updateProgress)
        huffmanLZWDecompress(updateProgress)
        modifiedDecompress(updateProgress)
        
        # Once done, show a message and close the modal
        messagebox.showinfo("Decompression Complete", "The image has been successfully compressed!")
        modal_window.destroy()
        
        # Enable the main window again
        app.attributes("-disabled", False)

    # Start the compression in a separate thread
    threading.Thread(target=decompress, daemon=True).start()
    

def clear_image():
    python = sys.executable
    subprocess.Popen([python, sys.argv[0]])  # Restart the app
    sys.exit()  # Close the current instance of the app


#endregion



#region --------------- Main Window -----------------------
app = ctk.CTk()  
app.title("Image Compression and Decompression")
app.geometry("1280x750")

title_font = ctk.CTkFont(family="Anonymous Pro", size=30, weight="bold")
text_font = ctk.CTkFont(family="Anonymous Pro", size=15, weight="normal")
text_font_1 = ctk.CTkFont(family="Anonymous Pro", size=15, weight="normal")
button_font = ctk.CTkFont(family="Anonymous Pro", size=20, weight="normal")
header_font = ctk.CTkFont(family="Anonymous Pro", size=20, weight="bold")

# Get screen width and height
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

# Calculate position to center the window
x_position = (screen_width // 2) - (1280 // 2)
y_position = (screen_height // 2) - (750 // 2)

# Set window position
app.geometry(f"1280x750+{x_position}+{y_position}")
#endregion

app.columnconfigure(0, weight=1)
app.columnconfigure(1, weight=11)
app.rowconfigure(0, weight=1) 
app.rowconfigure(1, weight=11) 

#region -------------------Title -----------------------------
title = ctk.CTkLabel(master=app, text="Image Compression and Decompression", font=title_font)
title.grid(row=0, column=0, columnspan=6, pady=2, padx=2, sticky=ctk.NSEW)
#endregion

#region ---------------First Frame UI ------------------------------
firstFrame = ctk.CTkFrame(master=app)
firstFrame.grid(row=1, column=0, pady=5, padx=5, sticky=ctk.NSEW)

firstFrame.rowconfigure(0, weight=1)
firstFrame.rowconfigure(1, weight=1)
firstFrame.columnconfigure(0, weight=1) 

# Image Holder Frame
mainImageHolderFrame = ctk.CTkFrame(firstFrame, fg_color='transparent')
mainImageHolderFrame.grid(row=0, column=0, pady=5, padx=5, sticky=ctk.N)

# Image widget
mainImageHolder = ctk.CTkImage(light_image=Image.open("assets/placeholder_image.jpg"),
                        dark_image=Image.open("assets/placeholder_image.jpg"),
                        size=(250, 250))
mainImageHolderWidget = ctk.CTkLabel(mainImageHolderFrame, image=mainImageHolder, text="")
mainImageHolderWidget.pack(pady=(45,5), padx=5)

# Textbox 
mainImageHolderTextBox = ctk.CTkTextbox(mainImageHolderFrame, width=250, height=100, font=text_font, wrap="word")
mainImageHolderTextBox.pack(pady=5, padx=5)
mainImageHolderTextBox.configure(state="disabled")
mainImageHolderTextBox.bind("<Enter>", lambda e: mainImageHolderTextBox.configure(cursor="hand2"))  # Change cursor on hover

# Button Frame
buttonFrame = ctk.CTkFrame(mainImageHolderFrame)
buttonFrame.pack(pady=(20, 5), padx=5)  

# Select Image Button
selectImageButton = ctk.CTkButton(buttonFrame, width=200, height=40, corner_radius=5,
                                text="Select Image", font=button_font, 
                                command=upload_image)
selectImageButton.pack(pady=10, padx=5)

# Compress Button
compressButton = ctk.CTkButton(buttonFrame, width=200, height=40, corner_radius=5,
                                text="Compress", font=button_font, 
                                command=lambda: compressImage(app))
compressButton.pack(pady=10, padx=5)
compressButton.configure(state="disabled")

# Decompress Button
decompressButton = ctk.CTkButton(buttonFrame, width=200, height=40, corner_radius=5,
                                text="Decompress", font=button_font, 
                                command=modalDecompress)
decompressButton.pack(pady=10, padx=5)
decompressButton.configure(state="disabled")

# Clear Button
clearButton = ctk.CTkButton(buttonFrame, width=200, height=40, corner_radius=5,
                                text="Clear", font=button_font, 
                                command=clear_image)
clearButton.pack(pady=10, padx=5)
#endregion




#region ----------------Second Frame ---------------
secondFrame = ctk.CTkFrame(master=app)
secondFrame.grid(row=1, column=1, pady=5, padx=5, sticky=ctk.NSEW)


# Configure secondFrame for images
secondFrame.rowconfigure(0, weight=0)  # First row for images
secondFrame.rowconfigure(1, weight=0)  # Second row for label
secondFrame.rowconfigure(2, weight=0)  # Third row for table header
secondFrame.rowconfigure(3, weight=0)  # Fourth row for Compressed Size Row
secondFrame.rowconfigure(4, weight=0)  # Fifth row for Compressed Ratio Row
secondFrame.rowconfigure(5, weight=0)  # Sixth row for Compressed Time Row
secondFrame.rowconfigure(6, weight=0)  # Seventh row for Decompressed Title
secondFrame.rowconfigure(7, weight=0)  # Eigth row for Decompressed Header
secondFrame.rowconfigure(8, weight=0)  # Ninth row for Decompressed PSNR
secondFrame.rowconfigure(9, weight=0)  # Tenth row for Decompressed PSNR
secondFrame.columnconfigure((0, 1, 2, 3), weight=1)  # Four columns for images

# Load the single placeholder image
placeholder_img = ctk.CTkImage(light_image=Image.open("assets/placeholder_image.jpg"),
                               dark_image=Image.open("assets/placeholder_image.jpg"),
                               size=(250, 250))

# Create individual image labels
img_label1 = ctk.CTkLabel(secondFrame, image=placeholder_img, text="")
img_label1.grid(row=0, column=0, pady=(45, 0), padx=20, sticky=ctk.N)
file_label1 = ctk.CTkLabel(secondFrame, text="", font=text_font_1, width=200, height=25, wraplength=250)
file_label1.grid(row=0, column=0, padx=0, pady=(10, 0), sticky="n")

img_label2 = ctk.CTkLabel(secondFrame, image=placeholder_img, text="")
img_label2.grid(row=0, column=1, pady=(45, 0), padx=20, sticky=ctk.N)
file_label2 = ctk.CTkLabel(secondFrame, text="", font=text_font_1, width=200, height=25, wraplength=250)
file_label2.grid(row=0, column=1, padx=0, pady=(10, 0), sticky="n")

img_label3 = ctk.CTkLabel(secondFrame, image=placeholder_img, text="")
img_label3.grid(row=0, column=2, pady=(45, 0), padx=20, sticky=ctk.N)
file_label3 = ctk.CTkLabel(secondFrame, text="", font=text_font_1, width=200, height=25, wraplength=250)
file_label3.grid(row=0, column=2, padx=0, pady=(10, 0), sticky="n")

img_label4 = ctk.CTkLabel(secondFrame, image=placeholder_img, text="")
img_label4.grid(row=0, column=3, pady=(45, 0), padx=20, sticky=ctk.N)
file_label4 = ctk.CTkLabel(secondFrame, text="", font=text_font_1, width=200, height=25, wraplength=250)
file_label4.grid(row=0, column=3, padx=0, pady=(10, 0), sticky="n")

def overlay_button_on(label, button_text, command=None):
    parent = label.master
    button = ctk.CTkButton(parent, text=button_text, command=command)
    button.place(in_=label, relx=0.5, rely=0.5, anchor="center")
    return button

btn1 = overlay_button_on(img_label1, "Upload bin file", upload_huffman_bin)
btn1.place_forget()

btn2 = overlay_button_on(img_label2, "Upload bin file", upload_lzw_bin)
btn2.place_forget()

btn3 = overlay_button_on(img_label3, "Upload bin file", upload_huffmanlzw_bin)
btn3.place_forget()

btn4 = overlay_button_on(img_label4, "Upload bin file", upload_modified_bin)
btn4.place_forget()
    

# Add "Compression Result" label below the images using grid
compressionResultLabel = ctk.CTkLabel(secondFrame, text="Compression Result", font=header_font)
compressionResultLabel.grid(row=1, column=0, columnspan=4, pady=(10, 5), padx=15, sticky=ctk.NW)

# Ensure secondFrame has 5 equally distributed columns
secondFrame.columnconfigure((0, 1, 2, 3, 4), weight=1)

# Compression Header Frame
compressionHeaderFrame = ctk.CTkFrame(secondFrame, height=40, fg_color="#4aaeef")  # Adjust height
compressionHeaderFrame.grid(row=2, column=0, columnspan=5, pady=(0, 5), padx=15, sticky=ctk.EW)  # Fix columnspan
compressionHeaderFrame.grid_propagate(False) 

# Configure the header frame to have five columns
compressionHeaderFrame.columnconfigure((0, 1, 2, 3, 4), weight=1)

metricAlgorithmHeader = ctk.CTkLabel(compressionHeaderFrame, text="Metric/Algorithm", font=header_font, anchor="center", justify="center")
metricAlgorithmHeader.grid(row=0, column=0, padx=5, pady=5, sticky=ctk.NSEW)

huffmanHeader = ctk.CTkLabel(compressionHeaderFrame, text="Huffman", font=header_font, anchor="center", justify="center")
huffmanHeader.grid(row=0, column=1, padx=(15, 5), pady=5, sticky=ctk.NSEW)

lzwHeader = ctk.CTkLabel(compressionHeaderFrame, text="LZW", font=header_font, anchor="center", justify="center")
lzwHeader.grid(row=0, column=2, padx=(30, 5), pady=5, sticky=ctk.NSEW)

huffmanLzwHeader = ctk.CTkLabel(compressionHeaderFrame, text="Huffman-LZW", font=header_font, anchor="center", justify="center")
huffmanLzwHeader.grid(row=0, column=3, padx=5, pady=5, sticky=ctk.NSEW)

modifiedHeader = ctk.CTkLabel(compressionHeaderFrame, text="Modified", font=header_font, anchor="center", justify="center")
modifiedHeader.grid(row=0, column=4, padx=5, pady=5, sticky=ctk.NSEW)


# Compressed Size Frame
compressedSizeFrame = ctk.CTkFrame(secondFrame, height=40, fg_color="#9fd9ff")  # Adjust height
compressedSizeFrame.grid(row=3, column=0, columnspan=5, pady=(0, 5), padx=15, sticky=ctk.EW)  # Fix columnspan
compressedSizeFrame.grid_propagate(False) 

compressedSizeFrame.columnconfigure((0, 1, 2, 3, 4), weight=1)

compressedSizeLabel = ctk.CTkLabel(compressedSizeFrame, text="Compressed Size (KB)", font=text_font, anchor="center", justify="center", width=120)
compressedSizeLabel.grid(row=0, column=0, padx=(20,5), pady=5, sticky=ctk.W)

huffmanSizeLabel = ctk.CTkLabel(compressedSizeFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
huffmanSizeLabel.grid(row=0, column=1, padx=(65,5), pady=5, sticky=ctk.W)

lzwSizeLabel = ctk.CTkLabel(compressedSizeFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
lzwSizeLabel.grid(row=0, column=2, padx=5, pady=5, sticky=ctk.W)

huffmanLzwSizeLabel = ctk.CTkLabel(compressedSizeFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
huffmanLzwSizeLabel.grid(row=0, column=3, padx=5, pady=5, sticky=ctk.W)

modifiedSizeLabel = ctk.CTkLabel(compressedSizeFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
modifiedSizeLabel.grid(row=0, column=4, padx=5, pady=5, sticky=ctk.EW)

# Compressed Ratio Frame
compressedRatioFrame = ctk.CTkFrame(secondFrame, height=40, fg_color="#4aaeef")  # Adjust height
compressedRatioFrame.grid(row=4, column=0, columnspan=5, pady=(0, 5), padx=15, sticky=ctk.EW)  # Fix columnspan
compressedRatioFrame.grid_propagate(False) 

compressedRatioFrame.columnconfigure((0, 1, 2, 3, 4), weight=1)

compressedRatioLabel = ctk.CTkLabel(compressedRatioFrame, text="Compressed Ratio", font=text_font, anchor="center", justify="center", width=120)
compressedRatioLabel.grid(row=0, column=0, padx=(20,5), pady=5, sticky=ctk.W)

huffmanRatioLabel = ctk.CTkLabel(compressedRatioFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
huffmanRatioLabel.grid(row=0, column=1, padx=(95,5), pady=5, sticky=ctk.W)

lzwRatioLabel = ctk.CTkLabel(compressedRatioFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
lzwRatioLabel.grid(row=0, column=2, padx=5, pady=5, sticky=ctk.W)

huffmanLzwRatioLabel = ctk.CTkLabel(compressedRatioFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
huffmanLzwRatioLabel.grid(row=0, column=3, padx=5, pady=5, sticky=ctk.W)

modifiedRatioLabel = ctk.CTkLabel(compressedRatioFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
modifiedRatioLabel.grid(row=0, column=4, padx=5, pady=5, sticky=ctk.EW)

# Compressed Time Frame
compressedTimeFrame = ctk.CTkFrame(secondFrame, height=40, fg_color="#9fd9ff")  # Adjust height
compressedTimeFrame.grid(row=5, column=0, columnspan=5, pady=(0, 5), padx=15, sticky=ctk.EW)  # Fix columnspan
compressedTimeFrame.grid_propagate(False) 

compressedTimeFrame.columnconfigure((0, 1, 2, 3, 4), weight=1)

compressedTimeLabel = ctk.CTkLabel(compressedTimeFrame, text="Compression Time (ms)", font=text_font, anchor="center", justify="center", width=120)
compressedTimeLabel.grid(row=0, column=0, padx=(20,5), pady=5, sticky=ctk.W)

huffmanTimeLabel = ctk.CTkLabel(compressedTimeFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
huffmanTimeLabel.grid(row=0, column=1, padx=(55,5), pady=5, sticky=ctk.W)

lzwTimeLabel = ctk.CTkLabel(compressedTimeFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
lzwTimeLabel.grid(row=0, column=2, padx=5, pady=5, sticky=ctk.W)

huffmanLzwTimeLabel = ctk.CTkLabel(compressedTimeFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
huffmanLzwTimeLabel.grid(row=0, column=3, padx=5, pady=5, sticky=ctk.W)

modifiedTimeLabel = ctk.CTkLabel(compressedTimeFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
modifiedTimeLabel.grid(row=0, column=4, padx=5, pady=5, sticky=ctk.EW)

#Decompression Label Title
decompressionResultLabel = ctk.CTkLabel(secondFrame, text="Decompression Result", font=header_font)
decompressionResultLabel.grid(row=6, column=0, columnspan=4, pady=(10, 5), padx=15, sticky=ctk.NW)

# Compression Header Frame
decompressionHeaderFrame = ctk.CTkFrame(secondFrame, height=40, fg_color="#4aaeef")  # Adjust height
decompressionHeaderFrame.grid(row=7, column=0, columnspan=5, pady=(0, 5), padx=15, sticky=ctk.EW)  # Fix columnspan
decompressionHeaderFrame.grid_propagate(False) 

# Configure the header frame to have five columns
decompressionHeaderFrame.columnconfigure((0, 1, 2, 3, 4), weight=1)

metricAlgorithmHeader2 = ctk.CTkLabel(decompressionHeaderFrame, text="Metric/Algorithm", font=header_font, anchor="center", justify="center")
metricAlgorithmHeader2.grid(row=0, column=0, padx=5, pady=5, sticky=ctk.NSEW)

huffmanHeader2 = ctk.CTkLabel(decompressionHeaderFrame, text="Huffman", font=header_font, anchor="center", justify="center")
huffmanHeader2.grid(row=0, column=1, padx=(15, 5), pady=5, sticky=ctk.NSEW)

lzwHeader2 = ctk.CTkLabel(decompressionHeaderFrame, text="LZW", font=header_font, anchor="center", justify="center")
lzwHeader2.grid(row=0, column=2, padx=(30, 5), pady=5, sticky=ctk.NSEW)

huffmanLzwHeader2 = ctk.CTkLabel(decompressionHeaderFrame, text="Huffman-LZW", font=header_font, anchor="center", justify="center")
huffmanLzwHeader2.grid(row=0, column=3, padx=5, pady=5, sticky=ctk.NSEW)

modifiedHeader2 = ctk.CTkLabel(decompressionHeaderFrame, text="Modified", font=header_font, anchor="center", justify="center")
modifiedHeader2.grid(row=0, column=4, padx=5, pady=5, sticky=ctk.NSEW)

# Compressed Size Frame
psnrFrame = ctk.CTkFrame(secondFrame, height=40, fg_color="#9fd9ff")  # Adjust height
psnrFrame.grid(row=8, column=0, columnspan=5, pady=(0, 5), padx=15, sticky=ctk.EW)  # Fix columnspan
psnrFrame.grid_propagate(False) 

psnrFrame.columnconfigure((0, 1, 2, 3, 4), weight=1)

psnrLabel = ctk.CTkLabel(psnrFrame, text="PSNR (dB)", font=text_font, anchor="center", justify="center", width=120)
psnrLabel.grid(row=0, column=0, padx=(0,5), pady=5, sticky=ctk.W)

huffmanPSNRLabel = ctk.CTkLabel(psnrFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
huffmanPSNRLabel.grid(row=0, column=1, padx=(125,5), pady=5, sticky=ctk.W)

lzwPSNRLabel = ctk.CTkLabel(psnrFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
lzwPSNRLabel.grid(row=0, column=2, padx=5, pady=5, sticky=ctk.W)

huffmanLzwPSNRLabel = ctk.CTkLabel(psnrFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
huffmanLzwPSNRLabel.grid(row=0, column=3, padx=5, pady=5, sticky=ctk.W)

modifiedPSNRLabel = ctk.CTkLabel(psnrFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
modifiedPSNRLabel.grid(row=0, column=4, padx=5, pady=5, sticky=ctk.EW)


# Decompressed Time Frame
decompressedTimeFrame = ctk.CTkFrame(secondFrame, height=40, fg_color="#4aaeef")  # Adjust height
decompressedTimeFrame.grid(row=9, column=0, columnspan=5, pady=(0, 5), padx=15, sticky=ctk.EW)  # Fix columnspan
decompressedTimeFrame.grid_propagate(False) 

decompressedTimeFrame.columnconfigure((0, 1, 2, 3, 4), weight=1)

decompressedTimeLabel = ctk.CTkLabel(decompressedTimeFrame, text="Decompression Time (ms)", font=text_font, anchor="center", justify="center", width=120)
decompressedTimeLabel.grid(row=0, column=0, padx=(20,5), pady=5, sticky=ctk.W)

huffmanDecompressedTimeLabel = ctk.CTkLabel(decompressedTimeFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
huffmanDecompressedTimeLabel.grid(row=0, column=1, padx=(40,5), pady=5, sticky=ctk.W)

lzwDecompressedTimeLabel = ctk.CTkLabel(decompressedTimeFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
lzwDecompressedTimeLabel.grid(row=0, column=2, padx=5, pady=5, sticky=ctk.W)

huffmanLzwDecompressedTimeLabel = ctk.CTkLabel(decompressedTimeFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
huffmanLzwDecompressedTimeLabel.grid(row=0, column=3, padx=5, pady=5, sticky=ctk.W)

modifiedDecompressedTimeLabel = ctk.CTkLabel(decompressedTimeFrame, text="0.0", font=text_font, anchor="center", justify="center", width=120)
modifiedDecompressedTimeLabel.grid(row=0, column=4, padx=5, pady=5, sticky=ctk.EW)

#endregion


app.mainloop()