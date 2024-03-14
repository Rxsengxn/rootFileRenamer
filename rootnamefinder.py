#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import pytesseract
import numpy as np
from tkinter import Tk, Entry, Button, messagebox 
from tkinter.filedialog import askdirectory

import sys

from os import listdir, mkdir, name
from os.path import isfile, join, exists
import shutil


root = Tk()
root.withdraw()

e = Entry(root)

e.pack()

def Click(event=None):
    global correct, mfr
    mfr = e.get().upper()
    print(mfr)
    e.delete(0, 'end')
    correct = True
    root.withdraw()

root.bind("<Return>", Click)
    
button = Button(root, text="Sisesta õiged symbolid", command=Click)
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

def viie_katse_parim(frame):
    global mfr, correct
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
    
    print(f"tulemus: {mfr}")

    cv2.namedWindow('Input', cv2.WINDOW_NORMAL)
    cv2.putText(input_img, str(mfr), (20, 80), cv2.FONT_HERSHEY_SIMPLEX,  
                   2, (0, 255, 0), 4, cv2.LINE_AA)
    cv2.imshow("Input", input_img)
    
    print("y - õige, n - vale")
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
            e.focus_set() 
        if correct == True:
            break
    
        try:
            if cv2.getWindowProperty('Input', cv2.WND_PROP_VISIBLE) <= 0:
                sys.exit()
        except cv2.error:
            sys.exit()

    cv2.destroyAllWindows()
    correct = ""

    if mfr == "":
        mfr = None
        
    return mfr

def write_name_manually():
    global mfr, correct
    mfr = input("Sisesta käsitsi: ")
    correct = True
    return


def tee_failideks():
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    print(onlyfiles)
    return onlyfiles

def katse(list_failidest):
    global input_img

    cv2.namedWindow('Input', cv2.WINDOW_NORMAL)

    for counter, juurepilt in enumerate(list_failidest):
        if juurepilt.endswith('.jpg') or juurepilt.endswith('.png'):
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
                print("Sellelt pildilt ei suudetud tuvastada sinist ristkülikut.")
                print(file)
                print()
                messagebox.showerror("Error", "Sellelt pildilt ei suudetud tuvastada sinist ristkülikut.")
                continue

            if number == None:
                print()
                print("Sellelt pildilt ei suudetud sümboleid tuvastada.")
                print(file)
                print()
                messagebox.showerror("Error", "Sellelt pildilt ei suudetud sümboleid tuvastada.")
                continue

            fileparts = juurepilt.split(".")
            
            fileparts2 = fileparts[0].split("_")
            
            ### path +
            new_filename = fileparts2[0] + "_" + str(number).strip() + "." + fileparts[1]
            
            shutil.copy(file, join(path,"output",new_filename))

            print(f"failinimi {counter}: {new_filename}")
    
if name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

mfr = ""
correct = ""

def main():
    global path
    path = askdirectory(title='Select Folder') # shows dialog box and return the path

    newpath = join(path, "output")
    if not exists(newpath):
        mkdir(newpath)

    list_failidest = tee_failideks()
    print(katse(list_failidest))
    
if __name__ == "__main__":
    main()