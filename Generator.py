import random
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from faker import Faker
import csv
import os
import time
import threading
import string
import unicodedata
import subprocess  # Добавим для корректного открытия папок
import math  # Для анимации флага

# Константы
UNIQUE_ID_LENGTH = 3  # Длина уникального идентификатора

class PhonebookGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📱 Генератор телефонной книги")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Создаем генераторы для обеих локалей
        self.ru_faker = Faker('ru_RU')
        self.en_faker = Faker('en_US')
        
        # Переменные
        self.name_format = tk.IntVar(value=3)
        self.alphabet_choice = tk.IntVar(value=1)
        self.prefix = tk.StringVar(value="+7")
        self.start_num = tk.IntVar(value=1000)
        self.end_num = tk.IntVar(value=2000)
        self.save_dir = tk.StringVar(value=os.path.expanduser("~"))
        self.progress = tk.DoubleVar(value=0)
        
        # Создаем canvas и scrollbar для прокрутки
        canvas = tk.Canvas(root)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Упаковка canvas и scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Создаем основной фрейм внутри scrollable_frame
        main_frame = ttk.Frame(scrollable_frame, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Секция формата имени
        format_frame = ttk.LabelFrame(main_frame, text="Формат имен", padding=10)
        format_frame.pack(fill=tk.X, pady=5)
        
        formats = [
            ("Имя + ID (Алексей_abc)", 1),
            ("Имя Фамилия + ID (Алексей Смирнов xyz)", 2),
            ("Фамилия И.О. + ID (Смирнов А.П. 123)", 3),
            ("Западный формат: Фамилия, Имя + ID (Smith, John 4d5)", 4),
            ("Полное ФИО + ID (Смирнов Алексей Петрович a1b)", 5)
        ]
        
        for text, value in formats:
            ttk.Radiobutton(format_frame, text=text, variable=self.name_format, 
                            value=value).pack(anchor=tk.W, padx=5, pady=2)
        
        # Секция алфавита
        alphabet_frame = ttk.LabelFrame(main_frame, text="Алфавит", padding=10)
        alphabet_frame.pack(fill=tk.X, pady=5)
        
        alphabets = [
            ("Кириллица (по умолчанию)", 1),
            ("Латиница", 2),
            ("Смешанный (оба алфавита)", 3)
        ]
        
        for text, value in alphabets:
            ttk.Radiobutton(alphabet_frame, text=text, variable=self.alphabet_choice, 
                           value=value).pack(anchor=tk.W, padx=5, pady=2)
        
        # Секция параметров номеров
        number_frame = ttk.LabelFrame(main_frame, text="Параметры номеров", padding=10)
        number_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(number_frame, text="Префикс номера:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(number_frame, textvariable=self.prefix, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(number_frame, text="Начальный номер:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(number_frame, textvariable=self.start_num, width=15).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(number_frame, text="Конечный номер:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(number_frame, textvariable=self.end_num, width=15).grid(row=2, column=1, padx=5, pady=5)
        
        # Секция сохранения
        save_frame = ttk.LabelFrame(main_frame, text="Сохранение", padding=10)
        save_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(save_frame, text="Папка для сохранения:").pack(anchor=tk.W, padx=5, pady=2)
        
        dir_frame = ttk.Frame(save_frame)
        dir_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Entry(dir_frame, textvariable=self.save_dir).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(dir_frame, text="Обзор", command=self.select_directory).pack(side=tk.RIGHT)
        
        # Прогресс-бар
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress, 
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Готов к генерации")
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Фрейм для кнопок внизу (фиксированный)
        button_frame = ttk.Frame(root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=10)
        
        # Создаем анимированный флаг СССР
        self.create_ussr_flag(button_frame)
        
        # Кнопка запуска генерации - БОЛЬШАЯ И ЗЕЛЕНАЯ (всегда видна)
        self.generate_button = tk.Button(
            button_frame,
            text="ЗАПУСК ГЕНЕРАЦИИ",
            command=self.start_generation,
            bg="#4CAF50",
            fg="white",
            font=('Arial', 14, 'bold'),
            padx=20,
            pady=15,
            relief=tk.RAISED,
            bd=3
        )
        self.generate_button.pack(fill=tk.X, pady=(0, 5), ipadx=10, ipady=5)
        
        # Кнопка выхода (тоже всегда видна)
        ttk.Button(button_frame, text="Выход", command=root.quit).pack(pady=(5, 0))
        
        # Привязываем прокрутку мышью к canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Обновляем размер canvas при изменении размера окна
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = event.width
            canvas.itemconfig(canvas.find_all()[0], width=canvas_width)
        
        canvas.bind("<Configure>", configure_canvas)
    
    def create_ussr_flag(self, parent):
        """Создает анимированный флаг СССР"""
        # Фрейм для флага
        flag_frame = ttk.Frame(parent)
        flag_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Canvas для флага
        self.flag_canvas = tk.Canvas(flag_frame, height=80, bg='#E6E6E6')
        self.flag_canvas.pack(fill=tk.X, padx=20)
        
        # Параметры флага
        self.flag_width = 200
        self.flag_height = 60
        self.wave_amplitude = 8
        self.wave_frequency = 0.02
        self.animation_speed = 0.1
        self.time_offset = 0
        
        # Запускаем анимацию
        self.animate_flag()
    
    def draw_flag(self):
        """Рисует флаг СССР с эффектом развевания"""
        self.flag_canvas.delete("all")
        
        # Получаем размеры canvas
        canvas_width = self.flag_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 400  # Значение по умолчанию
        
        canvas_height = self.flag_canvas.winfo_height()
        
        # Центрируем флаг
        start_x = (canvas_width - self.flag_width) // 2
        start_y = (canvas_height - self.flag_height) // 2
        
        # Количество сегментов для эффекта развевания
        segments = 20
        segment_width = self.flag_width // segments
        
        for i in range(segments):
            x1 = start_x + i * segment_width
            x2 = start_x + (i + 1) * segment_width
            
            # Вычисляем волновое смещение
            wave_offset1 = math.sin(self.time_offset + i * self.wave_frequency) * self.wave_amplitude
            wave_offset2 = math.sin(self.time_offset + (i + 1) * self.wave_frequency) * self.wave_amplitude
            
            y1_top = start_y + wave_offset1
            y2_top = start_y + wave_offset2
            y1_bottom = start_y + self.flag_height + wave_offset1
            y2_bottom = start_y + self.flag_height + wave_offset2
            
            # Рисуем красный фон флага
            points = [x1, y1_top, x2, y2_top, x2, y2_bottom, x1, y1_bottom]
            self.flag_canvas.create_polygon(points, fill='#CC0000', outline='#CC0000')
        
        # Добавляем серп и молот (упрощенная версия)
        center_x = start_x + self.flag_width // 4
        center_y = start_y + self.flag_height // 2
        
        # Волновое смещение для символов
        symbol_wave = math.sin(self.time_offset + self.flag_width // 4 * self.wave_frequency) * self.wave_amplitude
        symbol_y = center_y + symbol_wave
        
        # Рисуем звезду (упрощенную)
        star_size = 8
        self.draw_star(center_x - 15, symbol_y, star_size, '#FFD700')
        
        # Рисуем серп (как дуга)
        self.flag_canvas.create_arc(center_x - 5, symbol_y - 8, center_x + 10, symbol_y + 8, 
                                   start=30, extent=180, style='arc', 
                                   outline='#FFD700', width=3)
        
        # Рисуем молот (как прямоугольник с ручкой)
        self.flag_canvas.create_rectangle(center_x + 5, symbol_y - 3, center_x + 15, symbol_y + 3, 
                                         fill='#FFD700', outline='#FFD700')
        self.flag_canvas.create_line(center_x + 10, symbol_y + 3, center_x + 10, symbol_y + 10, 
                                    fill='#FFD700', width=2)
    
    def draw_star(self, x, y, size, color):
        """Рисует пятиконечную звезду"""
        points = []
        for i in range(10):
            angle = math.pi * i / 5
            if i % 2 == 0:
                radius = size
            else:
                radius = size * 0.4
            
            px = x + radius * math.cos(angle - math.pi/2)
            py = y + radius * math.sin(angle - math.pi/2)
            points.extend([px, py])
        
        self.flag_canvas.create_polygon(points, fill=color, outline=color)
    
    def animate_flag(self):
        """Анимирует флаг"""
        self.draw_flag()
        self.time_offset += self.animation_speed
        
        # Продолжаем анимацию
        self.root.after(50, self.animate_flag)
    
    def select_directory(self):
        directory = filedialog.askdirectory(initialdir=self.save_dir.get())
        if directory:
            self.save_dir.set(directory)
    
    def generate_unique_id(self):
        """Генерирует уникальный буквенно-цифровой идентификатор"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(UNIQUE_ID_LENGTH))
    
    def normalize_name(self, name):
        """Нормализует имя, удаляя диакритические знаки"""
        normalized = unicodedata.normalize('NFD', name)
        return ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    
    def generate_name_with_id(self, name_format, used_names, locale='ru_RU', mixed_alphabets=False):
        """Генерирует имя с фамилией, инициалами и уникальным ID"""
        while True:
            # Определяем локаль для генерации
            if mixed_alphabets and random.random() > 0.7:  # 30% шанс использовать другой алфавит
                current_locale = 'en_US' if locale == 'ru_RU' else 'ru_RU'
            else:
                current_locale = locale
            
            # Выбираем соответствующий генератор
            local_faker = self.en_faker if current_locale == 'en_US' else self.ru_faker
            
            # Генерируем имя
            first_name = local_faker.first_name()
            last_name = local_faker.last_name()
            middle_name = local_faker.first_name() if current_locale == 'ru_RU' else local_faker.last_name()
            
            # Нормализуем имена для лучшей читаемости
            first_name = self.normalize_name(first_name)
            last_name = self.normalize_name(last_name)
            middle_name = self.normalize_name(middle_name)
            
            # Генерируем уникальный идентификатор
            unique_id = self.generate_unique_id()
            
            # Форматируем имя с ID после фамилии/инициалов
            if name_format == 1:  # Только имя + ID
                name = f"{first_name}_{unique_id}"
            elif name_format == 2:  # Имя + фамилия + ID
                name = f"{first_name} {last_name} {unique_id}"
            elif name_format == 3:  # Фамилия + инициалы + ID
                initials = f"{first_name[0]}.{middle_name[0]}." if middle_name else f"{first_name[0]}."
                name = f"{last_name} {initials} {unique_id}"
            elif name_format == 4:  # Западный формат: Фамилия, Имя + ID
                name = f"{last_name}, {first_name} {unique_id}"
            else:  # Полное ФИО + ID
                name = f"{last_name} {first_name} {middle_name} {unique_id}"
            
            # Проверяем уникальность
            if name not in used_names:
                used_names.add(name)
                return name
    
    def update_progress(self, current, total):
        """Обновляет прогресс-бар и статус"""
        percent = (current / total) * 100
        self.progress.set(percent)
        self.status_label.config(text=f"Генерация: {current}/{total} контактов ({percent:.1f}%)")
        self.root.update_idletasks()
    
    def show_message(self, title, message):
        """Показывает всплывающее сообщение"""
        messagebox.showinfo(title, message)
    
    def open_directory(self, path):
        """Безопасное открытие папки для всех ОС"""
        try:
            if os.name == 'nt':
                # Используем explorer для Windows
                os.startfile(path)
            elif sys.platform == 'darwin':
                # Для macOS
                subprocess.Popen(['open', path])
            else:
                # Для Linux
                subprocess.Popen(['xdg-open', path])
        except Exception as e:
            print(f"Ошибка при открытии папки: {str(e)}")
    
    def generation_thread(self):
        """Поток для выполнения генерации"""
        try:
            # Получаем параметры из интерфейса
            name_format = self.name_format.get()
            alphabet_choice = self.alphabet_choice.get()
            prefix = self.prefix.get()
            start = self.start_num.get()
            end = self.end_num.get()
            save_dir = self.save_dir.get()
            
            # Проверка введенных данных
            if not prefix:
                self.show_message("Ошибка", "Пожалуйста, введите префикс номера")
                return
                
            if start >= end:
                self.show_message("Ошибка", "Начальный номер должен быть меньше конечного")
                return
                
            total_contacts = end - start + 1
            if total_contacts > 100000:
                if not messagebox.askyesno("Подтверждение", 
                                          f"Вы собираетесь сгенерировать {total_contacts} контактов. Это может занять много времени. Продолжить?"):
                    return
            
            locale = 'ru_RU'
            mixed_alphabets = False
            
            if alphabet_choice == 2:
                locale = 'en_US'
            elif alphabet_choice == 3:
                mixed_alphabets = True
            
            # Создание имени файла
            filename = f"contacts_{prefix}_{start}-{end}.csv"
            full_path = os.path.join(save_dir, filename)
            
            # Проверка существования файла
            if os.path.exists(full_path):
                if not messagebox.askyesno("Подтверждение", 
                                          f"Файл '{filename}' уже существует. Перезаписать?"):
                    return
            
            # Начало генерации
            start_time = time.time()
            self.status_label.config(text="Подготовка к генерации...")
            self.generate_button.config(state=tk.DISABLED, bg="#8BC34A")  # Делаем кнопку неактивной
            self.root.update()
            
            # Генерация данных
            contacts = []
            max_digits = len(str(end))
            all_used_names = set()
            
            for i, num in enumerate(range(start, end + 1)):
                suffix = str(num).zfill(max_digits)
                phone = f"{prefix}{suffix}"
                
                # Генерируем имя с ID
                name = self.generate_name_with_id(
                    name_format, 
                    all_used_names, 
                    locale,
                    mixed_alphabets
                )
                
                contacts.append({"Name": name, "Phone": phone})
                
                # Обновляем прогресс каждые 100 контактов или на последнем
                if (i + 1) % 100 == 0 or i == total_contacts - 1:
                    self.update_progress(i + 1, total_contacts)
            
            # Сохранение файла
            with open(full_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["Name", "Phone"])
                writer.writeheader()
                writer.writerows(contacts)
            
            # Расчет статистики
            total_time = time.time() - start_time
            file_size = os.path.getsize(full_path) / 1024  # Размер в КБ
            
            # Показ результатов
            result_message = (
                f"✅ Генерация завершена успешно!\n\n"
                f"📂 Файл: {full_path}\n"
                f"📊 Размер файла: {file_size:.2f} КБ\n"
                f"👥 Всего контактов: {total_contacts}\n"
                f"🔑 Уникальных имен: {len(all_used_names)}\n"
                f"⏱ Время генерации: {total_time:.2f} секунд\n"
                f"⚡ Скорость: {total_contacts/total_time:.1f} контактов/сек"
            )
            
            self.show_message("Готово", result_message)
            self.status_label.config(text="Генерация завершена успешно!")
            self.progress.set(0)
            
            # Восстанавливаем кнопку
            self.generate_button.config(state=tk.NORMAL, bg="#4CAF50")
            
            # Открытие папки с файлом
            self.open_directory(save_dir)
                
        except Exception as e:
            self.show_message("Ошибка", f"Произошла ошибка:\n{str(e)}")
            self.status_label.config(text="Ошибка при генерации")
            self.progress.set(0)
            self.generate_button.config(state=tk.NORMAL, bg="#4CAF50")  # Восстанавливаем кнопку
    
    def start_generation(self):
        """Запускает генерацию в отдельном потоке"""
        # Сброс прогресса
        self.progress.set(0)
        self.status_label.config(text="Запуск генерации...")
        self.root.update()
        
        # Запуск в отдельном потоке, чтобы не блокировать интерфейс
        threading.Thread(target=self.generation_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Центрирование окна
    window_width = 700
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    app = PhonebookGeneratorApp(root)
    root.mainloop()