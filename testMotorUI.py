import tkinter as tk
from tkinter import Label, Entry, Button, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import serial
import time
import threading

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gauge & Graph")
        self.geometry("800x600")

        self.gauge_frame = tk.Frame(self)
        self.gauge_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.figure = Figure(figsize=(4, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.gauge_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.label = Label(self.gauge_frame, text="", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.max_value_entry = Entry(self.gauge_frame, width=10)
        self.max_value_entry.pack(pady=5)

        self.max_value_button = Button(self.gauge_frame, text="Actualizar Máximo", command=self.update_max_value)
        self.max_value_button.pack(pady=5)

        self.pid_frame = tk.Frame(self.gauge_frame)
        self.pid_frame.pack(pady=10)

        self.p_label = Label(self.pid_frame, text="P:")
        self.p_label.grid(row=0, column=0)
        self.p_entry = Entry(self.pid_frame, width=10)
        self.p_entry.grid(row=0, column=1, padx=5)

        self.i_label = Label(self.pid_frame, text="I:")
        self.i_label.grid(row=0, column=2)
        self.i_entry = Entry(self.pid_frame, width=10)
        self.i_entry.grid(row=0, column=3, padx=5)

        self.d_label = Label(self.pid_frame, text="D:")
        self.d_label.grid(row=0, column=4)
        self.d_entry = Entry(self.pid_frame, width=10)
        self.d_entry.grid(row=0, column=5, padx=5)

        self.pid_button = Button(self.pid_frame, text="Actualizar PID", command=self.update_pid_values)
        self.pid_button.grid(row=0, column=6, padx=5)

        self.graph_frame = tk.Frame(self)
        self.graph_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.graph_figure = Figure(figsize=(4, 4), dpi=100)
        self.graph_ax = self.graph_figure.add_subplot(111)
        self.graph_canvas = FigureCanvasTkAgg(self.graph_figure, master=self.graph_frame)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.serial_port = 'COM12'
        self.serial_baud = 9600
        self.arduino = serial.Serial(self.serial_port, self.serial_baud, timeout=0.1)

        self.max_value = 600

        self.p_value = 0.0
        self.i_value = 0.0
        self.d_value = 0.0

        self.time_data = []
        self.rpm_data = []
        self.start_time = time.time()

        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        self.serial_thread.start()

        self.update_plot()

    def read_serial_data(self):
        while True:
            if self.arduino.in_waiting > 0:
                serial_data = self.arduino.readline().decode("utf-8").strip()
                print(f"Datos recibidos: {serial_data}")  # Imprimir datos recibidos para depuración

                try:
                    if serial_data:
                        parts = serial_data.split(",")
                        data_dict = {}

                        for part in parts:
                            key, value = part.split("=")
                            data_dict[key.strip()] = value.strip()

                        if "RPM" in data_dict:
                            rpm_value = int(data_dict["RPM"])
                            self.label.config(text=f"RPM actual: {rpm_value}")

                            current_time = time.time() - self.start_time
                            self.time_data.append(current_time)
                            self.rpm_data.append(rpm_value)

                            # Mantener sólo los últimos 100 puntos de datos
                            self.time_data = self.time_data[-100:]
                            self.rpm_data = self.rpm_data[-100:]

                            self.update_graph()
                        else:
                            print("RPM no encontrado en los datos recibidos.")
                except ValueError as e:
                    print(f"Error de conversión: {e}")  # Imprimir el error de conversión para depuración
                except Exception as e:
                    print(f"Error inesperado: {e}")  # Imprimir cualquier otro error inesperado

    def update_graph(self):
        self.graph_ax.clear()
        self.graph_ax.plot(self.time_data, self.rpm_data, color='blue')
        self.graph_ax.set_xlabel("Tiempo (s)")
        self.graph_ax.set_ylabel("RPM")
        self.graph_ax.set_title("RPM vs. Tiempo")
        self.graph_canvas.draw()

    def update_plot(self):
        self.after(20, self.update_plot)

    def update_max_value(self):
        try:
            max_value = int(self.max_value_entry.get())
            self.max_value = max_value
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce un valor entero válido para el máximo.")

    def update_pid_values(self):
        try:
            self.p_value = float(self.p_entry.get())
            self.i_value = float(self.i_entry.get())
            self.d_value = float(self.d_entry.get())

            pid_values = f"{self.p_value},{self.i_value},{self.d_value}\n"
            self.arduino.write(pid_values.encode())

            messagebox.showinfo("PID Actualizado", f"Valores PID actualizados:\nP: {self.p_value}\nI: {self.i_value}\nD: {self.d_value}")
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce valores numéricos válidos para PID.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
