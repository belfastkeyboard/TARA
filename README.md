# TARA
Text Analysis and Recognition Automation

TARA is a simple and lightweight text analysis program built to scan and spellcheck images and documents. 

# Features

- **Optical Character Recognition**
  - Powered by Google's Tesseract OCR.
  - Supports .jpg, .png, and .pdf filetypes.
- **Spellchecking**
  - Powered by SymSpell.
  - Supports .txt files.
- **User Interface**
  - Powered by PyQt5. 
  - Simple and easy to use graphical user interface.
- **Batch Processing**
  - Can handle multiple files.
  - Pass it a folder and it will work out how to process it on its own! 

# To Do:
- Additional settings provided
- Pickle dictionaries option (loads faster)
- Multi-threading for I/O operations
- Streamline process

# Build

Clone the repo
```
git clone https://github.com/belfastkeyboard/TARA
cd TARA
```

Run GNU make
```
make
```

# Use

See 'Help' in the menu.

Frequency dictionaries (standard, bigram) from SymSpell are provided.
It is recommended to build your own dictionary if the spellchecker is struggling.
