import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import pydicom
from PIL import Image, ImageTk
import numpy as np

class DICOMApp:
    def __init__(self, master):
        self.master = master
        self.master.title("DICOM Viewer")
        self.master.geometry("1200x1000")

        # Top buttons
        self.top_frame = ttk.Frame(self.master)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(self.top_frame, text="Open Folder", command=self.open_folder).pack(padx=10, pady=5, side=tk.LEFT)
        ttk.Button(self.top_frame, text="Start storescp", command=self.start_storescp).pack(padx=10, pady=5, side=tk.LEFT)
        ttk.Button(self.top_frame, text="Send DICOM", command=self.send_dicom_file).pack(padx=10, pady=5, side=tk.LEFT)

        # Left panel with Treeview
        self.left_frame = ttk.Frame(self.master)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.treeview = ttk.Treeview(self.left_frame)
        self.treeview.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.treeview.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)

        # Right panel for image and metadata
        self.right_frame = ttk.Frame(self.master)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.right_frame, bg="black", height=700)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.metadata_label = ttk.Label(self.right_frame, anchor="w", justify="left")
        self.metadata_label.pack(fill=tk.X, padx=10, pady=10)

        # Sliders with labels
        self.slider_frame = ttk.Frame(self.right_frame)
        self.slider_frame.pack(pady=10)

        # Contrast (Window Width)
        self.contrast_frame = ttk.Frame(self.slider_frame)
        self.contrast_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(self.contrast_frame, text="Contrast").pack()
        self.window_width = tk.DoubleVar()
        self.width_slider = ttk.Scale(self.contrast_frame, from_=1, to=1000, variable=self.window_width, command=self.update_image)
        self.width_slider.pack()

        # Brightness (Window Center)
        self.brightness_frame = ttk.Frame(self.slider_frame)
        self.brightness_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(self.brightness_frame, text="Brightness").pack()
        self.window_center = tk.DoubleVar()
        self.center_slider = ttk.Scale(self.brightness_frame, from_=-1000, to=1000, variable=self.window_center, command=self.update_image)
        self.center_slider.pack()

        self.dicom_data = None
        self.storescp_process = None

    def open_folder(self):
        self.folder_path = filedialog.askdirectory(title="Select Folder")
        if self.folder_path:
            self.treeview.delete(*self.treeview.get_children())
            self.populate_treeview(self.folder_path)
            self.treeview.bind("<<TreeviewSelect>>", self.show_image)

    def populate_treeview(self, folder_path, parent=""):
        try:
            files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".dcm")])
            for file in files:
                self.treeview.insert(parent, "end", text=file, values=[os.path.join(folder_path, file)])
        except Exception as e:
            print("Error reading directory:", e)

    def show_image(self, event):
        selected_item = self.treeview.focus()
        file_path = self.treeview.item(selected_item, "values")
        if file_path:
            self.display_dicom_image(file_path[0])

    def display_dicom_image(self, file_path):
        try:
            ds = pydicom.dcmread(file_path)
            self.dicom_data = ds
            image_data = ds.pixel_array

            # Get or calculate windowing
            window_width = ds.get("WindowWidth")
            window_center = ds.get("WindowCenter")
            if isinstance(window_width, pydicom.multival.MultiValue):
                window_width = float(window_width[0])
            if isinstance(window_center, pydicom.multival.MultiValue):
                window_center = float(window_center[0])
            if window_width is None:
                window_width = float(np.max(image_data) - np.min(image_data))
            if window_center is None:
                window_center = float((np.max(image_data) + np.min(image_data)) / 2)

            # Set sliders
            self.window_width.set(window_width)
            self.window_center.set(window_center)
            self.width_slider.config(from_=1, to=max(window_width * 2, 500))
            self.center_slider.config(from_=np.min(image_data), to=np.max(image_data))

            # Apply windowing and display image
            image_data = self.apply_windowing(image_data, window_width, window_center)
            image = Image.fromarray(image_data).convert("L")
            self.display_image(image)

            # Show metadata
            metadata = f"Patient Name: {ds.get('PatientName', 'N/A')}\n"
            metadata += f"Patient ID: {ds.get('PatientID', 'N/A')}\n"
            metadata += f"Modality: {ds.get('Modality', 'N/A')}\n"
            metadata += f"Study Date: {ds.get('StudyDate', 'N/A')}\n"
            self.metadata_label.config(text=metadata)

        except Exception as e:
            self.metadata_label.config(text=f"Error loading image: {e}")

    def apply_windowing(self, image_data, window_width, window_center):
        try:
            window_width = max(float(window_width), 1)
            window_center = float(window_center)
        except:
            window_width = np.max(image_data) - np.min(image_data)
            window_center = (np.max(image_data) + np.min(image_data)) / 2

        lower = window_center - (window_width / 2)
        upper = window_center + (window_width / 2)
        windowed = np.clip(image_data, lower, upper)
        windowed = ((windowed - lower) / (upper - lower) * 255.0).astype(np.uint8)
        return windowed

    def update_image(self, _=None):
        if self.dicom_data:
            window_width = self.window_width.get()
            window_center = self.window_center.get()
            image_data = self.dicom_data.pixel_array
            image_data = self.apply_windowing(image_data, window_width, window_center)
            image = Image.fromarray(image_data).convert("L")
            self.display_image(image)

    def display_image(self, image):
        self.canvas.delete("all")
        image = image.resize((512, 512), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(10, 10, anchor=tk.NW, image=self.photo)

    def start_storescp(self):
        storage_dir = "received_dicom"
        os.makedirs(storage_dir, exist_ok=True)
        try:
            storescp_path = os.path.join(os.path.dirname(__file__), "dcm4che-5.25.1", "bin", "storescp.bat")
            if not os.path.exists(storescp_path):
                raise FileNotFoundError(f"{storescp_path} not found!")
            self.storescp_process = subprocess.Popen([
                storescp_path, "-b", "STORESCP:11112", "--directory", storage_dir
            ])
            messagebox.showinfo("Info", f"storescp started. Listening on port 11112.\nSaving to {storage_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start storescp: {e}")

    def send_dicom_file(self):
        selected_item = self.treeview.selection()
        if selected_item:
            dicom_path = self.treeview.item(selected_item)["values"][0]
            try:
                storescu_path = os.path.join(os.path.dirname(__file__), "dcm4che-5.25.1", "bin", "storescu.bat")
                if not os.path.exists(storescu_path):
                    raise FileNotFoundError(f"{storescu_path} not found!")
                subprocess.run([storescu_path, "-c", "STORESCP@localhost:11112", dicom_path])
                messagebox.showinfo("Info", "DICOM file sent successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send DICOM file: {e}")

def main():
    root = tk.Tk()
    app = DICOMApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

