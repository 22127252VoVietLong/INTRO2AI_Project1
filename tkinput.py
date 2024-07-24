import tkinter as tk



window = tk.Tk()
window.geometry('400x200')
inputFile = tk.StringVar()
filepath = ""

def getFile():
    if (inputFile.get() != ""):
        file = inputFile.get()
    inputFile.set("")
    return text

label = tk.Label(window,text="Input file:")
text = tk.Entry(window, textvariable=inputFile,  bd=2, width=100)
label.pack()
text.pack()
button = tk.Button(window, text="Submit", width=50, command = getFile)
button.pack()
window.mainloop()