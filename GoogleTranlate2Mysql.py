import time
import urllib.request
import sys
import re
import pymysql

typ = sys.getfilesystemencoding()

#to_l,from_l: auto/zh/zh-TW...
def GoogleTranslate(querystr, to_l="zh-TW", from_l="en"):
    
    google_agent = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.165063 Safari/537.36 AppEngine-Google."}
    flag = 'class="t0">'
    tarurl = "http://translate.google.com/m?hl=%s&sl=%s&q=%s" % (to_l, from_l, querystr.replace(" ", "+"))
    
    for error in range(5):
        try:
            request = urllib.request.Request(tarurl, headers=google_agent)
            page = str(urllib.request.urlopen(request).read().decode(typ))
            break;
        except Exception as e:
            print(e)
            continue;
    time.sleep(0.1)      
    target = page[page.find(flag) + len(flag):]
    target = target.split("<")[0]
    return target

#print(GoogleTranslate("speak english"))

def get_regex():
    regex = []
    special_words = ['.*(?:多拉|哆啦)[Aa]夢',
                     '漢堡QQ糖', "M&M's", "\d{2}姨" 
                    ]
    
    special_words = "|".join(special_words)
    regex += [special_words]
    # << 先用中文分開所有字串 >>
    #regex += [r'\b[a-zA-Z]{1,2}\ *號[^\w\b']
    regex += [r'[\d\.]+[合][\d\.]+']
    regex += [r'[\d\.]+[倍元入種切枚包組箱粒支號盒公分升斤束片張重瓦尺年份吋寸度瓶]{1,2}']
    regex += [r'[LMXSlmxs]{1,2}\ *[號]{1,2}']
    regex += [r'[\u4e00-\ufaff /]+']
    # 數字＋單位
    regex += [r'\d+\.?\d*(?:[mM][lL]|[kK][gG]|[cC][mM]|[oO][zZ]|gm|g|[cC][cC]|%)']
    
    #regex += ['[a-zA-Z\d\'\"\.\*\-&~]+']
    
    # << 英文部分處理 >>
    # 數字加一個 " 或 ' 結束 (avex note: 使用 re.Local 時 ' " 無法配合\b判斷, 故要獨立)
    regex += [r'\d+\.?\d*[\"\'%/]']
    # ex, 123 x 456
    regex += [r'\d+\ *[\*xX]\ *\d+']
    # 數字加一個以英文字母結束; 
    regex += [r'\d+\.?\d+\b']
    regex += [r'\d+\.?\d*[A-Za-z]\b']
    regex += [r'\d+\.?\d*[A-Za-z]+']
    
    # 英文
    regex += [r'[a-zA-Z]+\.[a-zA-Z]+\b']
    #regex += [r'\b[a-zA-Z,\.\~]+\b']
    #regex += [r'\b[a-zA-Z]+\b']
    # 大寫英文
    #regex += [r'(?<=[\d\.])[A-Z]+\b|[A-Z]+\b']
    
    # 數字
    regex += [r'\d+\"?\'?']
    
    # 英文含數字
    regex += [r'[a-zA-Z\d\-\+\'\ \"\.~/]+']

    s_reg = "|".join(regex)
    #print(s_reg)
    #r = re.compile(s_reg, re.IGNORECASE)
    r = re.compile(s_reg, re.L)
    
    return r


def split_ch_en_Translate(text):
    result = []
    inputtext = text
    dline = get_regex().findall(inputtext)
    for ele in dline:
        try:
            value = GoogleTranslate(ele)
            result.append(value) 
        except Exception as e:
            value = ele
            result.append(value)
    inputtext = ''.join(result)    
    return inputtext




conn= pymysql.connect(
        host='databda.ddns.net',
        port = 3306,
        user='root',
        passwd='iiibda',
        db ='htc',
        charset='utf8',
        )     

cur = conn.cursor()



#創建數據表
#cur.execute("CREATE TABLE App1_English_Chinese_app_store_comment_ch_tw (id varchar(255),Review_Text varchar(255),translate_title varchar(255),translate_comment varchar(255))")
 
#提取查尋條件的數據
cur.execute("SELECT * FROM App1_English_Chinese_app_store_comment")

#cur.execute("SELECT * FROM App1_English_Chinese_app_store_comment order by id limit 299 offset 701")
#(2013, 'Lost connection to MySQL server during query ([Errno 60] Operation timed out)')


#id,Review Title ,Review_Text ,translate_title ,translate_comment ,ckipTerms ,isEng
#0 , 1            ,2        ,    3              , 4               , 5         , 6 

#將查詢到的紀錄負值給變量lines,循環語句print出
lines = cur.fetchall()
#往下列出n項
#lines = cur.fetchmany(10)
for line in lines:
    #print(line)    
    try:
        Id = line[0]
        Review_Text   = split_ch_en_Translate(line[2])
        translate_title  = split_ch_en_Translate(line[3])
        translate_comment  = split_ch_en_Translate(line[4])     
        
        cur.execute("INSERT IGNORE INTO App1_English_Chinese_app_store_comment_ch_tw VALUES ('"+Id+"','"+Review_Text+"','"+translate_title+"','"+translate_comment+"')")     
        conn.commit()  #提交保存
        
        print("INSERT IGNORE INTO App1_English_Chinese_app_store_comment_ch_tw VALUES ('"+Id+"','"+Review_Text+"','"+translate_title+"','"+translate_comment+"')")
    except Exception as e:
        print(e)
        continue


cur.close()
conn.close() 

print('Mission Complete')