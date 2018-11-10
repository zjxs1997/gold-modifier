from modify import readMoveList, loadGbcData, loadMoveList, loadTJData, filePath, pmStartAddress, moveStartAddress

byteData = loadGbcData(filePath)
dataList = list(byteData)

pmlist = loadTJData()
movedict = loadMoveList()

ml, ll, ol = readMoveList(dataList, moveStartAddress)
appendSet = set()
for i in range(len(ml)):
    for j in range(len(ml[i])):
        key = hex(ml[i][j])[2:]
        if len(key) == 1:
            key = '0' + key
        if key not in movedict and ml[i][j] not in appendSet:
            appendSet.add(ml[i][j])
            print(pmlist[i].strip(), ll[i][j], ml[i][j])


