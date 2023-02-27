import os, glob
import os.path
import json
import numpy as np
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sys



def xml_file_names(input_dir):
    files = os.listdir(input_dir)


    condition = ".xml"
    xml_files = [file for file in files if file.endswith(condition)]
    xml_file_names = [file.rstrip(condition) for file in xml_files]


    print(xml_file_names)
    return xml_file_names

def cleansing_xml(file, config):
    with open(config["input_dir"] + "/"+file+".xml", "r", encoding='UTF8') as f:
        xml_text = f.read()

    new_text = xml_text.replace("<FWSPACE/>", "")
    new_text = new_text.replace("<NBSPACE/>", "")
    new_text = new_text.replace("<TAB/>", "")
    new_text = new_text.replace("<LINEBREAK/>", "")
    with open(config["input_dir"] +"/"+file+".xml", "w", encoding='UTF8') as f:
        f.write(new_text)

def init_rsc(input_dir):
    with open(input_dir + "/config.json", "r", encoding='utf-8') as f:
        contents = f.read()
        while "/*" in contents:
            preComment, postComment = contents.split('/*', 1)
            contents = preComment + postComment.split('*/',1)[1]
        return json.loads(contents.replace("'", '"'))

def preprocess_config(config):
    if not config['usage_title']:
        config['sen_num'] = config['sen_num']-1
        config['max_sen'] = config['max_sen']-1


def multi(P, p_num):

    for text in P[p_num].findall("TEXT"):
        if text.find("CHAR")!=None:
            return text

    return P[p_num].find("TEXT")

#여러가지 text태그 중 TABLE태그를 포함하고 있는 text태그 리턴
def multi_table(P, p_num):

    for text in P[p_num].findall("TEXT"):

        if text.find("TABLE")!=None:
            return text
    return P[p_num].find("TEXT")



def span_loop(P, p_num):


    ## or (file_num==1 and p_num==1037) or (file_num==1 and p_num==2030)
    while(True):
        ##if(file_num==2 and p_num==56):
        ##    p_num=p_num+1

        if(p_num >= len(P)):
            break
        if(P[p_num].find("TEXT")==None):
            p_num=p_num+1
        if(p_num >= len(P)):
            break
        if(P[p_num].find("TEXT").find("PICTURE")!=None ):
            break
        if(multi_container(P, p_num).find("CONTAINER")!=None):

            #json_num = json_num + 1

            break

        if(multi_table(P, p_num).find("TABLE")!=None):

            #json_num = json_num + 1

            break

        if (multi(P, p_num).find("CHAR")==None or len(add_sen(P[p_num]).strip())==0):

            p_num= p_num+1

        else:

            #json_num = json_num + 1


            break

    return p_num
def add_sen(p):

    text=""
    for i in p.findall("TEXT"):
        for chr in i.findall("CHAR"):
            if(chr!=None and chr.text!=None):
                text = text + chr.text

    return text

def combine_syllables(syllables):
    txt = ""
    i = 0
    while i < len(syllables):
        combined=[]
        for j in range(i, len(syllables)):

            if len(syllables[j])==1:
                combined.append(syllables[j])
            else:

                break

        if(len(combined) == 0):
            txt = txt + syllables[i] + " "
            i+=1
        else:
            txt = txt + ''.join(combined) + " "
            i+=len(combined)
    return txt
def container_process(container):
    container_text = ""
    for elem in container.iter():
        if elem.tag == "CHAR" and elem.text != None:
            container_text = container_text + elem.text + " "
    return container_text


def multi_container(P, p_num):


    for text in P[p_num].findall("TEXT"):
        if text.find("CONTAINER")!=None:
            return text
    return P[p_num].find("TEXT")

def cell_content(p_list):
    text=""
    for p in p_list:
        if p.find("TEXT").find("TABLE") != None:
            row_list = p.find("TEXT").find("TABLE").findall("ROW")
            table=[]
            for row in row_list:
                cell_list = row.findall("CELL")
                line = []
                for cell in cell_list:
                    row_content = cell_content(cell.find("PARALIST").findall("P"))
                    line.append(row_content.strip())
                table.append(line)
            for i, row in enumerate(table):
                table[i] = ' '.join(row)
            text = text + ' '.join(table) + " "

        elif(len(add_sen(p).strip())!=0):
            text =  text + add_sen(p) + " "
    return text

def delete_span_table(table):
    for i in range(len(table)):
        for j in range(len(table[i])):
            table[i][j] = combine_syllables(table[i][j].split())

def table_discriminate(tb):
    row_list = tb.findall("ROW")
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

def print_head(table, j, merge_head):

    text=""
    head = ""
    for i in range(merge_head+1):
        if(head!=table[i][j].strip()):
            head=table[i][j].strip()
            text = text + head + " "

    return text

def table_sen(table, i, merge_head):

    text = ""
    for j in range(np.array(table).shape[1]):
        text = text +" "+ print_head(table, j, merge_head).strip() + " " + table[i][j].strip()
    return text


def unmerge_xml_table(table_node, merge_head):


    row_count = int(table_node.attrib["RowCount"])
    col_count = int(table_node.attrib["ColCount"])
    table = [[None for _ in range(col_count)] for _ in range(row_count)]

    for row_i, row in enumerate(table_node.findall("ROW")):
        row_cells = row.findall("CELL")
        for cell in row_cells:
            col_addr = int(cell.attrib["ColAddr"])
            row_addr = int(cell.attrib["RowAddr"])
            col_span = int(cell.attrib["ColSpan"])
            row_span = int(cell.attrib["RowSpan"])
            text = cell_content(cell.find("PARALIST").findall("P"))
            if(row_i==0 and row_span>1):
                merge_head = row_span-1
            for i in range(row_addr, row_addr + row_span):
                for j in range(col_addr, col_addr + col_span):
                    table[i][j] = text

    return table, merge_head
#xml 테이블을 html코드로 만들어주는 함수
def xml_to_html_table(xml_table_node):
    html = '<table>'
    for row in xml_table_node.findall('ROW'):
        html += '<tr>'
        for cell in row.findall('CELL'):
            col_span = int(cell.get('ColSpan', 1))
            row_span = int(cell.get('RowSpan', 1))
            text = cell_content(cell.find("PARALIST").findall("P"))
            html += f'<td colspan="{col_span}" rowspan="{row_span}">{text}</td>'
        html += '</tr>'
    html += '</table>'
    return html

def combine_individual_sentence(P, p_num, max, isAdd):
    max_sen = max
    isAdded = isAdd
    if(p_num <= len(P)-1 and multi(P, p_num).find("CHAR") != None and len(add_sen(P[p_num]).strip())!=0 and P[p_num].find("TEXT").find("TABLE") == None):
        isAdded=True

    if(p_num <= len(P)-1 and (multi(P, p_num).find("CHAR") == None or len(add_sen(P[p_num]).strip())==0) and not isAdded and P[p_num].find("TEXT").find("TABLE") == None):

        p_num = span_loop(P, p_num)
        max_sen+=1
    return p_num, max_sen, isAdded

def process_MERGE_TABLE(tb, row_list, json_format, json_num, config, json_list):
    merge_head=config["merge_head"]


    row = int(tb.get("RowCount"))
    col = int(tb.get("ColCount"))

    table, merge_head = unmerge_xml_table(tb, merge_head)
    delete_span_table(table)





    html = xml_to_html_table(tb)

    if(len(row_list)==1):
        jo_text = json_format["문장0"]
        json_data = json_format.copy()
        json_data["타입"] = "table"
        json_data["소스"] = "passage"
        json_data["문장{}".format(config['sen_num'])] = ' '.join(table[0]).strip()
        json_data["조내용"] = json_data["문장0"].strip() + " " + json_data["문장1"].strip() if config['usage_title'] else json_data["문장0"].strip()
        json_data["조번호"] = str(json_num)
        json_data["html"] = html
        json_num= json_num+1
        json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)
        json_conv = json_conv.replace("\\\"", "\"")
        json_conv = json_conv.replace("\\\\", "\\")
        json_list.append(json_conv)



    for i in range(merge_head+1, len(row_list)):
        jo_text = json_format["문장0"].strip()
        json_data = json_format.copy()

        json_data["타입"] = "table"
        json_data["소스"] = "passage"
        json_data["문장{}".format(config['sen_num'])] = table_sen(table, i, merge_head).strip()
        json_data["조내용"] = json_data["문장0"].strip() + " " + json_data["문장1"].strip() if config['usage_title'] else json_data["문장0"].strip()
        json_data["조번호"] = str(json_num)
        json_data["html"] = html
        json_num= json_num+1
        json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)
        json_conv = json_conv.replace("\\\"", "\"")
        json_conv = json_conv.replace("\\\\", "\\")
        json_list.append(json_conv)
    return json_num

def process_UNMERGE_TABLE(tb, table, json_format, json_num, config, json_list):
    merge_head=config["merge_head"]
    row_list = tb.findall("ROW")
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

    html = xml_to_html_table(tb)
    if(len(row_list)==1):

        json_data = json_format.copy()
        json_data["타입"] = "table"
        json_data["소스"] = "passage"
        json_data["문장{}".format(config['sen_num'])] = ' '.join(table[0]).strip()
        json_data["조내용"] = json_data["문장0"].strip() + " " + json_data["문장1"].strip() if config['usage_title'] else json_data["문장0"].strip()
        json_data["조번호"] = str(json_num)
        json_data["단위번호"] = '{}-0-0-{}'.format(config['file_num'], json_num)
        json_data["html"] = html
        json_num= json_num+1
        json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)
        json_conv = json_conv.replace("\\\"", "\"")
        json_conv = json_conv.replace("\\\\", "\\")
        json_list.append(json_conv)


    for i in range(1, len(row_list)):

        json_data = json_format.copy()
        json_data["타입"] = "table"
        json_data["소스"] = "passage"

        json_data["문장{}".format(config['sen_num'])] = table_sen(table, i, merge_head).strip()
        json_data["조내용"] = json_data["문장0"].strip() + " " + json_data["문장1"].strip() if config['usage_title'] else json_data["문장0"].strip()
        json_data["조번호"] = str(json_num)
        json_data["단위번호"] = '{}-0-0-{}'.format(config['file_num'], json_num)
        json_data["html"] = html
        json_num= json_num+1
        json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)
        json_conv = json_conv.replace("\\\"", "\"")
        json_conv = json_conv.replace("\\\\", "\\")
        json_list.append(json_conv)
    return json_num


def process_EMPTY_TABLE(tb, table, json_format, json_num, config, json_list):
    empty_html = xml_to_html_table(tb)
    json_data = json_format.copy()
    json_data["타입"] = "table"
    json_data["소스"] = "table"

    sen1 = ""
    for row in table:
        for cell in row:
            if(len(cell)!=0):
                sen1 = sen1 + cell.strip() +" "

    json_data["문장{}".format(config['sen_num'])] = sen1.strip()
    json_data["조내용"] = json_data["문장0"].strip() + " " + json_data["문장1"].strip() if config['usage_title'] else json_data["문장0"].strip()
    json_data["조번호"] = str(json_num)
    json_data["단위번호"] = '{}-0-0-{}'.format(config['file_num'], json_num)
    json_data["html"] = empty_html
    json_num= json_num+1
    json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)

    json_conv = json_conv.replace("\\\"", "\'")
    json_conv = json_conv.replace("\\\\", "\\")
    json_list.append(json_conv)
    return json_num


def process_CONTAINER(P, p_num, json_format, json_num, config, json_list):
    json_data = json_format.copy()

    if(p_num <= len(P)-1 and multi_container(P, p_num).find("CONTAINER")!=None):
        if(len(container_process(multi_container(P, p_num).find("CONTAINER"))) != 0):
            json_data["문장{}".format(config['sen_num'])] = container_process(multi_container(P, p_num).find("CONTAINER"))
            json_data["조내용"] = json_data["문장0"].strip()+ " " + json_data["문장1"].strip() if config['usage_title'] else json_data["문장0"]
            json_data["조번호"] = str(json_num)
            json_data['단위번호'] = '{}-0-0-{}'.format(config['file_num'], json_num)
            json_num+=1
            json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)
            json_conv = json_conv.replace("\\\"", "\"")
            json_conv = json_conv.replace("\\\\", "\\")
            json_list.append(json_conv)
        p_num+=1
    return json_num, p_num

def process_PICTURE(P, p_num, json_format, json_num, config, json_list):
    max_sen=config["max_sen"]
    sen_num=config["sen_num"]

    if(p_num <= len(P)-1 and P[p_num].find("TEXT").find("PICTURE") !=None and sen_num <= max_sen):

        json_data = json_format.copy()
        jo_text=json_format["문장0"] if config['usage_title'] else ""
        if(P[p_num].find("TEXT").find("PICTURE").find("SHAPEOBJECT").find("CAPTION")!=None ):

            for cap_p in P[p_num].find("TEXT").find("PICTURE").find("SHAPEOBJECT").find("CAPTION").find("PARALIST").findall("P"):
                if(cap_p.find("TEXT")   !=None):
                    if(cap_p.find("TEXT").find("CHAR")!= None and cap_p.find("TEXT").find("CHAR").text!=None):

                        jo_text = (jo_text +" "+ combine_syllables(add_sen(cap_p).split())).strip()


                        data = "{}".format(add_sen(cap_p)).strip()
                        json_data["문장{}".format(sen_num)] = data
                        sen_num+=1
                   
            jo_text = jo_text
            json_data["조내용"] = jo_text
            json_data["조번호"] = str(json_num)
            json_data["단위번호"] = '{}-0-0-{}'.format(config['file_num'], json_num)
            if len(json_data) > 15 or not config['usage_title']:

                json_num+=1

                json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)
                json_conv = json_conv.replace("\\\"", "\"")
                json_conv = json_conv.replace("\\\\", "\\")
                json_list.append(json_conv)
                sen_num=config['sen_num']
    return json_num

def process_PASSAGE(P, p_num, json_format, json_num, config, json_list):
    if(p_num <= len(P)-1 and multi_table(P, p_num).find("TABLE")==None):
        json_data = json_format.copy()
        isAdded = config["isAdded"]
        max_sen=config["max_sen"]
        sen_num=config["sen_num"]
        jo_text=json_format["문장0"] if config['usage_title'] else ""

        while(p_num <= len(P)-1 and multi(P, p_num).find("CHAR") != None and sen_num <= max_sen ):

            if(len(add_sen(P[p_num]).strip())==0):
                p_num+=1
                break


            #띄어쓰기 없애기
            jo_text = (jo_text +" "+ combine_syllables(add_sen(P[p_num]).split())).strip()

            data = "{}".format(combine_syllables(add_sen(P[p_num]).split())).strip()

            #띄어쓰기 없애기
            if(len(add_sen(P[p_num]).replace(" ", ""))==2):
                data = "{}".format(add_sen(P[p_num]).replace(" ", ""))

            ##print("s: %d" % (sen_num))
            if len(data.strip())>0:
                json_data["문장{}".format(sen_num)] = data.strip()
                sen_num+=1

            p_num+=1
            '''
            if(p_num <= len(P)-1 and multi(P, p_num).find("CHAR") != None and len(add_sen(P[p_num]))!=0 and P[p_num].find("TEXT").find("TABLE") == None):
                isAdded=True

            if(p_num <= len(P)-1 and (multi(P, p_num).find("CHAR") == None or len(add_sen(P[p_num]))==0) and not isAdded and P[p_num].find("TEXT").find("TABLE") == None):

                p_num = span_loop(P, p_num)
                max_sen+=1
                '''
            if config["combining_individual_sentence"]:
                p_num, max_sen, isAdded = combine_individual_sentence(P, p_num, max_sen, isAdded)

            if(p_num > len(P)-1 or multi_table(P, p_num).find("TABLE")!=None or multi_container(P, p_num).find("CONTAINER") != None):
                break




        jo_text = jo_text
        json_data["조내용"] = jo_text.strip()
        json_data["조번호"] = str(json_num)
        json_data["단위번호"] = '{}-0-0-{}'.format(config['file_num'], json_num)

        if len(json_data) > 15:

            json_num+=1

            json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)
            json_conv = json_conv.replace("\\\"", "\"")
            json_conv = json_conv.replace("\\\\", "\\")
            json_list.append(json_conv)
            sen_num=config['sen_num']
            isAdded=False
    return json_num, p_num

def process_TABLE(P, p_num, json_format, json_num, config, json_list):
    isEmpty = config["isEmpty"]
    if(p_num <= len(P)-1 and multi_table(P, p_num).find("TABLE")!=None):

            if(multi(P, p_num).find("CHAR")!=None and multi(P, p_num).find("CHAR").text!=None and len(multi(P, p_num).find("CHAR").text.replace(" ", ""))!=0):

                json_data = json_format.copy()
                if config['usage_title']:
                    json_data["문장1"] = add_sen(P[p_num])
                    jo_text = json_data["문장0"].strip() + " " + json_data["문장1"].strip()
                else:
                    json_data["문장0"] = add_sen(P[p_num])
                    jo_text = json_data["문장0"].strip()

                json_data["조내용"] = jo_text
                json_data["조번호"] = str(json_num)
                json_data["단위번호"] = '{}-0-0-{}'.format(config['file_num'], json_num)

                json_num+=1
                json_conv = json.dumps(json_data,indent = 4, ensure_ascii=False)
                json_conv = json_conv.replace("\\\"", "\"")
                json_conv = json_conv.replace("\\\\", "\\")
                json_list.append(json_conv)

            for t, txt in enumerate(P[p_num].findall("TEXT")):
                for tb_i, tb in enumerate(txt.findall("TABLE")):
                    if tb != None:

                        row_list = tb.findall("ROW")
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
                        for row in table:
                            for cell in row:
                                if(len(cell)==0):
                                    isEmpty = True

                        #공백이 있는 테이블 처리
                        if(isEmpty):
                            json_num = process_EMPTY_TABLE(tb, table, json_format, json_num, config, json_list)
                            isEmpty=False

### p_num가 1증가될때의 코드가 꼭 이부분이여야 하는지 첨이여도되는지 확인

                            continue


                        #unmerge 테이블 처리
                        if table_discriminate(tb)=="passage":
                            json_num = process_UNMERGE_TABLE(tb, table, json_format, json_num, config, json_list)

                        #merged된 테이블 처리
                        elif(table_discriminate(tb)=="table"):
                            json_num = process_MERGE_TABLE(tb, row_list, json_format, json_num, config, json_list)





                    else:
                        if t == len(P[p_num].findall("TEXT"))-1 and tb_i == len(txt.findall("TABLE"))-1:
                            p_num=p_num+1

                        continue


            p_num=p_num+1
    return json_num, p_num



def preprocess(file_name, config):

    f = open(config["output_dir"] +"/"+file_name+".txt", 'w', encoding='utf-8')

    json_list = []
    json_num = config["json_num"]
    p_num = config["p_num"]
    json_format = {
"소스": "passage",
"파일명": file_name +".hwp",
"조번호": "{}".format(json_num),
"장번호": "0",
"절제목": "",
"문서번호": str(file_num),
"장제목": "",
"조제목": "",
"문서제목": file_name,
"단위번호": "{}-0-0-{}".format(config['file_num'], json_num),
"html": "",
"절번호": "0",
"타입": "passage",
"문장0": file_name
}


    tree = ET.parse(config["input_dir"]+"/"+file_name+".xml")
    root = tree.getroot()
    section_list = root.find("BODY").findall("SECTION")

    for i, section in enumerate(section_list):

        P = section.findall("P")
        p_num = span_loop(P, p_num)

        while(p_num <= len(P)-1):
            ##PICTURE 태그가 있는 부분 처리
            json_num = process_PICTURE(P, p_num, json_format, json_num, config, json_list)

            ##CONTAINER 태그가 있는 부분 처리
            json_num, p_num = process_CONTAINER(P, p_num, json_format, json_num, config, json_list)


            #테이블이 없는 일반 단락 부분 처리
            json_num, p_num = process_PASSAGE(P, p_num, json_format, json_num, config, json_list)

            #테이블이 있는 일반 단락 부분 처리
            json_num, p_num = process_TABLE(P, p_num, json_format, json_num, config, json_list)



            p_num = span_loop(P, p_num)
        p_num = 0

    for json in json_list:
        f.write(json)
        f.write("\n")

    f.close()



def parsing(file_name, config):



    cleansing_xml(file_name, config)

    preprocess(file_name, config)

if __name__ == '__main__':

    input_dir = os.path.dirname(os.path.realpath(__file__)) + "/" + sys.argv[1]
    output_dir = os.path.dirname(os.path.realpath(__file__)) + "/" + sys.argv[2]
    config = init_rsc(os.path.dirname(os.path.realpath(__file__)))

    config["input_dir"] = input_dir
    config["output_dir"] = output_dir

    preprocess_config(config)

    file_names = xml_file_names(input_dir)

    #parsing(18, "연구원 정보화 용역사업 보안관리 실무 매뉴얼_2014-02-19_9245_연구원 정보화 용역사업 보안관리 실무 매뉴얼 140217_정보보안실", config)


    for i, file_name in enumerate(file_names):
        file_num = i + config['begin_number']
        config['file_num'] = file_num
        parsing(file_name, config)
