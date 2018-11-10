import tkinter as tk
from tkinter import ttk
 
win = tk.Tk()
win.title("Python GUI")    # 添加标题

en = ttk.Entry(win)
en.pack()

def a():
    en.pack_forget()

btn = tk.Button(win, text='man', command=a)
btn.pack()

win.mainloop()

