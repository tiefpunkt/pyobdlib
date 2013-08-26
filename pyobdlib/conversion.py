# Conversions used in sensors module

def noop(code):
    #fixme
    return code

def to_int(str):
    #i = eval("0x" + str, {}, {})
    #return i
    return int(str, 16)

def to_maf(code):
    code = to_int(code)
    return code * 0.00132276

def to_throttle_pos(code):
    code = to_int(code)
    return code * 100.0 / 255.0

def to_intake_m_pres(code): # in kPa
    code = to_int(code)
    return code / 0.14504
    
def to_rpm(code):
    code = to_int(code)
    return code / 4

def to_percent_scale(code):
    code = to_int(code)
    return code * 100.0 / 255.0

def to_timing_advance(code):
    code = to_int(code)
    return (code - 128) / 2.0

def to_temp_c(code):
    code = to_int(code)
    return code - 40 

def to_fuel_trim_percent(code):
    code = to_int(code)
    return (code - 128.0) * 100.0 / 128

def dtc_decrypt(code):
    #first byte is byte after PID and without spaces
    num = to_int(code[:2]) #A byte
    res = []

    if num & 0x80: # is mil light on
        mil = 1
    else:
        mil = 0
        
    # bit 0-6 are the number of dtc's. 
    num = num & 0x7f
    
    res.append(num)
    res.append(mil)
    
    numB = to_int(code[2:4]) #B byte
      
    for i in range(0,3):
        res.append(((numB>>i)&0x01)+((numB>>(3+i))&0x02))
    
    numC = to_int(code[4:6]) #C byte
    numD = to_int(code[6:8]) #D byte
       
    for i in range(0,7):
        res.append(((numC>>i)&0x01)+(((numD>>i)&0x01)<<1))
    
    res.append(((numD>>7)&0x01)) #EGR SystemC7  bit of different 
    
    return res

def to_bitstring(str):
    bitstring = ""
    for i in str:
        # silly type safety, we don't want to eval random stuff
        if type(i) == type(''): 
            v = eval("0x%s" % i)
            if v & 8 :
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 4:
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 2:
                bitstring += '1'
            else:
                bitstring += '0'
            if v & 1:
                bitstring += '1'
            else:
                bitstring += '0'                
    return bitstring








def speed_mph(code):
    code = to_int(code)
    return code / 1.609
