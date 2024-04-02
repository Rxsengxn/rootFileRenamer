#!/usr/bin/env python3
# -*- coding: utf-8 -*-

### From Kert K & Jako A

#from datetime import datetime
import cv2
import pytesseract
import numpy as np
from tkinter import Tk, Entry, Button, messagebox, Frame, Label
from tkinter.filedialog import askdirectory

import sys

from os import listdir, mkdir, name
from os.path import isfile, join, exists
import shutil
import re

# For disabling the askwindow "x" closing function
def disable_event():
   pass

# Main window
root = Tk()

root.protocol("WM_DELETE_WINDOW", disable_event)

root.withdraw()



entryField = Entry(root)

entryField.pack()

def Click(event=None):
    global correct, mfr
    mfr = entryField.get().upper()
    #print(f"input: {mfr}")
    entryField.delete(0, 'end')
    if mfr == "": 
        correct = ""
    else: 
        correct = True
    
    root.withdraw()

root.bind("<Return>", Click)
    
button = Button(root, text="Input correct symbols", command=Click)
button.pack()



### Definitions for asking the user for initial setup things
# Dialog box for asking about the output folder
askUserWindow = Tk()
askUserWindow.title("Choose an option")
# Adjust size
askUserWindow.geometry("400x120")
 
# set minimum window size value
askUserWindow.minsize(400, 150)
# Set protocol of closing this window
askUserWindow.protocol("WM_DELETE_WINDOW", disable_event)

askUserWindow.withdraw()

labelForText = Label(askUserWindow,
                    text='Use default ("output") folder for the output files?',
                    font = ("Arial", 18),
                    wraplength=350)
labelForText.pack(pady=20)

askFrame = Frame(askUserWindow)
askFrame.pack(pady=10)

# Buttons yes an no before the start of the main program
choose = ""
def Click_yes(event=None):
    global different_output, choose
    
    different_output = True
    choose = True
    labelForText.config(text="Continue where you left off?")
    
    askUserWindow.withdraw()


def Click_no(event=None):
    global different_output, choose
    
    different_output = False
    choose = True
    labelForText.config(text="Continue where you left off?")

    askUserWindow.withdraw()


button_yes = Button(askFrame, text="Yes", command=Click_no)
button_yes.pack(side="left", padx=(10, 100))

button_no = Button(askFrame, text="No", command=Click_yes)
button_no.pack(side="left", padx=(100, 10))





def symbol_integrity_check(symbol):
    '''
    Check for symbols and if they are correct.
    Expected: 1-2 numbers and a letter (A-D)
    
    :param symbol: symbol that the program interpreted
    :return: returns checked symbol
    '''
    
    if symbol != "":
        numbers = 0
        numberstart = 0
        numberstartb = True
        for iter, i in enumerate(symbol):
            if i.isnumeric():
                numbers += 1
                if numberstartb == True:
                    numberstart = iter
                    numberstartb = False
            if i.isalpha():
                if numbers < 1:
                    return None
                if numbers > 2:
                    numberstart = iter-2
                return symbol[numberstart:iter+1]
            
        # If the last character of the symbol is read as '8' and it's supposed to be 'B' 
        if symbol[-1].isnumeric() and int(symbol[-1]) == 8:
            s = list(symbol)
            s[-1] = 'B'
            symbol = "".join(s)
            return symbol
    return None

mfr = ""
correct = ""
skip = False

def search_for_symbols(frame):
    global mfr, correct, go_back, skip
    '''
    Searches a set of symbols from the input image.
    
    :param frame: input image (works better when already thresholded)
    :return: set of symbols it found from the picture
    '''
    
    correct = ""
    
    # Trained model searching for symbols from thresholded image
    symbols = pytesseract.image_to_string(frame,
                                        lang='eng',
                                        config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789ABCD').strip()
    
    # Check symbols integrity
    mfr = symbol_integrity_check(symbols)
    
    print(f"Result: {mfr}")

    # Show the picture to the user who then verifies the final symbols

    cv2.namedWindow('Input', cv2.WINDOW_NORMAL)
    cv2.putText(input_img,
                str(mfr),
                (len(input_img[0])//3, len(input_img)//10*7+10),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (0, 255, 0),
                4,
                cv2.LINE_AA)
    cv2.imshow("Input", input_img)
    
    # User input for what shoud happen next
    print("(y)es/correct, (n)o/wrong, go (b)ack, (s)kip this picture")
    while True:
        root.update()
        key = cv2.waitKey(1) & 0xFF
        if (key  == ord("y") and correct == ""):
            correct = True
            break
        
        if ((key  == ord("n") or mfr is None) and correct == ""):
            correct = False
            root.lift()
            root.deiconify()
            entryField.focus_set()
            
        if (key == ord("b")):
            go_back = True
            root.withdraw()
            break
        
        if correct == True:
            break
        
        if (key == ord("s")):
            skip = True
            root.withdraw()
            break
    
        # Check for if the window has been closed, the program should exit
        try:
            if cv2.getWindowProperty('Input', cv2.WND_PROP_VISIBLE) <= 0:
                quit_program()
        except cv2.error as e:
            messagebox.showerror("error", f"error: {e}")
            quit_program()

    cv2.destroyAllWindows()
    correct = ""

    if mfr == "":
        mfr = None
        
    return mfr


def path_to_files():
    '''
    Takes in the path and finds all pictures from this folder and puts them into a list to return.
    
    :return: list of pictures from the path given to the program beforehand.
    '''
    onlyfiles = [f for f in listdir(path) if (isfile(join(path, f)) and (f.endswith('.jpg') or f.endswith('.png')))]
    print(onlyfiles)
    return onlyfiles

def main_loop(list_failidest, progress:list):
    global input_img, skip
    '''
    Here happens the main loop of the program.
    
    :param list_failidest: list of files to be processed
    :param progress: list of the already progressed pictures previous session. 
    Read once before the program start from a specified file.
    '''

    cv2.namedWindow('Input', cv2.WINDOW_NORMAL)
    
    # Handle a picture at a time from the list given with the parameter to this function.
    for juurepilt in moveGenerator(list_failidest):
        if juurepilt.endswith('.jpg') or juurepilt.endswith('.png'):
            # If using the progress, skip the ones already processed.
            if len(progress) > 0:
                if juurepilt in progress:
                    progress.remove(juurepilt)
                    continue
            
            number = None
            file = join(path, juurepilt)
            
            # Outputting the file currently processing
            print(file)
            input_img = cv2.imread(file)
            
            # Cropping the image so we only deal with the part of the picture where the label is located.
            input_img = input_img[int(len(input_img)/10*8):, int(len(input_img[0])/10*7):]
            
            # Adding some image manipulation for easier detection.
            blurred = cv2.blur(input_img, (13,13))
    
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

            mask = cv2.inRange(hsv,np.array([92,118,152]),np.array([152,255,255]))

            cnts,_ = cv2.findContours(mask, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

            rects = []
            for cnt in cnts:
                rect = cv2.boundingRect(cnt)
                rects.append(rect)
                
            rects = sorted(rects, key=lambda x: x[2]*x[3], reverse=True)
            if rects:
                x,y,w,h = rects[0]
                
                cv2.rectangle(input_img,(x,y),(x+w,y+h),(0,0,255),2)
                #saast = cv2.resize(saast, (1008, 756))
                #cv2.imshow("Input", saast)
                #cv2.imshow("mask", mask)

                cropped_input = input_img[y+20:y+h-20, x+20:x+w-20]

                #mask = mask[y:y+h, x:x+w]
                #input = cv2.dilate(mask, np.ones((10,10)), iterations=1)

                input = cv2.blur(cropped_input, (5,5))
                _, input = cv2.threshold(input,np.mean(input),255,cv2.THRESH_BINARY_INV)
                input = cv2.dilate(input, np.ones((9,9)), iterations=1)
                input= cv2.copyMakeBorder(input,10,10,10,10,cv2.BORDER_CONSTANT,value=(0, 0, 255))

                number = search_for_symbols(input)
                
            # If there were no BLUE rectangle detected.
            else:
                cv2.imshow("Input", input_img)
                cv2.waitKey(1000)
                print()
                print("Couldn't find blue rectangle from this picture.")
                print(file)
                print()
                messagebox.showerror("Error", "Couldn't find a blue rectangle from this picture.")
                continue

            if go_back or skip:
                continue

            if number == None:
                print()
                print("Couldn't find symbols from this picture.")
                print(file)
                print()
                messagebox.showerror("Error", "Couldn't find symbols from this picture.")
                continue

            # Adding the found and presumably correct (determined by the user) symbol 
            # to already found dict of symbols.
            found_symbols(number)

            fileparts = juurepilt.split(".")
            
            fileparts2 = fileparts[0].split("_")
            
            ### path +
            new_filename = fileparts2[0] + "_" + str(number).strip() + "." + fileparts[1]
            new_path = join(path,"output",new_filename)

            # If the file exists already, add X before the name of the file to not 
            # overwrite the correct file in case of wrong human input.
            if isfile(new_path):
                new_path = join(path,"output",("X" + new_filename))
                #print(f"new_path: {new_path}")
                messagebox.showwarning("Warning", "File already exists. Added 'X' to the start of the file name.")

            # Copy and rename the file to the output location with a new name.
            shutil.copy(file, new_path)
            
            ### TODO
            ### Write to a log file
            
            
            ### Write the processed file to a progress file
            write_progress(juurepilt, path)

            print(f"failinimi {i}: new_filename: {new_filename} , path: {new_path}")


# Idea of saving the progress:
# if first loading up, checks if the directory has a file named ".progress.txt":
# if no, then its going to continue and its gonna make it.
# If yes, then it will ask the user if it wants to use it.
 
# If the user chooses to not use it, the program will continue as it would with
# no progress file and add to the current one or make a new file with new information.
# If the user chooses to use the savefile the programm will skip every file that is in
# the file and continue where the user left off previously.

# The information that it saves: only the original filenames of the pictures,
# which have been renamed&copied.
def write_progress(info, path):
    '''
    Write the original name of the processed file to a progress file.
    
    :param info: the name of the processed file.
    :param path: path of the progress file.
    '''
    try:
        with open(join(path, ".progress.txt"), "a+", encoding="UTF-8") as outputfile:
            outputfile.write(info+"\n")
    except Exception as e:
        print("Unexpected error:", sys.exc_info()[0])
        messagebox.showerror("error", f"Unexpected error:, {sys.exc_info()[0]}\n{e}")
        quit_program()
        
def read_progress(path):
    '''
    Read from the progress file. Should only get here is the file exists.
    
    :param path: path of the progress file.
    :returns: progress as a list.
    '''
    try:
        with open(join(path, ".progress.txt"), "r", encoding="UTF-8") as outputfile:
            progress = [line.strip() for line in outputfile.readlines()]
    except Exception as e:
        print("Unexpected error:", sys.exc_info()[0])
        messagebox.showerror("error", f"Unexpected error:, {sys.exc_info()[0]}\n{e}")
        quit_program()
    return progress


i = 0
go_back = False
def moveGenerator(failid):
    global i, go_back
    '''
    A way to move between the files.
    
    :param failid: list of to be proccessed files.
    :yields: a new file to be proccessed based on user input.
    '''
    
    while i < len(failid):
        if go_back and i > 2:
            i -= 1
            go_back = False
        else:
            i += 1
        yield failid[i-1]
        
found = {}
def found_symbols(new_symbol):
    '''
    Adds the found symbol (if its a symbol) to the dict of found symbols.
    
    :param new_symbol: the found symbol.
    '''
    
    if new_symbol == '' or new_symbol == None:
        return

    extracted = re.split(r'([0-9]+)([A-Z])', new_symbol)[1:-1]
    #print(f"extracted {extracted}")
    
    key, value = extracted#re.split(r'([a-z])', new_symbol)
    key = int(key)
    
    #print(f"extracted: key: {key}, value: {value}")
    
    if key in found:
        if value not in found.get(key):
            found[key].append(value)
    
    else:
        found[key] = [value]
        
missing_numbers = []
missing_letters = []

def missing(found_dict:dict):
    global missing_numbers, missing_letters
    '''
    Determines if there are missing sides or "numbers" missing from the files
    and outputs it to the user as a info message at the end of the program.
    If there is more than 5 of the files at the end are missing then assume
    that user checked incorrectly and the finder exits.
    
    :param found_dict: a dictionary of the found symbols.
    '''
    keys = list(found_dict.keys())
    fmtf = 0
    i = min(keys)
    while i <= max(keys):
        
        if i not in keys:
            missing_numbers.append(i)
            fmtf += 1
        elif len(found_dict[i]) < 4:
            #print(found_dict[i])
            if "A" not in found_dict[i]:
                missing_letters.append(str(i)+"A")
            if "B" not in found_dict[i]:
                missing_letters.append(str(i)+"B")
            if "C" not in found_dict[i]:
                missing_letters.append(str(i)+"C")
            if "D" not in found_dict[i]:
                missing_letters.append(str(i)+"D")
            fmtf = 0
        else:
            fmtf = 0
        if fmtf > 4:
            missing_numbers = missing_numbers[:-5] 
            break
        i += 1
        
    print(f"Missing numbers: {missing_numbers} \nMissing sides: {missing_letters}")

    messagebox.showwarning("Warning", f"Missing numbers: {missing_numbers} \nMissing sides: {missing_letters}")
    
log = []
def quit_program():
    '''
    Exiting when program finishes of error occurs.
    '''
    
    '''
    try:
        print(f"saving log . . .")
        with open(newpath+"log.log", "+a", encoding="UTF-8") as logfile:
            logfile.write(f"{datetime.now()}\n")
            logfile.writelines(log)
            logfile.write("\n")
            
    except Exception as e:
        print("Unexpected error:", sys.exc_info()[0])
        messagebox.showerror("error", f"Unexpected error:, {sys.exc_info()[0]}")'''
    
    sys.exit()

    
    
### For running it on windows
if name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


newpath = ""
different_output = False
def main():
    global path, newpath, choose
    '''
    The MAIN function of the program.
    '''
    
    try:
        # Shows the dialog box and returns the path
        path = askdirectory(title='Select Folder of the files to be handled')

        # If the path is not specified, i.e. the user presses "cancel" in the select folder window
        if path == ():
            quit_program()
        
        askUserWindow.deiconify()
        
        while choose == "":
            askUserWindow.update()
            pass
        choose = ""

        # where the output files should go    
        if different_output:
            # A window asking the user for output folder name and location asking if 
            # user wants to do that or accepts the default option folder named: "output"
            newpath = askdirectory(title='Select Folder for the output files to go to')
        else:
            newpath = join(path, "output")
            
        print(f"newpath: {newpath}")
            
                
        if not exists(newpath):
            mkdir(newpath)

        progress = []

        if ".progress.txt" in listdir(path):

            askUserWindow.deiconify()
            
            while choose == "":
                askUserWindow.update()
                pass

            ### if user presses Yes if it wants to continue using a saved progress file.
            if not different_output:
                progress = read_progress(path)

        print("Joudsin siia")

        list_failidest = path_to_files()
        
        # Starting the finding of the symbols.
        print(main_loop(list_failidest, progress))
        
        if len(found) > 0:
            missing(found)
            
        messagebox.showinfo("info", "Program finished!")
        
    except Exception as e:
        messagebox.showerror("error", f"Unexpected error:, {sys.exc_info()[0]}\n{e}")

        print(f"error: {e}")
        
        quit_program()
    
if __name__ == "__main__":
    main()