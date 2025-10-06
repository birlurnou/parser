import customtkinter as ctk
import threading
import subprocess
import sys
import os
import queue
import signal
from tkinter import scrolledtext
import psutil
# https://github.com/birlurnou

class ParserGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Парсер FitBase")

        # Настраиваем размер и центрируем окно
        window_width = 1000
        window_height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Устанавливаем тёмную тему и синий цвет
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Создаем основной фрейм
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Парсер FitBase",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(10, 10))

        # Фрейм для кнопок
        self.buttons_frame = ctk.CTkFrame(self.main_frame)
        self.buttons_frame.pack(fill="x", pady=(0, 20))

        # Кнопки запуска парсеров
        self.abonements_button = ctk.CTkButton(
            self.buttons_frame,
            text="Все абонементы",
            command=self.run_abonements,
            font=ctk.CTkFont(size=16),
            height=40,
            fg_color="#2b5b84",
            hover_color="#1e4161"
        )
        self.abonements_button.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.services_button = ctk.CTkButton(
            self.buttons_frame,
            text="Все услуги",
            command=self.run_services,
            font=ctk.CTkFont(size=16),
            height=40,
            fg_color="#2b5b84",
            hover_color="#1e4161"
        )
        self.services_button.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.freezes_button = ctk.CTkButton(
            self.buttons_frame,
            text="Заморозки",
            command=self.run_freezes,
            font=ctk.CTkFont(size=16),
            height=40,
            fg_color="#2b5b84",
            hover_color="#1e4161"
        )
        self.freezes_button.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        # Кнопка очистки вывода
        self.clear_button = ctk.CTkButton(
            self.buttons_frame,
            text="Очистить вывод",
            command=self.clear_output,
            font=ctk.CTkFont(size=14),
            height=35,
            fg_color="#5d5d5d",
            hover_color="#424242"
        )
        self.clear_button.pack(side="left", padx=10, pady=10)

        # Кнопка остановки
        self.stop_button = ctk.CTkButton(
            self.buttons_frame,
            text="Остановить",
            command=self.stop_script,
            font=ctk.CTkFont(size=14),
            height=35,
            fg_color="#8b0000",
            hover_color="#660000",
            state="disabled"  # Изначально отключена
        )
        self.stop_button.pack(side="left", padx=10, pady=10)

        # Область вывода
        self.output_label = ctk.CTkLabel(
            self.main_frame,
            text="Консоль:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.output_label.pack(anchor="w", pady=(0, 10), padx=(10, 0))

        self.output_text = scrolledtext.ScrolledText(
            self.main_frame,
            wrap="word",
            bg="#2b2b2b",
            fg="white",
            insertbackground="white",
            font=("Consolas", 10),
            height=20
        )
        self.output_text.pack(fill="both", expand=True)

        # Статус бар
        self.status_var = ctk.StringVar(value="Готов к работе")
        self.status_bar = ctk.CTkLabel(
            self.main_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12)
        )
        self.status_bar.pack(fill="x", pady=(10, 0))

        # Очередь для вывода
        self.output_queue = queue.Queue()

        # Текущий процесс
        self.current_process = None
        self.is_running = False

        # Запускаем проверку очереди
        self.check_queue()

    def check_queue(self):
        """Проверяет очередь на наличие новых сообщений"""
        try:
            while True:
                message = self.output_queue.get_nowait()
                self.output_text.insert("end", message)
                self.output_text.see("end")

                # Обновляем статус для важных сообщений
                if "обработан" in message.lower() or "ошибка" in message.lower():
                    lines = message.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            self.status_var.set(line.strip()[:50])
                            break
        except queue.Empty:
            pass
        finally:
            # Планируем следующую проверку
            self.after(100, self.check_queue)

    def print_output(self, text):
        """Добавляет текст в очередь вывода"""
        self.output_queue.put(text)

    def run_script(self, script_name):
        """Запускает скрипт в отдельном потоке с реальным выводом"""

        def run():
            try:
                self.is_running = True
                self.print_output(f"\n{'=' * 50}\n")
                self.print_output(f"Запуск {script_name}...\n")
                self.print_output(f"{'=' * 50}\n\n")

                # Блокируем кнопки во время выполнения
                self.abonements_button.configure(state="disabled")
                self.services_button.configure(state="disabled")
                self.freezes_button.configure(state="disabled")
                self.stop_button.configure(state="normal")  # Включаем кнопку остановки
                self.status_var.set(f"Выполняется {script_name}...")

                # Запускаем скрипт с реальным выводом
                self.current_process = subprocess.Popen(
                    [sys.executable, script_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    bufsize=1,
                    universal_newlines=True
                )

                # Читаем вывод в реальном времени
                while True:
                    if not self.is_running:
                        break
                    line = self.current_process.stdout.readline()
                    if not line:
                        break
                    self.print_output(line)

                # Ждем завершения процесса
                if self.is_running:
                    return_code = self.current_process.wait()
                    if return_code == 0:
                        self.print_output(f"\n✓ {script_name} успешно завершен!\n")
                        self.status_var.set(f"{script_name} завершен")
                    else:
                        self.print_output(f"\n✗ {script_name} завершен с кодом ошибки: {return_code}\n")
                        self.status_var.set(f"Ошибка в {script_name}")
                else:
                    self.print_output(f"\n⏹ {script_name} принудительно остановлен\n")
                    self.status_var.set(f"{script_name} остановлен")

            except Exception as e:
                error_msg = f"✗ Ошибка при запуске {script_name}: {str(e)}\n"
                self.print_output(error_msg)
                self.status_var.set(f"Ошибка в {script_name}")
            finally:
                # Разблокируем кнопки
                self.abonements_button.configure(state="normal")
                self.services_button.configure(state="normal")
                self.freezes_button.configure(state="normal")
                self.stop_button.configure(state="disabled")  # Отключаем кнопку остановки
                self.current_process = None
                self.is_running = False

        # Запускаем в отдельном потоке
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    def run_abonements(self):
        """Запускает парсер абонементов"""
        self.run_script("abonements.py")

    def run_services(self):
        """Запускает парсер услуг"""
        self.run_script("services.py")

    def run_freezes(self):
        """Запускает парсер заморозок"""
        self.run_script("freezes.py")

    def clear_output(self):
        """Очищает область вывода"""
        self.output_text.delete(1.0, "end")
        self.status_var.set("Вывод очищен")

    def stop_script(self):
        """Останавливает текущий выполняемый скрипт и все дочерние процессы"""
        if self.current_process and self.is_running:
            self.is_running = False
            self.print_output("\n\n⏹ Запрос на остановку...\n")
            self.status_var.set("Останавливается...")

            try:
                # Получаем основной процесс
                main_process = psutil.Process(self.current_process.pid)

                # Получаем все дочерние процессы
                children = main_process.children(recursive=True)

                # Завершаем все дочерние процессы
                for child in children:
                    try:
                        child.terminate()
                    except:
                        pass

                # Ждем завершения дочерних процессов
                gone, still_alive = psutil.wait_procs(children, timeout=3)

                # Принудительно убиваем оставшиеся процессы
                for child in still_alive:
                    try:
                        child.kill()
                    except:
                        pass

                # Завершаем основной процесс
                main_process.terminate()
                try:
                    main_process.wait(timeout=2)
                except:
                    main_process.kill()

                self.print_output("✓ Все процессы остановлены\n")
                self.status_var.set("Выполнение остановлено")

            except Exception as e:
                self.print_output(f"Ошибка при остановке: {str(e)}\n")
                # Пробуем стандартный метод как запасной вариант
                try:
                    self.current_process.terminate()
                    self.current_process.wait(timeout=2)
                except:
                    try:
                        self.current_process.kill()
                    except:
                        pass

    def on_closing(self):
        """Действия при закрытии окна"""
        # Останавливаем процесс если он запущен
        if self.current_process and self.is_running:
            self.stop_script()
            # Даем время на завершение
            self.after(1000, self.destroy)
        else:
            self.destroy()


if __name__ == "__main__":
    # Проверяем наличие необходимых файлов
    required_files = ["abonements.py", "services.py", "freezes.py", "user.txt"]
    missing_files = [f for f in required_files if not os.path.exists(f)]

    if missing_files:
        print(f"Ошибка: Отсутствуют необходимые файлы: {', '.join(missing_files)}")
        print("Убедитесь, что все файлы находятся в той же папке, что и программа.")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    app = ParserGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()