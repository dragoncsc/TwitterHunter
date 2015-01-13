from Tkinter import *


class GUI():

    def __init__(self):
        self.master = Tk()
        self.master.geometry("450x150+200+200")
        self.master.title("Twitter Hunter")

    def launchGUI(self, func):

        def show_entry_fields(func1):
            self.quit.grid_remove()
            self.subject.grid_remove()

            func1(e1.get(), e2.get())


        Label(self.master, text="Welcome to Twitter Hunter").grid(row=0, column=0)
        Label(self.master, text="Clearly, you have no life").grid(row=1, column=0)

        Label(self.master, text="First Subject: ").grid(row=2)
        Label(self.master, text="Second Subject: ").grid(row=4)

        e1 = Entry(self.master)
        e2 = Entry(self.master)

        e1.grid(row=2, column=1)
        e2.grid(row=4, column=1)

        self.quit = Button(self.master, text='Quit', command=self.master.quit)
        self.quit.grid(row=6, column=0, sticky=W, pady=4)
        self.subject = Button(self.master, text='Show', command=lambda: show_entry_fields(func))
        self.subject.grid(row=6, column=2, sticky=W, pady=4)
        mainloop()

    def results(self, launch):
        self.master.geometry("600x450")
        Label(self.master, compound=CENTER, text="      ").grid(row=7, column=1)
        self.title = Label(self.master, compound=CENTER, text="Tweet Results: ").grid(row=8, column=1)

        for item in launch:
            Label(self.master, compound=CENTER, text=item).grid(column=1)

        self.quit2 = Button(self.master, compound=CENTER, text='Finish', command=self.master.quit)
        self.quit2.grid(column=1, row=20)
