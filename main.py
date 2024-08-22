import customtkinter as ctk
import PIL
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sqlite3

ctk.set_appearance_mode("dark")
STATE_COLORS = { "pendiente": "#ff6759", "en progreso": "#ffd359", "completada": "#caff59"}

db_connection = sqlite3.connect("db.db")
db_cursor = db_connection.cursor()

def get_estado(id):
    db_cursor.execute("select nombre from Estados where id = ?", (id,))
    return db_cursor.fetchall()[0][0]

class SubTask:
    def __init__(self, title, state, priority):
        self.title = title
        self.state = state
        self.priority = priority

def load_image(name, extension, size=None):
    light = PIL.Image.open(f"assets/icons/{name}_light.{extension}")
    dark = PIL.Image.open(f"assets/icons/{name}_dark.{extension}")
    assert(dark.size == light.size)
    if size is None:
        size = dark.size
    return ctk.CTkImage(light_image=light, dark_image=dark, size=size)

ICONS = {
    "go_back_arrow": load_image("go_back_arrow", "png", (30, 30)),
    "edit": load_image("edit", "png", (30, 30)),
    "trash": load_image("trash", "png", (30, 30)),
}

class App(ctk.CTk):
    def on_close(self):
        plt.close("all")
        self.destroy()

    def __init__(self):
        super().__init__()

        self.title("Gestión de Tareas")
        self.geometry("1080x720")


        # Dictionary to hold frames
        self.frames = {}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        def MakeFrame(F):
            match F.__name__:
                case Main_Task_Frame.__name__:
                    db_cursor.execute("select titulo, descripcion from Tareas where id=1")
                    titulo, descripcion = db_cursor.fetchall()[0]

                    db_cursor.execute("select titulo, id_estado, prioridad from Tareas where id in (select id_subtarea from Subtareas where id_tarea=1)")
                    subtareas = db_cursor.fetchall()

                    return F(parent=self, controller=self, titulo=titulo, descripcion=descripcion, subtareas=subtareas)

                case Dashboard_Frame.__name__:
                    db_cursor.execute("select count(*) from Tareas where id_estado = (select id from Estados where nombre='completada')")
                    n_completadas = db_cursor.fetchall()[0][0]

                    db_cursor.execute("select count(*) from Tareas where id_estado = (select id from Estados where nombre='en progreso')")
                    n_en_progreso = db_cursor.fetchall()[0][0]

                    db_cursor.execute("select count(*) from Tareas where id_estado = (select id from Estados where nombre='pendiente')")
                    n_pendientes = db_cursor.fetchall()[0][0]

                    db_cursor.execute("select count(*) from Tareas")
                    total_tareas = db_cursor.fetchall()[0][0]

                    return F(parent=self, controller=self, n_completadas=n_completadas, n_en_progreso=n_en_progreso, n_pendientes=n_pendientes, total_tareas=total_tareas)

        screens = (Main_Task_Frame, Dashboard_Frame)
        for F in screens:
            frame = MakeFrame(F)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Main_Task_Frame.__name__)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_frame(self, page_name):
        match page_name:
            case Main_Task_Frame.__name__:
                f = self.frames[page_name]
                f.subtareas_frame.bind_all("<Button-4>", lambda _: f.subtareas_frame._parent_canvas.yview_scroll(-1, "units"))
                f.subtareas_frame.bind_all("<Button-5>", lambda _: f.subtareas_frame._parent_canvas.yview_scroll(+1, "units"))
        if page_name not in self.frames:
            print(f"Error: {page_name} is not in the application frames.")
            exit(1)
        frame = self.frames[page_name]
        frame.update_idletasks()
        frame.tkraise()


class SubTask_Widget(ctk.CTkFrame):
    def __init__(self, parent, subtarea, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        # state and priority frame
        self.sapf = ctk.CTkFrame(self)
        self.sapf.grid(row=0, column=0, padx=40, pady=20, sticky="ew")

        self.state_label = ctk.CTkLabel(self.sapf, text=subtarea.state, text_color=STATE_COLORS[subtarea.state], font=ctk.CTkFont(size=12))
        self.state_label.pack()

        self.priority_label = ctk.CTkLabel(self.sapf, text=f"{subtarea.priority}", font=ctk.CTkFont(size=16))
        self.priority_label.pack()

        self.title = ctk.CTkLabel(self, text=subtarea.title, font=ctk.CTkFont(weight="bold", size=20))
        self.title.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # edit icon and trash frame
        self.eatf = ctk.CTkFrame(self)
        self.eatf.grid(row=0, column=2, padx=40, pady=20, sticky="ew")

        self.edit_sub_icon = ctk.CTkLabel(self.eatf, image=ICONS["edit"], text="")
        self.edit_sub_icon.bind("<Button-1>", lambda _: None)
        self.edit_sub_icon.pack(pady=10)

        self.trash_sub_icon = ctk.CTkLabel(self.eatf, image=ICONS["trash"], text="")
        self.trash_sub_icon.bind("<Button-1>", lambda _: self.destroy())
        self.trash_sub_icon.pack(pady=10)

class Main_Task_Frame(ctk.CTkFrame):
    def __init__(self, parent, controller, titulo, descripcion, subtareas):
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

        self.back_icon = ctk.CTkLabel(self, image=ICONS["go_back_arrow"], text="")
        self.back_icon.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # db_cursor.execute("select titulo, descripcion from Tareas where id=1")
        # db_cursor.fetchall()[0]
        self.titulo, self.descripcion = titulo, descripcion

        self.title_entry = ctk.CTkEntry(self, font=ctk.CTkFont(weight="bold", size=36), justify="center", width=600)
        self.title_entry.insert(0, self.titulo)
        self.title_entry.grid(row=0, column=1, padx=10, pady=10)

        self.desc_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(size=24))
        self.desc_textbox.insert("1.0", descripcion)
        self.center_description()
        self.desc_textbox.bind("<KeyRelease>", lambda _: self.center_description())
        self.desc_textbox.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.subtareas = subtareas
        for i, subtarea in enumerate(subtareas):
            estado = get_estado(subtarea[1])
            self.subtareas[i] = SubTask(title=subtarea[0], state=estado, priority=subtarea[2])

        self.subtareas_frame = ctk.CTkScrollableFrame(self)
        self.subtareas_frame.grid_columnconfigure(0, weight=1)
        self.subtareas_frame.bind_all("<Button-4>", lambda _: self.subtareas_frame._parent_canvas.yview_scroll(-1, "units"))
        self.subtareas_frame.bind_all("<Button-5>", lambda _: self.subtareas_frame._parent_canvas.yview_scroll(+1, "units"))
        self.subtareas_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        for index, subtarea in enumerate(subtareas):
            widget = SubTask_Widget(self.subtareas_frame, subtarea, border_color=STATE_COLORS[subtarea.state], border_width=2)
            widget.grid(row=index, column=0, padx=10, pady=10, sticky="ew")
        self.subtareas_frame.grid(row=2, column=1, padx=20, pady=20)

        self.go_to_dashboard_button = ctk.CTkButton(
            self,
            text="Ir al Dashboard",
            command=lambda: controller.show_frame(Dashboard_Frame.__name__))
        self.go_to_dashboard_button.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.save_icon = ctk.CTkButton(
            self,
            text="Guardar",
            command=lambda: None)
        self.save_icon.grid(row=3, column=1, padx=10, pady=10, sticky="e")


        self.bind("<Button-1>", lambda event: self.focus_set())

    def center_description(self):
        self.desc_textbox.tag_config("center", justify="center")
        self.desc_textbox.tag_add("center", "1.0", "end")



class Dashboard_Frame(ctk.CTkFrame):
    def __init__(self, parent, controller, n_completadas, n_en_progreso, n_pendientes, total_tareas):
        super().__init__(parent)
        self.controller = controller

        self.n_completadas = n_completadas
        self.n_en_progreso = n_en_progreso
        self.n_pendientes = n_pendientes
        self.total_tareas = total_tareas

        self.grid_columnconfigure(0, weight=1) # column for back arrow.
        self.grid_columnconfigure(1, weight=1) # column for title.
        self.grid_columnconfigure(2, weight=1) # empty space to the right.

        self.grid_rowconfigure(0, weight=0) # row for back icon and title.
        self.grid_rowconfigure(1, weight=0) # row for total number of tasks.
        self.grid_rowconfigure(2, weight=0) # row for number of completed tasks.
        self.grid_rowconfigure(3, weight=0) # row for number of in progress tasks.
        self.grid_rowconfigure(4, weight=0) # row for number of pending tasks.
        self.grid_rowconfigure(5, weight=1) # row for chart from matplotlib.
        self.grid_rowconfigure(6, weight=0) # row for the go to dashboard button.

        self.back_icon = ctk.CTkLabel(self, image=ICONS["go_back_arrow"], text="")
        self.back_icon.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.title_label = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(weight="bold", size=36))
        self.title_label.grid(row=0, column=1, padx=10, pady=10)

        font = ctk.CTkFont(size=20)

        self.total_tareas_frame = ctk.CTkFrame(self)
        _ = ctk.CTkLabel(self.total_tareas_frame, text="Número ", font=font).pack(side="left")
        _ = ctk.CTkLabel(self.total_tareas_frame, text="total ", font=font, text_color="#69c3ff").pack(side="left")
        _ = ctk.CTkLabel(self.total_tareas_frame, text=f"de tareas: {self.total_tareas}", font=font).pack(side="left")
        self.total_tareas_frame.grid(row=1, column=1, padx=20, pady=20)

        self.n_completadas_frame = ctk.CTkFrame(self)
        _ = ctk.CTkLabel(self.n_completadas_frame, text="Número ", font=font).pack(side="left")
        _ = ctk.CTkLabel(self.n_completadas_frame, text="tareas completadas", font=font, text_color=STATE_COLORS["completada"]).pack(side="left")
        _ = ctk.CTkLabel(self.n_completadas_frame, text=f": {self.n_completadas}", font=font).pack(side="left")
        self.n_completadas_frame.grid(row=2, column=1, padx=20, pady=20)

        self.n_en_progreso_frame = ctk.CTkFrame(self)
        _ = ctk.CTkLabel(self.n_en_progreso_frame, text="Número ", font=font).pack(side="left")
        _ = ctk.CTkLabel(self.n_en_progreso_frame, text="tareas en progreso", font=font, text_color=STATE_COLORS["en progreso"]).pack(side="left")
        _ = ctk.CTkLabel(self.n_en_progreso_frame, text=f": {self.n_en_progreso}", font=font).pack(side="left")
        self.n_en_progreso_frame.grid(row=3, column=1, padx=20, pady=20)

        self.n_pendientes_frame = ctk.CTkFrame(self)
        _ = ctk.CTkLabel(self.n_pendientes_frame, text="Número ", font=font).pack(side="left")
        _ = ctk.CTkLabel(self.n_pendientes_frame, text="tareas pendientes", font=font, text_color=STATE_COLORS["pendiente"]).pack(side="left")
        _ = ctk.CTkLabel(self.n_pendientes_frame, text=f": {self.n_pendientes}", font=font).pack(side="left")
        self.n_pendientes_frame.grid(row=4, column=1, padx=20, pady=20)

        porcentajes = [
            (n_completadas / total_tareas) * 100,
            (n_en_progreso / total_tareas) * 100,
            (n_pendientes  / total_tareas) * 100,
        ]

        self.pie_frame = ctk.CTkFrame(self)
        fig, ax = plt.subplots(facecolor="#2b2b2b")
        _, texts, autotexts = ax.pie(porcentajes, labels=["Completadas", "En progreso", "Pendientes"], autopct="%1.1f%%")
        for text in texts:
            text.set_color("white")
            text.set_fontsize(14)
        for text in autotexts:
            text.set_color("white")
            text.set_fontsize(12)
        canvas = FigureCanvasTkAgg(figure=fig, master=self.pie_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        self.pie_frame.grid(row=5, column=1, padx=20, pady=20)

        self.go_to_tarea_individual_button = ctk.CTkButton(
            self,
            text="Ir a Tarea Individual",
            command=lambda: controller.show_frame(Main_Task_Frame.__name__))
        self.go_to_tarea_individual_button.grid(row=6, column=1, padx=10, pady=10, sticky="s")


# Initialize and run the application
app = App()
app.mainloop()
