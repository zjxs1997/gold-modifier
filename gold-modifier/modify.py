from tkinter import *
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk

filePath = 'E:\\gold\\gold.gbc'
pmStartAddress = 0x51aaa
# sa[0:6]: hp, wg, wf, sd, tg, tf
# sa[7:9]: type1, type2
# sa[8]:捕获度, sa[9]:经验值
moveStartAddress = 0x42b59


# 从gbc的list数据中获取技能表信息，返回的是三个长度为251的list ml，ll，ol
# ml表示每个宝可梦的升级可学习技能list，元素是二进制代码
# ll对应几级学习该技能， ol则是该宝可梦的技能表在list中的开始地址（偏移）
def readMoveList(dataList, moveStartAddress):
    cnt = 0
    offset = moveStartAddress
    moveList = []
    levelList = []
    offsetList = []
    while cnt < 251:
        offsetList.append(offset)
        tempMoveList = []
        tempLevelList = []
        while dataList[offset] != 0:
            tempLevelList.append(dataList[offset])
            tempMoveList.append(dataList[offset + 1])
            offset += 2
        offset += 1
        while dataList[offset] != 0:
            offset += 1
        offset += 1
        moveList.append(tempMoveList)
        levelList.append(tempLevelList)
        cnt += 1
    
    return moveList, levelList, offsetList

# 返回进化列表
def readEvolveList(dataList, evolveStartAddress):
    cnt = 0
    evolution = []
    way = []
    pm = []
    offset = []

    while cnt < 251:
        offset.append(evolveStartAddress)
        tempe = [dataList[evolveStartAddress]]
        tempw = [dataList[evolveStartAddress+1]]
        tempp = [dataList[evolveStartAddress+2]]
        if dataList[evolveStartAddress] == 0 or dataList[evolveStartAddress] == 5 or dataList[evolveStartAddress+3] == 0:
            evolution.append(tempe)
            way.append(tempw)
            pm.append(tempp)
            if dataList[evolveStartAddress] == 0:
                evolveStartAddress += 1
            else:
                evolveStartAddress += 4
            while dataList[evolveStartAddress] != 0:
                evolveStartAddress += 1
            evolveStartAddress += 1
            cnt += 1
            continue
        theoffset = 3
        while dataList[evolveStartAddress + theoffset] != 0:
            tempe.append(dataList[evolveStartAddress+theoffset])
            tempw.append(dataList[evolveStartAddress+theoffset+1])
            tempp.append(dataList[evolveStartAddress+theoffset+2])
            theoffset += 3
        evolution.append(tempe)
        way.append(tempw)
        pm.append(tempp)
        evolveStartAddress += (theoffset+1)
        while dataList[evolveStartAddress] != 0:
            evolveStartAddress += 1
        evolveStartAddress += 1
        cnt += 1
    return evolution, way, pm, offset

# 返回bytes数据类型的gbc数据
def loadGbcData(filePath=filePath):
    fin = open(filePath, 'rb')
    fileBytes = fin.read(-1)
    fin.close()
    return fileBytes

# 返回pmList,格式如 #001, 妙蛙种子, フシギダネ, Bulbasaur, 草, 毒
def loadTJData(filePath='data\\tujian.txt'):
    fin = open(filePath, encoding='utf-8')
    pmlist = fin.readlines()[1:]
    return pmlist

# 返回关于属性的dict和reverse-dict
def loadType(filePath='data\\type.txt'):
    fin = open(filePath, encoding='utf-8')
    typeDict = dict()
    reverseTypeDict = dict()
    index = 0
    for line in fin:
        sp = line.split()
        typeDict[sp[1]] = int(sp[0])
        reverseTypeDict[int(sp[0])] = index
        index += 1
    fin.close()
    return typeDict, reverseTypeDict

# 读取技能表，返回一个字典，key是二进制代码(str)，value是相应的技能说明list：属性，中文名，日语名，威力，命中，pp，说明
def loadMoveList(filePath='data\\moveData.txt'):
    fin = open(filePath, encoding='utf-8')
    moveList = []
    moveDict = dict()
    reverseMoveDict = dict()
    hexHead = [str(i) for i in range(10)] + ['a','b','c','d','e','f']
    for line in fin:
        line = line.strip()
        if line[0] not in hexHead:
            currentType = line
            continue
        sp = line.split()
        moveDict[eval('0x' + sp[0])] = [currentType] + sp[1:]
        reverseMoveDict[sp[1]] = eval('0x' + sp[0])
        moveList.append(sp)
    
    return moveDict, reverseMoveDict

# 读取道具表 
def loadItemList(filePath='data\\item.txt'):
    fin = open(filePath, encoding='utf-8')
    itemDict = dict()
    reverseItemDict = dict()
    for line in fin:
        sp = line.split()
        val = eval('0x' + sp[0])
        itemDict[val] = sp[1]
        reverseItemDict[sp[1]] = val
    fin.close()
    return itemDict, reverseItemDict

# 用于保存修改后的gbc文件到磁盘上
def storeModifyData(dataList, filePath='E:\\gold-modify.gbc'):
    fout = open(filePath, 'wb')
    dataBytes = bytes(dataList)
    fout.write(dataBytes)
    fout.close()


class modifyClass(Tk):

    def __init__(self):
        super().__init__()
        self.title('gold-modifier')
        self.successLoadData = False
        
        self.pmStartAddress = 0x51aaa
        self.moveStartAddress = 0x42b59
        self.profPmOffsets = [0x4e5bc, 0x4e5fe, 0x4e63a]
        self.evolveStartAddress = 0x42b55
        
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill='both', expand='yes')

        menuBar = Menu(self)
        fileMenu = Menu(menuBar, tearoff=False)
        fileMenu.add_command(label='打开', command=self.loadData)
        fileMenu.add_command(label='另存为', command=self.saveData)

        aboutMenu = Menu(menuBar, tearoff=False)
        aboutMenu.add_command(label='关于', command=self.showAbout)

        menuBar.add_cascade(label='文件', menu=fileMenu)
        menuBar.add_cascade(label='关于', menu=aboutMenu)

        self['menu'] = menuBar

        # 载入数据
        self.pmList = loadTJData()
        self.moveDict, self.reverseMoveDict = loadMoveList()
        self.typeDict, self.reverseTypeDict = loadType()
        self.itemDict, self.reverseItemDict = loadItemList()

        # 增加标签 todo
        self.addPokemonTab()
        self.addProfTab()



    def addPokemonTab(self):
        self.pmFrameRoot = Frame(self)
        self.pmFrameRoot.pack()
        self.pmFrameLeft = Frame(self.pmFrameRoot)
        self.pmFrameLeft.pack(side=LEFT)
        self.pmFrameRight = Frame(self.pmFrameRoot)
        self.pmFrameRight.pack(side=RIGHT)

        self.pmData = Frame(self.pmFrameLeft)
        self.pmData.pack(side=TOP, padx=10, pady=20)
        self.pmRace = Frame(self.pmFrameLeft)
        self.pmRace.pack(side=BOTTOM, padx=20, pady=20)
        self.pmSkill = Frame(self.pmFrameRight)
        self.pmSkill.pack(side=TOP, padx=10, pady=20)
        self.pmEvolve = Frame(self.pmFrameRight)
        self.pmEvolve.pack(side=BOTTOM, padx=10, pady=20)

        # 选择pm的frame
        self.pmLabel = Label(self.pmData, text='选择pokemon')
        self.pmLabel.pack(side=TOP)
        self.pmChosen = ttk.Combobox(self.pmData)
        self.pmChosen['values'] = [''.join(pm.split(', ')[:2]) for pm in self.pmList]
        self.pmChosen.pack(side=BOTTOM)
        self.pmChosen.bind("<<ComboboxSelected>>", self.changePm)

        # 修改种族和属性的frame 
        raceList = ['HP', '物攻', '物防', '速度', '特攻', '特防', '属性1', '属性2', '捕获度', '经验值']
        self.raceLabels = []
        self.raceEntrys = []
        for index, string in enumerate(raceList):
            self.raceLabels.append(Label(self.pmRace, text=string))
            self.raceLabels[index].grid(column=0, row=index)
            if index == 6 or index == 7:
                self.raceEntrys.append(ttk.Combobox(self.pmRace))
                self.raceEntrys[index]['values'] = list(self.typeDict.keys())
                self.raceEntrys[index].bind('<<ComboboxSelected>>', self.changeRace)
            else:
                self.raceEntrys.append(ttk.Entry(self.pmRace))
                self.raceEntrys[index].bind('<Key-Return>', self.changeRace)
            self.raceEntrys[index].grid(column=1, row=index)
        
        self.moveLevelLabel = Label(self.pmSkill, text='等级')
        self.moveNameLabel = Label(self.pmSkill, text='技能')
        self.moveLevelLabel.grid(column=0, row=0)
        self.moveNameLabel.grid(column=1, row=0)
        self.moveLevelList = []
        self.moveNameList = []

        '''
        进化相关 太复杂了不想写了
        self.evolveWayLabel = Label(self.pmEvolve, text='进化方式')
        self.evolveLevelLabel = Label(self.pmEvolve, text='进化等级/使用道具/亲密度方式')
        self.evolvePmLabel = Label(self.pmEvolve, text='进化成的pm')
        self.evolveWayLabel.grid(column=0, row=0)
        self.evolveLevelLabel.grid(column=1, row=0)
        self.evolvePmLabel.grid(column=2, row=0)
        self.evolveWayComboboxes = []
        self.evolveLevelComboboxes = []
        self.evolvePmComboboxes = []
        '''
        self.nb.add(self.pmFrameRoot, text='pokemon')

    
    def addProfTab(self):
        self.profFrame = Frame(self)
        self.profFrame.pack()
        self.profLabelList = []
        self.profPmList = []
        self.profLevelList = []
        self.profItemList = []
        self.profPmNameLabel = Label(self.profFrame, text='宝可梦')
        self.profPmNameLabel.grid(column=1, row=0)
        self.profLevelLabel = Label(self.profFrame, text='等级')
        self.profLevelLabel.grid(column=2, row=0)
        self.profItemLabel = Label(self.profFrame, text='道具')
        self.profItemLabel.grid(column=3, row=0)

        for i in range(3):
            self.profLabelList.append(Label(self.profFrame, text='精灵%d' % (i+1)))
            self.profLabelList[i].grid(column=0, row=i+1)
            pmCombobox = ttk.Combobox(self.profFrame)
            pmCombobox['values'] = [''.join(pm.split(', ')[:2]) for pm in self.pmList]
            self.profPmList.append(pmCombobox)
            self.profPmList[i].grid(column=1, row=i+1)
            self.profPmList[i].bind('<<ComboboxSelected>>', self.changeProfPm)
            self.profLevelList.append(ttk.Entry(self.profFrame))
            self.profLevelList[i].grid(column=2, row=i+1)
            self.profLevelList[i].bind('<Key-Return>', self.changeProfPm)
            itemCombobox = ttk.Combobox(self.profFrame)
            itemCombobox['values'] = list(self.reverseItemDict.keys())
            self.profItemList.append(itemCombobox)
            self.profItemList[i].grid(column=3, row=i+1)
        
        self.nb.add(self.profFrame, text='初始pm')


    
    def showAbout(self):
        messagebox.showinfo('关于', '精灵宝可梦-金（日语版）数据修改器\nmade by xs')
    
    def loadData(self):
        filePath = askopenfilename()
        if filePath == '':
            return
        self.fileBytes = loadGbcData(filePath)
        self.dataList = list(self.fileBytes)
        self.moveList, self.levelList, self.moveOffsetList = readMoveList(self.dataList, self.moveStartAddress)
        self.evolveWayList, self.evolveLevelList, self.evolvePmList, self.evolveOffsetList = readEvolveList(self.dataList, self.evolveStartAddress)
        self.successLoadData = True

        for i in range(3):
            self.profPmList[i].current(self.dataList[self.profPmOffsets[i]]-1)
            self.profLevelList[i].insert(0, str(self.dataList[self.profPmOffsets[i]+1]))
            itemName = self.itemDict[self.dataList[self.profPmOffsets[i] + 2]]
            index = self.profItemList[i]['values'].index(itemName)
            self.profItemList[i].current(index)

        print("successfully load %d bytes data" % (len(self.fileBytes)))

    def saveData(self):
        if not hasattr(self, 'fileBytes'):
            messagebox.showerror('错误', '没有数据可以写入！\n请先载入数据！')
            return
        filePath = asksaveasfilename()
        storeModifyData(self.dataList, filePath)

    def changePm(self, *args):
        if not self.successLoadData:
            return
        pmStr = self.pmChosen.get()
        number = int(pmStr[1:4])
        startAdd = self.pmStartAddress + (number-1)*32
        for i in range(10):
            if i == 6 or i == 7:
                self.raceEntrys[i].current(self.reverseTypeDict[self.dataList[startAdd + i]])
                continue
            self.raceEntrys[i].delete(0, END)
            self.raceEntrys[i].insert(0, str(self.dataList[startAdd + i]))

        for i in range(len(self.moveLevelList)):
            self.moveLevelList[i].grid_forget()
            self.moveNameList[i].grid_forget()
        self.moveLevelList.clear()
        self.moveNameList.clear()
        for i in range(len(self.moveList[number-1])):
            move = self.moveList[number-1][i]
            level = self.levelList[number-1][i]
            levelEntry = ttk.Entry(self.pmSkill)
            levelEntry.insert(0, str(level))
            levelEntry.bind("<Key-Return>", self.changeMoveData)
            self.moveLevelList.append(levelEntry)
            self.moveLevelList[i].grid(column=0, row=i+1)

            moveCombobox = ttk.Combobox(self.pmSkill)
            moveCombobox['values'] = list(self.reverseMoveDict.keys())
            moveCombobox.current(moveCombobox['values'].index(self.moveDict[move][1]))
            moveCombobox.bind("<<ComboboxSelected>>", self.changeMoveData)
            self.moveNameList.append(moveCombobox)
            self.moveNameList[i].grid(column=1, row=i+1)

        '''
        进化相关 但是逻辑太复杂不想写GUI
        for i in range(len(self.evolvePmComboboxes)):
            self.evolvePmComboboxes[i].grid_forget()
            self.evolveWayComboboxes[i].grid_forget()
            self.evolveLevelComboboxes[i].grid_forget()
        self.evolvePmComboboxes.clear()
        self.evolveWayComboboxes.clear()
        self.evolveLevelComboboxes.clear()

        for i in range(len(self.evolvePmList[number-1])):
            if self.evolveWayList[number-1][i] == 0:
                break
            wayCombo = ttk.Combobox(self.pmEvolve)
            wayCombo['values'] = ['升级', '使用道具', '通讯进化', '亲密度进化']
            wayCombo.current(self.evolveWayList[number-1][i] - 1)
            wayCombo.bind('<<ComboboxSelected>>', self.changeEvolve)
            self.evolveWayComboboxes.append(wayCombo)
            self.evolveWayComboboxes[i].grid(column=0, row=i+1)

            if self.evolve
        '''



    def changeRace(self, event):
        pmStr = self.pmChosen.get()
        number = int(pmStr[1:4])
        startAdd = self.pmStartAddress + (number-1)*32
        findError = False
        for i in range(10):
            if i == 6 or i == 7:
                typeStr = self.raceEntrys[i].get()
                self.dataList[startAdd + i] = self.typeDict[typeStr]
                continue
            string = self.raceEntrys[i].get()
            if not string.isnumeric():
                findError = True
                break
            number = int(string)
            if number < 0 or number > 255:
                findError = True
                break
            self.dataList[startAdd + i] = number
        if findError:
            self.raceEntrys[i].delete(0, END)
            self.raceEntrys[i].insert(0, str(self.dataList[startAdd + i]))
            messagebox.showerror('错误', '请输入0-255之间的数字！')
            return

    def changeMoveData(self, event):
        pmStr = self.pmChosen.get()
        number = int(pmStr[1:4])
        offset = self.moveOffsetList[number - 1]
        findError = False
        for i in range(len(self.moveLevelList)):
            level = self.moveLevelList[i].get()
            if not level.isnumeric():
                findError = True
                break
            number = int(level)
            if number < 1 or number > 100:
                findError = True
                break
            self.dataList[offset + i * 2] = number
            moveStr = self.moveNameList[i].get()
            self.dataList[offset + i * 2 + 1] = self.reverseMoveDict[moveStr]
        if findError:
            self.raceEntrys[i].delete(0, END)
            self.raceEntrys[i].insert(0, str(self.dataList[offset + 2 * i]))
            messagebox.showerror('错误', '请输入1-100之间的数字！')

    def changeProfPm(self, event):
        findError = False
        for i in range(3):
            number = int(self.profPmList[i].get()[1:4])
            self.dataList[self.profPmOffsets[i]] = number
            number = int(self.profLevelList[i].get())
            if number < 1 or number > 100:
                findError = True
                break
            self.dataList[self.profPmOffsets[i]+1] = number
            item = self.profItemList[i].get()
            number = self.reverseItemDict[item]
            self.dataList[self.profPmOffsets[i]+2] = number
        if findError:
            self.profLevelList[i].delete(0, END)
            self.profLevelList[i].insert(0, str(self.profPmOffsets[i] + 1))
            messagebox.showerror('错误', '请输入1-100之间的数字！')

    def changeEvolve(self, event):
        pass


if __name__ == '__main__':

    root = modifyClass()
    root.mainloop()



