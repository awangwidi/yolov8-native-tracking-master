from tkinter import ttk
import tkinter as tk
import customtkinter
import os
import pymysql


from PIL import Image
import main


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        style = ttk.Style()
        self.title("Detektor Pelanggaran UI Test")
        self.geometry("700x450")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "python.png")), size=(250, 250))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "chat_light.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))
        self.refresh = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "refresh.png")), size=(25,25))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Detektor Pelanggaran", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Database",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Video List",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Dark", "Light", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create home frame
        self.home_frame = customtkinter.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.large_test_image)
        self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)

        self.home_frame_button_1 = customtkinter.CTkButton(self.home_frame, text="Start Program", image=self.image_icon_image, command=main.main)
        self.home_frame_button_1.grid(row=1, column=0, padx=20, pady=10)
        # self.home_frame_button_2 = customtkinter.CTkButton(self.home_frame, text="CTkButton", image=self.image_icon_image, compound="right")
        # self.home_frame_button_2.grid(row=2, column=0, padx=20, pady=10)
        # self.home_frame_button_3 = customtkinter.CTkButton(self.home_frame, text="CTkButton", image=self.image_icon_image, compound="top")
        # self.home_frame_button_3.grid(row=3, column=0, padx=20, pady=10)
        # self.home_frame_button_4 = customtkinter.CTkButton(self.home_frame, text="CTkButton", image=self.image_icon_image, compound="bottom", anchor="w")
        # self.home_frame_button_4.grid(row=4, column=0, padx=20, pady=10)

        # create database frame
        self.database_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.database_frame.grid_columnconfigure(0, weight=1)
        self.dbtree = ttk.Treeview(self.database_frame)
        ctk_dbtree_scrollbar = customtkinter.CTkScrollbar(self.database_frame, command=self.dbtree.yview)
        ctk_dbtree_scrollbar.grid(row=0, column=1, pady=10,sticky="ns")
        self.dbtree.configure(yscrollcommand=ctk_dbtree_scrollbar.set)
        self.dbtree.grid(row=0,column=0,padx=20,pady=20,sticky="nsew")
        self.dbtree['columns'] = ("id", "Tanggal", "Jenis Pelanggaran")

        self.dbtree.column("#0", width=0, stretch=False)
        self.dbtree.column("id", anchor="w", width=25)
        self.dbtree.column("Tanggal", anchor="center", width=120)
        self.dbtree.column("Jenis Pelanggaran", anchor="w", width=240)

        #headings
        self.dbtree.heading("#0", text="Label", anchor="w")
        self.dbtree.heading("id", text="ID", anchor="w")
        self.dbtree.heading("Tanggal", text="Tanggal", anchor="center")
        self.dbtree.heading("Jenis Pelanggaran", text="Jenis Pelanggaran", anchor="w")

        # Create Striped Row Tags
        self.dbtree.tag_configure('oddrow', background="white")
        self.dbtree.tag_configure('evenrow', background="lightblue")
        self.db_refresh_button = customtkinter.CTkButton(self.database_frame, text="Refresh", image=self.refresh, command=self.view, fg_color="blue", hover_color="darkblue", text_color="white")
        self.db_refresh_button.grid(row=1, column=0, padx=20, pady=20)

        
        # create video list in directory frame
        self.video_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.video_frame.grid_columnconfigure(0, weight=1)
        self.dirtree=ttk.Treeview(self.video_frame,show='tree')
        self.dirtree.grid(row=1,column=0, padx=20, pady = 20, sticky="nsew")
        
        ctk_tree_scrollbar = customtkinter.CTkScrollbar(self.video_frame, command=self.dirtree.yview)
        ctk_tree_scrollbar.grid(row=1, column=1, pady= 10, sticky="ns")
        self.dirtree.configure(yscrollcommand=ctk_tree_scrollbar.set)
        directory='VideoPelanggar'
        self.path=os.path.relpath(directory)
        self.dirtree.heading('#0',text='Dir: ddsfsdf'+directory,anchor='w')
        self.directory_refresh_button = customtkinter.CTkButton(self.video_frame, text="Refresh", image=self.refresh, command=self.traverse_dir, fg_color="blue", hover_color="darkblue", text_color="white")
        self.directory_refresh_button.grid(row=2, column=0, padx=20, pady=20)
        

        # select default frame
        self.select_frame_by_name("home")


    def traverse_dir(self):
        self.cleardir()
        self.node=self.dirtree.insert('','end',text=self.path, open=True)
        for dir in os.listdir(self.path):
            self.dirtree.insert(self.node,'end',text=dir,open=False)
        
            
    def cleardir(self):
        for files in self.dirtree.get_children():
            self.dirtree.delete(files)

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.database_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.database_frame.grid_forget()
        if name == "frame_3":
            self.video_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.video_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")
        self.view()

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")
        self.traverse_dir()

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def view(self):
        conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        db='violation_db',
        charset='utf8', # type: ignore
        )

        cursor = conn.cursor()
        sql = "SELECT * FROM pelanggar;"
        cursor.execute(sql)
        self.clear()
        rows = ()
        rows += cursor.fetchall()
        for row in rows:
            self.dbtree.insert(parent='', iid = row[0], index='end', text='', values=(row[0], row[1], row[2]))
        conn.close()
    
    def clear(self):
        for row in self.dbtree.get_children():
            self.dbtree.delete(row)

if __name__ == "__main__":
    app = App()
    app.mainloop()

