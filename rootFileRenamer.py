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


def disable_event():
   pass

# Main window
root = Tk()
root.withdraw()


# Dialog box for asking about the output folder
askUserWindow = Tk()
askUserWindow.title("Choose an option")
# Adjust size
askUserWindow.geometry("400x150")
 
# set minimum window size value
askUserWindow.minsize(400, 150)

askUserWindow.protocol("WM_DELETE_WINDOW", disable_event)

askUserWindow.withdraw()

labelForText = Label(askUserWindow,
                    text='Use default ("output") folder for the output files?',
                    font = ("Arial", 18),
                    wraplength=350)
labelForText.pack(pady=20)

askFrame = Frame(askUserWindow)
askFrame.pack(pady=10)

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



root.protocol("WM_DELETE_WINDOW", disable_event)

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

def kontroll(symbol):
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

def viie_katse_parim(frame):
    global mfr, correct, go_back, skip
    '''
    Searches a set of symbols from the input image.
    
    :param frame: input image (works better when already thresholded)
    :return: set of symbols it found from the picture
    '''
    
    correct = ""
    
    symbols = pytesseract.image_to_string(frame,
                                        lang='eng',
                                        config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789ABCD').strip()
    mfr = kontroll(symbols)
    
    print(f"Result: {mfr}")

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
    
        try:
            if cv2.getWindowProperty('Input', cv2.WND_PROP_VISIBLE) <= 0:
                quit_program()
        except cv2.error as e:
            messagebox.showerror("error", f"error: {e}")
            quit_program()
            #sys.exit()

    cv2.destroyAllWindows()
    correct = ""

    if mfr == "":
        mfr = None
        
    return mfr


def tee_failideks():
    onlyfiles = [f for f in listdir(path) if (isfile(join(path, f)) and (f.endswith('.jpg') or f.endswith('.png')))]
    print(onlyfiles)
    return onlyfiles

def katse(list_failidest, progress:list):
    global input_img, skip

    cv2.namedWindow('Input', cv2.WINDOW_NORMAL)
    
        
    for juurepilt in moveGenerator(list_failidest):
        if juurepilt.endswith('.jpg') or juurepilt.endswith('.png'):
            if len(progress) > 0:
                if juurepilt in progress:
                    progress.remove(juurepilt)
                    continue
            
            number = None
            file = join(path, juurepilt)
            
            print(file)
            input_img = cv2.imread(file)
            input_img = input_img[int(len(input_img)/10*8):, int(len(input_img[0])/10*7):]
            
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

                number = viie_katse_parim(input)
            else:
                cv2.imshow("Input", input_img)
                cv2.waitKey(1000)
                print()
                print("Couldn't find blue rectangle from this picture.")
                print(file)
                print()
                messagebox.showerror("Error", "Couldn't find blue rectangle from this picture.")
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

            found_symbols(number)

            fileparts = juurepilt.split(".")
            
            fileparts2 = fileparts[0].split("_")
            
            ### path +
            new_filename = fileparts2[0] + "_" + str(number).strip() + "." + fileparts[1]
            new_path = join(path,"output",new_filename)

            ### If the file exists already, add X before the name of the file to not 
            # overwrite the correct file in case of wrong human input
            if isfile(new_path):
                #print("EROOROROOROROO")
                new_path = join(path,"output",("X" + new_filename))
                #print(f"new_path: {new_path}")
                messagebox.showerror("Error", "File already exists. Added 'X' to the start of the file name.")

            shutil.copy(file, new_path)
            
            ### Write to a log file
            
            
            ### Write the processed file to a progress file
            write_progress(juurepilt, path)

            print(f"failinimi {i}: new_filename: {new_filename} , path: {new_path}")


# progress save idea
# if first loading up, checks if the directory has a file named ".progress.txt":
# if no, then its going to continue and its gonna make it.
# If yes, then it will ask the user if it wants to use it.
 
# If the user chooses to not use it, the program will continue as it would with
# no progress file and add to the current one or make a new file with new information.
# If the user chooses to use the savefile the programm will skip every file that is in
# the file and continue where the user left off previously.

# The information that it saves: only the original filenames of the pictures, which have been "renamed"/copied.
def write_progress(info, path):
    try:
        with open(join(path, ".progress.txt"), "a+", encoding="UTF-8") as outputfile:
            outputfile.write(info+"\n")
    except Exception as e:
        print("Unexpected error:", sys.exc_info()[0])
        messagebox.showerror("error", f"Unexpected error:, {sys.exc_info()[0]}\n{e}")
        quit_program()
        
def read_progress(path):
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
    
    while i < len(failid):
        if go_back and i > 2:
            i -= 1
            go_back = False
        else:
            i += 1
        yield failid[i-1]
        
found = {}
def found_symbols(new_symbol):
    global run
    
    if new_symbol == '' or new_symbol == None:
        run = False
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
    keys = list(found_dict.keys())
    i = 1
    while i <= max(keys):
        
        if i not in keys:
            missing_numbers.append(i)
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
        i += 1
        
    print(f"Missing numbers: {missing_numbers} \nMissing sides: {missing_letters}")

    messagebox.showwarning("Warning", f"Missing numbers: {missing_numbers} \nMissing sides: {missing_letters}")
    
log = []
def quit_program():
    
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
    
    try:
        path = askdirectory(title='Select Folder of the files to be handled') # shows dialog box and return the path
        
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

        list_failidest = tee_failideks()
        
        print(katse(list_failidest, progress))
        
        if len(found) > 0:
            missing(found)
            
        messagebox.showinfo("info", "Program finished!")
        
    except Exception as e:
        messagebox.showerror("error", f"Unexpected error:, {sys.exc_info()[0]}\n{e}")

        print(f"error: {e}")
        
        quit_program()
    
if __name__ == "__main__":
    main()