import customtkinter as ctk
import socket
import threading

# === Налаштування ===
SERVER_HOST = 'localhost'
SERVER_PORT = 8080


class LogiTalkApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None

        self.title("LogiTalk - Chat App")
        self.geometry("700x500")
        self.resizable(False, False)

        # ====== ЛІВА ПАНЕЛЬ (налаштування) ======
        self.sidebar = ctk.CTkFrame(self, width=150, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.label_logo = ctk.CTkLabel(self.sidebar, text="⚙️ Налаштування", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_logo.pack(pady=(20, 10))

        self.mode_switch = ctk.CTkSwitch(self.sidebar, text="Світла/Темна", command=self.change_mode)
        self.mode_switch.pack(pady=10)

        # ====== ПРАВА ЧАСТИНА (чат) ======
        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # Поле для виводу повідомлень
        self.textbox = ctk.CTkTextbox(self.chat_frame, width=500, height=300)
        self.textbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.textbox.insert("end", "👋 Ласкаво просимо до LogiTalk!\n")
        self.textbox.configure(state="disabled")

        # Поле вводу повідомлень
        self.entry = ctk.CTkEntry(self.chat_frame, placeholder_text="Введіть повідомлення...")
        self.entry.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # Кнопка "Надіслати"
        self.send_button = ctk.CTkButton(self.chat_frame, text="Надіслати", command=self.send_message)
        self.send_button.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # ====== Вікно логіну ======
        self.login_window = ctk.CTkToplevel(self)
        self.login_window.title("Вхід у LogiTalk")
        self.login_window.geometry("300x200")
        self.login_window.resizable(False, False)

        ctk.CTkLabel(self.login_window, text="Введіть ім’я користувача:").pack(pady=20)
        self.username_entry = ctk.CTkEntry(self.login_window, placeholder_text="Ваше ім’я")
        self.username_entry.pack(pady=10)
        ctk.CTkButton(self.login_window, text="Підключитися", command=self.login).pack(pady=10)

    # ====== Зміна теми ======
    def change_mode(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if current == "Dark" else "dark")

    # ====== Вхід ======
    def login(self):
        name = self.username_entry.get().strip()
        if name:
            self.username = name
            try:
                self.sock.connect((SERVER_HOST, SERVER_PORT))
                threading.Thread(target=self.receive_messages, daemon=True).start()
                self.add_message(f"🔹 {self.username} приєднався до чату!\n")
                self.login_window.destroy()
            except Exception as e:
                self.add_message(f"❌ Не вдалося підключитись до сервера: {e}\n")

    # ====== Відправлення ======
    def send_message(self):
        message = self.entry.get().strip()
        if message and self.username:
            full_message = f"{self.username}: {message}"
            try:
                self.sock.sendall(full_message.encode("utf-8"))
            except:
                self.add_message("⚠️ Втрата зв’язку із сервером!\n")
            self.entry.delete(0, "end")

    # ====== Прийом ======
    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                msg = data.decode("utf-8")
                self.add_message(msg + "\n")
            except:
                break

    # ====== Додавання у чат ======
    def add_message(self, msg):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", msg)
        self.textbox.configure(state="disabled")
        self.textbox.see("end")


if __name__ == "__main__":
    app = LogiTalkApp()
    app.mainloop()
