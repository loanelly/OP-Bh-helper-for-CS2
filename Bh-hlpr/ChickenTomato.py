import tkinter as tk
import time
import random
import threading
import ctypes

# Коды клавиш Windows API (Virtual-Key Codes)
VK_SPACE = 0x20
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04
VK_XBUTTON1 = 0x05  # 4-я кнопка мыши (Назад)
VK_XBUTTON2 = 0x06  # 5-я кнопка мыши (Вперед)

# Словарь человеческих названий для спец-клавиш
KEY_NAMES = {
    0x20: "SPACE (ПРОБЕЛ)",
    0x01: "ЛЕВАЯ КНОПКА МЫШИ (ЛКМ)",
    0x02: "ПРАВАЯ КНОПКА МЫШИ (ПКМ)",
    0x04: "КОЛЕСИКО МЫШИ (СКМ)",
    0x05: "4-Я КНОПКА МЫШИ (XBUTTON1)",
    0x06: "5-Я КНОПКА МЫШИ (XBUTTON2)",
    0x10: "SHIFT",
    0x11: "CTRL",
    0x12: "ALT"
}

def press_space():
    """Имитация аппаратного нажатия пробела через Win32 API"""
    ctypes.windll.user32.keybd_event(VK_SPACE, 0, 0, 0) # Нажать
    time.sleep(0.002)
    ctypes.windll.user32.keybd_event(VK_SPACE, 0, 2, 0) # Отпустить

class BhopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CS2 BHOP (Tkinter)")
        self.root.geometry("420x240")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c3e50")

        # Настройки по умолчанию (Сразу ставим 5-ю кнопку мыши)
        self.current_bind_code = VK_XBUTTON2
        self.current_bind_name = KEY_NAMES[VK_XBUTTON2]
        self.is_running = False
        self.is_listening = False

        # Интерфейс
        self.label_title = tk.Label(root, text="CS2 BHOP ASSISTANT", font=("Arial", 16, "bold"), fg="#ecf0f1", bg="#2c3e50")
        self.label_title.pack(pady=15)

        self.btn_bind = tk.Button(root, text=f"Бинд: {self.current_bind_name}", font=("Arial", 10, "bold"), 
                                  command=self.start_binding, width=32, bg="#34495e", fg="#ecf0f1", relief="flat")
        self.btn_bind.pack(pady=10)

        self.btn_toggle = tk.Button(root, text="ЗАПУСТИТЬ", font=("Arial", 12, "bold"), 
                                    command=self.toggle_program, width=15, bg="#27ae60", fg="#ecf0f1", relief="flat")
        self.btn_toggle.pack(pady=10)

        self.label_status = tk.Label(root, text="Статус: Остановлено", font=("Arial", 10), fg="#e74c3c", bg="#2c3e50")
        self.label_status.pack(pady=10)

        # Фоновый поток для проверки зажатия кнопок во время игры
        self.bhop_thread = threading.Thread(target=self.bhop_loop, daemon=True)
        self.bhop_thread.start()

    def start_binding(self):
        """Включение режима сканирования клавиш"""
        if self.is_listening:
            return
        self.is_listening = True
        self.btn_bind.configure(text="Нажмите любую кнопку мыши или клавы...", bg="#e67e22")
        
        # Запуск сканирования Windows API в отдельном потоке, чтобы GUI не зависал
        threading.Thread(target=self.windows_key_scanner, daemon=True).start()

    def windows_key_scanner(self):
        """Прямой опрос Windows на предмет нажатия абсолютно любой кнопки"""
        time.sleep(0.2) # Небольшая задержка, чтобы не поймать клик от самой кнопки "Бинд"
        
        while self.is_listening:
            # Проверяем диапазон виртуальных кодов клавиш Windows от 1 до 255
            for code in range(1, 256):
                # Проверяем старший бит (клавиша зажата прямо сейчас)
                if (ctypes.windll.user32.GetAsyncKeyState(code) & 0x8000) != 0:
                    # Получаем красивое имя из словаря или генерируем стандартное
                    if code in KEY_NAMES:
                        name = KEY_NAMES[code]
                    else:
                        name = f"КЛАВИША (КОД: {code})"
                    
                    self.current_bind_code = code
                    self.current_bind_name = name
                    self.is_listening = False
                    
                    # Безопасное обновление интерфейса из фонового потока
                    self.root.after(0, self.update_bind_button)
                    return
            time.sleep(0.01)

    def update_bind_button(self):
        self.btn_bind.configure(text=f"Бинд: {self.current_bind_name}", bg="#34495e")

    def toggle_program(self):
        if self.is_listening:
            return
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_toggle.configure(text="СТОП", bg="#c0392b")
            self.label_status.configure(text="Статус: Работает (Зажмите бинд в игре)", fg="#2ecc71")
        else:
            self.btn_toggle.configure(text="ЗАПУСТИТЬ", bg="#27ae60")
            self.label_status.configure(text="Статус: Остановлено", fg="#e74c3c")

    def is_bind_pressed(self):
        """Проверка зажата ли выбранная кнопка"""
        return (ctypes.windll.user32.GetAsyncKeyState(self.current_bind_code) & 0x8000) != 0

    def bhop_loop(self):
        while True:
            if self.is_running and not self.is_listening:
                if self.is_bind_pressed():
                    clicks = random.randint(100, 140)
                    base_delay = 1.0 / clicks
                    
                    press_space()
                    time.sleep(base_delay)
                    
                    # Легитимизация (микро-паузы)
                    if random.random() < 0.15:
                        time.sleep(random.uniform(0.01, 0.03))
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = BhopApp(root)
    root.mainloop()
