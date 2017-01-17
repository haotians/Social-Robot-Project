# coding=utf-8
from __future__ import division
import tkFileDialog
import Tkinter as Tk
import lib_train as lt


class MainPage(Tk.Frame):
    """Gui that show group messages and open or build new groups."""

    def _create_widgets(self):
        self.bn_open_group = Tk.Button(self.Frame11, text="Group List", fg="blue",
                                       bg="AntiqueWhite", command=self._button_open_group)
        self.bn_open_group.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.label_group_name = Tk.Message(self.Frame11, width="10i",
                                           text="If you want to create a new group,\n Enter a new group's name below: ",
                                           fg="black", bg='#FFDEAD')
        self.label_group_name.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.txt_group_name = Tk.Text(self.Frame11, height=2, width=15)
        self.txt_group_name.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.bn_new_group = Tk.Button(self.Frame11, text="Add new group",
                                      fg="blue", bg="AntiqueWhite", command=self._button_new_group)
        self.bn_new_group.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.label_warning = Tk.Message(self.Frame1112, width="10i",
                                        text="-------------------------separation line-------------------------"
                                             "--------", fg="green", bg="FloralWhite")
        self.label_warning.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.label_operate_group = Tk.Message(self.Frame12, width="10i",
                                              text="Please enter the group's name\n which you want to operate below:",
                                              fg="black", bg="#FFDEAD")
        self.label_operate_group.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.txt_operate_group = Tk.Text(self.Frame12, height=1, width=15)
        self.txt_operate_group.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.label_person_name = Tk.Message(self.Frame12, width="10i",
                                            text="If you want to create a new person,\n Please enter his name below: ",
                                            fg="black", bg="#FFDEAD")
        self.label_person_name.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.txt_add_person_name = Tk.Text(self.Frame12, height=2, width=15)
        self.txt_add_person_name.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.bn_new_person = Tk.Button(self.Frame12, text="Add New Person",
                                       fg="blue", bg="AntiqueWhite", command=self._button_new_person)
        self.bn_new_person.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.bn_add_photo = Tk.Button(self.Frame12, text="Choose the imgFiles",
                                      fg="blue", bg="AntiqueWhite", command=self._button_add_photo)
        self.bn_add_photo.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.bn_train = Tk.Button(self.Frame12, text="Train",
                                  fg="blue", bg="AntiqueWhite", command=self._button_train)
        self.bn_train.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.bn_del_group = Tk.Button(self.Frame12, text="Delete Group:",
                                      fg="red", bg="AntiqueWhite", command=self._button_del_group)
        self.bn_del_group.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.label_warning_two = Tk.Message(self.Frame1213, width="10i",
                                            text="-------------------------separation line--------------------"
                                                 "-------------", fg="green", bg="FloralWhite")
        self.label_warning_two.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.bn_person_list = Tk.Button(self.Frame13, text="Person List",
                                        fg="blue", bg="AntiqueWhite", command=self._button_person_list)
        self.bn_person_list.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.label_person = Tk.Message(self.Frame13, width="10i",
                                       text="Please enter the person's name \n which you want to "
                                            "delete(photo or person): ", fg="black", bg="#FFDEAD")
        self.label_person.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.txt_person_name = Tk.Text(self.Frame13, height=1, width=15)
        self.txt_person_name.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.bn_del_photo = Tk.Button(self.Frame13, text="Delete photos of the person",
                                      fg="red", bg="AntiqueWhite", command=self._button_del_photo)
        self.bn_del_photo.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.bn_del_person = Tk.Button(self.Frame13, text="Delete Person",
                                       fg="red", bg="AntiqueWhite", command=self._button_del_person)
        self.bn_del_person.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.menu_bar.add_command(label="WELCOME !")

        message = "EWayBot"
        self.label = Tk.Message(self.Frame2, width="10i", text=message)
        self.label.pack(side=Tk.TOP, fill=Tk.X)

        self.log_txt = Tk.Text(self.Frame2, height=15, width=55)
        scr = Tk.Scrollbar(self.Frame2)
        scr.config(command=self.log_txt.yview)
        self.log_txt.config(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y", expand=False)
        self.log_txt.config(state=Tk.DISABLED)
        self.log_txt.pack(side=Tk.TOP, fill="y", expand=True)
        self.log_txt.config(state=Tk.NORMAL)
        self.log_txt.insert(Tk.INSERT, "Hello, welcome to EWayBot \n")
        self.log_txt.config(state=Tk.DISABLED)

    def __init__(self, master=None):
        root = Tk.Tk()
        root.geometry("680x650+400+60")
        self.menu_bar = Tk.Menu(root)
        root.config(menu=self.menu_bar)
        Tk.Frame.__init__(self, root)
        self.Frame1 = Tk.Frame(master, bg="white", relief=Tk.RIDGE, borderwidth=5)
        self.Frame1.pack(side=Tk.LEFT, fill=Tk.BOTH)

        self.Frame11 = Tk.Frame(self.Frame1, bg="white", relief=Tk.SUNKEN, borderwidth=2)
        self.Frame11.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.Frame1112 = Tk.Frame(self.Frame1, bg="white", relief=Tk.SUNKEN, borderwidth=2)
        self.Frame1112.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.Frame12 = Tk.Frame(self.Frame1, bg="white", relief=Tk.SUNKEN, borderwidth=2)
        self.Frame12.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.Frame1213 = Tk.Frame(self.Frame1, bg="white", relief=Tk.SUNKEN, borderwidth=2)
        self.Frame1213.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.Frame13 = Tk.Frame(self.Frame1, bg="white", relief=Tk.SUNKEN, borderwidth=2)
        self.Frame13.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.Frame2 = Tk.Frame(master, bg='snow', relief=Tk.RIDGE, borderwidth=5)
        self.Frame2.pack(side=Tk.LEFT, fill=Tk.BOTH)

        self._create_widgets()
        self.pack()
        self.train = lt.FaceTrain()

    def _button_open_group(self):
        open_group_return = self.train.open_group()
        info = "Current Groups :\n"
        self.log_txt.config(state=Tk.NORMAL)
        self.log_txt.insert(Tk.INSERT, info)
        self.log_txt.config(state=Tk.DISABLED)
        for x in range(len(open_group_return)):
            group_names = open_group_return[x]['group_name']
            info1 = group_names
            self.log_txt.config(state=Tk.NORMAL)
            self.log_txt.insert(Tk.INSERT, info1 + "\n")
            self.log_txt.config(state=Tk.DISABLED)
        self.log_txt.config(state=Tk.NORMAL)
        self.log_txt.insert(Tk.INSERT, "\n")
        self.log_txt.config(state=Tk.DISABLED)

    def _button_new_group(self):
        group_name = self.txt_group_name.get(1.0, Tk.END)
        group_name = group_name[:len(group_name)-1]
        group_name_return = self.train.create_group(group_name)
        info = "success create group: " + group_name_return
        self.log_txt.config(state=Tk.NORMAL)
        self.log_txt.insert(Tk.INSERT, info + "\n")
        self.log_txt.config(state=Tk.DISABLED)

    def _button_new_person(self):
        person_name = self.txt_add_person_name.get(1.0, Tk.END)
        person_name = person_name[:len(person_name)-1]
        string_group_name = self.txt_operate_group.get(1.0, Tk.END)
        string_group_name = string_group_name[:len(string_group_name)-1]
        if string_group_name.strip() == '':
            info = "Please enter the group's name : "
            self.log_txt.config(state=Tk.NORMAL)
            self.log_txt.insert(Tk.INSERT, "\n" + info + "\n")
            self.log_txt.config(state=Tk.DISABLED)
            return
        else:
            group_name = string_group_name
        person_name_return = self.train.add_person(person_name, group_name)
        info = "success add a new person: " + person_name_return + " in group:" + group_name
        self.log_txt.config(state=Tk.NORMAL)
        self.log_txt.insert(Tk.INSERT, "\n" + info + "\n")
        self.log_txt.config(state=Tk.DISABLED)

    def _button_add_photo(self):
        person_name = self.txt_add_person_name.get(1.0, Tk.END)
        person_name = person_name[:len(person_name)-1]
        my_formats = [
            ('Image files', ('*.bmp', '*.png', '*.jpg', '*.gif')),
            ('Windows Bitmap', '*.bmp'),
            ('Portable Network Graphics', '*.png'),
            ('JPEG / JPG', '*.jpg'),
            ('Computer Server GIF', '*.gif'),
            ("All", '*.*')
            ]
        add_photo_return = self.train.add_photo(person_name, tkFileDialog.askopenfilenames(filetypes=my_formats))
        info = "success add %d" % add_photo_return + " face(s) in person:" + person_name
        self.log_txt.config(state=Tk.NORMAL)
        self.log_txt.insert(Tk.INSERT, info + "\n")
        self.log_txt.config(state=Tk.DISABLED)

    def _button_train(self):
        person_name = self.txt_add_person_name.get(1.0, Tk.END)
        person_name = person_name[:len(person_name)-1]
        train_return = self.train.train_face(person_name)
        session_id = train_return
        info = "train success, session_id: %s" % session_id
        self.log_txt.config(state=Tk.NORMAL)
        self.log_txt.insert(Tk.INSERT, info + "\n")
        self.log_txt.config(state=Tk.DISABLED)

    def _button_del_group(self):
        group_name = self.txt_operate_group.get(1.0, Tk.END)
        group_name = group_name[:len(group_name)-1]
        delete_group_return = self.train.delete_group(group_name)
        info = "success delete group: " + delete_group_return
        self.log_txt.config(state=Tk.NORMAL)
        self.log_txt.insert(Tk.INSERT, "\n" + info + "\n")
        self.log_txt.config(state=Tk.DISABLED)

    def _button_person_list(self):
        person_list_return = self.train.person_list()
        info2 = "Current Person List :"
        self.log_txt.config(state=Tk.NORMAL)
        self.log_txt.insert(Tk.INSERT, info2 + "\n")
        self.log_txt.config(state=Tk.DISABLED)
        for x in range(len(person_list_return)):
            person_names = person_list_return[x]['person_name']
            info3 = person_names
            self.log_txt.config(state=Tk.NORMAL)
            self.log_txt.insert(Tk.INSERT, info3 + "\n")
            self.log_txt.config(state=Tk.DISABLED)
        self.log_txt.config(state=Tk.NORMAL)
        self.log_txt.insert(Tk.INSERT, "\n")
        self.log_txt.config(state=Tk.DISABLED)

    def _button_del_photo(self):
        person_name = self.txt_person_name.get(1.0, Tk.END)
        person_name = person_name[:len(person_name)-1]
        faces_return = self.train.get_person_face(person_name)
        count_num = 0
        for x in range(len(faces_return)):
            person_face_id = faces_return[x]['face_id']
            delete_photo_return = self.train.delete_photo_by_face_id(person_name, person_face_id)
            count_num = count_num + delete_photo_return
        info = "delete %d" % count_num + "photo(s) in person:" + person_name
        self.log_txt.config(state=Tk.NORMAL)
        self.log_txt.insert(Tk.INSERT, info + "\n")
        self.log_txt.config(state=Tk.DISABLED)

    def _button_del_person(self):
        person_name = self.txt_person_name.get(1.0, Tk.END)
        person_name = person_name[:len(person_name)-1]
        delete_person_return = self.train.delete_person(person_name)
        info = "success delete person: " + delete_person_return
        self.log_txt.config(state=Tk.NORMAL)
        self.log_txt.insert(Tk.INSERT, info + "\n")
        self.log_txt.config(state=Tk.DISABLED)

if __name__ == '__main__':
    test = MainPage()
    test.master.title("样本训练")
    test.mainloop()
