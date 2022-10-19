# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 13:36:21 2022

@author: BognarJ


"""



import xml.etree.ElementTree as Xet
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import csv

selection = 0

class SelectionBox(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.selection = tk.IntVar()
        self.selection.set(0)
        self.header = tk.Label(self, text = "Siemens CT Protocol Comparison Tool", font="Helvetic 12 bold")
        self.header.grid(row=0,column=0,columnspan=9)
        self.author = tk.Label(self, text = "Please report any bugs/errors to joshua.bognar@health.qld.gov.au", font='Helvetica 9 italic')
        self.author.grid(row=1,column=0,columnspan=9)
        self.description = tk.Label(self, text = "Select the CT series from the below options and press 'OK.' \n You will then be prompted to open two files which should be .xml files of full protocol exports. \n You will then be prompted to save a file which will detail the differences in the second .xml file compared to the first.")
        self.description.grid(row=2, column=0,columnspan=9)
        
        self.radio1 = tk.Radiobutton(self, text="Force", variable = self.selection, value = 1)
        self.radio1.grid(row=4, column=4, stick=tk.W)
        self.radio2 = tk.Radiobutton(self, text="X", variable = self.selection, value = 2)
        self.radio2.grid(row=4, column=5, stick=tk.W)
        self.button = tk.Button(self, width=12, text="OK",
                                command = lambda : pass_selection(self.selection.get()))
        self.button.grid(row=7,column=0,columnspan=9, pady=(0,10))
        
def pass_selection(x):
    global selection
    selection=x
    root.destroy()
       

#cols = ["Protocol", "Range", "SeriesDescription", "RefKV", "Voltage", "QualityRefMAs", "CustomMAs", "CustomMAsA", "CustomMAsB", "CAREkV",
#        "OptimizeSliderPosition", "Care", "CareDoseType", "CTDIw", "FastAdjustLimitScanTime", "FastAdjustLimitMaxMAs", 
#        "DoseNotificationValueCTDIvol", "DoseNotificationValueDLP", "RotTime", "ScanTime", "Delay", "PitchFactor", "Feed", "SliceEffective",
#        "Acq.", "ReconSliceEffective", "ReconIncr", "NoOfImages", "Kernel", "Window", "ApiId", "Comment1", "Comment2", "Transfer1", "Transfer2",
#        "Transfer3", "SyngoViaTaskflow", "SyngoViaProcessingID", "ScanStart", "ScanEnd", "Pulsing", "PulsingStart", "PulsingEnd", "BestPhase", "PaseStart", "Multiphase" ]



#fpath = "C:/Users/bognarj/OneDrive - Queensland Health/xml Protocol Checker/"
#file = "PL.xml"
#file2 = "PL2.xml"
#out = "text.csv"

### File opening and error handling for accessing an xml file
def get_filename():
    root = tk.Tk()
    root.withdraw
    file = filedialog.askopenfilename(title = 'Select a file',
                                           filetypes = (("xml files", "*.xml*"),
                                                        ("all files", "*.*")),
                                           parent = root)
    try:
        xmlparse = Xet.parse(file)
    except:
        return_error("Unable to open file")
    root.destroy()
    return xmlparse

### File saving and error handling for saving csv output file
def save_file(output_list):
    root = tk.Tk()
    root.withdraw()
    files = [("CSV",'*.csv')]
    save_file = filedialog.asksaveasfilename(filetypes=files, defaultextension=files)
    with open(save_file,'w',encoding="UTF8",newline='') as f:
        writer = csv.writer(f)
        writer.writerows(output_list)
    return None

### Function to ensure xml file selected matches series
def dict_checker(file, series):
    try:
        if series == "s":
            test_dict = s_xml_to_dict(file)
        elif series == "x":
            test_dict = x_xml_to_dict(file)
    except UnboundLocalError:
        return_error("Ensure selected CT series is correct and try again")
    if len(test_dict) == 0:
        return_error("Ensure selected CT series is correct and try again")
    else:
        return test_dict
    
### Generic function to display a message box with an input string and close the program 
def return_error(string):
    root = tk.Tk()
    messagebox.showerror(title = 'Error',
                         message = string,
                         parent = root)
    root.destroy()
    sys.exit()

### Function to convert xml file to dictionary format for Somatom series CT
def s_xml_to_dict(xmlparse):
    
    root = xmlparse.getroot()
    
    recon_cols = set()
        
    for i in root.find("Mode").iter():
        if i.tag == "ReconJob":
            for r in i.iter():
                if r.tag != "ReconJob":
                    recon_cols.add(r.tag)
        
    top_dict = {}
        
    for i in root.find("Mode").iter():
        if i.tag == "ProtocolName":
            name = i.text
            top_dict[name] = {}
            #print(name)
            
        if i.tag == "ScanEntry":
            for j in i.iter():
                if j.tag != "ScanEntry":
                    if j.tag == "Range":
                        range_name = j.text
                        top_dict[name][range_name] = {}
                    else:
                        if j.tag not in recon_cols:
                            top_dict[name][range_name][j.tag] = j.text
                
        if i.tag == "ReconJob":
            for r in i.iter():
                if r.tag != "ReconJob":
    
                    if r.tag =="SeriesDescription":
                        recon_name = r.text
                        top_dict[name][range_name][recon_name] = {}
                    else:
                        top_dict[name][range_name][recon_name][r.tag] = r.text
    return top_dict

### Function to convert xml file to dictionary format for X series CT
def x_xml_to_dict(xmlparse):
    
    def name_get(it):
        for i in it.iter():
            if i.tag == "Name":
                return i.text      
    
    root = xmlparse.getroot()
    
    top_dict = {}
    prot_vals = {}   
    for i in root.find("Mode").iter("ScanEntry"):
        #if i.tag == "ScanEntry":

        if list(i.attrib.values())[0] == "Protocol":
             name = name_get(i)
             top_dict[name] = {}
             for k in list(i):
                 if k.tag != "ScanEntry" and k.text != None:
                     prot_vals[k.tag] = k.text

       
        elif list(i.attrib.values())[0] == "Range":
            range_name = name_get(i)   
            top_dict[name][range_name] = {}
            for k in list(i):
                if k.tag != "ScanEntry" and k.text != None:
                    top_dict[name][range_name][k.tag] = k.text
            for key in list(prot_vals.keys()):
                top_dict[name][range_name][key] = prot_vals[key]
                                 
        elif list(i.attrib.values())[0] == "ReconCompound":
            recon_list = []
            for k in list(i):
                #print(len(k))
                if k.tag == "Name":
                    for l in list(k):
                        recon_list.append(l.text)
                        top_dict[name][range_name][l.text] = {}
                if len(recon_list) == len(k):
                    for pair in zip(recon_list,k):
                        top_dict[name][range_name][pair[0]][k.tag] = pair[1].text
                        #print(pair[1].tag)
                elif len(k) == 1:
                    for recon in recon_list:
                        top_dict[name][range_name][recon][k.tag] = list(k)[0].text

        
        
    return top_dict

### Function to compare two dictionaries of the format created from xml_to_dict functions
def compare_dicts(dict1, dict2):
    output_csv = [["Error","Protocol","Range","Recon","Field","Value 1","Value 2"]]
    for protocol in list(dict1.keys()):
        try:
            views = dict2[protocol]
        except KeyError:
            #print("Protocol not found: " + protocol)
            output_csv.append(["Missing Protocol",protocol])
            continue
            
        for view in list(dict1[protocol].keys()):
            try:
                v = dict2[protocol][view]
            except KeyError:
                #print("Range not found: " + protocol + " -> " + view)
                output_csv.append(["Missing Range",protocol,view])
                continue
            
            for parameter in list(dict1[protocol][view].items()):
                if type(parameter[1]) == dict:
                    try:
                        r = dict2[protocol][view][parameter[0]]
                    except KeyError:
                        #print("Recon not found: " + protocol + " -> " + view + " -> " + parameter[0])
                        output_csv.append(["Missing Recon",protocol,view,parameter[0]])
                        continue
                    
                    for recon_parameter in list(dict1[protocol][view][parameter[0]].keys()):
                        if dict1[protocol][view][parameter[0]][recon_parameter] != dict2[protocol][view][parameter[0]][recon_parameter]:
                            #print("Recon value mismatch: " + protocol + " -> " + view + " -> " + parameter[0] + " -> " + recon_parameter)
                            output_csv.append(["Recon Value Mismatch",protocol,view,parameter[0],recon_parameter,dict1[protocol][view][parameter[0]][recon_parameter],dict2[protocol][view][parameter[0]][recon_parameter]])
                else:
                    if dict1[protocol][view][parameter[0]] != dict2[protocol][view][parameter[0]]:
                        #print("Value mismatch: "  + protocol + " -> " + view + " -> " + parameter[0])
                        output_csv.append(["Value Mismatch",protocol,view,"",parameter[0],dict1[protocol][view][parameter[0]],dict2[protocol][view][parameter[0]]])   
    return output_csv
 
root = tk.Tk()
root.resizable(False,False)
SelectionBox(root).pack(side='top', fill='both', expand=True)
root.mainloop()

#f1 = get_filename()
#f2 = get_filename()

dict1 = None
dict2 = None

if selection == 0:
    #print('No Selection')
    return_error("No CT series selected")
    #Message box and close

elif selection == 1:
    #print("Somatom series selected")
    dict1 = dict_checker(get_filename(), "s")
    dict2 = dict_checker(get_filename(), "s")
        
elif selection == 2:
    #print("X series selected")
    dict1 = dict_checker(get_filename(), "x")
    dict2 = dict_checker(get_filename(), "x")
    #test_dict = test_fun(f1)


save_file(compare_dicts(dict1, dict2))

#test_dict1 = xml_to_dict(f1)
#test_dict2 = xml_to_dict(f2)

#output = compare_dicts(test_dict1, test_dict2)

#save_file(output)