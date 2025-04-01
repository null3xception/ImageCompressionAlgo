import tkinter as tk
import customtkinter as ctk
from PIL import Image
from tkinter import filedialog
import os
import file_handling
import huffman_coding
import time
import tkinter.messagebox as messagebox
from lzw_coding import lzw_compress, lzw_decompress, calculate_psnr, load_uploaded_image, save_decompressed_image
import threading


ctk.set_appearance_mode("light")  
ctk.set_default_color_theme("dark-blue")  

compressed_image_bit_string = None
image_bit_string = None

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

def lzwDecompress(progress_callback, compressed_data, original_image):
    
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
    
    return decompressed_image

#endregion


#region ----------- Functions -------------------------
def upload_image():
    global uploadedImagePath
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
    
    if file_path:  # Check if a file is selected
        uploadedImagePath = file_path
        img = Image.open(file_path)

        # Update image holder
        new_image = ctk.CTkImage(light_image=img, dark_image=img, size=(250, 250))
        mainImageHolderWidget.configure(image=new_image)
        mainImageHolderWidget.image = new_image  # Prevent garbage collection

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


def compressImage(app):
    def updateProgress(value, algorithm):
        progress.set(value)  # Set the value of the progress bar
        percentage_label.configure(text=f"{value}% - {algorithm}")  # Update the percentage label to show the algorithm
        app.update_idletasks()

    # Create a new top-level window to act as a modal
    modal_window = ctk.CTkToplevel(app)
    modal_window.geometry("400x200")
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
        
        # Once done, show a message and close the modal
        messagebox.showinfo("Compression Complete", "The image has been successfully compressed!")
        modal_window.destroy()
        
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
    modal_window.geometry("400x200")
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
        compressed_data, original_image = lzwCompress(updateProgress)
        lzwDecompress(updateProgress, compressed_data, original_image)
        
        # Once done, show a message and close the modal
        messagebox.showinfo("Decompression Complete", "The image has been successfully compressed!")
        modal_window.destroy()
        
        # Enable the main window again
        app.attributes("-disabled", False)

    # Start the compression in a separate thread
    threading.Thread(target=decompress, daemon=True).start()
    

def clear_image():
    # Reset image holder to placeholder image
    placeholder_image = ctk.CTkImage(light_image=Image.open("assets/placeholder_image.jpg"),
                                     dark_image=Image.open("assets/placeholder_image.jpg"),
                                     size=(250, 250))
    mainImageHolderWidget.configure(image=placeholder_image)
    mainImageHolderWidget.image = placeholder_image  # Prevent garbage collection

    # Clear textbox content
    mainImageHolderTextBox.configure(state="normal")  # Enable editing
    mainImageHolderTextBox.delete("1.0", "end")  # Remove all text
    mainImageHolderTextBox.configure(state="disabled")  # Make read-only again


#endregion



#region --------------- Main Window -----------------------
app = ctk.CTk()  
app.title("System Name")
app.geometry("1280x720")

title_font = ctk.CTkFont(family="Anonymous Pro", size=30, weight="bold")
text_font = ctk.CTkFont(family="Anonymous Pro", size=15, weight="normal")
button_font = ctk.CTkFont(family="Anonymous Pro", size=20, weight="normal")
header_font = ctk.CTkFont(family="Anonymous Pro", size=20, weight="bold")

# Get screen width and height
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

# Calculate position to center the window
x_position = (screen_width // 2) - (1280 // 2)
y_position = (screen_height // 2) - (720 // 2)

# Set window position
app.geometry(f"1280x720+{x_position}+{y_position}")
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
mainImageHolderWidget.pack(pady=(20,5), padx=5)

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

# Decompress Button
decompressButton = ctk.CTkButton(buttonFrame, width=200, height=40, corner_radius=5,
                                text="Decompress", font=button_font, 
                                command=lambda: decompressImage(app))
decompressButton.pack(pady=10, padx=5)

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
img_label1.grid(row=0, column=0, pady=(25, 0), padx=20, sticky=ctk.N)

img_label2 = ctk.CTkLabel(secondFrame, image=placeholder_img, text="")
img_label2.grid(row=0, column=1, pady=(25, 0), padx=20, sticky=ctk.N)

img_label3 = ctk.CTkLabel(secondFrame, image=placeholder_img, text="")
img_label3.grid(row=0, column=2, pady=(25, 0), padx=20, sticky=ctk.N)

img_label4 = ctk.CTkLabel(secondFrame, image=placeholder_img, text="")
img_label4.grid(row=0, column=3, pady=(25, 0), padx=20, sticky=ctk.N)

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