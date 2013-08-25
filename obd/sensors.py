 #!/usr/bin/env python
###########################################################################
# obd_sensors.py
#
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)
# Copyright 2009 Secons Ltd. (www.obdtester.com)
#
# This file is part of pyOBD.
#
# pyOBD is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pyOBD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyOBD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###########################################################################

def hex_to_int(str):
    i = eval("0x" + str, {}, {})
    return i

def maf(code):
    code = hex_to_int(code)
    return code * 0.00132276

def throttle_pos(code):
    code = hex_to_int(code)
    return code * 100.0 / 255.0

def intake_m_pres(code): # in kPa
    code = hex_to_int(code)
    return code / 0.14504
    
def rpm(code):
    code = hex_to_int(code)
    return code / 4

def speed_kmh(code):
    return hex_to_int(code)

def speed_mph(code):
    code = hex_to_int(code)
    return code / 1.609

def percent_scale(code):
    code = hex_to_int(code)
    return code * 100.0 / 255.0

def timing_advance(code):
    code = hex_to_int(code)
    return (code - 128) / 2.0

def sec_to_min(code):
    code = hex_to_int(code)
    return code / 60

def temp(code):
    code = hex_to_int(code)
    return code - 40 

def cpass(code):
    #fixme
    return code

def fuel_trim_percent(code):
    code = hex_to_int(code)
    return (code - 128.0) * 100.0 / 128

def dtc_decrypt(code):
    #first byte is byte after PID and without spaces
    num = hex_to_int(code[:2]) #A byte
    res = []

    if num & 0x80: # is mil light on
        mil = 1
    else:
        mil = 0
        
    # bit 0-6 are the number of dtc's. 
    num = num & 0x7f
    
    res.append(num)
    res.append(mil)
    
    numB = hex_to_int(code[2:4]) #B byte
      
    for i in range(0,3):
        res.append(((numB>>i)&0x01)+((numB>>(3+i))&0x02))
    
    numC = hex_to_int(code[4:6]) #C byte
    numD = hex_to_int(code[6:8]) #D byte
       
    for i in range(0,7):
        res.append(((numC>>i)&0x01)+(((numD>>i)&0x01)<<1))
    
    res.append(((numD>>7)&0x01)) #EGR SystemC7  bit of different 
    
    return res

def hex_to_bitstring(str):
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

class Sensor:
    def __init__(self, shortName, sensorName, sensorcommand, sensorValueFunction, u):
        self.shortname = shortName
        self.name = sensorName
        self.cmd  = sensorcommand
        self.value= sensorValueFunction
        self.unit = u

SENSORS = [
    Sensor("pids"                  , "          Supported PIDs", "0100", hex_to_bitstring ,""       ),    
    Sensor("dtc_status"            , "Status Since DTC Cleared", "0101", dtc_decrypt      ,""       ),    
    Sensor("dtc_ff"                , "DTC Causing Freeze Frame", "0102", cpass            ,""       ),    
    Sensor("fuel_status"           , "      Fuel System Status", "0103", cpass            ,""       ),
    Sensor("load"                  , "   Calculated Load Value", "01041", percent_scale    ,""       ),    
    Sensor("temp"                  , "     Coolant Temperature", "0105", temp             ,"C"      ),
    Sensor("short_term_fuel_trim_1", "    Short Term Fuel Trim", "0106", fuel_trim_percent,"%"      ),
    Sensor("long_term_fuel_trim_1" , "     Long Term Fuel Trim", "0107", fuel_trim_percent,"%"      ),
    Sensor("short_term_fuel_trim_2", "    Short Term Fuel Trim", "0108", fuel_trim_percent,"%"      ),
    Sensor("long_term_fuel_trim_2" , "     Long Term Fuel Trim", "0109", fuel_trim_percent,"%"      ),
    Sensor("fuel_pressure"         , "      Fuel Rail Pressure", "010A", cpass            ,""       ),
    Sensor("manifold_pressure"     , "Intake Manifold Pressure", "010B", intake_m_pres    ,"psi"    ),
    Sensor("rpm"                   , "              Engine RPM", "010C1", rpm              ,""       ),
    Sensor("speed"                 , "           Vehicle Speed", "010D1", speed_kmh       ,"km/h"    ),
    Sensor("timing_advance"        , "          Timing Advance", "010E", timing_advance   ,"degrees"),
    Sensor("intake_air_temp"       , "         Intake Air Temp", "010F", temp             ,"C"      ),
    Sensor("maf"                   , "     Air Flow Rate (MAF)", "0110", maf              ,"lb/min" ),
    Sensor("throttle_pos"          , "       Throttle Position", "01111", throttle_pos     ,"%"      ),
    Sensor("secondary_air_status"  , "    Secondary Air Status", "0112", cpass            ,""       ),
    Sensor("o2_sensor_positions"   , "  Location of O2 sensors", "0113", cpass            ,""       ),
    Sensor("o211"                  , "        O2 Sensor: 1 - 1", "0114", fuel_trim_percent,"%"      ),
    Sensor("o212"                  , "        O2 Sensor: 1 - 2", "0115", fuel_trim_percent,"%"      ),
    Sensor("o213"                  , "        O2 Sensor: 1 - 3", "0116", fuel_trim_percent,"%"      ),
    Sensor("o214"                  , "        O2 Sensor: 1 - 4", "0117", fuel_trim_percent,"%"      ),
    Sensor("o221"                  , "        O2 Sensor: 2 - 1", "0118", fuel_trim_percent,"%"      ),
    Sensor("o222"                  , "        O2 Sensor: 2 - 2", "0119", fuel_trim_percent,"%"      ),
    Sensor("o223"                  , "        O2 Sensor: 2 - 3", "011A", fuel_trim_percent,"%"      ),
    Sensor("o224"                  , "        O2 Sensor: 2 - 4", "011B", fuel_trim_percent,"%"      ),
    Sensor("obd_standard"          , "         OBD Designation", "011C", cpass            ,""       ),
    Sensor("o2_sensor_position_b"  ,"  Location of O2 sensors" , "011D", cpass            ,""       ),
    Sensor("aux_input"             , "        Aux input status", "011E", cpass            ,""       ),
    Sensor("engine_time"           , " Time Since Engine Start", "011F", sec_to_min       ,"min"    ),
    Sensor("pids2"                 , "PIDs_supported_[21_-_40]", "0120", hex_to_bitstring ,""    ),
    Sensor("Distance_traveled_with_", "Distance_traveled_with_m", "0121", cpass       ,""    ),
    Sensor("Fuel_Rail_Pressure_(rel", "Fuel_Rail_Pressure_(rela", "0122", cpass       ,""    ),
    Sensor("Fuel_Rail_Pressure_(die", "Fuel_Rail_Pressure_(dies", "0123", cpass       ,""    ),
    Sensor("O2S1_WR_lambda"        , "     O2S1_WR_lambda(1)   ", "0124", cpass       ,""    ),
    Sensor("O2S2_WR_lambda"        , "     O2S2_WR_lambda(1)   ", "0125", cpass       ,""    ),
    Sensor("O2S3_WR_lambda"        , "     O2S3_WR_lambda(1)   ", "0126", cpass       ,""    ),
    Sensor("O2S4_WR_lambda"        , "     O2S4_WR_lambda(1)   ", "0127", cpass       ,""    ),
    Sensor("O2S5_WR_lambda"        , "     O2S5_WR_lambda(1)   ", "0128", cpass       ,""    ),
    Sensor("O2S6_WR_lambda"        , "     O2S6_WR_lambda(1)   ", "0129", cpass       ,""    ),
    Sensor("O2S7_WR_lambda"        , "     O2S7_WR_lambda(1)   ", "012A", cpass       ,""    ),
    Sensor("O2S8_WR_lambda"        , "     O2S8_WR_lambda(1)   ", "012B", cpass       ,""    ),
    Sensor("Commanded_EGR"         , "           Commanded_EGR", "012C", cpass       ,""    ),
    Sensor("EGR_Error"             , "               EGR_Error", "012D", cpass       ,""    ),
    Sensor("Commanded_evaporative_p", "Commanded_evaporative_pu", "012E", cpass       ,""    ),
    Sensor("Fuel_Level_Input"      , "        Fuel_Level_Input", "012F", cpass       ,""    ),
    Sensor("of_warm-ups_since_cod", "of_warm-ups_since_code", "0130", cpass       ,""    ),
    Sensor("Distance_traveled_since", "Distance_traveled_since_", "0131", cpass       ,""    ),
    Sensor("Evap._System_Vapor_Pres", "Evap._System_Vapor_Press", "0132", cpass       ,""    ),
    Sensor("Barometric_pressure"   , "     Barometric_pressure", "0133", cpass       ,""    ),
    Sensor("O2S1_WR_lambda"        , "     O2S1_WR_lambda(1)  ", "0134", cpass       ,""    ),
    Sensor("O2S2_WR_lambda"        , "     O2S2_WR_lambda(1)"  , "0135", cpass       ,""    ),
    Sensor("O2S3_WR_lambda	"   , "     O2S3_WR_lambda(1)	", "0136", cpass       ,""    ),
    Sensor("O2S4_WR_lambda"   , "     O2S4_WR_lambda(1)	", "0137", cpass       ,""    ),
    Sensor("O2S5_WR_lambda"   , "     O2S5_WR_lambda(1)	", "0138", cpass       ,""    ),
    Sensor("O2S6_WR_lambda"   , "     O2S6_WR_lambda(1)	", "0139", cpass       ,""    ),
    Sensor("O2S7_WR_lambda 	"   , "     O2S7_WR_lambda(1)", "013A", cpass       ,""    ),
    Sensor("O2S8_WR_lambda	"   , "     O2S8_WR_lambda(1)	", "013B", cpass       ,""    ),
    Sensor("Catalyst_Temperature	" , "   Catalyst_Temperature	", "013C", cpass       ,""    ),
    Sensor("Catalyst_Temperature	" , "   Catalyst_Temperature	", "013D", cpass       ,""    ),
    Sensor("Catalyst_Temperature	" , "   Catalyst_Temperature	", "013E", cpass       ,""    ),
    Sensor("Catalyst_Temperature	" , "   Catalyst_Temperature	", "013F", cpass       ,""    ),
    Sensor("pids3", "PIDs_supported_[41_-_60]", "0140", hex_to_bitstring       ,""    ),
    Sensor("Monitor_status_this_dri", "Monitor_status_this_driv", "0141", cpass       ,""    ),
    Sensor("Control_module_voltage", "  Control_module_voltage", "0142", cpass       ,""    ),
    Sensor("Absolute_load_value"   , "     Absolute_load_value", "0143", cpass       ,""    ),
    Sensor("Command_equivalence_rat", "Command_equivalence_rati", "0144", cpass       ,""    ),
    Sensor("Relative_throttle_posit", "Relative_throttle_positi", "0145", cpass       ,""    ),
    Sensor("Ambient_air_temperature", " Ambient_air_temperature", "0146", cpass       ,""    ),
    Sensor("Absolute_throttle_posit", "Absolute_throttle_positi", "0147", cpass       ,""    ),
    Sensor("Absolute_throttle_posit", "Absolute_throttle_positi", "0148", cpass       ,""    ),
    Sensor("Accelerator_pedal_posit", "Accelerator_pedal_positi", "0149", cpass       ,""    ),
    Sensor("Accelerator_pedal_posit", "Accelerator_pedal_positi", "014A", cpass       ,""    ),
    Sensor("Accelerator_pedal_posit", "Accelerator_pedal_positi", "014B", cpass       ,""    ),
    Sensor("Commanded_throttle_actu", "Commanded_throttle_actua", "014C", cpass       ,""    ),
    Sensor("Time_run_with_MIL_on"  , "    Time_run_with_MIL_on", "014D", cpass       ,""    ),
    Sensor("Time_since_trouble_code", "Time_since_trouble_codes", "014E", cpass       ,""    ),
    Sensor("Maximum_value_for_equiv", "Maximum_value_for_equiva", "014F", cpass       ,""    ),
    Sensor("Maximum_value_for_air_f", "Maximum_value_for_air_fl", "0150", cpass       ,""    ),
    Sensor("Fuel_Type"             , "               Fuel_Type", "0151", cpass       ,""    ),
    Sensor("Ethanol_fuel_%"        , "          Ethanol_fuel_%", "0152", cpass       ,""    ),
    Sensor("Absolute_Evap_system_Va", "Absolute_Evap_system_Vap", "0153", cpass       ,""    ),
    Sensor("Evap_system_vapor_press", "Evap_system_vapor_pressu", "0154", cpass       ,""    ),
    Sensor("Short_term_secondary_ox", "Short_term_secondary_oxy", "0155", cpass       ,""    ),
    Sensor("Long_term_secondary_oxy", "Long_term_secondary_oxyg", "0156", cpass       ,""    ),
    Sensor("Short_term_secondary_ox", "Short_term_secondary_oxy", "0157", cpass       ,""    ),
    Sensor("Long_term_secondary_oxy", "Long_term_secondary_oxyg", "0158", cpass       ,""    ),
    Sensor("Fuel_rail_pressure_(abs", "Fuel_rail_pressure_(abso", "0159", cpass       ,""    ),
    Sensor("Relative_accelerator_pe", "Relative_accelerator_ped", "015A", cpass       ,""    ),
    Sensor("Hybrid_battery_pack_rem", "Hybrid_battery_pack_rema", "015B", cpass       ,""    ),
    Sensor("Engine_oil_temperature", "  Engine_oil_temperature", "015C", cpass       ,""    ),
    Sensor("Fuel_injection_timing" , "   Fuel_injection_timing", "015D", cpass       ,""    ),
    Sensor("Engine_fuel_rate"      , "        Engine_fuel_rate", "015E", cpass       ,""    ),
    Sensor("Emission_requirements_t", "Emission_requirements_to", "015F", cpass       ,""    ),
    Sensor("pids4", "PIDs_supported_[61_-_80]", "0160", hex_to_bitstring       ,""    ),
    Sensor("Driver's_demand_engine_", "Driver's_demand_engine_-", "0161", cpass       ,""    ),
    Sensor("Actual_engine_-_percent", "Actual_engine_-_percent_", "0162", cpass       ,""    ),
    Sensor("Engine_reference_torque", " Engine_reference_torque", "0163", cpass       ,""    ),
    Sensor("Engine_percent_torque_d", "Engine_percent_torque_da", "0164", cpass       ,""    ),
    Sensor("Auxiliary_input_/_outpu", "Auxiliary_input_/_output", "0165", cpass       ,""    ),
    Sensor("Mass_air_flow_sensor"  , "    Mass_air_flow_sensor", "0166", cpass       ,""    ),
    Sensor("Engine_coolant_temperat", "Engine_coolant_temperatu", "0167", cpass       ,""    ),
    Sensor("Intake_air_temperature_", "Intake_air_temperature_s", "0168", cpass       ,""    ),
    Sensor("Commanded_EGR_and_EGR_E", "Commanded_EGR_and_EGR_Er", "0169", cpass       ,""    ),
    Sensor("Commanded_Diesel_intake", "Commanded_Diesel_intake_", "016A", cpass       ,""    ),
    Sensor("Exhaust_gas_recirculati", "Exhaust_gas_recirculatio", "016B", cpass       ,""    ),
    Sensor("Commanded_throttle_actu", "Commanded_throttle_actua", "016C", cpass       ,""    ),
    Sensor("Fuel_pressure_control_s", "Fuel_pressure_control_sy", "016D", cpass       ,""    ),
    Sensor("Injection_pressure_cont", "Injection_pressure_contr", "016E", cpass       ,""    ),
    Sensor("Turbocharger_compressor", "Turbocharger_compressor_", "016F", cpass       ,""    ),
    Sensor("Boost_pressure_control", "  Boost_pressure_control", "0170", cpass       ,""    ),
    Sensor("Variable_Geometry_turbo", "Variable_Geometry_turbo_", "0171", cpass       ,""    ),
    Sensor("Wastegate_control"     , "       Wastegate_control", "0172", cpass       ,""    ),
    Sensor("Exhaust_pressure"      , "        Exhaust_pressure", "0173", cpass       ,""    ),
    Sensor("Turbocharger_RPM"      , "        Turbocharger_RPM", "0174", cpass       ,""    ),
    Sensor("Turbocharger_temperatur", "Turbocharger_temperature", "0175", cpass       ,""    ),
    Sensor("Turbocharger_temperatur", "Turbocharger_temperature", "0176", cpass       ,""    ),
    Sensor("Charge_air_cooler_tempe", "Charge_air_cooler_temper", "0177", cpass       ,""    ),
    Sensor("Exhaust_Gas_temperature", "Exhaust_Gas_temperature_", "0178", cpass       ,""    ),
    Sensor("Exhaust_Gas_temperature", "Exhaust_Gas_temperature_", "0179", cpass       ,""    ),
    Sensor("Diesel_particulate_filt", "Diesel_particulate_filte", "017A", cpass       ,""    ),
    Sensor("Diesel_particulate_filt", "Diesel_particulate_filte", "017B", cpass       ,""    ),
    Sensor("Diesel_Particulate_filt", "Diesel_Particulate_filte", "017C", cpass       ,""    ),
    Sensor("NOx_NTE_control_area_st", "NOx_NTE_control_area_sta", "017D", cpass       ,""    ),
    Sensor("PM_NTE_control_area_sta", "PM_NTE_control_area_stat", "017E", cpass       ,""    ),
    Sensor("Engine_run_time"       , "         Engine_run_time", "017F", cpass       ,""    ),
    Sensor("pids5", "PIDs_supported_[81_-_A0]", "0180", hex_to_bitstring       ,""    ),
    Sensor("Engine_run_time_for_Aux", "Engine_run_time_for_Auxi", "0181", cpass       ,""    ),
    Sensor("Engine_run_time_for_Aux", "Engine_run_time_for_Auxi", "0182", cpass       ,""    ),
    Sensor("NOx_sensor"            , "              NOx_sensor", "0183", cpass       ,""    ),
    Sensor("Manifold_surface_temper", "Manifold_surface_tempera", "0184", cpass       ,""    ),
    Sensor("NOx_reagent_system"    , "      NOx_reagent_system", "0185", cpass       ,""    ),
    Sensor("Particulate_matter_(PM)", "Particulate_matter_(PM)_", "0186", cpass       ,""    ),
    Sensor("Intake_manifold_absolut", "Intake_manifold_absolute", "0187", cpass       ,""    ),
	    ]
     
    
#___________________________________________________________

def test():
    for i in SENSORS:
        print i.name, i.value("F")

if __name__ == "__main__":
    test()
