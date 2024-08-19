import customtkinter as ctk
import sqlite3
import PIL

ctk.set_appearance_mode("dark")
STATE_COLORS = { "pendiente": "#ff6759", "en progreso": "#ffd359", "completada": "#caff59"}

db_connection = sqlite3.connect("db.db")
db_cursor = db_connection.cursor()

def get_estado(id):
    db_cursor.execute("select nombre from Estados where id = ?", (id,))
    return db_cursor.fetchall()[0][0]

class Tarea:
    def __init__(self, title, desc, state):
        self.title = title
        self.desc = desc
        self.state = state

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
        self.show_frame("Tarea_Individual")

    def show_frame(self, page_name):
        match page_name:
            case Tarea_Individual.__name__:
                f = self.frames[page_name]
                f.subtareas_frame.bind_all("<Button-4>", lambda _: f.subtareas_frame._parent_canvas.yview_scroll(-1, "units"))
                f.subtareas_frame.bind_all("<Button-5>", lambda _: f.subtareas_frame._parent_canvas.yview_scroll(+1, "units"))
            case Dashboard.__name__:
                f = self.frames[page_name]
                f.frame.bind_all("<Button-4>", lambda _: f.frame._parent_canvas.yview_scroll(-1, "units"))
                f.frame.bind_all("<Button-5>", lambda _: f.frame._parent_canvas.yview_scroll(+1, "units"))
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

        self.title = ctk.CTkLabel(self, text=subtarea.title, font=ctk.CTkFont(weight="bold", size=20))
        self.title.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.desc = ctk.CTkLabel(self, text=subtarea.desc, justify="left", font=ctk.CTkFont(size=16))
        self.desc.grid(row=1, column=0, padx=100, pady=10, sticky="ew")


class Tarea_Individual(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1) # column for back arrow.
        self.grid_columnconfigure(1, weight=1) # column for title, textbox, etc.
        self.grid_columnconfigure(2, weight=1)

        self.grid_rowconfigure(0, weight=0) # row for icon and label.
        self.grid_rowconfigure(1, weight=0) # row for the textbox.
        self.grid_rowconfigure(2, weight=1) # row for the frame of subtareas.
        self.grid_rowconfigure(3, weight=0) # filler space between.
        self.grid_rowconfigure(4, weight=0) # row for the go to dashboard button.

        self.back_icon = ctk.CTkLabel(self, image=controller.icons["go_back_arrow"], text="")
        self.back_icon.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        db_cursor.execute("select titulo, descripcion from Tareas where id=1")
        titulo, descripcion = db_cursor.fetchall()[0]

        self.title_entry = ctk.CTkEntry(self, font=ctk.CTkFont(weight="bold", size=36), justify="center", width=600)
        self.title_entry.insert(0, titulo)
        self.title_entry.grid(row=0, column=1, padx=10, pady=10)

        self.edit_title_icon = ctk.CTkLabel(self, image=controller.icons["edit"], text="")
        self.edit_title_icon.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.edit_title_icon.bind("<Button-1>", lambda event: self.title_entry.focus_set())

        self.desc_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(size=24))
        self.desc_textbox.insert("1.0", descripcion)
        self.center_description()
        self.desc_textbox.bind("<KeyRelease>", lambda _: self.center_description())
        self.desc_textbox.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        db_cursor.execute("select titulo, descripcion, id_estado from Tareas where id in (select id_subtarea from Subtareas where id_tarea=1)")
        subtareas = db_cursor.fetchall()
        for i, subtarea in enumerate(subtareas):
            estado = get_estado(subtarea[2])
            desc = subtarea[1].replace("\\n", "\n").replace("\\t", "\t")
            subtareas[i] = Tarea(subtarea[0], desc, estado)

        self.subtareas_frame = ctk.CTkScrollableFrame(self)
        self.subtareas_frame.grid_columnconfigure(0, weight=1)
        self.subtareas_frame.bind_all("<Button-4>", lambda _: self.subtareas_frame._parent_canvas.yview_scroll(-1, "units"))
        self.subtareas_frame.bind_all("<Button-5>", lambda _: self.subtareas_frame._parent_canvas.yview_scroll(+1, "units"))
        self.subtareas_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        for index, subtarea in enumerate(subtareas):
            widget = Subtarea(self.subtareas_frame, subtarea, border_color=STATE_COLORS[subtarea.state], border_width=2)
            widget.grid(row=index, column=0, padx=10, pady=10, sticky="ew")
            edit_sub_icon = ctk.CTkLabel(self.subtareas_frame, image=controller.icons["edit"], text="")
            edit_sub_icon.grid(row=index, column=0, padx=40, pady=20, sticky="e")
            state_label = ctk.CTkLabel(self.subtareas_frame, text=subtarea.state, text_color=STATE_COLORS[subtarea.state], font=ctk.CTkFont(size=12))
            state_label.grid(row=index, column=0, padx=40, pady=20, sticky="w")
        self.subtareas_frame.grid(row=2, column=1, padx=20, pady=20)

        self.go_to_dashboard_button = ctk.CTkButton(
            self,
            text="Ir al Dashboard",
            command=lambda: controller.show_frame("Dashboard"))
        self.go_to_dashboard_button.grid(row=3, column=1, pady=10)

        self.bind("<Button-1>", lambda event: self.focus_set())

    def center_description(self):
        self.desc_textbox.tag_config("center", justify="center")
        self.desc_textbox.tag_add("center", "1.0", "end")



class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1) # column for back arrow.
        self.grid_columnconfigure(1, weight=1) # column for title.
        self.grid_columnconfigure(2, weight=1) # empty space to the right.

        self.grid_rowconfigure(0, weight=0) # row for back icon and title.
        self.grid_rowconfigure(1, weight=0) # row for numero de tareas.
        self.grid_rowconfigure(2, weight=1) # row for scrollable frame.
        self.grid_rowconfigure(3, weight=0) # row for the go to dashboard button.

        self.back_icon = ctk.CTkLabel(self, image=controller.icons["go_back_arrow"], text="")
        self.back_icon.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.title_label = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(weight="bold", size=36))
        self.title_label.grid(row=0, column=1, padx=10, pady=10)

        db_cursor.execute("select count(*) from Tareas where id_estado = (select id from Estados where nombre='completada')")
        num = db_cursor.fetchall()[0][0]
        self.tareas_completadas_frame = ctk.CTkFrame(self)
        _ = ctk.CTkLabel(self.tareas_completadas_frame, text="Numero de ", font=ctk.CTkFont(size=20)).pack(side="left")
        _ = ctk.CTkLabel(self.tareas_completadas_frame, text="tareas completadas", font=ctk.CTkFont(size=20), text_color=STATE_COLORS["completada"]).pack(side="left")
        _ = ctk.CTkLabel(self.tareas_completadas_frame, text=f": {num}", font=ctk.CTkFont(size=20)).pack(side="left")
        self.tareas_completadas_frame.grid(row=1, column=1, padx=20, pady=20)

        self.frame = ctk.CTkScrollableFrame(self)
        self.frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        def listing(row):
            f = ctk.CTkFrame(self.frame)
            s = get_estado(row[1])
            l = ctk.CTkLabel(f, text=row[0], text_color=STATE_COLORS[s], font=ctk.CTkFont(size=22))
            l.bind("<Enter>", lambda _: l.configure(fg_color="gray"))
            l.bind("<Leave>", lambda _: l.configure(fg_color="transparent"))
            l.pack(anchor="center")
            f.pack(anchor="center", pady=10)

        db_cursor.execute("select titulo, id_estado, id from Tareas")
        tareas = db_cursor.fetchall()
        for t in tareas:
            listing(t)

        self.go_to_tarea_individual_button = ctk.CTkButton(
            self,
            text="Ir a Tarea Individual",
            command=lambda: controller.show_frame("Tarea_Individual"))
        self.go_to_tarea_individual_button.grid(row=3, column=1, padx=10, pady=10, sticky="s")


# Initialize and run the application
app = App()
app.mainloop()
