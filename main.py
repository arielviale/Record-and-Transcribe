import os
import tempfile
import wave
import pyaudio
import pyperclip
import threading
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from groq import Groq

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Lee la API key desde la variable de entorno
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError("La variable de entorno GROQ_API_KEY no está definida.")

# Inicializa el cliente de transcripción
client = Groq(api_key=api_key)

# Variables globales
grabando = False

def grabar_audio(frecuencia_muestreo=16000, canales=1, fragmento=1024):
    global grabando
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=canales,
        rate=frecuencia_muestreo,
        input=True,
        frames_per_buffer=fragmento,
    )
    frames = []
    while grabando:
        data = stream.read(fragmento)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()
    return frames, frecuencia_muestreo

def guardar_audio(frames, frecuencia_muestreo, canales):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_temp:
        wf = wave.open(audio_temp.name, "wb")
        wf.setnchannels(canales)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(frecuencia_muestreo)
        wf.writeframes(b"".join(frames))
        wf.close()
        return audio_temp.name

def transcribir_audio(ruta_archivo_audio):
    try:
        with open(ruta_archivo_audio, "rb") as archivo:
            transcripcion = client.audio.transcriptions.create(
                file=(os.path.basename(ruta_archivo_audio), archivo.read()),
                model="whisper-large-v3",
                prompt="el audio es de una persona normal trabajando",
                response_format="text",
                language="es",
            )
        return transcripcion
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error durante la transcripción: {str(e)}")
        return None

def copiar_transcripcion_al_portapapeles(texto):
    pyperclip.copy(texto)
    messagebox.showinfo("Transcripción copiada", "La transcripción se ha copiado al portapapeles.")

def iniciar_grabacion():
    global grabando
    grabando = True
    btn_grabar.config(state="disabled")
    btn_detener.config(state="normal")
    threading.Thread(target=procesar_grabacion).start()

def detener_grabacion():
    global grabando
    grabando = False
    btn_grabar.config(state="normal")
    btn_detener.config(state="disabled")

def procesar_grabacion():
    frames, frecuencia_muestreo = grabar_audio(canales=1)
    archivo_audio_temp = guardar_audio(frames, frecuencia_muestreo, canales=1)
    print("Transcribiendo...")
    transcripcion = transcribir_audio(archivo_audio_temp)
    if transcripcion:
        print("\nTranscripción:")
        print(transcripcion)
        copiar_transcripcion_al_portapapeles(transcripcion)
    os.unlink(archivo_audio_temp)

# Configuración de la interfaz gráfica
ventana = tk.Tk()
ventana.title("Record and Transcribe")
ventana.geometry("400x200")

lbl_instruccion = tk.Label(ventana, text="Presiona el botón para grabar audio y transcribirlo:")
lbl_instruccion.pack(pady=10)

btn_grabar = tk.Button(ventana, text="Iniciar Grabación", command=iniciar_grabacion, bg="green", fg="white", font=("Arial", 12))
btn_grabar.pack(pady=10)

btn_detener = tk.Button(ventana, text="Detener Grabación", command=detener_grabacion, bg="red", fg="white", font=("Arial", 12), state="disabled")
btn_detener.pack(pady=10)

ventana.mainloop()











