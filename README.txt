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
-