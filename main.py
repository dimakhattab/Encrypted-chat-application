from tkinter import *
from encrypted_chat import SecureChat
 #THE GUI
window = Tk()
window.title("Secure Chat")
SChat = None

#Connection buttons to initialize and close connection
buttons = Frame(window)
buttons.pack(pady = 5)
b1 = Button(buttons,text='Init connection',width=15,height=1, command=lambda: launch_conn())
b1.pack(side='left')
b2 = Button(buttons,text='Close connection',width=15,height=1, command=lambda: end_conn())
b2.pack(side='right')

#Message window (Middle)
messages = Text(window, state='disabled')
messages.pack(side='top', anchor='s', expand=True)


#Input (bottom)
inputx = Frame(window)
inputx.pack(side='bottom', anchor='s', fill=X)

input_user = StringVar()
input_field = Entry(inputx, text=input_user)
input_field.pack(side='left', anchor='s', fill=X, expand = True)

b3 = Button(inputx,text='Send',width=15,height=1, command=lambda: Enter_pressed())
b3.pack(side='right', fill=None, expand=False)


def bstatus(stat):
    if stat:
        b1["state"] = "disabled"
        b2["state"] = "active"
        input_field.bind("<Return>", Enter_pressed)
    else:
        b1["state"] = "active"
        b2["state"] = "disabled"
        input_field.unbind("<Return>")
        
bstatus(False)

def launch_conn():
    #Window
    tkWindow = Toplevel(window)
    tkWindow.geometry('200x100')  
    tkWindow.title('New connection')

    #HST label and text entry box
    HSTLabel = Label(tkWindow, text="Host").grid(row=0, column=0)
    HST = StringVar()
    HSTEntry = Entry(tkWindow, textvariable=HST).grid(row=0, column=1)  

    #PRT label and PRT entry box
    PRTLabel = Label(tkWindow,text="Port").grid(row=1, column=0)  
    PRT = StringVar()
    PRTEntry = Entry(tkWindow, textvariable=PRT, show='*').grid(row=1, column=1)  

    ## Create button
    ssbuttons = Frame(tkWindow)
    ssbuttons.grid(row=4, column=0, sticky="E")
    #ssbuttons.pack(pady = 5)
    sButton = Button(ssbuttons, text="Server", command=lambda: init_conn(HST.get(), PRT.get(), "server", messages, tkWindow))  
    sButton.pack(side='left')
    cButton = Button(ssbuttons, text="Client", command=lambda: init_conn(HST.get(), PRT.get(), "client", messages, tkWindow))
    cButton.pack(side='right')
      

def init_conn(HST, PRT, mode, messages, pop):
    global SChat
    SChat = SecureChat(HST, PRT, mode, messages)
    if SChat.status:
        bstatus(True)
        pop.destroy()
    else:
        SChat = None
        bstatus(False)

def end_conn():
    global SChat
    SChat = None
    bstatus(False) 

def Enter_pressed(event = None):
    global SChat
    if SChat is None:
        return None
    
    input_get = input_field.get()
    SChat.chat(input_get)
    input_user.set('')
    return "break"


frame = Frame(window)  
frame.pack()

window.mainloop()