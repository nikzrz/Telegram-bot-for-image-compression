import os
import subprocess
from PIL import Image
from collections import Counter
from telegram.ext import Updater, MessageHandler, Filters

class Node:
    def __init__(self, val, freq):
        self.val = val
        self.freq = freq
        self.left = None
        self.right = None

def preprocessing(image_path):
    image = Image.open(image_path)
    image = image.convert('L')  # convert to grayscale
    image = image.resize((256,256), Image.ANTIALIAS) #resize image to reduce size
    image.save(image_path)

def compress(image_path):
    # Read the image
    with open(image_path, 'rb') as img:
        image_data = img.read()

    # Count the frequency of each byte in the image
    freq = Counter(image_data)

    # Create a list of nodes for the Huffman tree
    nodes = [Node(val, freq) for val, freq in freq.items()]

    # Build the Huffman tree
    while len(nodes) > 1:
        nodes.sort(key=lambda x: x.freq)
        left = nodes.pop(0)
        right = nodes.pop(0)
        parent = Node(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        nodes.append(parent)

    # Build the code table from the Huffman tree
    codes = {}
    def build_code(node, code):
        if node.val is not None:
            codes[node.val] = code
            return
        build_code(node.left, code + '0')
        build_code(node.right, code + '1')
    build_code(nodes[0], '')

    # Compress the image data using the code table
    compressed_data = ''.join([codes[b] for b in image_data])

    # Save the compressed data to a file
    with open('compressed.bin', 'wb') as f:
        f.write(int(compressed_data, 2).to_bytes((len(compressed_data) + 7) // 8, byteorder='big'))

def handle_image(bot, update):
    file_id = update.message.photo[-1].file_id
    newFile = bot.get_file(file_id)
    newFile.download('temp.jpg')
    preprocessing('temp.jpg')
    compress('temp.jpg')
    bot.send_document(chat_id=update.message.chat_id, document=open('compressed.bin', 'rb'))
    os.remove('temp.jpg')
    os.remove('compressed.bin')

def main():
    updater = Updater(YOUR_TOKEN) # Replace YOUR_TOKEN with your bot's token
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.photo, handle_image))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

