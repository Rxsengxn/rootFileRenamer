from datetime import datetime
import re

import sys
from tkinter import Tk, Entry, Button, messagebox 
from tkinter.filedialog import askdirectory


root = Tk()
root.withdraw()

def disable_event():
   pass

root.protocol("WM_DELETE_WINDOW", disable_event)

save_progress = None
def Click_yes(event=None):
    global save_progress
    
    save_progress = True
    root.withdraw()


def Click_no(event=None):
    global save_progress
    
    save_progress = False
    root.withdraw()
    
button_yes = Button(root, text="Yes", command=Click_no)
button_yes.pack()

button_no = Button(root, text="No", command=Click_yes)
button_no.pack()



found = {}
def found_symbols(new_symbol):
    global run
    
    if new_symbol == '':
        run = False
        return

    extracted = re.split(r'([0-9]+)([A-Z])', new_symbol)[1:-1]
    print(f"extracted {extracted}")
    
    key, value = extracted#re.split(r'([a-z])', new_symbol)
    key = int(key)
    
    print(f"extracted: key: {key}, value: {value}")
    
    if key in found:
        if value not in found.get(key):
            found[key].append(value)
    
    else:
        found[key] = [value]
    
run = True
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
            print(found_dict[i])
            if "A" not in found_dict[i]:
                missing_letters.append(str(i)+"A")
            if "B" not in found_dict[i]:
                missing_letters.append(str(i)+"B")
            if "C" not in found_dict[i]:
                missing_letters.append(str(i)+"C")
            if "D" not in found_dict[i]:
                missing_letters.append(str(i)+"D")
        i += 1
        
newpath = ""
log = []
def write_progress(current_file:str):
    try:
        with open(newpath+".progress.txt", "+a", encoding="UTF-8") as progress_file:
            ##progress_file.write(f"{datetime.now()}\n")
            progress_file.write(current_file+"\n")
            
    except Exception as e:
        print("Unexpected error:", sys.exc_info()[0])
        messagebox.showerror("error", f"Unexpected error:, {sys.exc_info()[0]}\n{e}")

saved_progress = []
def read_progress(file:str):
    global saved_progress

    try:
        with open(file, "r", encoding="UTF-8") as progress_file:
            saved_progress = progress_file.readlines()
            
    except Exception as e:
        print("Unexpected error:", sys.exc_info()[0])
        messagebox.showerror("error", f"Unexpected error:, {sys.exc_info()[0]}\n{e}")
            


def main():
    global newpath
    """
    input_symbols = ["2A", "4C", "1A", "2C","1B", "2B", "1D", "1C"]
    
    #while run:
    for x in input_symbols:
        found_symbols(x)#input("input a symbol: "))
    missing(found)
        
    
    print(f"keys: {found.keys()}, values: {found.values()}")
    
    print(f"missing numbers: {missing_numbers}, missing 'sides': {missing_letters}")"""
    
    newpath = askdirectory("Set the directory of pictures")
        
    root.deiconify()
    
    while save_progress == None:
        pass
    
    if save_progress:
        
        read_progress(newpath+".progress.txt")
    
    data = ["test10.jpg", "test2.jpg", "test3.jpg", "test5.jpg", "test4.jpg", "test6.jpg", "test9.jpg",
            "test12.jpg", "test15.jpg", "test7.jpg", "test55.jpg", "test23.jpg", "test0.jpg", "test16.jpg",
            "test11.jpg", "test13.jpg", "test22.jpg", "test8.jpg"]
    i = 0
    while True:
        info = data[i]
        if info in saved_progress:
            continue
        else:
            print(info + "pole saved")
        write_progress(info)
        i += 1
    
    
if __name__ == "__main__":
    main()