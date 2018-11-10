fin = open("E:\\gold\\gold.gbc", 'rb')
fileBytes = fin.read(-1)
fin.close()
dataList = list(fileBytes)

startAdd = 0x42b55
cnt = 0
evolution = []
way = []
pm = []
offset = []

while cnt < 251:
    offset.append(startAdd)
    tempe = [dataList[startAdd]]
    tempw = [dataList[startAdd+1]]
    tempp = [dataList[startAdd+2]]
    if dataList[startAdd] == 0 or dataList[startAdd] == 5 or dataList[startAdd+3] == 0:
        evolution.append(tempe)
        way.append(tempw)
        pm.append(tempp)
        if dataList[startAdd] == 0:
            startAdd += 1
        else:
            startAdd += 4
        while dataList[startAdd] != 0:
            startAdd += 1
        startAdd += 1
        cnt += 1
        continue
    # if dataList[startAdd+3] == 0:
    theoffset = 3
    while dataList[startAdd + theoffset] != 0:
        tempe.append(dataList[startAdd+theoffset])
        tempw.append(dataList[startAdd+theoffset+1])
        tempp.append(dataList[startAdd+theoffset+2])
        theoffset += 3
    evolution.append(tempe)
    way.append(tempw)
    pm.append(tempp)
    startAdd += (theoffset+1)
    while dataList[startAdd] != 0:
        startAdd += 1
    startAdd += 1
    cnt += 1

