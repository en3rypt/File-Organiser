from tkinter import *
from tkinter import messagebox, ttk, filedialog
import os
import shutil
import time
import matplotlib.figure
import matplotlib.patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
from pathlib import Path
from formats import *
from datetime import datetime

###########################GRAPH###############################
###############################################################
##### Threading
def refresh():
    main.update()
    main.after(1000, refresh)


def start_graph():
    refresh()
    threading.Thread(target=graph).start()


def check1(path, formats):
    k = 0
    for format in formats:
        n = str(format)
        if path.endswith(str(format)) or path.endswith(str(format).lower()):
            k += 1

    return k


def graph():
    global total_size,frame21
    try:
        frame21.destroy()
        frame21 = Frame(tab2, relief=SUNKEN, width=999, height=450, bd=3)
        frame21.place(x =0,y=0,height = 444,width = 998) #grid(row=0, column=0, sticky='ew')
    except:
        pass
    refresh()
    vc = 0
    oc = 0
    ic = 0
    ac = 0
    cc = 0
    ec = 0
    fc = 0
    total_size = 0
    la = Label(frame21, text='LOADING FILE DISTRIBUTION', font="Calibri 50")
    la.pack()
    progress = ttk.Progressbar(frame21, orient=HORIZONTAL, length=500, mode='determinate')
    progress.pack()
    total = len(contents)
    length = 0
    for paths in contents:
        for path in contents[paths]:
            total_size += os.stat(path).st_size
            vc += check1(path, video_formats)
            for other in other_formats:
                oc += check1(path, other)

            ic += check1(path, image_formats)

            ec += check1(path, exe_formats)

            ac += check1(path, audio_formats)

            cc += check1(path, compressed_formats)
            fc += check1(path, files_formats)
        length += 100 / total
        progress['value'] = length
    progress.destroy()
    la.config(text="FILE DISTRIBUTION", font="Calibri 30")
    fig = matplotlib.figure.Figure(figsize=(7, 3.5))
    fig.patch.set_facecolor('#F0F0F0')
    ax = fig.add_subplot(111)
    label = [f"VIDEO FILES = {vc}", f"IMAGE FILES = {ic}", f"DOCUMENTS = {fc}", f"AUDIO FILES = {ac}" , f"COMPRESSED FILES = {cc}", f"APPLICATIONS = {ec}", f"OTHERS = {oc}"]
    size = [vc, ic, fc, ac, cc, ec, oc]
    l=['','','','','','','']

    for i in range(len(size)-1,-1,-1):
        if size[i] ==0:
            label.pop(i)
            l.pop(i)
    for i in range(size.count(0)):
        size.remove(0)

    fig.suptitle("")
    ax.pie(size, labels=l)
    circle = matplotlib.patches.Circle((0, 0), 0.7, color='#F0F0F0')
    ax.add_artist(circle)
    chartBox = ax.get_position()
    ax.set_position([chartBox.x0, chartBox.y0, chartBox.width * 1, chartBox.height])
    ax.legend(loc='upper center', labels=label, bbox_to_anchor=(-0.35, 0.8), shadow=True, ncol=1)
    canvas = FigureCanvasTkAgg(fig, master=frame21)
    canvas.get_tk_widget().pack()
    canvas.draw()
    l21 = Label(frame21, text=f'Total Size of selected files:  {get_size(None,total_size)}', font="15")
    l21.pack()
    if b32["state"] == "disabled":
        b32['state'] = NORMAL




###############################################################
# calling  next page

def insert_tree(abspath):
    try:
        root_node = tree.insert('', 'end', abspath, text=abspath, open=True)
        process_directory_new(root_node, abspath)
    except PermissionError:
        messagebox.showinfo('PermissionError', f'[WinError 5] Access is denied: {abspath}')


def process_directory_new(parent, path):
    msg_folder = ''
    msg_file = ''
    try:
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            if os.path.isdir(abspath):
                if abspath not in contents:
                    contents[abspath] = []
                    oid = tree.insert(parent, 'end', abspath, text=p, open=False)
                    process_directory_new(oid, abspath)
                else:
                    msg_folder += abspath + '\n'
            else:
                if abspath not in contents[path]:
                    contents[path].append(abspath)
                else:
                    msg_file += abspath + '\n'
    except PermissionError:
        messagebox.showinfo('PermissionError', f'[WinError 5] Access is denied: {path}')

    if msg_folder:
        messagebox.showinfo('FOLDER(S) ALREADY ADDED:', msg_folder)
    if msg_file:
        messagebox.showinfo('FILE(S) ALREADY ADDED:', msg_file)


def browser_folder():
    root2 = Toplevel(main)
    root2.withdraw()
    folder = filedialog.askdirectory()
    if folder:
        folder = os.path.abspath(folder)
        if folder in contents:
            messagebox.showinfo("FOLDER ALREADY ADDED!", folder)
        else:
            contents[folder] = []
            insert_tree(folder)

    root2.mainloop()

def select_dest():
    global dest
    root2 = Toplevel(main)
    root2.withdraw()
    dest = filedialog.askdirectory()
    size = 0
    if dest:
        parent = dest[0]
        for i in contents:
            if parent in i:
                for path in contents[i]:
                    size+= os.path.getsize(path)
        total, used, free = shutil.disk_usage(parent+":/")
        if (total_size - size < free):
            dest_str.set(dest)
        else:
            messagebox.showinfo("WARNING!", f"Folder Size not enough\nTotal space available in {parent} = {get_size(None,free)}\nTotal size of selected files = {get_size(None,total_size)}")
    root2.mainloop()


def display_tree1():
    pass


def gettype(path):
    return path.split('.')[-1]


def getdate(path):
    return time.ctime(os.path.getctime(path))


def get_size(path, ns=None):
    size =0
    if path:
        size = os.path.getsize(path)
    KB = 1024.0
    MB = KB * KB
    GB = MB * KB
    if ns != None and ns >= 0:
        size = ns
    if size >= GB:
        return ('{:,.1f} GB').format(size / GB)
    elif size >= MB:
        return ('{:,.1f} MB').format(size / MB)
    elif size >= KB:
        return ('{:,.1f} KB').format(size / KB)
    else:
        return ('{} bytes').format(size)


def get_folder_size(path):
    total_size = 0
    total_file = 0
    total_folder = 0
    for path, dirs, files in os.walk(path):
        for dir1 in dirs:
            fp = os.path.join(path, dir1)
            if fp in contents:
                total_folder += 1
        for f in files:
            fp = os.path.join(path, f)
            if path in contents:
                if fp in contents[path]:
                    total_size += os.path.getsize(fp)
                    total_file += 1
    return total_size, total_file, total_folder


def selectItem(a):
    node = tree.focus()
    size, file, folder = get_folder_size(node)
    l1.configure(text='Name: {}'.format(os.path.basename(node)))
    l2.configure(text='Location:   {}'.format(node))
    l3.configure(text='Contains:   {} File(s), {} Folder(s)'.format(file, folder))
    l4.configure(text='Size:            {} ({} bytes)'.format(get_size(None, size), size))
    l5.configure(text='File:')
    l6.configure(text='Location:')
    l7.configure(text='Size:')
    l8.configure(text='Modified:')
    for i in tree1.get_children():
        tree1.delete(i)
    for path in os.listdir(node):
        abspath = os.path.join(node, path)

        if abspath in contents[node]:
            path_type = abspath.split('.')[-1]
            pa = time.ctime(os.path.getctime(abspath)).split(' ')
            path_date = pa[-3] + '-' + pa[1] + '-' + pa[-1] + ' ' + pa[-2].split(':')[0] + ':' + pa[-2].split(':')[1]
            path_size = get_size(abspath)
            tree1.insert('', 'end', abspath, text=os.path.basename(abspath), values=(path_date, path_type, path_size),
                         open=False)


def view_info(a):
    node = tree1.focus()
    pa = time.ctime(os.path.getctime(node)).split(' ')
    path_date = pa[-3] + '-' + pa[1] + '-' + pa[-1] + ' ' + pa[-2].split(':')[0] + ':' + pa[-2].split(':')[1]
    path_size = get_size(node)
    l5.configure(text='File: {}'.format(os.path.basename(node)))
    l7.configure(text='Size:            {} ({} bytes)'.format(path_size, os.path.getsize(node)))
    l6.configure(text='Location:   {}'.format(node))
    l8.configure(text='Modified:   {}'.format(path_date))
    # tree.selection_remove(tree.focus())


def check_empty(parent):
    paths = tree.get_children(parent)
    for path in paths:
        if os.path.isdir(path):
            check_empty(path)
        if path in contents:
            if not (contents[path] or tree.get_children(path)):
                contents.pop(path)
                tree.delete(path)


def remove_element():
    node = tree1.focus()
    if node:
        contents[tree.focus()].remove(node)
        tree1.delete(node)
        paths = tree.get_children(tree.focus())
        if paths:
            count = 0
            for path in paths:
                if (contents[path]):
                    pass
                else:
                    count += 1

            if count == len(paths):
                contents.pop(tree.focus())
                tree.delete(tree.focus())
        else:
            if contents[tree.focus()]:
                pass
            else:
                contents.pop(tree.focus())
                tree.delete(tree.focus())

    else:
        messagebox.showinfo("Warning", "Select a file to remove!")
    check_empty(None)


def recursive_remove(paths):
    for path in paths:
        if os.path.isdir(path):
            recursive_remove(tree.get_children(path))
            if path in contents:
                contents.pop(path)


def remove_folder():
    node = tree.focus()
    if node:
        recursive_remove(tree.get_children(node))
        l1.configure(text='Name:')
        l2.configure(text='Location:')
        l3.configure(text='Contains:')
        l4.configure(text='Size:')
        l5.configure(text='File:')
        l6.configure(text='Location:')
        l7.configure(text='Size:')
        l8.configure(text='Modified:')
        for i in tree1.get_children():
            tree1.delete(i)
        tree.delete(node)
        contents.pop(node)
    else:
        messagebox.showinfo("Warning", "Select a folder to remove!")
    check_empty(None)

def get_str():
    s = ""
    q = ""
    if CheckVar1.get():
        s+= "Audio Files\n"
    if CheckVar2.get():
        s+= "Video Files\n"
    if CheckVar3.get():
        s += "Image Files\n"
    if CheckVar4.get():
        s += "Executable Files\n"
    if CheckVar5.get():
        s += "Documents\n"
    if CheckVar6.get():
        s += "Compressed Files\n"
    if CheckVar7.get():
        s += "System Files\n"
    if CheckVar8.get():
        s += "Plugin Files\n"
    if CheckVar9.get():
        s += "Developer Files\n"
    if CheckVar10.get():
        s += "Backup Files\n"
    if CheckVar11.get():
        s += "Other Files\n"
    if CheckVar12.get():
        s += "Combine remaining files as Misc Files\n"
    if s:
        q = "Selected File Formats:\n"
        q = q+s
    q+="\n"
    if lis.get(0,lis.size()):
        q+="Selected Custom File Formats:\n"
        for i in lis.get(0,lis.size()):
            q+=f"{i}\n"
    q+="\n"
    if lis0.get(0,lis0.size()):
        q+="Selected Exception File formats:\n"
        for i in lis0.get(0,lis0.size()):
            q+=f"{i}\n"

    return q


######### CHANGE PAGE ###############
def next_tab1(prev, curr):
    count = 0
    for i in contents:
        if contents[i]:
            count += 1
    if count:
        nb.tab(curr, state='normal')
        nb.select(curr)
        start_graph()
        nb.tab(prev, state='disabled')
    else:
        messagebox.showinfo('ALERT!', 'Choose files/folders to organise')

def next_tab2(prev,curr):
    if dest_str.get():
        nb.tab(curr, state='normal')
        nb.select(curr)
        nb.tab(prev, state='disabled')
    else:
        messagebox.showinfo('ALERT!', 'Choose destination folder to proceed.')


def next_tab3(prev,curr):
    arr = lis.get(0,lis.size())
    if (CheckVar1.get() or CheckVar2.get() or CheckVar3.get() or CheckVar4.get() or CheckVar5.get() or CheckVar6.get() or CheckVar7.get() or CheckVar8.get() or CheckVar9.get() or CheckVar10.get() or CheckVar11.get() or CheckVar12.get() or arr):
        string = get_str()
        answer = messagebox.askyesno(title='Confirmation',message=string)
        if answer:
            nb.tab(curr, state='normal')
            nb.select(curr)
            nb.tab(prev, state='disabled')
            start_organise()

    else:
        messagebox.showinfo('ALERT!', 'Select Formats to organise')

################################################
############ PREVIOUS #######################
def previous_tab(prev, curr):
    nb.tab(prev, state='normal')
    nb.select(prev)
    nb.tab(curr, state='disabled')

############################################
def check_ext(exn):
    if exn in audio_formats:
        return True
    elif exn in video_formats:
        return True
    elif exn in exe_formats:
        return True
    elif exn in files_formats:
        return True
    else:
        for i in image_formats:
            if exn in i:
                return True

        for i in other_formats:
            if exn in i:
                return True
        return False


def add_ext():
    c_ext = ext.get()
    cus = lis.get(0,lis.size())
    ex = lis0.get(0,lis0.size())
    if (c_ext):
        if c_ext not in cus:
            if check_ext(c_ext.upper()):
                if c_ext not in ex:
                    lis.insert(END, c_ext)
                    ext.set("")
                else:
                    messagebox.showinfo('ALERT!', 'Format already added in Exceptions!')
                    ext.set("")
            else:
                messagebox.showinfo('ALERT!', 'Enter a valid format.')
                ext.set("")
        else:
            messagebox.showinfo('ALERT!', 'Extension already added.')
            ext.set("")

    else:
        messagebox.showinfo('ALERT!', 'Enter an extension to add.')

def add_exp():
    c_ext = exp.get()
    cus = lis0.get(0,lis0.size())
    ex = lis.get(0,lis.size())
    if (c_ext):
        if c_ext not in cus:
            if check_ext(c_ext.upper()):
                if c_ext not in ex:
                    lis0.insert(END,c_ext)
                    exp.set("")
                else:
                    messagebox.showinfo('ALERT!', 'Format already added in Custom Extension!')
                    exp.set("")
            else:
                messagebox.showinfo('ALERT!', 'Enter a valid format.')
                exp.set("")
        else:
            messagebox.showinfo('ALERT!', 'Extenssion already added.')
            exp.set("")

    else:
        messagebox.showinfo('ALERT!', 'Enter an extension to add.')

##########################
def create_folder():
    global selected_formats,combined_formats
    selected_formats = {}
    combined_formats=[]
    destination = dest_str.get()
    extensions = lis.get(0, lis.size())
    lis1 = [CheckVar1, CheckVar2, CheckVar3, CheckVar4, CheckVar5, CheckVar6, CheckVar7, CheckVar8, CheckVar9, CheckVar10, CheckVar11, CheckVar12]
    names = ["Audio Files", "Video Files", "Image Files", "Executable Files", "Documents", "Compressed Files", "System Files", "Plugin Files", "Developer Files","backup Files", "Other Files", "MISC Files"]
    formats = [audio_formats, video_formats, image_formats,exe_formats,files_formats,compressed_formats,system_formats,plugin_formats,developer_formats,backup_formats,other_files,[]]
    for e in extensions:
        n = destination+"/"+e.split(".")[-1]
        if not os.path.exists(n):
            os.mkdir(n)
            lis2.insert(END,f"[CREATE]  : Created new folder '{Path(n)}'")
        else:
            lis2.insert(END,f"[SKIPPED] : '{Path(n)}' Folder already exists")

    for i in range(1,12):
        if lis1[i-1].get():
            selected_formats[names[i-1]] = formats[i-1]
            n = destination + "/" + names[i-1]
            if not os.path.exists(n):
                os.mkdir(n)
                lis2.insert(END,f"[CREATE]  : Created new folder '{Path(n)}'")
            else:
                lis2.insert(END,f"[SKIPPED] : '{Path(n)}' Folder already exists")
        elif CheckVar12.get():
            combined_formats.append(formats[i-1])
    if CheckVar12.get():
        n = destination + "/" + "Combined Files"
        if not os.path.exists(n):
            os.mkdir(n)
            lis2.insert(END, f"[CREATE]  : Created new folder '{Path(n)}'")
        else:
            lis2.insert(END, f"[SKIPPED] : '{Path(n)}' Folder already exists")




def check_path(path,i):
    new_source = os.path.splitext(path)[0] + str(i) + "." + os.path.splitext(path)[-1]
    if os.path.exists(new_source):
        return check_path(path,i+1)
    else:
        return i


##########
def refresh1():
    main.update()
    main.after(1000, refresh1)


def start_organise():
    refresh()
    threading.Thread(target=organise).start()
##########
def organise():
    refresh()
    create_folder()
    destination = dest_str.get()
    exceptions = lis0.get(0,lis0.size())
    extensions = lis.get(0,lis.size())
    total = len(contents)
    length = 0
    for dir in contents:
        for path in contents[dir]:
            lis2.insert(END, f"[MOVING]  : '{Path(path)}'")
            ex = os.path.splitext(path)[-1]
            if ex.upper() in exceptions or ex.lower() in exceptions:
                lis2.insert(END, f"[SKIPPED] : Exception file encountered  '{Path(path)}'")
            elif ex.upper() in extensions or ex.lower() in extensions:
                n_source = destination+"/"+ex.split(".")[-1] + "/" + os.path.basename(path)
                if os.path.exists(n_source):
                    lis2.insert(END, f"[EXISTS]  : File already exists in destination folder '{os.path.basename(path)}'")
                    n_source = check_path(n_source, 1)
                    new_path = os.path.splitext(path)[0] + str(n_source) + "." + os.path.splitext(path)[-1]
                    os.rename(path, new_path)
                    lis2.insert(END, f"[RENAMED] : File renamed to '{os.path.basename(new_path)}'")
                else:
                    new_path = path
                dest = shutil.move(new_path, destination+"/"+ex.split(".")[-1])
                lis2.insert(END, f"[SUCCESS]  : File Moved to '{Path(dest)}'")
            elif selected_formats:
                for i in selected_formats:
                    if ex.upper() in selected_formats[i] or ex.upper() in selected_formats[i]:
                        n_source = destination + "/" + i + "/" + os.path.basename(path)
                        if os.path.exists(n_source):
                            lis2.insert(END,f"[EXISTS]  : File already exists in destination folder '{os.path.basename(path)}'")
                            n_source = check_path(n_source, 1)
                            new_path = os.path.splitext(path)[0] + str(n_source) + "." + os.path.splitext(path)[-1]
                            os.rename(path, new_path)
                            lis2.insert(END, f"[RENAMED] : File renamed to '{os.path.basename(new_path)}'")
                        else:
                            new_path = path
                        dest = shutil.move(new_path, destination + "/" + i)
                        lis2.insert(END, f"[SUCCESS]  : File Moved to '{Path(dest)}'")
                        break

            elif combined_formats:
                folder = "Combined Files"
                for i in combined_formats:
                    pass
                    if ex.upper() in i or ex.upper() in i:
                        n_source = destination + "/" + folder + "/" + os.path.basename(path)
                        if os.path.exists(n_source):
                            lis2.insert(END,f"[EXISTS]  : File already exists in destination folder '{os.path.basename(path)}'")
                            n_source = check_path(n_source, 1)
                            new_path = os.path.splitext(path)[0] + str(n_source) + "." + os.path.splitext(path)[-1]
                            os.rename(path, new_path)
                            lis2.insert(END, f"[RENAMED] : File renamed to '{os.path.basename(new_path)}'")
                        else:
                            new_path = path
                        dest = shutil.move(new_path, destination + "/" + folder)
                        lis2.insert(END, f"[SUCCESS]  : File Moved to '{Path(dest)}'")
                        break
            else:
                lis2.insert(END, f"[ERROR]  : File not moved '{Path(path)}'")
            length += 100 / total
            progress1['value'] = length

    lis2.insert(END, f"[SUCCESS]  : Task Completed")
##########################
def log():
    d = "C:/LOGS"
    if not os.path.exists(d):
        os.mkdir(d)
    now = datetime.now()
    folder = now.strftime("FOLOGS_%m-%d-%Y_%H-%M-%S")
    f = open(f"C:/LOGS/{folder}.txt","w")
    txt = lis2.get(0,lis2.size())
    for i in txt:
        f.write(f"{i}\n")
    f.close()
    messagebox.showinfo('ALERT!', 'Logs created successfully')


def exit():
    main.destroy()

def organiser_page():
    global contents,w32,  progress1, tree, tree1, l1, l2, l3, l4, l5, l6, l7, l8, nb, dest_str, frame21, lis2, tab2, e01, b32, ext, lis, exp, lis0
    global CheckVar1, CheckVar2, CheckVar3, CheckVar4, CheckVar5, CheckVar6, CheckVar7, CheckVar8, CheckVar9, CheckVar10, CheckVar11, CheckVar12
    dest_str = StringVar()
    ext = StringVar()
    exp = StringVar()

    CheckVar1 = IntVar()
    CheckVar2 = IntVar()
    CheckVar3 = IntVar()
    CheckVar4 = IntVar()
    CheckVar5 = IntVar()
    CheckVar6 = IntVar()
    CheckVar7 = IntVar()
    CheckVar8 = IntVar()
    CheckVar9 = IntVar()
    CheckVar10 = IntVar()
    CheckVar11 = IntVar()
    CheckVar12 = IntVar()

    contents = {}
    rows = 0
    while rows < 50:
        main.rowconfigure(rows, weight=1)
        main.columnconfigure(rows, weight=1)
        rows += 1
    nb = ttk.Notebook(main)
    nb.grid(row=0, column=0, columnspan=55, rowspan=55, sticky='NESW')

    # SOURCE FOLDER //  TAB 1
    tab1 = ttk.Frame(nb)
    nb.add(tab1, text="Source folder")
    #############################
    #            TREE VIEW 1
    tree = ttk.Treeview(tab1, height=28)
    tree.column("#0", width=300, minwidth=300, stretch=NO)
    ysb = Scrollbar(tab1, orient=VERTICAL, command=tree.yview)
    xsb = Scrollbar(tab1, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscroll=ysb.set, xscroll=xsb.set)
    tree.heading("#0", text="Catalog", anchor=W)
    tree.grid(row=0, column=0)
    tree.bind('<<TreeviewSelect>>', selectItem)
    ysb.grid(row=0, column=1, sticky='ns')
    xsb.grid(row=1, column=0, sticky='ew')

    ############################
    #               TREEVIEW 2
    frame0 = Frame(tab1, relief=SUNKEN, width=675, height=100, bd=3)
    frame0.place(x=320, y=0)
    l1 = Label(frame0, text='Name: ', font=('arial', 15))
    l1.place(x=0, y=0)

    l2 = Label(frame0, text='Location: ')
    l2.place(x=0, y=30)

    l3 = Label(frame0, text='Contains: ')
    l3.place(x=0, y=50)

    l4 = Label(frame0, text='Size: ')
    l4.place(x=0, y=70)

    bb1 = Button(frame0, text='remove folder', command=remove_folder)
    bb1.place(x=560, y=60)

    frame1 = Frame(tab1)
    frame1.grid(row=0, column=2)
    tree1 = ttk.Treeview(frame1, height=17)
    tree1["columns"] = ("one", "two", "three")
    tree1.column("#0", width=330, minwidth=270, stretch=NO)
    tree1.column("one", width=125, minwidth=50, stretch=NO)
    tree1.column("two", width=100, minwidth=50)
    tree1.column("three", width=100, minwidth=50, stretch=NO)
    ysb = Scrollbar(frame1, orient=VERTICAL, command=tree1.yview)
    xsb = Scrollbar(frame1, orient=HORIZONTAL, command=tree1.xview)
    tree1.configure(yscroll=ysb.set, xscroll=xsb.set)
    tree1.heading("#0", text="Name", anchor=W)
    tree1.heading("one", text="Date modified", anchor=W)
    tree1.heading("two", text="Type", anchor=W)
    tree1.heading("three", text="Size", anchor=W)
    tree1.grid(row=0, column=0)
    ysb.grid(row=0, column=1, sticky='ns')
    xsb.grid(row=1, column=0, sticky='ew')
    tree1.bind('<<TreeviewSelect>>', view_info)

    frame2 = Frame(tab1, relief=SUNKEN, width=675, height=110, bd=3)
    frame2.place(x=320, y=485)
    ####
    l5 = Label(frame2, text='File: ', font=('arial', 15))
    l5.place(x=50, y=0)
    l6 = Label(frame2, text='Location: ')
    l6.place(x=0, y=40)

    l7 = Label(frame2, text='Size: ')
    l7.place(x=0, y=60)

    l8 = Label(frame2, text='Modified: ')
    l8.place(x=0, y=80)
    bb2 = Button(frame2, text='remove', command=remove_element)
    bb2.place(x=600, y=60)
    ####

    b2 = Button(tab1, text="Next", command=lambda: next_tab1(tab1, tab2))
    b2.place(x=900, y=620)


    b4 = Button(tab1, text="Browse folders", command=browser_folder)
    b4.place(x=100, y=620)

    ######################################
    ## tab 2
    # DESTINATION
    tab2 = ttk.Frame(nb)
    frame21 = Frame(tab2, relief=SUNKEN, width=999, height=450, bd=3)
    frame21.place(x = 0,y=0,height = 444,width = 998) #grid(row=0, column=0, sticky='ew')
    nb.add(tab2, text="Destination", state='disabled')
    tab2.grid_columnconfigure(0,weight=1)

    frame22 = Frame(tab2, relief=SUNKEN, width=997, height=250, bd=3)
    frame22.place(x = 0,y = 450) #grid(row=1, column=0, sticky='news')
    nb.add(tab2, text="Destination", state='disabled')
    tab2.grid_columnconfigure(0, weight=1)
    lab0 = Label(frame22, text='DESTINATION FOLDER',font = "calibri 30")
    lab0.place(x=330,y=0) #pack() #grid(row = 0,column = 0)
    lab1 = Label(frame22, text='Enter Destination : ', font="15")
    lab1.place(x =250,y=100)
    e01 = Entry(frame22, textvariable=dest_str,state="disabled", width=30,font = "15",bd = 3)
    e01.place(x = 440,y=100)

    b22 = Button(frame22, text="Next", command=lambda: next_tab2(tab2, tab3))
    b22.place(x=900, y=165)

    b32 = Button(frame22, text='Previous',state = "normal", command=lambda: previous_tab(tab1, tab2))
    b32.place(x=50, y=165)


    b02 = Button(frame22, text="Delete Folder",command = lambda: dest_str.set(""))
    b02.place(x = 350,y=165)
    
    b42 = Button(frame22, text="Browse Folder",command = select_dest)
    b42.place(x = 500,y = 165)

    ########################################
    tab3 = ttk.Frame(nb)
    nb.add(tab3, text="Parameters", state='disabled')
    frame31 = Frame(tab3, relief=SUNKEN, width=490, height=420, bd=3)
    frame31.place(x=0, y=0, height=420, width=490)

    lab = Label(frame31, text="Exceptions", font="12").pack()
    inf0 = Canvas(frame31, relief=SUNKEN, width=400, height=450, bd=0)
    inf0.pack()

    lis0 = Listbox(inf0, height=16, width=50, bd=2)
    lis0.pack(side=LEFT)
    scroll0 = Scrollbar(inf0)
    scroll0.pack(side=RIGHT, fill=BOTH)
    lis0.config(yscrollcommand=scroll0.set)
    scroll0.config(command=lis0.yview)

    e31 = Entry(frame31, textvariable=exp, width=30, bd=2)
    e31.place(x=145, y=310)

    b31 = Button(frame31, text="Remove exception", command=lambda : lis0.delete(ANCHOR))
    b31.place(x=70, y=350)

    b32 = Button(frame31, text="Add exception", command=add_exp)
    b32.place(x=330, y=350)


    ######################
    frame32 = Frame(tab3, relief=SUNKEN, width=496, height=420, bd=3)
    frame32.place(x=500, y=0, height=420, width=496)
    lab = Label(frame32,text = "Custom Extensions",font = "12").pack()
    inf = Canvas(frame32, relief=SUNKEN, width=400, height=450, bd=0)
    inf.pack()

    lis = Listbox(inf,height = 16,width =  50,bd = 2)
    lis.pack(side = LEFT)
    scroll = Scrollbar(inf)
    scroll.pack(side=RIGHT, fill=BOTH)
    lis.config(yscrollcommand=scroll.set)
    scroll.config(command=lis.yview)

    e31 = Entry(frame32, textvariable=ext, width=30, bd=2)
    e31.place(x = 145, y=310)

    b31 = Button(frame32, text="Remove extension", command=lambda : lis.delete(ANCHOR))
    b31.place(x=70, y=350)

    b32 = Button(frame32, text="Add extension", command=add_ext)
    b32.place(x=330, y=350)


    b22 = Button(tab3, text="Next", command=lambda: next_tab3(tab3, tab4))
    b22.place(x=900, y=630)
    b32 = Button(tab3, text='Previous', command=lambda: previous_tab(tab2, tab3))
    b32.place(x=50, y=630)

    frame33 = Frame(tab3, relief=SUNKEN, width=997, height=180, bd=3)
    frame33.place(x=0, y=430, height=180, width=997)




    C1 = Checkbutton(frame33, text="Audio files", variable=CheckVar1,onvalue=1, offvalue=0, height=5,width=20)
    C1.grid(row = 0,column = 0)
    C2 = Checkbutton(frame33, text="Video files", variable=CheckVar2,onvalue=1, offvalue=0, height=5,width=20)
    C2.grid(row = 0,column = 1)

    C3 = Checkbutton(frame33, text="Image files", variable=CheckVar3, onvalue=1, offvalue=0, height=5, width=20)
    C3.grid(row = 0,column = 2)
    C4 = Checkbutton(frame33, text="Executable files", variable=CheckVar4, onvalue=1, offvalue=0, height=5, width=20)
    C4.grid(row = 0,column = 3)

    C5 = Checkbutton(frame33, text="Documents", variable=CheckVar5, onvalue=1, offvalue=0, height=5, width=20)
    C5.grid(row = 0,column = 4)
    C6 = Checkbutton(frame33, text="Compressed files", variable=CheckVar6, onvalue=1, offvalue=0, height=5, width=20)
    C6.grid(row = 0,column = 5)

    C7 = Checkbutton(frame33, text="System files", variable=CheckVar7, onvalue=1, offvalue=0, height=5, width=20)
    C7.grid(row = 1,column = 0)
    C8 = Checkbutton(frame33, text="Plugin files", variable=CheckVar8, onvalue=1, offvalue=0, height=5, width=20)
    C8.grid(row = 1,column = 1)

    C9 = Checkbutton(frame33, text="Developer files", variable=CheckVar9, onvalue=1, offvalue=0, height=5, width=20)
    C9.grid(row=1, column=2)

    C10 = Checkbutton(frame33, text="backup files", variable=CheckVar10, onvalue=1, offvalue=0, height=5, width=20)
    C10.grid(row=1, column=3)

    C11 = Checkbutton(frame33, text="Other files", variable=CheckVar11, onvalue=1, offvalue=0, height=5, width=20)
    C11.grid(row=1, column=4)

    C12 = Checkbutton(frame33, text="Combine other files", variable=CheckVar12, onvalue=1, offvalue=0, height=5, width=20)
    C12.grid(row=1, column=5)
    ########################################

    tab4 = ttk.Frame(nb)
    nb.add(tab4, text="Execution", state='disabled')
    b22 = Button(tab4, text="Close")
    frame41 = Frame(tab4, relief=SUNKEN, width=997, height=150, bd=0)
    frame41.place(x=0, y=0, height=150, width=997)
    L41 = Label(frame41,text = "Execution",font = "15").pack()
    progress1 = ttk.Progressbar(frame41, orient=HORIZONTAL, length=995, mode='determinate')
    progress1.place(x =0,y = 125)

    frame42 = Frame(tab4, relief=SUNKEN, width=997, height=400, bd=0)
    frame42.place(x=0, y=150, height=400, width=997)
    lis2 = Listbox(frame42, height=25, width=162, bd=2)
    lis2.pack(side=LEFT)
    scroll2 = Scrollbar(frame42)
    scroll2.pack(side=RIGHT, fill=BOTH)
    lis2.config(yscrollcommand=scroll2.set)
    scroll2.config(command=lis2.yview)
    w32 = Button(tab4, text='Exit', command=exit)
    w32.place(x=50, y=630)

    w32 = Button(tab4, text='Create Logs', command=log)
    w32.place(x=500, y=630)


def main_page():
    global main
    main = Tk()
    main.title("File Organiser")
    p1 = PhotoImage(file = 'folder.png')
    main.iconphoto(False, p1)
    main.geometry("1000x700")
    organiser_page()
    main.mainloop()


if __name__ == '__main__':
    main_page()
