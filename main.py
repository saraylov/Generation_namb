import random
import os
import time
import threading
import string
import unicodedata
import csv
from faker import Faker

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import platform

# Константы
UNIQUE_ID_LENGTH = 3

class PhonebookGeneratorApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ru_faker = Faker('ru_RU')
        self.en_faker = Faker('en_US')
        
        # Переменные
        self.name_format = 3
        self.alphabet_choice = 1
        self.prefix = "+7"
        self.start_num = 1000
        self.end_num = 2000
        
        # Путь для сохранения (адаптирован для Android)
        if platform == 'android':
            from android.storage import primary_external_storage_path
            self.save_dir = primary_external_storage_path()
        else:
            self.save_dir = os.path.expanduser("~")
    
    def build(self):
        # Основной layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Заголовок
        title = Label(text='📱 Генератор телефонной книги', 
                     font_size=dp(18), size_hint_y=None, height=dp(50))
        main_layout.add_widget(title)
        
        # Прокручиваемая область
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Секция формата имени
        format_section = self.create_format_section()
        content.add_widget(format_section)
        
        # Секция алфавита
        alphabet_section = self.create_alphabet_section()
        content.add_widget(alphabet_section)
        
        # Секция параметров номеров
        number_section = self.create_number_section()
        content.add_widget(number_section)
        
        # Секция сохранения
        save_section = self.create_save_section()
        content.add_widget(save_section)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        # Прогресс-бар
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=dp(30))
        main_layout.add_widget(self.progress_bar)
        
        # Статус
        self.status_label = Label(text='Готов к генерации', 
                                 size_hint_y=None, height=dp(30))
        main_layout.add_widget(self.status_label)
        
        # Кнопка генерации
        self.generate_button = Button(text='ЗАПУСК ГЕНЕРАЦИИ', 
                                     size_hint_y=None, height=dp(60),
                                     background_color=(0.3, 0.7, 0.3, 1))
        self.generate_button.bind(on_press=self.start_generation)
        main_layout.add_widget(self.generate_button)
        
        return main_layout
    
    def create_format_section(self):
        section = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        section.bind(minimum_height=section.setter('height'))
        
        title = Label(text='Формат имен:', font_size=dp(16), 
                     size_hint_y=None, height=dp(30))
        section.add_widget(title)
        
        formats = [
            ("Имя + ID (Алексей_abc)", 1),
            ("Имя Фамилия + ID (Алексей Смирнов xyz)", 2),
            ("Фамилия И.О. + ID (Смирнов А.П. 123)", 3),
            ("Западный формат: Фамилия, Имя + ID (Smith, John 4d5)", 4),
            ("Полное ФИО + ID (Смирнов Алексей Петрович a1b)", 5)
        ]
        
        self.format_checkboxes = []
        for text, value in formats:
            layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
            checkbox = CheckBox(active=(value == 3), size_hint_x=None, width=dp(30))
            label = Label(text=text, text_size=(None, None))
            
            def on_checkbox_active(checkbox, active, val=value):
                if active:
                    self.name_format = val
                    for cb in self.format_checkboxes:
                        if cb != checkbox:
                            cb.active = False
            
            checkbox.bind(active=on_checkbox_active)
            self.format_checkboxes.append(checkbox)
            
            layout.add_widget(checkbox)
            layout.add_widget(label)
            section.add_widget(layout)
        
        return section
    
    def create_alphabet_section(self):
        section = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        section.bind(minimum_height=section.setter('height'))
        
        title = Label(text='Алфавит:', font_size=dp(16), 
                     size_hint_y=None, height=dp(30))
        section.add_widget(title)
        
        alphabets = [
            ("Кириллица (по умолчанию)", 1),
            ("Латиница", 2),
            ("Смешанный (оба алфавита)", 3)
        ]
        
        self.alphabet_checkboxes = []
        for text, value in alphabets:
            layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
            checkbox = CheckBox(active=(value == 1), size_hint_x=None, width=dp(30))
            label = Label(text=text, text_size=(None, None))
            
            def on_checkbox_active(checkbox, active, val=value):
                if active:
                    self.alphabet_choice = val
                    for cb in self.alphabet_checkboxes:
                        if cb != checkbox:
                            cb.active = False
            
            checkbox.bind(active=on_checkbox_active)
            self.alphabet_checkboxes.append(checkbox)
            
            layout.add_widget(checkbox)
            layout.add_widget(label)
            section.add_widget(layout)
        
        return section
    
    def create_number_section(self):
        section = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        section.bind(minimum_height=section.setter('height'))
        
        title = Label(text='Параметры номеров:', font_size=dp(16), 
                     size_hint_y=None, height=dp(30))
        section.add_widget(title)
        
        # Префикс
        prefix_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        prefix_layout.add_widget(Label(text='Префикс номера:', size_hint_x=0.4))
        self.prefix_input = TextInput(text=self.prefix, size_hint_x=0.6, multiline=False)
        self.prefix_input.bind(text=self.on_prefix_change)
        prefix_layout.add_widget(self.prefix_input)
        section.add_widget(prefix_layout)
        
        # Начальный номер
        start_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        start_layout.add_widget(Label(text='Начальный номер:', size_hint_x=0.4))
        self.start_input = TextInput(text=str(self.start_num), size_hint_x=0.6, 
                                    multiline=False, input_filter='int')
        self.start_input.bind(text=self.on_start_change)
        start_layout.add_widget(self.start_input)
        section.add_widget(start_layout)
        
        # Конечный номер
        end_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        end_layout.add_widget(Label(text='Конечный номер:', size_hint_x=0.4))
        self.end_input = TextInput(text=str(self.end_num), size_hint_x=0.6, 
                                  multiline=False, input_filter='int')
        self.end_input.bind(text=self.on_end_change)
        end_layout.add_widget(self.end_input)
        section.add_widget(end_layout)
        
        return section
    
    def create_save_section(self):
        section = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        section.bind(minimum_height=section.setter('height'))
        
        title = Label(text='Сохранение:', font_size=dp(16), 
                     size_hint_y=None, height=dp(30))
        section.add_widget(title)
        
        dir_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        dir_layout.add_widget(Label(text='Папка для сохранения:', size_hint_x=0.6))
        browse_button = Button(text='Обзор', size_hint_x=0.4)
        browse_button.bind(on_press=self.select_directory)
        dir_layout.add_widget(browse_button)
        section.add_widget(dir_layout)
        
        # Показываем текущую папку
        self.dir_label = Label(text=self.save_dir, text_size=(None, None), 
                              size_hint_y=None, height=dp(30))
        section.add_widget(self.dir_label)
        
        return section
    
    def on_prefix_change(self, instance, value):
        self.prefix = value
    
    def on_start_change(self, instance, value):
        try:
            self.start_num = int(value) if value else 1000
        except ValueError:
            self.start_num = 1000
    
    def on_end_change(self, instance, value):
        try:
            self.end_num = int(value) if value else 2000
        except ValueError:
            self.end_num = 2000
    
    def select_directory(self, instance):
        content = BoxLayout(orientation='vertical')
        
        filechooser = FileChooserListView(path=self.save_dir)
        content.add_widget(filechooser)
        
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        select_button = Button(text='Выбрать')
        cancel_button = Button(text='Отмена')
        
        popup = Popup(title='Выберите папку', content=content, size_hint=(0.9, 0.9))
        
        def on_select(instance):
            if filechooser.selection:
                selected_path = filechooser.selection[0]
                if os.path.isdir(selected_path):
                    self.save_dir = selected_path
                else:
                    self.save_dir = os.path.dirname(selected_path)
                self.dir_label.text = self.save_dir
            popup.dismiss()
        
        def on_cancel(instance):
            popup.dismiss()
        
        select_button.bind(on_press=on_select)
        cancel_button.bind(on_press=on_cancel)
        
        buttons.add_widget(select_button)
        buttons.add_widget(cancel_button)
        content.add_widget(buttons)
        
        popup.open()
    
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
        self.progress_bar.value = percent
        self.status_label.text = f"Генерация: {current}/{total} контактов ({percent:.1f}%)"
    
    def show_message(self, title, message):
        """Показывает всплывающее сообщение"""
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, text_size=(dp(300), None)))
        
        button = Button(text='OK', size_hint_y=None, height=dp(50))
        content.add_widget(button)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.6))
        button.bind(on_press=popup.dismiss)
        popup.open()
    
    def generation_thread(self):
        """Поток для выполнения генерации"""
        try:
            # Получаем параметры
            name_format = self.name_format
            alphabet_choice = self.alphabet_choice
            prefix = self.prefix
            start = self.start_num
            end = self.end_num
            save_dir = self.save_dir
            
            # Проверка введенных данных
            if not prefix:
                Clock.schedule_once(lambda dt: self.show_message("Ошибка", "Пожалуйста, введите префикс номера"), 0)
                return
                
            if start >= end:
                Clock.schedule_once(lambda dt: self.show_message("Ошибка", "Начальный номер должен быть меньше конечного"), 0)
                return
                
            total_contacts = end - start + 1
            
            locale = 'ru_RU'
            mixed_alphabets = False
            
            if alphabet_choice == 2:
                locale = 'en_US'
            elif alphabet_choice == 3:
                mixed_alphabets = True
            
            # Создание имени файла
            filename = f"contacts_{prefix}_{start}-{end}.csv"
            full_path = os.path.join(save_dir, filename)
            
            # Начало генерации
            start_time = time.time()
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', "Подготовка к генерации..."), 0)
            Clock.schedule_once(lambda dt: setattr(self.generate_button, 'disabled', True), 0)
            
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
                    Clock.schedule_once(lambda dt, current=i+1, total=total_contacts: self.update_progress(current, total), 0)
            
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
            
            Clock.schedule_once(lambda dt: self.show_message("Готово", result_message), 0)
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', "Генерация завершена успешно!"), 0)
            Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 0), 0)
            Clock.schedule_once(lambda dt: setattr(self.generate_button, 'disabled', False), 0)
                
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_message("Ошибка", f"Произошла ошибка:\n{str(e)}"), 0)
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', "Ошибка при генерации"), 0)
            Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 0), 0)
            Clock.schedule_once(lambda dt: setattr(self.generate_button, 'disabled', False), 0)
    
    def start_generation(self, instance):
        """Запускает генерацию в отдельном потоке"""
        # Сброс прогресса
        self.progress_bar.value = 0
        self.status_label.text = "Запуск генерации..."
        
        # Запуск в отдельном потоке, чтобы не блокировать интерфейс
        threading.Thread(target=self.generation_thread, daemon=True).start()

if __name__ == "__main__":
    PhonebookGeneratorApp().run()