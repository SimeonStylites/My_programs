# This is a sample Python script
import tkinter as tk

password = '144'

def check_pass():
    if entry.get()=='144':
        print('correct')


def main():
    global space
    global button
    global entry
    root = tk.Tk()
    frame1 = tk.Frame(root)
    frame1.pack(side=tk.TOP)

    frame11 = tk.Frame(frame1)
    frame11.pack(side=tk.LEFT)
    space1 = tk.Canvas(frame11, width=500, height=500, bg='white')
    space1.pack(side=tk.TOP)
    button11 = tk.Button(frame11, text="Press1")
    button11.pack(side=tk.BOTTOM)

    frame12 = tk.Frame(frame1)
    frame12.pack(side=tk.RIGHT)
    space2 = tk.Canvas(frame12, width=500, height=500, bg='black')
    space2.pack(side=tk.TOP)
    button12 = tk.Button(frame12, text="Press2")
    button12.pack(side=tk.BOTTOM)

    frame2 = tk.Frame(root)
    frame2.pack(side=tk.BOTTOM)

    pass_try = tk.StringVar()
    entry = tk.Entry(frame2, textvariable=pass_try)
    entry.pack(side=tk.LEFT)

    button = tk.Button(frame2, text="Press", command=check_pass)
    button.pack(side=tk.LEFT)

    root.mainloop()


if __name__ == '__main__':
    main()
