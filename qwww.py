import os
import sys
import json
import time
import win32gui
import win32con
import win32api
import win32ui
import keyboard
import threading
import pydirectinput
import pyautogui
import numpy as np
import cv2
from PIL import Image, ImageTk, ImageGrab
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog, scrolledtext
from ttkthemes import ThemedStyle
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import random
import ctypes
import win32process
import traceback

# Настройки PyDirectInput
pydirectinput.PAUSE = 0  # Отключаем паузы между действиями
pydirectinput.FAILSAFE = False  # Отключаем защиту от сбоев

# Функция для получения корректного пути к ресурсам
def resource_path(relative_path):
    try:
        # PyInstaller создает временную папку и хранит путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Словарь виртуальных кодов клавиш
VIRTUAL_KEYS = {
    # Буквы
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
    'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
    'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
    'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
    'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59,
    'z': 0x5A,
    
    # Цифры (основная клавиатура)
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    
    # Цифры (numpad)
    'num0': 0x60, 'num1': 0x61, 'num2': 0x62, 'num3': 0x63,
    'num4': 0x64, 'num5': 0x65, 'num6': 0x66, 'num7': 0x67,
    'num8': 0x68, 'num9': 0x69,
    
    # Функциональные клавиши
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
    'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
    'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
    
    # Специальные клавиши
    'backspace': 0x08, 'tab': 0x09, 'enter': 0x0D,
    'shift': 0x10, 'ctrl': 0x11, 'alt': 0x12,
    'pause': 0x13, 'capslock': 0x14, 'esc': 0x1B,
    'space': 0x20, 'pageup': 0x21, 'pagedown': 0x22,
    'end': 0x23, 'home': 0x24,
    
    # Стрелки
    'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
    
    # Управление
    'insert': 0x2D, 'delete': 0x2E,
    
    # Символы
    ';': 0xBA, '=': 0xBB, ',': 0xBC, '-': 0xBD, '.': 0xBE,
    '/': 0xBF, '`': 0xC0, '[': 0xDB, '\\': 0xDC, ']': 0xDD,
    '\'': 0xDE,
    
    # Numpad специальные
    'num_multiply': 0x6A, 'num_add': 0x6B, 'num_subtract': 0x6D,
    'num_decimal': 0x6E, 'num_divide': 0x6F,
    
    # Дополнительные клавиши
    'numlock': 0x90, 'scrolllock': 0x91,
    'left_shift': 0xA0, 'right_shift': 0xA1,
    'left_ctrl': 0xA2, 'right_ctrl': 0xA3,
    'left_alt': 0xA4, 'right_alt': 0xA5,
    
    # Медиа клавиши
    'browser_back': 0xA6, 'browser_forward': 0xA7,
    'browser_refresh': 0xA8, 'browser_stop': 0xA9,
    'browser_search': 0xAA, 'browser_favorites': 0xAB,
    'browser_home': 0xAC,
    'volume_mute': 0xAD, 'volume_down': 0xAE, 'volume_up': 0xAF,
    'media_next': 0xB0, 'media_prev': 0xB1,
    'media_stop': 0xB2, 'media_play_pause': 0xB3,
    
    # Дополнительные символы
    'win': 0x5B, 'right_win': 0x5C, 'apps': 0x5D,
    'sleep': 0x5F, 'print_screen': 0x2C,
}

# Параметры для создания scancode
MAPVK_VK_TO_VSC = 0

class AntiAFKApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anti-AFK COD")
        
        # Применяем тему
        self.style = ThemedStyle(self.root)
        self.style.set_theme("clearlooks")  # Меняем тему на clearlooks
        
        # Устанавливаем цвет фона
        self.root.configure(bg=self.style.lookup('TFrame', 'background'))
        
        # Устанавливаем фиксированный размер окна (ширина x высота)
        window_width = 600
        window_height = 900  # Увеличиваем высоту окна
        
        # Получаем размеры экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Вычисляем координаты для центрирования окна
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Устанавливаем размер и положение окна
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Запрещаем изменение размера окна
        self.root.resizable(False, False)
        
        # Путь к файлу настроек
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
        
        # Флаги активности функций
        self.walking_enabled = tk.BooleanVar(value=True)
        self.image_search_enabled = tk.BooleanVar(value=True)
        
        # Основные переменные
        self.running = False
        self.target_window_handle = None
        self.template_images = []
        self.search_area = None
        self.keyboard = KeyboardController()
        self.current_key_index = 0
        self.window_handles = []  # Добавляем список окон
        
        # Последовательность клавиш (по умолчанию WASD)
        self.key_sequence = ['w', 'a', 's', 'd']
        
        # Переменные для слайдеров
        self.wasd_hold_duration = tk.DoubleVar(value=0.5)
        self.wasd_pause_duration = tk.DoubleVar(value=1.0)
        self.image_search_delay = tk.DoubleVar(value=1.0)
        self.image_match_threshold = tk.DoubleVar(value=80.0)  # Добавляем переменную для порога совпадения
        
        # Загружаем сохраненные настройки
        self.load_settings()
        
        # Создаем журнал действий
        self.log_messages = []
        
        # Создаем интерфейс
        self.create_gui()
        
        # Настраиваем горячие клавиши
        self.setup_hotkeys()
        
        # Загружаем сохраненные изображения
        self.load_saved_images()
        
        # Обновляем список окон при запуске
        self.refresh_windows()
        
    def log_action(self, message, action_type="INFO"):
        """Логирует действие в журнал"""
        try:
            # Получаем текущее время
            current_time = time.strftime("%H:%M:%S", time.localtime())
            
            # Форматируем сообщение
            log_message = f"[{current_time}] [{action_type}] {message}\n"
            
            # Добавляем сообщение в журнал
            if hasattr(self, 'log_text'):
                self.log_text.insert(tk.END, log_message)
                self.log_text.see(tk.END)  # Прокручиваем к последней записи
                
                # Ограничиваем количество строк в журнале (оставляем последние 1000 строк)
                lines = self.log_text.get('1.0', tk.END).splitlines()
                if len(lines) > 1000:
                    self.log_text.delete('1.0', f"{len(lines) - 1000}.0")
        except Exception as e:
            print(f"Ошибка при логировании: {e}")
            traceback.print_exc()

    def clear_log(self):
        """Очищает журнал"""
        if hasattr(self, 'log_text'):
            self.log_text.delete('1.0', tk.END)
            self.log_action("Журнал очищен")

    def create_gui(self):
        # Создаем главный контейнер с вкладками
        self.tab_control = ttk.Notebook(self.root)
        
        # Создаем вкладку для основных элементов управления
        main_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(main_tab, text='Управление')
        
        # Создаем вкладку для журнала
        log_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(log_frame, text='Журнал')
        
        # Создаем вкладку для настройки клавиш
        keys_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(keys_tab, text='Настройка клавиш')
        
        # Создаем и настраиваем виджет для журнала
        log_frame = ttk.LabelFrame(log_frame, text="Журнал действий")
        log_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Создаем текстовое поле для журнала с полосой прокрутки
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=70, wrap=tk.WORD)
        self.log_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Добавляем кнопку очистки журнала
        clear_button = ttk.Button(log_frame, text="Очистить журнал", command=self.clear_log)
        clear_button.pack(pady=5)
        
        # Добавляем первую запись в журнал
        self.log_action("Программа запущена", "СИСТЕМА")
        
        # Создаем стиль для фреймов
        frame_style = ttk.Style()
        frame_style.configure('Custom.TFrame', background='#f0f0f0')
        
        # Создаем фрейм для кнопок
        button_frame = ttk.Frame(main_tab, style='Custom.TFrame')
        button_frame.pack(padx=5, pady=5, fill='x')
        
        # Создаем кнопки
        self.start_button = ttk.Button(button_frame, text='Старт (F7)', command=self.start)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(button_frame, text='Стоп (F8)', command=self.stop)
        self.stop_button.pack(side='left', padx=5)
        
        # Создаем фрейм для выбора окна
        window_frame = ttk.Frame(main_tab, style='Custom.TFrame')
        window_frame.pack(padx=5, pady=5, fill='x')
        
        # Добавляем метку и кнопку для выбора окна
        ttk.Label(window_frame, text="Окно:").pack(side='left', padx=5)
        self.window_var = tk.StringVar(value="Не выбрано")
        ttk.Label(window_frame, textvariable=self.window_var).pack(side='left', padx=5)
        ttk.Button(window_frame, text="Выбрать", command=self.select_window).pack(side='left', padx=5)

        # Фрейм для чекбоксов
        functions_frame = ttk.LabelFrame(main_tab, text="Активные функции", padding=10, style='Custom.TFrame')
        functions_frame.pack(fill="x", padx=10, pady=5)
        
        # Чекбоксы для включения/отключения функций
        ttk.Checkbutton(functions_frame, text="Ходьба WASD (F10)", 
                       variable=self.walking_enabled).pack(anchor="w", pady=2)
        ttk.Checkbutton(functions_frame, text="Поиск изображений (F11)", 
                       variable=self.image_search_enabled).pack(anchor="w", pady=2)

        # Фрейм для слайдеров
        sliders_frame = ttk.LabelFrame(main_tab, text="Настройки задержек", padding=10, style='Custom.TFrame')
        sliders_frame.pack(fill="x", padx=10, pady=5)

        # Слайдер длительности зажатия WASD
        hold_frame = ttk.Frame(sliders_frame)
        hold_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(hold_frame, text="Длительность зажатия WASD (сек):").pack(side="left")
        self.wasd_hold_label = ttk.Label(hold_frame, text=str(self.wasd_hold_duration.get()))
        self.wasd_hold_label.pack(side="right", padx=5)
        wasd_hold_slider = ttk.Scale(sliders_frame, from_=0.1, to=10.0, 
                                   variable=self.wasd_hold_duration,
                                   command=lambda v: self.update_slider_value(self.wasd_hold_label, v),
                                   orient=tk.HORIZONTAL)
        wasd_hold_slider.pack(fill="x", padx=5)

        # Слайдер паузы между зажатиями WASD
        pause_frame = ttk.Frame(sliders_frame)
        pause_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(pause_frame, text="Пауза между зажатиями WASD (сек):").pack(side="left")
        self.wasd_pause_label = ttk.Label(pause_frame, text=str(self.wasd_pause_duration.get()))
        self.wasd_pause_label.pack(side="right", padx=5)
        wasd_pause_slider = ttk.Scale(sliders_frame, from_=0.1, to=5.0, 
                                    variable=self.wasd_pause_duration,
                                    command=lambda v: self.update_slider_value(self.wasd_pause_label, v),
                                    orient=tk.HORIZONTAL)
        wasd_pause_slider.pack(fill="x", padx=5)

        # Слайдер паузы между итерациями поиска изображений
        search_frame = ttk.Frame(sliders_frame)
        search_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(search_frame, text="Пауза между поиском изображений (сек):").pack(side="left")
        self.image_search_label = ttk.Label(search_frame, text=str(self.image_search_delay.get()))
        self.image_search_label.pack(side="right", padx=5)
        image_search_slider = ttk.Scale(sliders_frame, from_=0.1, to=5.0, 
                                      variable=self.image_search_delay,
                                      command=lambda v: self.update_slider_value(self.image_search_label, v),
                                      orient=tk.HORIZONTAL)
        image_search_slider.pack(fill="x", padx=5)

        # Слайдер порога совпадения изображений
        threshold_frame = ttk.Frame(sliders_frame)
        threshold_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(threshold_frame, text="Порог совпадения изображений (%):").pack(side="left")
        self.image_match_threshold_label = ttk.Label(threshold_frame, text=str(self.image_match_threshold.get()))
        self.image_match_threshold_label.pack(side="right", padx=5)
        image_match_threshold_slider = ttk.Scale(sliders_frame, from_=0, to=100, 
                                               variable=self.image_match_threshold,
                                               command=lambda v: self.update_slider_value(self.image_match_threshold_label, v),
                                               orient=tk.HORIZONTAL)
        image_match_threshold_slider.pack(fill="x", padx=5)

        # Фрейм для координат мыши
        mouse_frame = ttk.LabelFrame(main_tab, text="Координаты мыши", style='Custom.TFrame')
        mouse_frame.pack(padx=10, pady=5, fill=tk.X)

        self.mouse_pos_label = ttk.Label(mouse_frame, text="Координаты: X: 0, Y: 0", font=('Courier', 10))
        self.mouse_pos_label.pack(pady=5)
        
        # Запускаем обновление координат мыши
        self.update_mouse_position()
        
        # Фрейм для работы с изображениями
        image_frame = ttk.LabelFrame(main_tab, text="Изображения для поиска", style='Custom.TFrame')
        image_frame.pack(padx=10, pady=5, fill=tk.X)

        # Кнопки для работы с изображениями
        image_buttons_frame = ttk.Frame(image_frame)
        image_buttons_frame.pack(fill=tk.X, pady=5)

        self.load_image_button = ttk.Button(image_buttons_frame, text="Добавить", command=self.load_template)
        self.load_image_button.pack(side=tk.LEFT, padx=5)

        self.remove_image_button = ttk.Button(image_buttons_frame, text="Удалить", command=self.remove_template)
        self.remove_image_button.pack(side=tk.LEFT, padx=5)

        # Кнопка для изменения приоритета
        self.priority_button = ttk.Button(image_buttons_frame, text="Изменить приоритет", command=self.change_priority)
        self.priority_button.pack(side=tk.LEFT, padx=5)

        # Список изображений с приоритетами
        self.images_listbox = tk.Listbox(image_frame, height=5, 
                                    bg=self.style.lookup('TFrame', 'background'),
                                    fg=self.style.lookup('TLabel', 'foreground'),
                                    selectmode=tk.SINGLE,
                                    exportselection=0)
        self.images_listbox.pack(fill=tk.X, pady=5, padx=5)

        # Фрейм для области поиска
        coord_frame = ttk.LabelFrame(main_tab, text="Область поиска", style='Custom.TFrame')
        coord_frame.pack(padx=10, pady=5, fill=tk.X)

        # Верхний левый угол
        ttk.Label(coord_frame, text="X1:").grid(row=0, column=0, padx=5)
        self.x1_entry = ttk.Entry(coord_frame, width=8)
        self.x1_entry.grid(row=0, column=1, padx=5)

        ttk.Label(coord_frame, text="Y1:").grid(row=0, column=2, padx=5)
        self.y1_entry = ttk.Entry(coord_frame, width=8)
        self.y1_entry.grid(row=0, column=3, padx=5)

        # Нижний правый угол
        ttk.Label(coord_frame, text="X2:").grid(row=1, column=0, padx=5)
        self.x2_entry = ttk.Entry(coord_frame, width=8)
        self.x2_entry.grid(row=1, column=1, padx=5)

        ttk.Label(coord_frame, text="Y2:").grid(row=1, column=2, padx=5)
        self.y2_entry = ttk.Entry(coord_frame, width=8)
        self.y2_entry.grid(row=1, column=3, padx=5)

        ttk.Label(coord_frame, text="(оставьте пустыми для поиска по всему экрану)").grid(row=2, column=0, columnspan=4, pady=5)

        # Статус
        self.status_label = ttk.Label(main_tab, text="Статус: Остановлено")
        self.status_label.pack(pady=10)

        # Размещаем вкладки
        self.tab_control.pack(expand=1, fill='both')

        # Создаем интерфейс вкладки настройки клавиш
        self.create_keys_tab(keys_tab)

    def create_keys_tab(self, parent):
        """Создает интерфейс вкладки настройки клавиш"""
        # Фрейм для списка текущих клавиш
        current_keys_frame = ttk.LabelFrame(parent, text="Текущая последовательность клавиш")
        current_keys_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Создаем список клавиш
        self.keys_listbox = tk.Listbox(current_keys_frame, height=10)
        self.keys_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Обновляем список клавиш
        self.update_keys_listbox()
        
        # Фрейм для кнопок управления
        buttons_frame = ttk.Frame(current_keys_frame)
        buttons_frame.pack(padx=5, pady=5, fill=tk.X)
        
        # Фрейм для добавления новой клавиши
        add_key_frame = ttk.Frame(buttons_frame)
        add_key_frame.pack(side=tk.LEFT, padx=5)
        
        # Создаем список клавиш по категориям
        key_categories = [
            "=== БУКВЫ ===",
            *[f"    {k}" for k in "abcdefghijklmnopqrstuvwxyz"],
            "=== ЦИФРЫ ===",
            *[f"    {k}" for k in "0123456789"],
            "=== NUMPAD ===",
            *[f"    num{k}" for k in range(10)],
            "    num_multiply",
            "    num_add",
            "    num_subtract",
            "    num_decimal",
            "    num_divide",
            "=== ФУНКЦИОНАЛЬНЫЕ ===",
            *[f"    f{k}" for k in range(1, 13)],
            "=== СПЕЦИАЛЬНЫЕ ===",
            "    backspace",
            "    tab",
            "    enter",
            "    shift",
            "    ctrl",
            "    alt",
            "    pause",
            "    capslock",
            "    esc",
            "    space",
            "    pageup",
            "    pagedown",
            "    end",
            "    home",
            "=== СТРЕЛКИ ===",
            "    left",
            "    up",
            "    right",
            "    down",
            "=== УПРАВЛЕНИЕ ===",
            "    insert",
            "    delete",
            "=== СИМВОЛЫ ===",
            "    ;",
            "    =",
            "    ,",
            "    -",
            "    .",
            "    /",
            "    `",
            "    [",
            "    \\",
            "    ]",
            "    '",
            "=== ДОПОЛНИТЕЛЬНЫЕ ===",
            "    numlock",
            "    scrolllock",
            "    left_shift",
            "    right_shift",
            "    left_ctrl",
            "    right_ctrl",
            "    left_alt",
            "    right_alt",
            "=== МЕДИА ===",
            "    browser_back",
            "    browser_forward",
            "    browser_refresh",
            "    browser_stop",
            "    browser_search",
            "    browser_favorites",
            "    browser_home",
            "    volume_mute",
            "    volume_down",
            "    volume_up",
            "    media_next",
            "    media_prev",
            "    media_stop",
            "    media_play_pause",
            "=== СИСТЕМНЫЕ ===",
            "    win",
            "    right_win",
            "    apps",
            "    sleep",
            "    print_screen"
        ]
        
        # Комбобокс для выбора клавиши
        self.new_key_var = tk.StringVar()
        key_combobox = ttk.Combobox(add_key_frame, textvariable=self.new_key_var, values=key_categories, width=30)
        key_combobox.pack(side=tk.LEFT, padx=5)
        
        # Настраиваем комбобокс чтобы заголовки категорий нельзя было выбрать
        def on_combobox_select(event):
            selected = key_combobox.get()
            if selected.startswith('==='):
                key_combobox.set('')
            else:
                # Убираем отступы при выборе
                self.new_key_var.set(selected.strip())
        
        key_combobox.bind('<<ComboboxSelected>>', on_combobox_select)
        
        # Кнопки управления
        ttk.Button(add_key_frame, text="Добавить клавишу", command=self.add_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Удалить выбранную", command=self.remove_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Очистить все", command=self.clear_keys).pack(side=tk.LEFT, padx=5)
        
        # Кнопки перемещения
        move_frame = ttk.Frame(buttons_frame)
        move_frame.pack(side=tk.RIGHT, padx=5)
        ttk.Button(move_frame, text="↑", width=3, command=self.move_key_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(move_frame, text="↓", width=3, command=self.move_key_down).pack(side=tk.LEFT, padx=2)

    def update_keys_listbox(self):
        """Обновляет список клавиш в интерфейсе"""
        self.keys_listbox.delete(0, tk.END)
        for i, key in enumerate(self.key_sequence, 1):
            self.keys_listbox.insert(tk.END, f"{i}. {key}")

    def add_key(self):
        """Добавляет новую клавишу в последовательность"""
        new_key = self.new_key_var.get().lower()
        if new_key in VIRTUAL_KEYS:
            self.key_sequence.append(new_key)
            self.update_keys_listbox()
            self.save_settings()
        else:
            messagebox.showerror("Ошибка", "Выберите клавишу из списка")

    def remove_key(self):
        """Удаляет выбранную клавишу из последовательности"""
        selection = self.keys_listbox.curselection()
        if selection:
            index = selection[0]
            self.key_sequence.pop(index)
            self.update_keys_listbox()
            self.save_settings()

    def clear_keys(self):
        """Очищает всю последовательность клавиш"""
        if messagebox.askyesno("Подтверждение", "Очистить всю последовательность клавиш?"):
            self.key_sequence = []
            self.update_keys_listbox()
            self.save_settings()

    def move_key_up(self):
        """Перемещает выбранную клавишу вверх по списку"""
        selection = self.keys_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            self.key_sequence[index], self.key_sequence[index-1] = self.key_sequence[index-1], self.key_sequence[index]
            self.update_keys_listbox()
            self.keys_listbox.selection_set(index-1)
            self.save_settings()

    def move_key_down(self):
        """Перемещает выбранную клавишу вниз по списку"""
        selection = self.keys_listbox.curselection()
        if selection and selection[0] < len(self.key_sequence) - 1:
            index = selection[0]
            self.key_sequence[index], self.key_sequence[index+1] = self.key_sequence[index+1], self.key_sequence[index]
            self.update_keys_listbox()
            self.keys_listbox.selection_set(index+1)
            self.save_settings()

    def update_mouse_position(self):
        """Обновляет отображение координат мыши"""
        if self.root.winfo_exists():
            try:
                x, y = pyautogui.position()
                self.mouse_pos_label.configure(text=f"Координаты: X: {x}, Y: {y}")
            except:
                pass
            self.root.after(100, self.update_mouse_position)  # Обновляем каждые 100 мс

    def save_images_list(self):
        """Сохранение списка путей к изображениям и координат области поиска"""
        try:
            data = {
                'images': [{
                    'path': img['path'],
                    'priority': img.get('priority', 1)
                } for img in self.template_images],
                'search_area': self.search_area
            }
            save_path = resource_path('templates/saved_images.json')
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить список изображений: {str(e)}")

    def load_saved_images(self):
        """Загрузка сохраненных изображений и координат при запуске"""
        try:
            save_path = resource_path('templates/saved_images.json')
            if os.path.exists(save_path):
                with open(save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Загружаем изображения
                for img_data in data.get('images', []):
                    try:
                        if not isinstance(img_data, dict):
                            continue
                            
                        img_path = img_data.get('path')
                        if not img_path:
                            continue
                            
                        # Преобразуем путь для текущего окружения
                        img_path = resource_path(os.path.join('templates', os.path.basename(img_path)))
                        image = cv2.imread(img_path)
                        if image is not None:
                            self.template_images.append({
                                'path': img_path,
                                'image': image,
                                'priority': img_data.get('priority', 1)
                            })
                    except Exception as e:
                        print(f"Ошибка загрузки изображения: {str(e)}")
                
                # Обновляем список в интерфейсе
                self.update_images_list()
                
                # Загружаем координаты области поиска
                self.search_area = data.get('search_area')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить сохраненные данные: {str(e)}")

    def start(self, _=None):
        """Запускает программу"""
        if not self.running:
            if not self.target_window_handle:
                messagebox.showwarning("Внимание", "Выберите окно игры!")
                return
            
            if not self.walking_enabled.get() and not self.image_search_enabled.get():
                messagebox.showwarning("Внимание", "Включите хотя бы одну функцию!")
                return
            
            self.running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.log_action("Программа запущена", "СТАРТ")
            self.status_label.config(text="Статус: Запущено")
            
            # Запускаем потоки для отправки клавиш и поиска изображений
            if self.walking_enabled.get():
                self.key_thread = threading.Thread(target=self.key_press_loop, daemon=True)
                self.key_thread.start()
            
            if self.image_search_enabled.get():
                self.image_thread = threading.Thread(target=self.image_search_loop, daemon=True)
                self.image_thread.start()

    def key_press_loop(self):
        """Отдельный поток для отправки клавиш"""
        while self.running:
            try:
                if self.target_window_handle:
                    self.press_sequential_key()
            except Exception as e:
                print(f"Ошибка в цикле отправки клавиш: {e}")
                traceback.print_exc()
                self.root.after(0, self.handle_error, str(e))

    def image_search_loop(self):
        """Отдельный поток для поиска изображений"""
        while self.running:
            try:
                if self.target_window_handle and self.template_images:
                    self.find_and_click_template()
                time.sleep(self.image_search_delay.get())  # Пауза между итерациями
            except Exception as e:
                print(f"Ошибка в цикле поиска изображений: {e}")
                traceback.print_exc()
                self.root.after(0, self.handle_error, str(e))

    def handle_error(self, error_message):
        """Обработка ошибок из потоков"""
        self.status_label.config(text=f"Ошибка: {error_message}")
        self.stop()

    def stop(self, _=None):
        """Останавливает программу"""
        if self.running:
            self.running = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.log_action("Программа остановлена", "СТОП")
            self.status_label.config(text="Статус: Остановлено")
            
            # Ждем завершения потоков
            if hasattr(self, 'key_thread') and self.key_thread.is_alive():
                self.key_thread.join(timeout=1.0)
            if hasattr(self, 'image_thread') and self.image_thread.is_alive():
                self.image_thread.join(timeout=1.0)

    def load_template(self):
        """Загрузка изображения для поиска"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if file_path:
            try:
                # Копируем файл в папку templates
                templates_dir = resource_path('templates')
                os.makedirs(templates_dir, exist_ok=True)
                new_path = os.path.join(templates_dir, os.path.basename(file_path))
                
                # Если файл уже существует, добавляем временную метку
                if os.path.exists(new_path):
                    base, ext = os.path.splitext(os.path.basename(file_path))
                    new_path = os.path.join(templates_dir, f"template_{int(time.time())}_{base}{ext}")
                
                # Копируем файл
                import shutil
                shutil.copy2(file_path, new_path)
                
                # Загружаем изображение с помощью OpenCV
                image = cv2.imread(new_path)
                if image is None:
                    raise Exception("Не удалось загрузить изображение")

                # Добавляем в список
                self.template_images.append({
                    'path': new_path,
                    'image': image,
                    'priority': 1  # Добавляем приоритет по умолчанию
                })

                # Обновляем список в интерфейсе
                self.update_images_list()
                
                # Сохраняем список изображений
                self.save_images_list()
                
                self.log_action(f"Добавлено изображение {os.path.basename(new_path)}", "СИСТЕМА")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")

    def remove_template(self):
        """Удаление выбранного изображения"""
        selection = self.images_listbox.curselection()
        if selection:
            index = selection[0]
            removed_image = self.template_images.pop(index)
            self.images_listbox.delete(index)
            self.log_action(f"Удалено изображение {os.path.basename(removed_image['path'])}", "СИСТЕМА")

    def clear_templates(self):
        """Очищает весь список изображений"""
        self.template_images.clear()
        self.images_listbox.delete(0, tk.END)
        self.log_action("Список изображений очищен", "СИСТЕМА")
        self.save_images_list()

    def get_window_screenshot(self):
        """Получает скриншот окна"""
        try:
            if not self.target_window_handle:
                return None

            # Получаем размеры окна
            window_rect = win32gui.GetWindowRect(self.target_window_handle)
            width = window_rect[2] - window_rect[0]
            height = window_rect[3] - window_rect[1]
            print(f"Размеры окна: {width}x{height}")

            try:
                # Создаем контекст устройства
                window_dc = win32gui.GetWindowDC(self.target_window_handle)
                dc_obj = win32ui.CreateDCFromHandle(window_dc)
                compatible_dc = dc_obj.CreateCompatibleDC()

                # Создаем битмап
                dataBitMap = win32ui.CreateBitmap()
                dataBitMap.CreateCompatibleBitmap(dc_obj, width, height)
                compatible_dc.SelectObject(dataBitMap)

                # Копируем изображение через user32.dll
                user32 = ctypes.WinDLL('user32', use_last_error=True)
                result = user32.PrintWindow(self.target_window_handle, compatible_dc.GetSafeHdc(), 2)
                if not result:
                    print("Ошибка при копировании окна")
                    return None

                # Преобразуем в массив numpy
                bmpinfo = dataBitMap.GetInfo()
                bmpstr = dataBitMap.GetBitmapBits(True)
                img = np.frombuffer(bmpstr, dtype='uint8')
                img.shape = (height, width, 4)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                # Освобождаем ресурсы
                win32gui.DeleteObject(dataBitMap.GetHandle())
                compatible_dc.DeleteDC()
                dc_obj.DeleteDC()
                win32gui.ReleaseDC(self.target_window_handle, window_dc)

                print(f"Сохранен скриншот размером: {img.shape}")
                return img

            except Exception as e:
                print(f"Ошибка при получении скриншота: {e}")
                traceback.print_exc()
                
                # Пробуем альтернативный метод через PIL
                try:
                    print("Пробуем альтернативный метод получения скриншота...")
                    screenshot = ImageGrab.grab(bbox=(window_rect[0], window_rect[1], window_rect[2], window_rect[3]))
                    img = np.array(screenshot)
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    print(f"Сохранен скриншот через PIL размером: {img.shape}")
                    return img
                except Exception as e2:
                    print(f"Ошибка при получении скриншота через PIL: {e2}")
                    traceback.print_exc()
                    return None

        except Exception as e:
            print(f"Общая ошибка при получении скриншота: {e}")
            traceback.print_exc()
            return None

    def activate_window(self):
        """Активирует окно игры"""
        try:
            if self.target_window_handle:
                # Проверяем, не свернуто ли окно
                placement = win32gui.GetWindowPlacement(self.target_window_handle)
                if placement[1] == win32con.SW_SHOWMINIMIZED:
                    win32gui.ShowWindow(self.target_window_handle, win32con.SW_RESTORE)
                
                # Пытаемся активировать окно
                foreground_window = win32gui.GetForegroundWindow()
                if foreground_window != self.target_window_handle:
                    # Получаем ID потоков
                    current_thread = win32api.GetCurrentThreadId()
                    foreground_thread = win32process.GetWindowThreadProcessId(foreground_window)[0]
                    target_thread = win32process.GetWindowThreadProcessId(self.target_window_handle)[0]
                    
                    # Присоединяем потоки
                    win32process.AttachThreadInput(current_thread, foreground_thread, True)
                    win32process.AttachThreadInput(current_thread, target_thread, True)
                    
                    try:
                        # Устанавливаем окно на передний план
                        win32gui.SetWindowPos(self.target_window_handle, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                           win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                        win32gui.SetWindowPos(self.target_window_handle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                           win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                        win32gui.SetForegroundWindow(self.target_window_handle)
                    finally:
                        # Отсоединяем потоки
                        win32process.AttachThreadInput(current_thread, foreground_thread, False)
                        win32process.AttachThreadInput(current_thread, target_thread, False)
                
                return True
        except Exception as e:
            print(f"Ошибка при активации окна: {e}")
            traceback.print_exc()
        return False

    def find_and_click_template(self):
        """Поиск и клик по шаблону"""
        try:
            # Получаем скриншот окна
            screenshot = self.get_window_screenshot()
            if screenshot is None:
                return False

            # Сортируем изображения по приоритету (от высшего к низшему)
            sorted_templates = sorted(self.template_images, key=lambda x: x.get('priority', 1), reverse=True)

            for template_data in sorted_templates:
                template = template_data['image']
                
                # Используем порог совпадения из слайдера
                threshold = self.image_match_threshold.get() / 100.0  # Преобразуем процент в значение от 0 до 1
                
                # Поиск шаблона на изображении
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                if max_val >= threshold:  # Используем настраиваемый порог
                    # Получаем координаты центра найденного изображения
                    h, w = template.shape[:2]
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2

                    # Получаем координаты окна
                    window_rect = win32gui.GetWindowRect(self.target_window_handle)
                    screen_x = window_rect[0] + center_x
                    screen_y = window_rect[1] + center_y

                    # Активируем окно перед кликом
                    if self.activate_window():
                        # Перемещаем курсор и выполняем клик
                        win32api.SetCursorPos((screen_x, screen_y))
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                        time.sleep(0.1)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                        
                        self.log_action(f"Найдено изображение {os.path.basename(template_data['path'])} (совпадение: {max_val:.2%})", "СИСТЕМА")
                        return True

            return False
        except Exception as e:
            print(f"Ошибка при поиске шаблона: {e}")
            traceback.print_exc()
            return False

    def click_at(self, x, y):
        """Отправляет клик через pydirectinput с задержками"""
        if not self.target_window_handle:
            return False

        try:
            # Получаем позицию окна
            window_rect = win32gui.GetWindowRect(self.target_window_handle)
            
            # Преобразуем координаты в абсолютные
            abs_x = window_rect[0] + x
            abs_y = window_rect[1] + y
            
            print(f"Относительные координаты: {x}, {y}")
            print(f"Абсолютные координаты: {abs_x}, {abs_y}")

            # Настраиваем pydirectinput для работы без активации окна
            pydirectinput.PAUSE = False
            
            # Отправляем клик
            pydirectinput.moveTo(abs_x, abs_y)
            time.sleep(0.1)  # Ждем перемещения
            
            # Нажимаем кнопку мыши
            pydirectinput.mouseDown()
            time.sleep(0.2)  # Держим нажатой
            
            # Отпускаем кнопку мыши
            pydirectinput.mouseUp()
            time.sleep(0.1)  # Ждем отпускания
            
            return True

        except Exception as e:
            print(f"Ошибка при отправке клика: {e}")
            traceback.print_exc()
            return False

    def click_at_alternative(self, x, y):
        """Альтернативный метод клика через PostMessage с предварительной активацией окна"""
        if not self.target_window_handle:
            return False

        try:
            # Получаем позицию окна
            window_rect = win32gui.GetWindowRect(self.target_window_handle)
            
            # Преобразуем координаты в абсолютные
            abs_x = window_rect[0] + x
            abs_y = window_rect[1] + y
            
            print(f"Относительные координаты: {x}, {y}")
            print(f"Абсолютные координаты: {abs_x}, {abs_y}")

            # Упаковываем координаты в LPARAM
            lparam = win32api.MAKELONG(x, y)

            # Получаем текущее активное окно
            old_window = win32gui.GetForegroundWindow()
            
            try:
                # Активируем наше окно (но не показываем его)
                win32gui.SetWindowPos(self.target_window_handle, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
                
                # Отправляем сообщения через PostMessage
                win32gui.PostMessage(self.target_window_handle, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
                time.sleep(0.1)
                win32gui.PostMessage(self.target_window_handle, win32con.WM_LBUTTONUP, 0, lparam)
                
            finally:
                # Восстанавливаем предыдущее окно
                if old_window:
                    win32gui.SetWindowPos(self.target_window_handle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
                    win32gui.SetForegroundWindow(old_window)

            return True

        except Exception as e:
            print(f"Ошибка при отправке клика: {e}")
            traceback.print_exc()
            return False

    def on_closing(self):
        """Обработчик закрытия окна"""
        self.save_images_list()
        self.root.destroy()

    def __del__(self):
        # Остановка слушателя при закрытии программы
        if hasattr(self, 'listener'):
            self.listener.stop()

    def refresh_windows(self):
        """Обновляет список окон"""
        def enum_window_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and not title.startswith("tk"):  # Исключаем окна tkinter
                    windows.append((hwnd, title))
            return True

        self.window_handles = []
        win32gui.EnumWindows(enum_window_callback, self.window_handles)

    def select_window(self):
        """Открывает диалог выбора окна"""
        if not self.window_handles:
            self.refresh_windows()
        
        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.root)
        dialog.title("Выберите окно")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Создаем список окон
        listbox = tk.Listbox(dialog, width=50)
        listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Заполняем список окон
        for hwnd, title in self.window_handles:
            listbox.insert(tk.END, title)
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                hwnd, title = self.window_handles[index]
                self.target_window_handle = hwnd
                self.window_var.set(title)
                self.log_action(f"Выбрано окно: {title}", "СИСТЕМА")
                dialog.destroy()
        
        # Кнопка выбора
        ttk.Button(dialog, text="Выбрать", command=on_select).pack(pady=5)
        
        # Кнопка обновления списка
        def refresh():
            self.refresh_windows()
            listbox.delete(0, tk.END)
            for hwnd, title in self.window_handles:
                listbox.insert(tk.END, title)
        
        ttk.Button(dialog, text="Обновить список", command=refresh).pack(pady=5)

    def setup_hotkeys(self):
        """Настройка горячих клавиш"""
        keyboard.on_press_key('F7', lambda _: self.start())
        keyboard.on_press_key('F8', lambda _: self.stop())
        keyboard.on_press_key('F10', lambda _: self.toggle_walking())
        keyboard.on_press_key('F11', lambda _: self.toggle_image_search())

    def toggle_walking(self, _=None):
        """Переключает функцию ходьбы"""
        current = self.walking_enabled.get()
        self.walking_enabled.set(not current)
        state = "включена" if not current else "выключена"
        self.log_action(f"Функция ходьбы {state} (F10)", "СИСТЕМА")
        
        # Если программа запущена, обновляем потоки
        if self.running:
            if not current:  # Если включили
                if not hasattr(self, 'key_thread') or not self.key_thread.is_alive():
                    self.key_thread = threading.Thread(target=self.key_press_loop, daemon=True)
                    self.key_thread.start()
            else:  # Если выключили
                if hasattr(self, 'key_thread'):
                    self.key_thread = None

    def toggle_image_search(self, _=None):
        """Переключает функцию поиска изображений"""
        current = self.image_search_enabled.get()
        self.image_search_enabled.set(not current)
        state = "включена" if not current else "выключена"
        self.log_action(f"Функция поиска изображений {state} (F11)", "СИСТЕМА")
        
        # Если программа запущена, обновляем потоки
        if self.running:
            if not current:  # Если включили
                if not hasattr(self, 'image_thread') or not self.image_thread.is_alive():
                    self.image_thread = threading.Thread(target=self.image_search_loop, daemon=True)
                    self.image_thread.start()
            else:  # Если выключили
                if hasattr(self, 'image_thread'):
                    self.image_thread = None

    def save_settings(self):
        """Сохраняет настройки в файл"""
        settings = {
            'wasd_hold_duration': self.wasd_hold_duration.get(),
            'wasd_pause_duration': self.wasd_pause_duration.get(),
            'image_search_delay': self.image_search_delay.get(),
            'image_match_threshold': self.image_match_threshold.get(),
            'key_sequence': self.key_sequence  # Добавляем сохранение последовательности клавиш
        }
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")

    def load_settings(self):
        """Загружает настройки из файла"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                self.wasd_hold_duration.set(settings.get('wasd_hold_duration', 0.5))
                self.wasd_pause_duration.set(settings.get('wasd_pause_duration', 1.0))
                self.image_search_delay.set(settings.get('image_search_delay', 1.0))
                self.image_match_threshold.set(settings.get('image_match_threshold', 80.0))
                self.key_sequence = settings.get('key_sequence', ['w', 'a', 's', 'd'])  # Загружаем последовательность клавиш
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")

    def update_slider_value(self, label, value):
        """Обновляет значение метки слайдера и сохраняет настройки"""
        label.config(text=f"{float(value):.1f}")
        self.save_settings()

    def press_sequential_key(self):
        """Отправляет последовательное нажатие клавиш напрямую в окно игры"""
        if not self.target_window_handle or not self.key_sequence:
            return
        
        key = self.key_sequence[self.current_key_index]
        vk_code = VIRTUAL_KEYS[key]
        scan_code = win32api.MapVirtualKey(vk_code, MAPVK_VK_TO_VSC)
        
        try:
            # Проверяем, активно ли окно игры
            is_game_active = win32gui.GetForegroundWindow() == self.target_window_handle
            method = "keybd_event" if is_game_active else "SendMessage"
            
            if is_game_active:
                # Если окно игры активно, используем keybd_event
                win32api.keybd_event(vk_code, scan_code, 0, 0)
                
                # Держим клавишу нажатой
                start_time = time.time()
                while time.time() - start_time < self.wasd_hold_duration.get() and self.running:
                    time.sleep(0.1)
                
                # Отпускаем клавишу
                win32api.keybd_event(vk_code, scan_code, win32con.KEYEVENTF_KEYUP, 0)
                
            else:
                # Если активно другое окно, используем SendMessage
                lparam_down = (scan_code << 16) | 1
                lparam_up = lparam_down | (3 << 30)
                
                # Отправляем нажатие клавиши
                win32api.SendMessage(self.target_window_handle, win32con.WM_KEYDOWN, vk_code, lparam_down)
                
                # Периодически отправляем WM_KEYDOWN для поддержания нажатия
                start_time = time.time()
                while time.time() - start_time < self.wasd_hold_duration.get() and self.running:
                    win32api.SendMessage(self.target_window_handle, win32con.WM_KEYDOWN, vk_code, lparam_down)
                    time.sleep(0.1)
                
                # Отправляем отпускание клавиши
                win32api.SendMessage(self.target_window_handle, win32con.WM_KEYUP, vk_code, lparam_up)
            
            self.log_action(f"Нажата клавиша {key}", method)
            
            # Переходим к следующей клавише
            self.current_key_index = (self.current_key_index + 1) % len(self.key_sequence)
            
            # Добавляем задержку между нажатиями
            time.sleep(self.wasd_pause_duration.get())
            
        except Exception as e:
            print(f"Ошибка при нажатии клавиши {key}: {e}")
            traceback.print_exc()

    def change_priority(self):
        """Изменение приоритета выбранного изображения"""
        selection = self.images_listbox.curselection()
        if selection:
            index = selection[0]
            current_priority = self.template_images[index].get('priority', 1)
            
            # Запрашиваем новый приоритет
            new_priority = simpledialog.askinteger("Приоритет", 
                                                 "Введите приоритет (1-10, где 1 - высший):",
                                                 initialvalue=current_priority,
                                                 minvalue=1, maxvalue=10)
            
            if new_priority is not None:
                self.template_images[index]['priority'] = new_priority
                self.update_images_list()
                self.save_images_list()
                self.log_action(f"Изменен приоритет изображения {os.path.basename(self.template_images[index]['path'])} на {new_priority}", "СИСТЕМА")

    def update_images_list(self):
        """Обновление списка изображений в интерфейсе"""
        self.images_listbox.delete(0, tk.END)
        for template in self.template_images:
            filename = os.path.basename(template['path'])
            priority = template.get('priority', 1)
            self.images_listbox.insert(tk.END, f"[P{priority}] {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AntiAFKApp(root)
    root.mainloop()
