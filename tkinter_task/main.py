import tkinter as tk


def check_word():
    global right_guesses
    global lists
    word = entry.get()
    for element in lists[list_number]:
        if element == word:
            right_guesses += 1
            lists[list_number].remove(word)
            counter["text"] = str(right_guesses)
    if right_guesses == 10:
        congratulations()


def congratulations():
    prize["text"] = "Congratulations! Very good memory!\nYour present is in the yoga mat!"


def change_list():
    global list_number
    list_number += 1
    list_number %= len(titles)
    mini_title["text"] = titles[list_number]


def unpack_lists(titles):
    lists = []
    for title in titles:
        file_name = title+".txt"
        with open(file_name) as input:
            for line in input:
                lists.append(line.split())
    return lists


def main():
    global titles
    global mini_title
    global entry
    global counter
    global lists
    global list_number
    global right_guesses
    global prize

    titles = ["African_capitals", "Hobbit_dwarves"]
    lists = unpack_lists(titles)
    list_number = 0
    right_guesses = 0

    root = tk.Tk()
    root.title("Lists_1")
    root.geometry("300x150")

    frame1 = tk.Frame(root)
    frame1.pack(side=tk.TOP)
    mini_title = tk.Label(frame1, text=titles[list_number])
    mini_title.pack(side=tk.LEFT)
    change_list_button = tk.Button(frame1, text="Change_list",command=change_list)
    change_list_button.pack(side=tk.RIGHT)

    frame2 = tk.Frame(root)
    frame2.pack(side=tk.TOP)
    word_try = tk.StringVar()
    entry = tk.Entry(frame2, textvariable=word_try)
    entry.pack(side=tk.LEFT)
    guess_button = tk.Button(frame2, text="Check",command=check_word)
    guess_button.pack(side=tk.RIGHT)

    counter = tk.Label(text=str(right_guesses))
    counter.pack(side=tk.TOP)

    prize = tk.Label(text="Guess more...")
    prize.pack(side=tk.TOP)

    root.mainloop()


if __name__ == '__main__':
    main()
