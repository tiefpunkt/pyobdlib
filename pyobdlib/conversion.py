# pyobdlib
# Copyright (C) 2004 Donour Sizemore
# Copyright (C) 2009 Secons Ltd.
# Copyright (C) 2013 Mark Embling
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

OBD_STANDARDS = {
	"01": "OBD-II as defined by the CARB",
	"02": "OBD as defined by the EPA",
	"03": "OBD and OBD-II",
	"04": "OBD-I",
	"05": "Not meant to comply with any OBD standard",
	"06": "EOBD (Europe)",
	"07": "EOBD and OBD-II",
	"08": "EOBD and OBD",
	"09": "EOBD, OBD and OBD II",
	"0A": "JOBD (Japan)",
	"0B": "JOBD and OBD II",
	"0C": "JOBD and EOBD",
	"0D": "JOBD, EOBD, and OBD II"
}

# Conversions used in sensors module

def noop(code):
    """Return the code with no conversion"""
    return code

def to_int(str):
    """Convert the code (hex string) into an integer"""
    #i = eval("0x" + str, {}, {})
    #return i
    return int(str, 16)
    
def to_bitstring(str):
    """Convert the given code into a bit string (binary string, equiv. 4 bytes)"""
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

def to_percent_scale(code):
    """Convert the given code to a percentage"""
    return round(to_int(code) * 100.0 / 255.0, 2)

def to_temp_c(code):
    """Convert the given code to a value in celsius"""
    return to_int(code) - 40 

def to_fuel_trim_percent(code):
    """Convert the code to a percentage using the fuel trim calculation"""
    return (to_int(code) - 128.0) * 100.0 / 128

def to_kpa_gauge(code):
    """Used for fuel pressure"""
    return to_int(code) * 3;

def to_rpm(code):
    """Convert code to RPM"""
    return to_int(code) / 4

def to_timing_advance(code):
    """Convert code to timing advance (in degrees relative to cyl #1)"""
    return (to_int(code) - 128) / 2.0

def to_maf_grams_sec(code):
    """Return correct grams/sec reading for MAF"""
    return to_int(code) / 100.0

def dtc_decode(code):
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

def to_ODB_standard(code):
	if code in OBD_STANDARDS:
		return OBD_STANDARDS[code]
	else:
		return "Invalid reply"


# Additional conversions that may be used in client code

def kmh_to_mph(kmh):
    """Converts a speed in km/h to MPH"""
    return kmh / 1.609

def kpa_to_psi(kpa):
    """Convert a value in kPa to PSI"""
    return kpa / 0.14504

def grams_sec_to_lb_min(grams_sec):
    """Convert a reading in grams/sec to lb/min"""
    return grams_sec * 0.132277

