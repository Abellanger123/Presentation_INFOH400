import tkinter as tk

root = tk.Tk()
root.title("tk")
root.geometry("400x250")  # Définit la taille initiale de la fenêtre

# Label "Hello World"
label = tk.Label(root, text="Hello World", font=("Arial", 14))
label.pack(pady=20)

# Création d'un cadre pour organiser les boutons
frame = tk.Frame(root)
frame.pack(expand=True)

# Ajout des boutons colorés
btn_red = tk.Button(frame, text="Red", bg="red", fg="white")
btn_red.grid(row=0, column=0, padx=10, pady=5)

btn_green = tk.Button(frame, text="Green", bg="green", fg="white")
btn_green.grid(row=0, column=1, padx=10, pady=5)

btn_blue = tk.Button(frame, text="Blue", bg="blue", fg="white")
btn_blue.grid(row=0, column=2, padx=10, pady=5)

# Bouton noir centré en dessous
btn_black = tk.Button(root, text="Black", bg="black", fg="white")
btn_black.pack(pady=10)

root.mainloop()





