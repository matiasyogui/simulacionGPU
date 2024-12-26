import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

TEMP_INITIAL = 70
TEMP_MIN = 50
TEMP_MAX = 80
HEAT_RATE = 0.2
KP = 5
KI = 1

time = [0]
temperature = [TEMP_INITIAL]
perturbation = 0
system_active = True
current_setpoint = TEMP_MIN
entrada_history = [TEMP_MIN]
error_history = [TEMP_MIN - TEMP_INITIAL]
perturbation_history = [0]
integral_error = 0
last_perturbation = 0

def update(frame):
    global time, temperature, entrada_history, error_history, perturbation_history
    global last_perturbation, integral_error, system_active, perturbation
    
    if system_active:
        time_step = 1
        current_temp = temperature[-1]
        
        # CÁLCULO DE LA SEÑAL DE ERROR
        error = current_setpoint - current_temp
        
        # PERTURBACIONES (modificado para que sea un efecto único)
        delta_temp = 0
        if perturbation != 0:
            delta_temp = perturbation
            last_perturbation = perturbation  # Guardamos el valor de la perturbación
            perturbation = 0  # Reset de la perturbación después de aplicarla
        
        # CÁLCULO DEL CONTROLADOR PI
        integral_error += error * time_step
        controller = KP * error + KI * integral_error
        fan_speed = float(abs(controller) / 100)
        fan_speed = min(1.0, max(0.0, fan_speed))

        # CÁLCULO DE LA RESPUESTA DEL SISTEMA (MODELO FÍSICO)
        if current_temp < current_setpoint:
            delta_temp += HEAT_RATE * time_step
        else:
            cooling_factor = (current_temp - current_setpoint) / 20
            cooling_factor = min(1.0, max(0.0, cooling_factor))
            delta_temp += -fan_speed * cooling_factor * time_step * 2

        new_temp = current_temp + delta_temp

        if new_temp >= TEMP_MAX:
            system_active = False
            print("Sistema detenido: temperatura máxima alcanzada")
        
        # ACTUALIZACIÓN DE HISTORIALES
        temperature.append(new_temp)
        entrada_history.append(current_setpoint)
        error_history.append(error)
        perturbation_history.append(last_perturbation)
        time.append(time[-1] + time_step)
        
        last_perturbation = 0
        
        # ACTUALIZACIÓN DE LA INTERFAZ
        interface.update_temp_label(new_temp)
        interface.update_error_label(error)
        interface.update_control_labels(integral_error, controller, fan_speed)
        interface.update_entry_label()

    # ACTUALIZACIÓN DE LA GRÁFICA
    line_temp.set_data(time, temperature)
    line_setpoint.set_data(time, entrada_history)
    line_error.set_data(time, error_history)
    line_perturbation.set_data(time, perturbation_history)
    
    ax1.relim()
    ax1.autoscale_view(scalex=True, scaley=False)
    
    return line_temp, line_setpoint, line_error, line_perturbation


# Configuración del gráfico
fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()

# Crear las líneas para cada señal
line_temp, = ax1.plot([], [], label="Temperatura actual (°C)", color="red")
line_setpoint, = ax1.plot([], [], label="Temperatura deseada", color="green", linestyle='--')
line_error, = ax2.plot([], [], label="Error", color="purple")
line_perturbation, = ax1.plot([], [], label="Perturbación", color="orange", alpha=0.5)

# Configurar límites y etiquetas
ax1.set_ylim(0, 95) 
ax2.set_ylim(-30, 45) 
ax2.axhline(0, color='black', linestyle='--', alpha=0.3)
ax1.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='80°C')

# Etiquetas de los ejes
ax1.set_xlabel("Tiempo (s)")
ax1.set_ylabel("Temperatura (°C)", color="red")
ax2.set_ylabel("Error (°C)", color="purple")

ax1.tick_params(axis='y', labelcolor="red")
ax2.tick_params(axis='y', labelcolor="purple")

plt.title("Sistema de Control de Temperatura")

# Agregar todas las leyendas en un solo lugar
lines = [line_temp, line_setpoint, line_error, line_perturbation]
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left')

class ControlInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Control de Sistema")
        self.root.geometry("1200x800")

        # Agregar protocolo de cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Frame para los controles
        self.frame_controls = tk.Frame(self.root)
        self.frame_controls.pack(fill=tk.X, padx=10, pady=5)

        # Frame para las perturbaciones (MOVER AQUÍ, ANTES DE USARLO)
        self.frame_pert = tk.LabelFrame(self.frame_controls, text="Perturbaciones a aplicar en el sistema")
        self.frame_pert.pack(side=tk.LEFT, padx=5, pady=5)

        # Controles para setpoint
        self.frame_set = tk.LabelFrame(self.frame_controls, text="Setpoint/Entrada")
        self.frame_set.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Label(self.frame_set, text="Valor en °C:").pack(side=tk.LEFT, padx=5)
        self.set_entry = tk.Entry(self.frame_set, width=10)
        self.set_entry.pack(side=tk.LEFT, padx=5)

        self.set_button = tk.Button(self.frame_set, text="Cambiar", command=self.change_setpoint)
        self.set_button.pack(side=tk.LEFT, padx=5)

        # Nuevo frame para mostrar la Entrada
        self.frame_entry = tk.LabelFrame(self.frame_controls, text="Entrada")
        self.frame_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Label para la Entrada
        self.entry_label = tk.Label(self.frame_entry,
                                     text="--.- °C",
                                     font=("Arial", 14, "bold"),
                                     fg="green")
        self.entry_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Temperatura actual
        self.frame_temp = tk.LabelFrame(self.frame_controls, text="Temperatura Actual")
        self.frame_temp.pack(side=tk.LEFT, padx=5, pady=5)

        # Label para la temperatura actual
        self.temp_label = tk.Label(self.frame_temp, 
                                    text="--.- °C", 
                                    font=("Arial", 14, "bold"),
                                    fg="red")
        self.temp_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Frame para el error
        self.frame_error = tk.LabelFrame(self.frame_controls, text="Error")
        self.frame_error.pack(side=tk.LEFT, padx=5, pady=5)

        # Label para el error actual
        self.error_label = tk.Label(self.frame_error, 
                                    text="--.- °C", 
                                    font=("Arial", 14, "bold"),
                                    fg="purple")
        self.error_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Input para perturbación
        tk.Label(self.frame_pert, text="Valor:").pack(side=tk.LEFT, padx=5)
        self.pert_entry = tk.Entry(self.frame_pert, width=10)
        self.pert_entry.pack(side=tk.LEFT, padx=5)
        
        self.pert_button = tk.Button(self.frame_pert, text="Aplicar", command=self.apply_perturbation)
        self.pert_button.pack(side=tk.LEFT, padx=5)

        # Frame para la gráfica
        self.frame_plot = tk.Frame(self.root)
        self.frame_plot.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Canvas para la gráfica
        self.canvas = FigureCanvasTkAgg(fig, master=self.frame_plot)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Agregar frame para botones de control del sistema
        self.frame_system_controls = tk.Frame(self.root)
        self.frame_system_controls.pack(pady=5)

        # Solo el botón de reinicio completo
        self.full_reset_button = tk.Button(self.frame_system_controls, 
                                         text="Reiniciar Simulación", 
                                         command=self.full_reset,
                                         bg="red",
                                         fg="white",
                                         font=("Arial", 12, "bold"))
        self.full_reset_button.pack(padx=5)

    def change_setpoint(self):
        global current_setpoint
        try:
            value = float(self.set_entry.get())
            current_setpoint = value
            print(f"Setpoint cambiado a {value}")
            self.set_entry.delete(0, tk.END)
        except ValueError:
            print("Entrada no válida. Ingrese un número.")

    def update_temp_label(self, temp):
        """Actualiza el label con la temperatura actual"""
        self.temp_label.config(text=f"{temp:.1f} °C")

    def update_error_label(self, error):
        """Actualiza el label con el error actual"""
        self.error_label.config(text=f"{error:.1f} °C")

    def update_control_labels(self, integral_error, controller, fan_speed):
        """Actualiza los labels de las variables de control"""
        # Eliminamos esta parte ya que ahora mostraremos la Entrada
        pass

    def update_entry_label(self):
        """Actualiza el label con la Entrada actual"""
        self.entry_label.config(text=f"{current_setpoint:.1f} °C")

    def on_closing(self):
        """Maneja el cierre de la ventana"""
        plt.close('all')
        self.root.quit()
        self.root.destroy()

    def reset_simulation(self):
        """Reinicia todas las variables de la simulación"""
        global time, temperature, perturbation, system_active, current_setpoint
        global entrada_history, error_history, perturbation_history, integral_error, last_perturbation, ani

        # Reiniciar variables globales
        time = [0]
        temperature = [TEMP_INITIAL]
        perturbation = 0
        system_active = True
        current_setpoint = TEMP_MIN
        entrada_history = [TEMP_MIN]
        error_history = [TEMP_MIN - TEMP_INITIAL]
        perturbation_history = [0]
        integral_error = 0
        last_perturbation = 0

        # Limpiar las líneas del gráfico
        line_temp.set_data([], [])
        line_setpoint.set_data([], [])
        line_error.set_data([], [])
        line_perturbation.set_data([], [])

        # Actualizar labels
        self.update_temp_label(TEMP_INITIAL)
        self.update_error_label(TEMP_MIN - TEMP_INITIAL)
        self.update_control_labels(0, 0, 0)

        # Crear nueva animación
        try:
            ani.event_source.stop()
        except:
            pass
            
        ani = FuncAnimation(fig, update, interval=500, blit=True)
        print("Simulación reiniciada")

    def full_reset(self):
        """Cierra la ventana actual y reinicia la aplicación"""
        global time, temperature, perturbation, system_active, current_setpoint
        global entrada_history, error_history, perturbation_history, integral_error, last_perturbation

        # Reiniciar todas las variables globales
        time = [0]
        temperature = [TEMP_INITIAL]
        perturbation = 0
        system_active = True
        current_setpoint = TEMP_MIN
        entrada_history = [TEMP_MIN]
        error_history = [TEMP_MIN - TEMP_INITIAL]
        perturbation_history = [0]
        integral_error = 0
        last_perturbation = 0

        plt.close('all')  # Cerrar todas las figuras de matplotlib
        self.root.destroy()
        main()

    def apply_perturbation(self):
        """Aplica la perturbación ingresada"""
        global perturbation
        try:
            value = float(self.pert_entry.get())
            perturbation = value
            print(f"Perturbación aplicada: {value}")
            self.pert_entry.delete(0, tk.END)
        except ValueError:
            print("Entrada no válida. Ingrese un número.")

def main():
    try:
        global interface, ani
        plt.close('all')
        interface = ControlInterface()
        ani = FuncAnimation(fig, update, interval=500, blit=True, cache_frame_data=False)
        interface.root.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")

if __name__ == "__main__":
    main()
