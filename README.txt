For the installation, 
I assume you have downloaded the zip folder and extracted this on your computer as well.

First, create a virtual environment for the packages to be installed 
run this on your terminal,
python -m venv venv

After that, activate the virtual enviroment by
. venv/Scripts/activate

your terminal should have like this 
-(venv) PS D:\Projects\ImageCompressionAlgo

once you're on the virtual enviroment, run
pip install -r requirements.txt

once the packages are done installing, 
go to the gui.py and see if you can run the System there


#Finding while working on this Project
- Huffman really works well here and gives a good result
- LZW on the other hand, is kinda complicated at first because compressing the colored image using this algo requires you to 
generate separate compressed bin file because we are dealing with 3 channels, (R, G, B),
of course we can concatenate the channels as well and put it in one single folder but the only problem is that the current LZW coding
have trouble reading the concatenated bin file while decompressing, which is why I searched around the net and luckily, 
we could try converting it into grayscale so it could generate only one channel and the current LZW coding algorithm can read it and 
decompress, HENCE, the display is on grayscale
-Huffman-LZW is the difficult one, since our huffman is compressing a colored image, once we compress it again with LZW, our bytes or codes 
became complicated, think of it like we have combined the two codes on each compressing algo and concatenated it, the whole bytes became 
unreadable for the decompression algorithm of lzw or huffman, that is why the image you see it corrupted, also I have printed the errors as to
why it is corrupted, more invalid bytes and patterns (You'll see it for yourself once you start running it). Also, are you wondering why the 
compressed size is bigger than original image? It is because our image gone through 2 stages of compression, the huffman and the lzw and we 
have concatenated the bytes into one single file. 
-Modified, was the difficult one though, I had to alter some parts of the algo especially the LZW, so what I did is that I first compressed the image
to lzw, hoping that it would have a difference unlike the Huffman-LZW, so after I compressed using the LZW algo, I then compressed it again to 
huffman because from what I have searched, it is a better approach to use LZW before Huffman, so yah that's what I did. Lastly, the compression size 
here is the biggest because not just we combined the two compressed binary files into a single file, it is because our image is on a complete state 
as well unlike the Huffman-LZW which is corrupted or incomplete. Hence, we decompressed the image like how it used to but the only downside is that
it is not optimal for compressing into a smaller size. Recommendations for the research? Maybe if we could find a way to optimize the compression size
of our modified algorithm, then that would be good.  