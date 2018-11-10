from tkinter import *
import tkinter.ttk as ttk

root = Tk()
root.title('test')

nb = ttk.Notebook(root)
nb.pack(fill='both', expand='yes')

f1 = Text(root)
f2 = Text(root)
f3 = Text(root)

f1 = Button(root, text='man')
f2 = Grid()

menuBar = Menu(root)
menuBar.add_command(label='man')
root['menu'] = menuBar

nb.add(f1, text='page1')
nb.add(f2, text='page2')
# nb.add(f3, text='page3')

root.mainloop()
