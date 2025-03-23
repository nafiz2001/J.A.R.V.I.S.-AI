import os
import webbrowser
import pyttsx3
import speech_recognition as sr
import subprocess
import sys
import psutil
import requests
import wikipedia
import tkinter as tk
from tkinter import scrolledtext, ttk  # Import ttk for themed widgets
import threading
import queue
from PIL import Image, ImageTk
from io import BytesIO
import time
import random
import pyautogui

# --- Configuration and Setup ---

def load_api_key():
    try:
        with open("api_key.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: api_key.txt not found.  Create it and add your API key.")
        return None  # Return None, not an empty string
    except Exception as e:
        print(f"Error loading API key: {e}")
        return None

GEMINI_API_KEY = "AIzaSyBgsC0m3ihgitP8w10Aoor4rcNSYosytho"

# --- Speech and Voice Functions ---

# Initialize pyttsx3 engine outside the speak function
engine = pyttsx3.init()

def speak(text, force_speak=False):
    """Speaks the given text aloud, only if speaking_mode is True."""
    global speaking_mode
    if speaking_mode or force_speak: #added force speak
        text = text.replace('*', '').replace('`', '')  # Basic cleanup
        print(f"Jervis (Speaking): {text}")
        engine.say(text)
        engine.runAndWait()  # This must be in the same function as .say()
    else:
        print(f"Jervis (Silent): {text}")

def listen():
    """Listens for voice commands and returns the recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")
        return ""

# --- Core Application Logic ---

def open_application(app_name):
    apps = {
        "notepad": "notepad.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "whatsapp": "C:\\Program Files (x86)\\WhatsApp\\WhatsApp.exe",  # Corrected path
    }
    if app_name in apps:
        try:  # Added error handling
            subprocess.Popen(apps[app_name], shell=True)
            display_message(f"Opening {app_name}")
        except FileNotFoundError:
            display_message(f"Could not find application: {app_name}")
        except Exception as e:
            display_message(f"Error opening {app_name}: {e}")
    else:
        display_message("Application not found in my list.")

def close_application(app_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if app_name.lower() in proc.info['name'].lower():
            try:
                os.kill(proc.info['pid'], 9)
                display_message(f"Closing {app_name}")
                return  # Exit after closing
            except Exception as e:
                display_message(f"Error closing {app_name}: {e}")
                return
    display_message("Application not found running.")

def open_website(site):
    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
    }
    if site in websites:
        webbrowser.open(websites[site])
        display_message(f"Opening {site}")
    else:
        display_message("Website not found in my list.")

def play_music():
    music_dir = "C:\\Users\\<YourUsername>\\Music"  # REPLACE WITH YOUR MUSIC DIR
    try:
        songs = os.listdir(music_dir)
        if songs:
            random_song = random.choice(songs)
            os.startfile(os.path.join(music_dir, random_song))
            display_message(f"Playing {random_song}")
        else:
            display_message("No music found in your music directory.")
    except FileNotFoundError:
        display_message("Music directory not found.  Check the path.")
    except Exception as e:
        display_message(f"Error playing music: {e}")

def tell_joke():
    jokes = [
       "Why don't programmers like nature? It has too many bugs!",
        "Why was the equal sign so humble? Because he wasn't greater than or less than anyone else.",
        "Why did the programmer quit his job? He didn't get arrays!",
        "An SQL query walks into a bar, walks up to two tables, and asks, 'Can I join you?'",
        "Why did the coffee go to the police? It got mugged."
    ]
    joke = random.choice(jokes)
    display_message(joke)
    if speaking_mode:  # Only speak if speaking mode is on
        speak(joke)

def control_volume(action):
    if "increase" in action:
        pyautogui.press("volumeup", presses=5)
        display_message("Volume increased.")
    elif "decrease" in action:
        pyautogui.press("volumedown", presses=5)
        display_message("Volume decreased.")
    elif "mute" in action:
        pyautogui.press("volumemute")
        display_message("Volume muted.")

def take_note():
    speak("What should I write?", force_speak=True)  # Force speak for the prompt
    note_text = listen()
    if note_text:
        try:
            with open("notes.txt", "a", encoding="utf-8") as f:
                f.write(note_text + "\n")
            display_message("Note saved.")
        except Exception as e:
            display_message(f"Error saving note: {e}")
    else:
        display_message("I didn't hear anything to note.")

def read_notes():
    try:
        with open("notes.txt", "r", encoding="utf-8") as f:
            notes = f.readlines()
        if notes:
            display_message("Here are your notes:")
            for note in notes:
                display_message(note.strip())
                speak(note.strip())
        else:
            display_message("No notes found.")
    except FileNotFoundError:
        display_message("Notes file not found.")
    except Exception as e:
        display_message(f"Error reading notes: {e}")

def system_control(action):
    if "shutdown" in action:
        display_message("Shutting down in 5 seconds...")
        speak("Shutting down.", force_speak=True)
        os.system("shutdown /s /t 5")
    elif "restart" in action:
        display_message("Restarting in 5 seconds...")
        speak("Restarting.", force_speak=True)
        os.system("shutdown /r /t 5")

def send_email():
    display_message("Email functionality is not yet implemented.")
    # Placeholder for email functionality

def get_gemini_response(prompt):
    if not GEMINI_API_KEY:
        return "API key not loaded.  Check your api_key.txt file."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.85,
            "topK": 40,
            "maxOutputTokens": 2048,
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)  # Add a timeout
        response.raise_for_status()  # Will raise an HTTPError for bad requests (4xx or 5xx)
        response_json = response.json()

        if 'candidates' in response_json and response_json['candidates']:
            first_candidate = response_json['candidates'][0]
            if 'content' in first_candidate and 'parts' in first_candidate['content']:
                text = first_candidate['content']['parts'][0].get('text')
                if text:
                    return text.replace('*', '').replace('`', '')  # Cleanup
                else:
                    return "Gemini returned an empty response."
            else:
                return "Gemini returned an unexpected response structure."
        else:
            return "No response from Gemini."

    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"
    except (KeyError, IndexError) as e:
        return f"Error parsing Gemini response: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def list_commands():
    commands = {
        "open [application name]": "Opens an application.",
        "close [application name]": "Closes an application.",
        "search [query]": "Performs a Google search.",
        "wikipedia [topic]": "Searches Wikipedia.",
        "play music": "Plays music from your music folder.",
        "tell a joke": "Tells a joke.",
        "volume increase/decrease/mute": "Controls system volume.",
        "take a note": "Takes a note and saves it.",
        "read notes": "Reads your saved notes.",
        "shutdown/restart": "Shuts down or restarts the computer.",
        "email": "Sends an email (not yet implemented).",
        "goodbye": "Exits the assistant.",
        "give me all commands": "Lists available commands.",
        "ai [query]": "Asks Gemini a question directly.",
        "start listening": "Activates voice control.",
        "stop listening": "Deactivates voice control.",
        "text mode": "Enter a mode for typing inputs.",
        "exit text mode": "exits text mode.",
    }
    display_message("Available commands:")
    for command, description in commands.items():
        display_message(f"- {command}: {description}")

# --- GUI Functions ---

def display_message(message):
    """Displays a message in the GUI's text area."""
    message_queue.put(message)

def send_command():
    """Gets the text from the command entry and processes it."""
    command_text = command_entry.get()
    command_entry.delete(0, tk.END)  # Clear entry
    if command_text:  # Avoid empty commands
        display_message(f"You: {command_text}")  # Show user's input
        process_command(command_text)

def update_gui():
    """Updates the GUI with messages from the message queue."""
    while True:
        try:
            message = message_queue.get(timeout=0.1)  # Non-blocking
            print(f"Updating GUI with message: {message}")  # Debugging statement
            message_area.config(state=tk.NORMAL)  # Enable editing
            message_area.insert(tk.END, message + "\n")
            message_area.config(state=tk.DISABLED)  # Disable editing
            message_area.see(tk.END)  # Scroll to the end
        except queue.Empty:
            pass  # Keep checking

def initialize_gui():
    """Sets up the Tkinter GUI."""
    global root, message_area, command_entry, listen_button, style
    root = tk.Tk()
    root.title("Jervis AI Assistant")
    root.geometry("600x500")
    root.configure(bg="#2c3e50")  # Dark blue background

    # Use ttk style for themed widgets
    style = ttk.Style(root)
    style.theme_use('clam')  # Use the 'clam' theme –  good cross-platform choice

    # Configure style
    style.configure("TLabel", foreground="white", background="#2c3e50", font=("Arial", 12))
    style.configure("TButton", foreground="#2c3e50", background="#ecf0f1", font=("Arial", 12))
    style.configure("TEntry", foreground="#2c3e50", fieldbackground="white", font=("Arial", 12))
    style.configure("TText", foreground="black", background="white", font=("Arial", 12))
    style.map("TButton",
        foreground=[('pressed', 'white'), ('active', 'white')],
        background=[('pressed', '!disabled', '#34495e'), ('active', '#3498db')]
    )
    # Try to load a Jervis icon (optional)
    try:
        image_path = "your_jervis_icon.png"  #  path to your icon file
        if os.path.exists(image_path):  # Check if the image exists
           img = Image.open(image_path)
           img = img.resize((50, 50), Image.LANCZOS)  # Use LANCZOS for high-quality resizing
           jervis_icon = ImageTk.PhotoImage(img)
           icon_label = tk.Label(root, image=jervis_icon, bg="#2c3e50")
           icon_label.image = jervis_icon  # Keep a reference
           icon_label.pack(pady=(10, 5))  # Add some padding at the top
        else:
            print("Icon file not found.")
    except Exception as e:
        print(f"Error loading icon: {e}")
    # Message area (ScrolledText)
    message_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=15, font=("Arial", 12))
    message_area.pack(padx=10, pady=(0, 10), expand=True, fill=tk.BOTH)
    message_area.config(state=tk.DISABLED)

    # Command entry
    command_entry = ttk.Entry(root, width=50, font=("Arial", 12))
    command_entry.pack(pady=5, padx=10)
    command_entry.bind("<Return>", lambda event: send_command())

    # Buttons Frame for better layout
    buttons_frame = ttk.Frame(root) # Create a frame for buttons
    buttons_frame.pack(pady=5, padx=10, fill=tk.X) #Pack

    # Send Button
    send_button = ttk.Button(buttons_frame, text="Send", command=send_command, width=15)
    send_button.pack(side=tk.LEFT, padx=5)

    # Listen/Stop Listen Button
    listen_button = ttk.Button(buttons_frame, text="Start Listening", command=toggle_listening, width=15)
    listen_button.pack(side=tk.LEFT, padx=5)

    # ---  Text Mode Functions (integrated) ---

def enter_text_mode():
    """Enters text mode, disabling speaking and using text input."""
    global speaking_mode
    speaking_mode = False  # Disable speaking
    display_message("Entering text mode.  Speak commands are disabled.")

def exit_text_mode():
   """Placeholder. In a full implementation, you might re-enable speaking."""
   global speaking_mode
   speaking_mode = True
   display_message("Exiting text mode. Speak commands enabled")

def toggle_listening():
    """Toggles the listening mode (activated by the button)."""
    global listening_thread, speaking_mode
    if listening_thread is None or not listening_thread.is_alive():
        speaking_mode = True  # Enable speaking when starting to listen
        listening_thread = threading.Thread(target=listen_for_commands, daemon=True)
        listening_thread.start()
        listen_button.config(text="Stop Listening")
    else:
        speaking_mode = False
        listen_button.config(text="Start Listening")  # Don't join, just update button
        display_message ("Stopped Listening")

def listen_for_commands():
    """Continuously listens for commands in a separate thread."""
    global speaking_mode
    display_message("Listening...")
    while speaking_mode:  # Use speaking_mode as the loop condition
        command = listen()
        if command:
            if "stop listening" in command or "stop speak" in command:
                display_message("Stopping listening mode.")
                speaking_mode = False  # Turn off speaking mode
                listen_button.config(text="Start Listening") #Change button
                break  # Exit the loop
            else:
                process_command(command)  # Process normally
        time.sleep(0.1)

def process_command(command):
    """Handles the given command."""
    if not command:
        return

    if "open" in command:
        open_application(command.replace("open", "").strip())
    elif "close" in command:
        close_application(command.replace("close", "").strip())
    elif "search" in command:
        webbrowser.open(f"https://www.google.com/search?q={command.replace('search', '').strip()}")
        display_message("Here are the search results.")
    elif "wikipedia" in command:
        try:
            topic = command.replace("wikipedia", "").strip()
            summary = wikipedia.summary(topic, sentences=2)
            display_message(summary)
            if speaking_mode:
                speak(summary)
        except wikipedia.exceptions.PageError:
            display_message("No Wikipedia page found for that topic.")
        except wikipedia.exceptions.DisambiguationError as e:
            display_message(f"Multiple results found.  Please be more specific. Options: {', '.join(e.options)}")
        except Exception as e:
             display_message(f"Error searching Wikipedia: {e}")
    elif "play music" in command:
        play_music()
    elif "tell me a joke" in command or "joke" in command:
        tell_joke()
    elif "volume" in command:
        control_volume(command)
    elif "take a note" in command:
        take_note()
    elif "read notes" in command:
        read_notes()
    elif "shutdown" in command or "restart" in command:
        system_control(command)
    elif "email" in command:
        send_email()  # Still a placeholder
    elif "goodbye" in command:
        display_message("Goodbye!")
        speak("Goodbye!", force_speak=True)
        root.destroy()
        sys.exit()
    elif "give me all commands" in command or "list commands" in command:
        list_commands()
    elif "text mode" in command:
        enter_text_mode()
    elif "exit text mode" in command:
        exit_text_mode()
    elif "ai" in command:
        query = command.replace("ai", "").strip()
        if query:
            response = get_gemini_response(query)
            display_message(response)
            if speaking_mode:
                speak(response)
        else:
            display_message("Please provide a query for the AI.")

    elif "stop listening" in command or "stop speak" in command:
            #This case is already handeled,
            pass # add if needed
    elif "start listening" in command: #Added Start listen command
        toggle_listening() # toggle method.
    else:
        # If no specific command is matched, try sending to Gemini
        response = get_gemini_response(command)
        display_message(response)
        if speaking_mode:
            speak(response)

# --- Main Program Execution ---

def main():
    global message_queue, listening_thread, speaking_mode
    speaking_mode = True  # Initially, speaking mode is on
    listening_thread = None  # Initialize the listening thread

    message_queue = queue.Queue()  # Queue for GUI updates

    initialize_gui()  # Set up the Tkinter window

    # Start the GUI update thread
    gui_thread = threading.Thread(target=update_gui, daemon=True)
    gui_thread.start()

    display_message("Jervis is ready.  Say 'start listening' to begin.")

    root.mainloop()  # Start the Tkinter main loop

if __name__ == "__main__":
    if GEMINI_API_KEY:
       main()
    else:
       print("Error: Missing API key.  Please add your API key to api_key.txt")
