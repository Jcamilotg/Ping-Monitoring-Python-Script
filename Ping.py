import subprocess
import platform
import time
import csv
import os
import re
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from datetime import datetime

Green="\033[1;33m"
Blue="\033[1;34m"
Grey="\033[1;30m"
Red="\033[1;31m"

print(" "+ Red + "_______________________________________________________________")
print(" |  " +Blue  +"  ____ ___ _   _  ____       _  ____ _____ ____ "+ Grey +"|")
print(" |  " +Blue  +" |  _ \_ _| \ | |/ ___|     | |/ ___|_   _/ ___|"+ Grey +"|")
print(" |  " +Blue  +" | |_) | ||  \| | |  _   _  | | |     | || |  _ "+ Grey +"|")
print(" |  " +Blue  +" |  __/| || |\  | |_| | | |_| | |___  | || |_| |"+ Grey +"|")
print(" |  " +Blue  +" |_|  |___|_| \_|\____|  \___/ \____| |_| \____|"+ Grey +"|")
print(" |  " +Blue  +"                                                "+ Grey +"|")
print(" "+ Red + "_______________________________________________________________")

horaini = timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")  # Solo la hora
horainiping = datetime.now()

# Dirección IP o dominio a hacer ping
HOST = input("\nIngresar Direccion IP o Dominio Y Presione Enter: ")  # Cambia por el dominio o IP deseado
intervalo = float(input("Ingrese el Intervalo del Ping en Segundos:   "))
nombre_log = input("\nIngrese Nombre del Archivo Log y Presione Enter:   ")
# Configuración del log
LOG_FILE = f"{nombre_log}.csv"

fallalist = []

# Máximo de puntos en la gráfica
MAX_POINTS = 86400  # Limita la memoria usada
times = deque(maxlen=MAX_POINTS)
latencies = deque(maxlen=MAX_POINTS)
failures = {}  # Diccionario para almacenar las fallas con fecha y hora

# Verifica si el archivo de log existe, si no, crea el encabezado
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Fecha", "Hora", "IP/Dominio", "Latencia (ms)"])  # Encabezados


# Función para realizar ping
def ping(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        result = subprocess.run(
            ["ping", param, "1", host],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout.lower()

        # Detecta si el resultado contiene latencia (para español o inglés)
        match = re.search(r"tiempo[=<]?\s?(\d+\.\d+|\d+|tiempo<1m|tiempo=1ms)m", output) or re.search(r"time[=<]?\s?(\d+\.\d+|\d+) ms", output)

        print(match)
        #Macbook linux
        #match = re.search(r"time[=<]?\s?(\d+\.\d+|\d+) ms", output)

        if match:
            return float(match.group(1))  # Extrae solo el número y convierte a float
        else:
            return None  # Fallo en la respuesta
    except Exception as e:
        print(f"Error: {e}")
        return None


# Función para almacenar datos en el log CSV
def log_ping(latency):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    with open(LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date_str, time_str, HOST, latency if latency is not None else "Fallo"])


# Función para actualizar la gráfica
def update(frame):
    latency = ping(HOST)
    timestamp = datetime.now().strftime("%H:%M:%S")  # Solo la hora

    times.append(timestamp)  # Agrega la hora
    #times.append(time.time())  # Agrega la marca de tiempo


    latencies.append(latency if latency is not None else 0)  # 0 en caso de fallo

    # Guardar en el log
    log_ping(latency)

    # Si es una falla, la registramos con su timestamp
    if latency is None:
        failures[timestamp] = 0  # Registrar la falla en el diccionario

    ax.clear()

    # Dibujar la línea del ping en azul
    ax.plot(times, latencies, marker="o", linestyle="-", color="b", label="Ping (ms)")


    # Dibujar todas las fallas registradas con puntos rojos
    for fail_time, fail_value in failures.items():
        if fail_time in times:  # Solo dibujar las fallas dentro del rango visible
            fallalist.append(fail_time)
            ax.scatter(fail_time, fail_value, color="red", s=100, label=f"Falla{fail_time}")
            ax.text(fail_time, fail_value, f"Falla{fail_time}", fontsize=10, color="red", ha="right", va="bottom", rotation=90)

    ax.axhline(y=0, color="r", linestyle="--", label="Cero (ms)")

    # 🔹 **Eliminar márgenes laterales**
    ax.set_xlim(auto=True)  # Ajustar automáticamente el eje X
    ax.set_ylim(min(latencies) - 1, max(latencies) + 1)  # Ajustar límites del eje Y

    # 🔹 **Ajustar el espacio de la gráfica**
    plt.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.15)  # Reduce márgenes generales

    # 🔹 **Optimizar etiquetas en el eje X**
    if len(times) > 15:  # Asegurar que haya suficientes elementos en la lista
        tick_positions = list(range(0, len(times), 15))  # Tomar cada 5 elementos
        tick_labels = [times[i] for i in tick_positions]  # Obtener los valores correspondientes

        ax.set_xticks(tick_positions)  # Definir las posiciones en el eje X
        ax.set_xticklabels(tick_labels, rotation=90, ha="right")  # Asignar etiquetas y girarlas
    #plt.xticks(rotation=90, ha="right")  # Gira y alinea etiquetas del eje X
    #ax.set_xticklabels(list(times)[::5], rotation=90, ha="right")
    horaping = datetime.now()
    #plt.xticks(rotation=90)  # Rota etiquetas para mejor visibilidad
    tiempo_transcurrido = (horaping - horainiping).total_seconds() / 60  # Convertir a minutos

    if failures:  # Verificar si hay fallas registradas
        ultima_falla = max(failures.keys())  # Última hora de falla registrada

        # Sumar tiempo total de fallas
        tiempo_total_fallas = len(failures) * intervalo  # Multiplica la cantidad de fallas por el intervalo

        mensaje_falla = f" | Última Falla: {ultima_falla} | Tiempo Total de Fallas: {tiempo_total_fallas:.1f} segundos"
    else:
        mensaje_falla = " | Sin Fallas registradas"


    ax.set_title(color="red",fontsize=20, label=(f"Ping a {HOST} | Intervalo:{intervalo} | Archivo_Log:{nombre_log} | Inicio Prueba: {horaini}"))
    ax.set_xlabel(f"Tiempo Transcurrido {tiempo_transcurrido:.1f} Minutos | Fallas Totales: {len(failures)}{mensaje_falla}",color="red",fontsize=20)
    ax.set_ylabel("Latencia (ms)")
    ax.legend()
    ax.grid(True)


# Configuración de la gráfica
#fig = plt.figure(figsize=(15, 7), dpi=100)
#fig, ax = plt.subplots()
fig, ax = plt.subplots(figsize=(15, 7), dpi=75)

ani = animation.FuncAnimation(fig, update, interval=(1000*intervalo), cache_frame_data=False)  # Cada 10 seg

plt.show()
