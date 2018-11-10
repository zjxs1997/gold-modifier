import re
import requests

dukanURL = r'https://wiki.52poke.com/wiki/%E5%AE%9D%E5%8F%AF%E6%A2%A6%E5%88%97%E8%A1%A8%EF%BC%88%E6%8C%89%E5%85%A8%E5%9B%BD%E5%9B%BE%E9%89%B4%E7%BC%96%E5%8F%B7%EF%BC%89'

dukanOutputPath = 'tujian.txt'

http = requests.get(dukanURL)
pageText = http.text

gen1Pattern = '<table class="roundy eplist s-关都">(.+?)</table>'
gen2Pattern = '<table class="roundy eplist s-城都">(.+?)</table>'
gen1Tele = re.compile(gen1Pattern, re.S)
gen2Tele = re.compile(gen2Pattern, re.S)
gen1List = gen1Tele.findall(pageText)[0]
gen2List = gen2Tele.findall(pageText)[0]

pmList = []

linePattern = '<tr>(.+?)</tr>'
lineTele = re.compile(linePattern, re.S)
columnPattern = '<td>(.+?)</td>'
columnTele = re.compile(columnPattern, re.S)
typePattern = '<td style.+?><a href=.+?>(.+?)</a>\n</td>'
typeTele = re.compile(typePattern, re.S)
hrefPattern = '<a href=.+?>(.+?)</a>'
hrefTele = re.compile(hrefPattern)


gen1pmLines = lineTele.findall(gen1List)[2:]
for line in gen1pmLines:
    columnData = columnTele.findall(line)
    # cD[1]: 全国图鉴，cD[3]href中内容是中文名，cD[4]日语名，cD[5]英文名
    pmList.append([columnData[1].strip(), hrefTele.findall(columnData[3])[0], columnData[4].strip(), columnData[5].strip()] + typeTele.findall(line))

gen2pmLines = lineTele.findall(gen2List)[2:]
for line in gen2pmLines:
    columnData = columnTele.findall(line)
    # cD[2], 
    pmList.append([columnData[2].strip(), hrefTele.findall(columnData[4])[0], columnData[5].strip(), columnData[6].strip()] + typeTele.findall(line))

fout = open(dukanOutputPath, 'w', encoding='utf-8')
fout.write('全国图鉴, 中文, 日文, 英文, 属性1, 属性2\n')
for line in pmList:
    fout.write(', '.join(line) + '\n')
fout.close()
