# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 11:28:11 2024

@author: SG
"""
import numpy as np
import xlwings as xw
import os
from openpyxl import workbook, load_workbook
from openpyxl.chart import ScatterChart, Reference, Series
from openpyxl.chart import Reference as opyxlReference

os.chdir("C:/Users/Laboratorio/scitificCalculation/imageHub/r")


# Load the workbook
filename = "r.xlsx"
wb = xw.Book(filename)
ws = wb.sheets[0]  # Assuming you want the first sheet

ws.range('D1').value = "I (45)-BG" #crossed
ws.range('E1').value = "I (-45)-BG" # parallel
ws.range('F1').value = "Sum"
ws.range('H1').value = "I_c"
ws.range('I1').value = "I_p"
ws.range('J1').value = "SQRT"
ws.range('K1').value = "2*ATAN"
ws.range('L1').value = "phase(π)"
ws.range('M1').value = "unwrapped(π)"


i=2
while i<19:
    ws.range(f'D{i}').formula= f"=B{i}-MIN(B:B)"
    ws.range(f'E{i}').formula= f"=C{i}-MIN(C:C)"
    ws.range(f'F{i}').formula= f"=E{i}+D{i}"
    ws.range(f'H{i}').formula= f"=D{i}/F{i}"
    ws.range(f'I{i}').formula= f"=E{i}/F{i}"
    ws.range(f'J{i}').formula= f"=SQRT(H{i}/I{i})" #Ic/Ip
    ws.range(f'K{i}').formula= f"=2*ATAN(J{i})"
    ws.range(f'L{i}').formula= f"=K{i}/PI()"
    
    i+=1
# Update values in columns H and I, 19 should be changed depending on how many rows in Excel.
for i in range(2, 19):
    # print(i)
    if ws.range(f'H{i}').value == 0:
        ws.range(f'H{i}').value = 1E-30
    if ws.range(f'I{i}').value == 0:
        ws.range(f'I{i}').value = 1E-30

# They are the last two cell adn the last cell, Get the values of M17 and M18 after evaluating the formulas
l17_value = ws.range('L17').value
l18_value = ws.range('L18').value

# print(f"Value of L17: {l17_value}")
# print(f"Value of L18: {l18_value}")
arr=[ws.range(f"L{k}").value for k in range(2,19)]
# Check if the value in M17 is greater than the value in M18
def unwrapfun_2(case_value_2):
    match case_value_2:
        case 0:
            for i in range(2, 19):             
                    ws.range(f'M{i}').value =-ws.range(f'L{i}').value
                
        case 1:
            for i in range(2, 19):
                if i>valleies[len(valleies)-1]-1:
                    ws.range(f'M{i}').value =-ws.range(f'L{i}').value
                else:
                    ws.range(f'M{i}').value =ws.range(f'L{i}').value
        case 2:
            for i in range(2, 19):
                if i>valleies[len(valleies)-1]-1:
                    ws.range(f'M{i}').value =-ws.range(f'L{i}').value
                elif i<valleies[len(valleies)-1] and i>peaks[len(peaks)-1]-1:
                    ws.range(f'M{i}').value =ws.range(f'L{i}').value
                else:
                    ws.range(f'M{i}').value =2-ws.range(f'L{i}').value
                
        case 3: 
            for i in range(2, 19):
                if i>valleies[len(valleies)-1]-1:
                    ws.range(f'M{i}').value =-ws.range(f'L{i}').value
                elif i<valleies[len(valleies)-1] and i>peaks[len(peaks)-1]-1:
                    ws.range(f'M{i}').value =ws.range(f'L{i}').value
                elif i<peaks[len(peaks)-1] and i>valleies[len(valleies)-2]-1:
                    ws.range(f'M{i}').value =2-ws.range(f'L{i}').value
                else:
                    ws.range(f'M{i}').value =2+ws.range(f'L{i}').value

# Assuming arr is already defined and contains values from the previous step

def unwrapfun_1(case_value):
    
    
    match case_value:
        case 0:
            for i in range(2, 19):
                ws.range(f'M{i}').value =ws.range(f'L{i}').value
                
        case 1:
            for i in range(2, 19):
                if i>peaks[len(peaks)]-1:
                    ws.range(f'M{i}').value =ws.range(f'L{i}').value
                else:
                    ws.range(f'M{i}').value =2-ws.range(f'L{i}').value
        case 2:
            for i in range(2, 19):
                
                if i>peaks[len(peaks)-1]-1:
                    ws.range(f'M{i}').value =ws.range(f'L{i}').value
                elif i<peaks[len(peaks)-1] and i>valleies[len(valleies)-1]-1:
                    ws.range(f'M{i}').value =2-ws.range(f'L{i}').value
                else:
                    ws.range(f'M{i}').value =2+ws.range(f'L{i}').value
                
        case 3:
            
            for i in range(2, 19):
                
                if i>peaks[len(peaks)-1]-1:
                    ws.range(f'M{i}').value =ws.range(f'L{i}').value
                elif i<peaks[len(peaks)-1] and i>valleies[len(valleies)-1]-1:
                    ws.range(f'M{i}').value =2-ws.range(f'L{i}').value
                elif i<valleies[len(valleies)-1] and i>peaks[len(peaks)-2]-1:
                    ws.range(f'M{i}').value =2+ws.range(f'L{i}').value
                else:
                    ws.range(f'M{i}').value =4-ws.range(f'L{i}').value
        case 4:
            for i in range(2, 19):
                
                if i>peaks[len(peaks)-1]-1:
                    ws.range(f'M{i}').value =ws.range(f'L{i}').value
                elif i<peaks[len(peaks)-1] and i>valleies[len(valleies)-1]-1:
                    ws.range(f'M{i}').value =2-ws.range(f'L{i}').value
                elif i<valleies[len(valleies)-1] and i>peaks[len(peaks)-2]-1:
                    ws.range(f'M{i}').value =2+ws.range(f'L{i}').value
                elif i<peaks[len(peaks)-2] and i>valleies[len(valleies)-2]-1:
                    ws.range(f'M{i}').value =4-ws.range(f'L{i}').value
                else:
                    ws.range(f'M{i}').value =4+ws.range(f'L{i}').value
peaks=[]
for j in range(1, len(arr) - 1):
    if arr[j-1] is not None and arr[j] is not None and arr[j+1] is not None:  # Check if the neighboring elements exist and are not None
        if arr[j] > arr[j+1] and arr[j] > arr[j-1]:# Check if the current element is a peak
            max_row = arr.index(arr[j]) + 2
            peaks.append(max_row)
            
            print(f"peaks of arr[{j}] {arr[j]}, {peaks}")
    else:
        # Handle the case where the previous or next element does not exist
        if arr[j-1] is None:
            print(f"arr[{j-1}] does not exist, arr[{j+1}] {arr[j+1]}")
        if arr[j+1] is None:
            print(f"arr[{j-1}] {arr[j-1]}, arr[{j+1}] does not exist")
valleies=[]
for j in range(1, len(arr) - 1):
    if arr[j-1] is not None and arr[j] is not None and arr[j+1] is not None:  # Check if the neighboring elements exist and are not None
        if arr[j] < arr[j+1] and arr[j] < arr[j-1]:  # Check if the current element is a peak
            mini_row=arr.index(arr[j])+2   
            valleies.append(mini_row)
            print(f"valley of arr[{j}] {arr[j]}, {valleies}")
    else:
        # Handle the case where the previous or next element does not exist
        if arr[j-1] is None:
            print(f"arr[{j-1}] does not exist, arr[{j+1}] {arr[j+1]}")
        if arr[j+1] is None:
            print(f"arr[{j-1}] {arr[j-1]}, arr[{j+1}] does not exist")

case_value_v=len(peaks)+len(valleies)

if l17_value > l18_value:
   unwrapfun_1(case_value_v) 
   print("there is no negative value in retardance")
else:
    unwrapfun_2(case_value_v)
    print("there is some negative value in retardance")        

wb.save(filename)
wb.close()

print(f"The file '{filename}' has been updated and saved.")

