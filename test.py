import re


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

def main():
    
    input_symbols = ["2A", "4C", "1A", "2C","1B", "2B", "1D", "1C"]
    
    #while run:
    for x in input_symbols:
        found_symbols(x)#input("input a symbol: "))
    missing(found)
        
    
    print(f"keys: {found.keys()}, values: {found.values()}")
    
    print(f"missing numbers: {missing_numbers}, missing 'sides': {missing_letters}")
    
    
if __name__ == "__main__":
    main()
    