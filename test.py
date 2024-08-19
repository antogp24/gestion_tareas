import customtkinter as ctk

app = ctk.CTk()

# Main list
main_frame = ctk.CTkFrame(app)
main_frame.pack(padx=10, pady=10)

# Item 1
item1 = ctk.CTkLabel(main_frame, text="Item 1")
item1.pack(anchor="w")

# Item 2 with sublist
item2 = ctk.CTkLabel(main_frame, text="Item 2")
item2.pack(anchor="w")

sublist_frame = ctk.CTkFrame(main_frame)
sublist_frame.pack(padx=20)

subitem2_1 = ctk.CTkLabel(sublist_frame, text="Subitem 2.1")
subitem2_1.pack(anchor="w")

subitem2_2 = ctk.CTkLabel(sublist_frame, text="Subitem 2.2")
subitem2_2.pack(anchor="w")

# Item 3
item3 = ctk.CTkLabel(main_frame, text="Item 3")
item3.pack(anchor="w")

app.mainloop()
