# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 14:45:12 2023

@author: USER
"""
"""
Created on Tue Jan 10 10:30:47 2023

@author: USER
"""

import os
import json
import numpy as np
file_list = os.listdir('C:/Users/USER/.spyder-py3/자료')
#여기에 파일번호를 넣으세요
file_num = 2

dir = "C:/Users/USER/.spyder-py3/자료/"



file_name = []
for file in file_list:
    if file.count(".") == 1: 
        name = file.split('.')[0]
        file_name.append(name)
    else:
        for k in range(len(file)-1,0,-1):
            if file[k]=='.':
                file_name.append(file[:k])
                break
                
print(file_name)
file = file_name[file_num]

#%%
# -*- coding: utf-8 -*-
"""
Spyder Editor


This is a temporary script file.
"""
import xml.etree.ElementTree as ET
tree = ET.parse(dir+file+".xml")

root = tree.getroot()

global p_num
global json_num
global source
global merge_head
sen_num = 1
isAdded = False
table_up2down = False
json_num = 0
p_num = 0
max_sen = 10
P = root.find("BODY").find("SECTION").findall("P")

#%%
def add_sen(p):
    
    text=""
    for i in p.findall("TEXT"):
        if(i.find("CHAR")!=None and i.find("CHAR").text!=None):
            text = text + i.find("CHAR").text.strip()
    return text

def span_loop(P):
    global p_num
    global json_num
    global source
    ## or (file_num==1 and p_num==1037) or (file_num==1 and p_num==2030)
    while(True):
        ##if(file_num==2 and p_num==56):
        ##    p_num=p_num+1
        if(p_num >= len(P)):
            return
        
        if(P[p_num].find("TEXT").find("TABLE")!=None):
            #json_num = json_num + 1
            source="table"
            break
        if(P[p_num].find("TEXT").find("CHAR")==None):
            p_num= p_num+1
            
        else:
            #json_num = json_num + 1
            source="passage"
            break
        
def cell_content(p_list):
    text=""
    for p in p_list:
        text =  text + add_sen(p) + " " 
    return text


def table_sen(table, i):
    
    text = ""
    for j in range(np.array(table).shape[1]):
        text = text +" "+ table[0][j] + " " + table[i][j]
    return text

def table_discriminate(p):
    row_list = p.find("TEXT").find("TABLE").findall("ROW")
    dc = []
    for row in row_list:
        cell_list = row.findall("CELL")
        dc.append(len(cell_list))
    dc.sort()
    reverse_dc = dc.copy()
    reverse_dc.sort(reverse=True)
    if(dc==reverse_dc):
        return "passage"
    else:
        return "table"

def mk_merge_table(p):
    j = int(p.find("TEXT").find("TABLE").get("ColCount"))
    i = int(p.find("TEXT").find("TABLE").get("RowCount"))
    table = [[0 for col in range(j)] for row in range(i)]
    
    for row in p.find("TEXT").find("TABLE").findall("ROW"):
        for cell in row.findall("CELL"):
            col_addr = int(cell.get("ColAddr"))
            row_addr = int(cell.get("RowAddr"))
            table[row_addr][col_addr] = cell_content(cell.find("PARALIST").findall("P")).strip()
    
    return table

def merge_table_sen(table, row, col):
    global merge_head 
    merge_head = 0
    for j in range(col):
        if(table[0][j]==0):
            table[0][j]=table[0][j-1]
    if (0 in table[1]):
        merge_head = 1
        for i in range(2, row):
            for j in range(col):
                if(table[i][j]==0):
                    table[i][j] = table[i][j-1]

def merge_table_sen2(table, row, col):
    global merge_head 
    merge_head = 0
    for j in range(col):
        if(table[0][j]==0):
            table[0][j]=table[0][j-1]
    if (0 in table[1]):
        merge_head = 1
        
    for i in range(1, row):
        for j in range(col):
            if(table[i][j]==0):
                table[i][j]=table[i-1][j]
def mk_merge_table_sen(table, i):
    global merge_head
    
    text = ""
    if(merge_head==1):
        for j in range(np.array(table).shape[1]):
            if(table[1][j]==0):
                text = text + " " + table[0][j] + " " + table[i][j]
            else:
                text = text + " " + table[0][j] +" " + table[1][j] + " " + table[i][j]
    elif(merge_head==0):
        for j in range(np.array(table).shape[1]):
            text = text + " " + table[0][j] + " " + table[i][j]
    return text


def delete_span_table(table):
    for i in range(len(table)):
        for j in range(len(table[i])):
            if('str' in str(type(table[i][j]))):
                if(len(table[i][j].replace(" ", ""))==2):    
                    table[i][j]=table[i][j].replace(" ", "")
    
def check_direction(table, row, col):
    print(table)
    global table_up2down
    for j in range(col-1):
        if table[0][j+1]==0:
            table_up2down = True



#%% 보험설계
# writedata.py
   
f = open("C:/Users/USER/.spyder-py3/"+file+".txt", 'w', encoding='utf-8')
span_loop(P)
while(p_num < len(P)-1):
    json_data = {
"소스": "passage",
"파일명": file+".hwp",
"조번호": "{}".format(json_num),
"장번호": "0",
"절제목": "",
"문서번호": str(file_num),
"장제목": "",
"조제목": "",
"문서제목": file,
"단위번호": "{}-0-0-{}".format(file_num, json_num),
"html": "",
"절번호": "0",
"타입": "passage",
"문장0": file
}   
    
    if(p_num <= len(P)-1 and P[p_num].find("TEXT").find("TABLE")==None):
        
        jo_text=file
        while(p_num <= len(P)-1 and P[p_num].find("TEXT").find("CHAR") != None and sen_num <= max_sen ):
            if(len(add_sen(P[p_num]))==0):
                p_num+=1
                break
            jo_text = jo_text +" "+ add_sen(P[p_num])
            data = "{}".format(add_sen(P[p_num])) 
            ##print("s: %d" % (sen_num))
            json_data["문장{}".format(sen_num)] = data
            sen_num+=1
            p_num+=1
            
            if(p_num <= len(P)-1 and P[p_num].find("TEXT").find("CHAR") != None and P[p_num].find("TEXT").find("TABLE") == None):
                isAdded=True
            
            if(p_num <= len(P)-1 and P[p_num].find("TEXT").find("CHAR") == None and not isAdded and P[p_num].find("TEXT").find("TABLE") == None):
                span_loop(P)
           
                
            if(p_num > len(P)-1 or P[p_num].find("TEXT").find("TABLE")!=None):
                break
            
            
                
            
        jo_text = jo_text
        json_data["조내용"] = jo_text
        json_data["조번호"] = str(json_num)
        json_num+=1
        json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)
        f.write(json_conv)
        f.write("\n")
        sen_num=1
        isAdded=False
        
    if(p_num <= len(P)-1 and P[p_num].find("TEXT").find("TABLE")!=None):
        if(table_discriminate(P[p_num])=="passage"):
            row_list = P[p_num].find("TEXT").find("TABLE").findall("ROW")
            table=[]
            for row in row_list:
                cell_list = row.findall("CELL")
                line = []
                for cell in cell_list:
                    row_content = cell_content(cell.find("PARALIST").findall("P"))
                    line.append(row_content.strip())
                table.append(line)
        
            #table head 중 공백 제거  
            
            delete_span_table(table)
                
        
            for i in range(1, len(row_list)):
                jo_text = file.strip()
                json_data = {
                        "소스": "table",
                        "파일명": file+".hwp",
                        "조번호": "{}".format(json_num),
                        "장번호": "0",
                        "절제목": "",
                        "문서번호": str(file_num),
                        "장제목": "",
                        "조제목": "",
                        "문서제목": file,
                        "단위번호": "{}-0-0-{}".format(file_num, json_num),
                        "html": "",
                        "절번호": "0",
                        "타입": table_discriminate(P[p_num]),
                        "문장0": file
                        }  
        
            
                json_data["문장1"] = table_sen(table, i).strip()
                json_data["조내용"] = json_data["문장0"].strip() + " " + json_data["문장1"].strip()
                json_data["조번호"] = str(json_num)
                json_num= json_num+1
                json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)
        
                f.write(json_conv)
                f.write("\n")
            p_num=p_num+1
        
        elif(table_discriminate(P[p_num])=="table"):
           table =  mk_merge_table(P[p_num])
           row = int(P[p_num].find("TEXT").find("TABLE").get("RowCount"))
           col = int(P[p_num].find("TEXT").find("TABLE").get("ColCount"))
           check_direction(table, row, col)
           
           merge_table_sen(table, row, col)
           
           delete_span_table(table)
           
           
           
           
           if table_up2down:
               
               for i in range(merge_head+1, row):
                   jo_text = file.strip()
                   json_data = {
                           "소스": "table",
                           "파일명": file+".hwp",
                           "조번호": "{}".format(json_num),
                           "장번호": "0",
                           "절제목": "",
                           "문서번호": str(file_num),
                           "장제목": "",
                           "조제목": "",
                           "문서제목": file,
                           "단위번호": "{}-0-0-{}".format(file_num, json_num),
                           "html": "",
                           "절번호": "0",
                           "타입": table_discriminate(P[p_num]),
                           "문장0": file
                           }  

            
                   json_data["문장1"] = mk_merge_table_sen(table, i).strip()
                   json_data["조내용"] = json_data["문장0"].strip() + " " + json_data["문장1"].strip()
                   json_data["조번호"] = str(json_num)
                   json_num= json_num+1
                   json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)
              
                   f.write(json_conv)
                   f.write("\n")
               p_num=p_num+1
               
           else:
               
               table =  mk_merge_table(P[p_num])
               merge_table_sen2(table, row, col)
               
               delete_span_table(table)
               print(table)
               for i in range(row):
                   jo_text = file.strip()
                   json_data = {
                           "소스": "table",
                           "파일명": file+".hwp",
                           "조번호": "{}".format(json_num),
                           "장번호": "0",
                           "절제목": "",
                           "문서번호": str(file_num),
                           "장제목": "",
                           "조제목": "",
                           "문서제목": file,
                           "단위번호": "{}-0-0-{}".format(file_num, json_num),
                           "html": "",
                           "절번호": "0",
                           "타입": table_discriminate(P[p_num]),
                           "문장0": file
                           }  

                   text = ""
                   for j in range(col):
                       text = text + table[i][j].strip() + " "
                   print(text)
                   json_data["문장1"] = text.strip()
                   json_data["조내용"] = json_data["문장0"].strip() + " " + json_data["문장1"]
                  
                   json_data["조번호"] = str(json_num)
                   json_num= json_num+1
                   json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)
                
                   f.write(json_conv)
                   f.write("\n")
               p_num=p_num+1
            
           
               
           
           
    span_loop(P)
    
    

    
f.close()
