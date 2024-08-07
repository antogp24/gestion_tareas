import customtkinter as ctk
import PIL

ctk.set_appearance_mode("light")
FONT="Times New Roman"

class Tarea:
    def __init__(self, title, desc):
        self.title = title
        self.desc = desc

class App(ctk.CTk):
    def load_image(name, extension, size=None):
        light = PIL.Image.open(f"assets/icons/{name}_light.{extension}")
        dark = PIL.Image.open(f"assets/icons/{name}_dark.{extension}")
        assert(dark.size == light.size)
        if size is None:
            size = dark.size
        return ctk.CTkImage(light_image=light, dark_image=dark, size=size)

    def __init__(self):
        super().__init__()

        self.title("Gestión de Tareas")
        self.geometry("1080x720")

        # Common icons
        self.icons = {
            "go_back_arrow": App.load_image("go_back_arrow", "png", (30, 30)),
            "edit": App.load_image("edit", "png", (30, 30)),
        }

        # Dictionary to hold frames
        self.frames = {}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        screens = (Tarea_Individual, Dashboard)
        for F in screens:
            frame = F(parent=self, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        if page_name not in self.frames:
            print(f"Error: {page_name} is not in the application frames.")
            exit(1)
        frame = self.frames[page_name]
        frame.update_idletasks()
        frame.tkraise()


class Subtarea(ctk.CTkFrame):
    def __init__(self, parent, subtarea, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(self, text=subtarea.title)
        self.title.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.desc = ctk.CTkLabel(self, text=subtarea.desc, width=parent.winfo_width())
        self.desc.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

class Tarea_Individual(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1) # column for back arrow.
        self.grid_columnconfigure(1, weight=1) # column for title, textbox, etc.
        self.grid_columnconfigure(2, weight=1)

        self.grid_rowconfigure(0, weight=0) # row for icon and label.
        self.grid_rowconfigure(1, weight=0) # row for the textbox.
        self.grid_rowconfigure(2, weight=0) # row for the frame of textboxes.
        self.grid_rowconfigure(3, weight=1) # filler space between.
        self.grid_rowconfigure(4, weight=0) # row for the go to dashboard button.

        self.back_icon = ctk.CTkLabel(self, image=controller.icons["go_back_arrow"], text="")
        self.back_icon.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.title_entry = ctk.CTkEntry(self, font=ctk.CTkFont(family=FONT, weight="bold", size=36), justify="center", width=600)
        self.title_entry.insert(0, "Título Tarea")
        self.title_entry.grid(row=0, column=1, padx=10, pady=10)

        self.edit_title_icon = ctk.CTkLabel(self, image=controller.icons["edit"], text="")
        self.edit_title_icon.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.edit_title_icon.bind("<Button-1>", lambda event: self.title_entry.focus_set())

        self.desc_textbox = ctk.CTkTextbox(self, width=self.winfo_screenwidth()*0.35, height=200, font=ctk.CTkFont(family=FONT, size=24))
        self.desc_textbox.grid(row=1, column=1, padx=10, pady=10, sticky="n")

        subtareas = []
        for i in range(10):
            subtareas.append(Tarea(f"Título Tarea {i+1}", f"Descripción Tarea {i+1}"))

        self.subtareas_frame = ctk.CTkScrollableFrame(self, width=self.winfo_screenwidth()*0.35)
        self.subtareas_frame.grid_columnconfigure(0, weight=1)
        for index, subtarea in enumerate(subtareas):
            widget = Subtarea(self.subtareas_frame, subtarea)
            widget.grid(row=index, column=0, padx=10, pady=10, sticky="ew")
        self.subtareas_frame.grid(row=2, column=1, padx=20, pady=20)

        self.go_to_dashboard_button = ctk.CTkButton(
            self,
            text="Ir al Dashboard",
            command=lambda: controller.show_frame("Dashboard"))
        self.go_to_dashboard_button.grid(row=3, column=1, pady=10)

        self.bind("<Button-1>", lambda event: self.focus_set())


class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1) # column for back arrow
        self.grid_columnconfigure(2, weight=1) # column for title

        self.grid_rowconfigure(0, weight=0) # row for icon and label.
        self.grid_rowconfigure(1, weight=1) # space between.
        self.grid_rowconfigure(2, weight=0) # row for the go to dashboard button.

        self.back_icon = ctk.CTkLabel(self, image=controller.icons["go_back_arrow"], text="")
        self.back_icon.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.title_label = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(family=FONT, weight="bold", size=36))
        self.title_label.grid(row=0, column=1, padx=10, pady=10)

        self.go_to_tarea_principal_button = ctk.CTkButton(
            self,
            text="Ir a Tarea Individual",
            command=lambda: controller.show_frame("Tarea_Individual"))
        self.go_to_tarea_principal_button.grid(row=2, column=1, pady=10)


# Initialize and run the application
app = App()
app.mainloop()
