import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import serial
import threading
import time

# Inicializar la comunicación serial con Arduino
arduino = serial.Serial("COM12", 9600)  # Reemplaza 'COM5' por el puerto correspondiente

# Listas para almacenar los valores de RPM y tiempo
datos_rpm = []
datos_tiempo = []
cantidad_muestras = 0
ref = 1100
lock = threading.Lock()  # Bloqueo para sincronizar el acceso a los datos

# Variables para almacenar los valores de Kp, Kd y Ki
kp = 0
kd = 0
ki = 0

# Variable para almacenar el estado de actualización de la gráfica
actualizar_grafica = True


# Función para leer los datos de RPM desde Arduino
def leer_rpm():
    global datos_rpm, datos_tiempo, cantidad_muestras
    while True:
        if arduino.in_waiting > 0:
            # Leer los datos desde Arduino
            rpm_str = arduino.readline().strip().decode()
            # Convertir la cadena de texto en un número de punto flotante (float)
            rpm = float(rpm_str)

            # Obtener el tiempo actual en segundos
            tiempo_actual = time.time()

            # Adquirir el bloqueo para acceder a los datos
            with lock:
                # Agregar el valor de RPM y tiempo a las listas de datos
                datos_rpm.append(rpm)
                datos_tiempo.append(tiempo_actual)
                cantidad_muestras += 1

                # Eliminar los valores más antiguos que están fuera del rango de tiempo deseado (últimos 2 segundos)
                while datos_tiempo and tiempo_actual - datos_tiempo[0] > 2:
                    datos_rpm.pop(0)
                    datos_tiempo.pop(0)


# Función para establecer los valores de Kp, Kd y Ki
# Función para establecer los valores de RPM, Kp, Kd y Ki
def establecer_parametros():
    global rpm, kp, kd, ki, ref
    rpm_str = entry_rpm.get()
    kp_str = entry_kp.get()
    kd_str = entry_kd.get()
    ki_str = entry_ki.get()
    if rpm_str and kp_str and kd_str and ki_str:
        rpm = int(rpm_str)
        kp = float(kp_str)
        kd = float(kd_str)
        ki = float(ki_str)
        #print("RPM: ",rpm)
        ref = int(rpm)
        # Enviar los valores de RPM, Kp, Kd y Ki a Arduino a través de la comunicación serial
        comando_parametros = f"\nRPM:{rpm} \nKp:{kp} \nKd:{kd} \nKi:{ki}\n"
        #comando_parametros = ""+str(rpm)+" "+str(kp)+" "+str(ki)+" "+str(kd)
        arduino.write(comando_parametros.encode())
    else:
        print("Error")
        # Alguno de los campos de entrada está vacío, puedes mostrar un mensaje de error o realizar alguna otra acción.

#Funcion para restablecer valores

def reset(rpm_label,kp_label,ki_label,kd_label):
    global rpm, kp, kd, ki
    rpm_str = "600"
    rpm_label.delete(0, END)
    rpm_label.insert(0,str(rpm_str))
    kp_str = "1"
    #kp_label.delete(0,END)
    kp_label.insert(0,str(kp_str))
    ki_str = "0.001"
    #ki_label.delete(0,END)
    ki_label.insert(0,str(ki_str))
    kd_str = "2"
    #kd_label.delete(0,END)
    kd_label.insert(0,str(kd_str))
    
    if rpm_str and kp_str and kd_str and ki_str:
        rpm = float(rpm_str)
        kp = float(kp_str)
        ki = float(ki_str)
        kd = float(kd_str)
        # Enviar los valores de RPM, Kp, Kd y Ki a Arduino a través de la comunicación serial
        #comando_parametros = f"\nRPM:{rpm} \nKp:{kp} \nKd:{kd} \nKi:{ki}\n"
        comando_parametros = f"{rpm} {kp} {ki} {kd}"
        arduino.write(comando_parametros.encode())
    else:
        print("Error")
        # Alguno de los campos de entrada está vacío, puedes mostrar un mensaje de error o realizar alguna otra acción.


# Crear la ventana principal
ventana = tk.Tk(baseName="Control")

# Configurar la ventana
ventana.title("Sistemas de Control - RPM")
ventana.geometry("640x650")

# Crear la etiqueta de RPM
etiqueta_rpm = tk.Label(ventana, text="RPM:")
etiqueta_rpm.grid(row=2, column=0, sticky="S")
entry_rpm = tk.Entry(ventana,width = 8)
entry_rpm.insert(0,"600")
entry_rpm.grid(row=3, column=0, sticky="N")

# Crear la etiqueta de Kp
etiqueta_kp = tk.Label(ventana, text="Kp:")
etiqueta_kp.grid(row=2, column=1, sticky="S")
entry_kp = tk.Entry(ventana,width = 8)
entry_kp.insert(0,"0.3")
entry_kp.grid(row=3, column=1, sticky="N")

# Crear la etiqueta de Ki
etiqueta_ki = tk.Label(ventana, text="Ki:")
etiqueta_ki.grid(row=2, column=2, sticky="S")
entry_ki = tk.Entry(ventana,width=8)
entry_ki.insert(0,"0.2")
entry_ki.grid(row=3, column=2, sticky="N")

# Crear la etiqueta de Kd
etiqueta_kd = tk.Label(ventana, text="Kd:")
etiqueta_kd.grid(row=2, column=3, sticky="S")
entry_kd = tk.Entry(ventana,width=8)#,textvariable="1")
entry_kd.insert(0,"0.1")
entry_kd.grid(row=3, column=3, sticky="N")



# Crear el botón para establecer los parámetros
boton_parametros = tk.Button(ventana, text="Enviar", width=6, command=establecer_parametros)
boton_parametros.grid(row=3, column=5)#, columnspan=8)
#boton_reset = tk.Button(ventana, text="Reset", width=6, command=reset(entry_rpm,entry_kp,entry_ki,entry_kd))
#boton_reset.grid(row=3, column=5)#, columnspan=8)

# Crear la etiqueta para mostrar el valor de RPM actualizado
etiqueta_rpm_actualizado = tk.Label(ventana, text="RPM:")
etiqueta_rpm_actualizado.grid(row=7, column=0,sticky="W")#, columnspan=8)
'''
error = tk.Label(ventana, text="Error: ")
error.grid(row=8, column=0, sticky = "W")

nombre1 = tk.Label(ventana, text=" ‣Jesús Abraham Ramírez Niebla - 01176033", font="Raleway 15 bold")
nombre1.grid(row=5, column=0, columnspan=8, sticky = "W")
nombre2 = tk.Label(ventana, text=" ‣José Carlos Ponce Odohui - 01169598", font="Raleway 15 bold")
nombre2.grid(row=6, column=0, columnspan=8, sticky = "W")
'''


# Crear la figura y el eje para el gráfico
fig, ax = plt.subplots()
(linea,) = ax.plot([], [], "b-", label='Lectura')
(linea_error,) = ax.plot([], [], "r--", label='Error')
ax.set_xlabel("Tiempo")
ax.set_ylabel("RPM")
ax.set_ylim(0, 1500)
ax.set_xlim(0, 3)
ax.set_title("Control de velocidad de Motor DC")

# Crear el lienzo de Matplotlib
lienzo = FigureCanvasTkAgg(fig, master=ventana)
lienzo.draw()
lienzo.get_tk_widget().grid(row=0, column=0, columnspan=8)

# Variable para almacenar el límite actual del eje X
limite_actual_x = ax.get_xlim()


def actualizar_grafico(frame):
    global datos_rpm, cantidad_muestras, limite_actual_x, actualizar_grafica, ref
    #error.labelText="Error: "+str((ref-datos_rpm[-1])/ref/100)
    
    with lock:
        cantidad = min(cantidad_muestras, len(datos_rpm))
        if cantidad > 0:
            linea.set_data(datos_tiempo[-cantidad:], datos_rpm[-cantidad:])
            #error.config(text="Error: {:.2f}".format(((int(ref) - float(datos_rpm[-1]))/int(ref))*100))
            etiqueta_rpm_actualizado.config(text="RPM: "+str(datos_rpm[-1]))
            if actualizar_grafica:
                limite_x = (datos_tiempo[-cantidad], datos_tiempo[-1])
                # Verificar si los límites son diferentes antes de establecerlos
                if limite_x[0] != limite_x[1]:
                    ax.set_xlim(limite_x)  # Actualizar el límite del eje X
                    limite_actual_x = limite_x
            else:
                # Restaurar el límite del eje X a su valor original
                ax.set_xlim(limite_actual_x)
                # Habilitar la actualización automática de la gráfica
                actualizar_grafica = True


"""
# Función de animación para actualizar el gráfico
def actualizar_grafico(frame):
    global datos_rpm, cantidad_muestras, limite_actual_x, actualizar_grafica
    with lock:
        cantidad = min(cantidad_muestras, len(datos_rpm))
        if cantidad > 0:
            linea.set_data(datos_tiempo[-cantidad:], datos_rpm[-cantidad:])
            
            # Agregar línea de error
            error = datos_rpm[-1]/ref  # Reemplaza 'calcular_error()' con tu lógica para obtener los valores de error
            ax.errorbar(datos_tiempo[-cantidad:], datos_rpm[-cantidad:], yerr=error, fmt='none', color='red')
            
            etiqueta_rpm_actualizado.config(text=str(datos_rpm[-1]))
            if actualizar_grafica:
                limite_x = (datos_tiempo[-cantidad], datos_tiempo[-1])
                if limite_x[0] != limite_x[1]:
                    ax.set_xlim(limite_x)
                    limite_actual_x = limite_x
            else:
                ax.set_xlim(limite_actual_x)
                actualizar_grafica = True
"""


# Crear la animación
animacion = FuncAnimation(fig, actualizar_grafico, frames=10, interval=100)

# Iniciar la lectura de datos de RPM en un hilo separado
hilo_lectura = threading.Thread(target=leer_rpm)
hilo_lectura.daemon = True
hilo_lectura.start()

# Iniciar el bucle principal de la interfaz gráfica
ventana.mainloop()