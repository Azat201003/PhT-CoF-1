import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date, timedelta
import calendar
from tkcalendar import DateEntry
import tktimepicker

class HabitsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Habits Tracker")
        self.root.geometry("1100x750")
        
        # Инициализация базы данных
        self.init_db()
        
        # Загрузка данных
        self.load_habits()
        self.load_stars()
        
        # Стиль
        self.setup_styles()
        
        # Переменные для управления видимостью
        self.current_page = None
        
        # Создание интерфейса
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        
        # Показываем главную страницу по умолчанию
        self.show_main()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цвета
        self.bg_color = "#f5f5f5"
        self.sidebar_color = "#2c3e50"
        self.header_color = "#34495e"
        self.good_color = "#2ecc71"
        self.bad_color = "#e74c3c"
        self.accent_color = "#3498db"
        
        self.root.configure(bg=self.bg_color)
    
    def create_header(self):
        header = tk.Frame(self.root, bg=self.header_color, height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        
        title = tk.Label(
            header, 
            text="Habits Tracker", 
            font=("Arial", 24, "bold"),
            bg=self.header_color,
            fg="white"
        )
        title.pack(pady=15)
    
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg=self.sidebar_color, width=200)
        sidebar.pack(fill=tk.Y, side=tk.LEFT)
        
        menu_items = [
            ("Главная", self.show_main),
            ("Список привычек", self.show_habits_list),
            ("Календарь привычек", self.show_calendar),
            ("Заметки", self.show_notes)
        ]
        
        for text, command in menu_items:
            btn = tk.Button(
                sidebar,
                text=text,
                font=("Arial", 12),
                bg=self.sidebar_color,
                fg="white",
                activebackground="#1a2530",
                activeforeground="white",
                bd=0,
                padx=20,
                pady=15,
                anchor="w",
                width=15,
                command=command
            )
            btn.pack(fill=tk.X)
            
            # Добавляем разделитель
            sep = tk.Frame(sidebar, height=1, bg="#1a2530")
            sep.pack(fill=tk.X, padx=10)
        
        # Кнопка выхода
        exit_btn = tk.Button(
            sidebar,
            text="Выход",
            font=("Arial", 12),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            bd=0,
            padx=20,
            pady=15,
            anchor="w",
            width=15,
            command=self.root.quit
        )
        exit_btn.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_main_content(self):
        # Основной контейнер
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        
        # Создаем все страницы заранее
        self.create_main_page()
        self.create_habits_list_page()
        self.create_calendar_page()
        self.create_notes_page()
        
        # Скрываем все страницы кроме главной
        self.hide_all_pages()
    
    def create_main_page(self):
        """Создаем главную страницу заранее"""
        self.main_page = tk.Frame(self.main_container, bg=self.bg_color)
        
        # Основной контейнер с двумя колонками
        main_frame = tk.Frame(self.main_page, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Левая колонка
        left_frame = tk.Frame(main_frame, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Правая колонка
        right_frame = tk.Frame(main_frame, bg=self.bg_color, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        # Звездочки (валюта)
        stars_frame = tk.Frame(left_frame, bg="white", bd=2, relief=tk.RAISED, padx=20, pady=10)
        stars_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.stars_label = tk.Label(
            stars_frame,
            text=f"★ {self.total_stars}",
            font=("Arial", 48, "bold"),
            bg="white",
            fg="#f1c40f"
        )
        self.stars_label.pack(pady=10)
        
        # Форма добавления привычки
        self.form_frame = tk.Frame(left_frame, bg="white", bd=2, relief=tk.RAISED, padx=20, pady=20)
        self.form_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            self.form_frame,
            text="Добавить выполненную привычку",
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(pady=(0, 10))
        
        # Выбор привычки
        tk.Label(self.form_frame, text="Привычка:", bg="white").pack(anchor="w", pady=(10, 0))
        
        self.habit_var = tk.StringVar()
        self.habit_combo = ttk.Combobox(self.form_frame, textvariable=self.habit_var, font=("Arial", 11))
        self.habit_combo.pack(fill=tk.X, pady=5)
        
        # Выбор даты и времени
        time_frame = tk.Frame(self.form_frame, bg="white")
        time_frame.pack(fill=tk.X, pady=10)
        
        # Дата
        tk.Label(time_frame, text="Дата:", bg="white").pack(side=tk.LEFT, padx=(0, 10))
        
        self.date_entry = DateEntry(
            time_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=("Arial", 10)
        )
        self.date_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Время
        tk.Label(time_frame, text="Время:", bg="white").pack(side=tk.LEFT, padx=(0, 10))
        
        # Поля для времени
        time_input_frame = tk.Frame(time_frame, bg="white")
        time_input_frame.pack(side=tk.LEFT)
        
        self.hour_var = tk.StringVar(value="12")
        self.minute_var = tk.StringVar(value="00")
        
        hour_spinbox = tk.Spinbox(
            time_input_frame,
            from_=0,
            to=23,
            width=3,
            textvariable=self.hour_var,
            font=("Arial", 10),
            format="%02.0f"
        )
        hour_spinbox.pack(side=tk.LEFT)
        
        tk.Label(time_input_frame, text=":", bg="white").pack(side=tk.LEFT, padx=2)
        
        minute_spinbox = tk.Spinbox(
            time_input_frame,
            from_=0,
            to=59,
            width=3,
            textvariable=self.minute_var,
            font=("Arial", 10),
            format="%02.0f"
        )
        minute_spinbox.pack(side=tk.LEFT)
        
        # Кнопка добавления
        add_btn = tk.Button(
            self.form_frame,
            text="Добавить привычку",
            bg=self.good_color,
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            command=self.add_habit_log
        )
        add_btn.pack(pady=20, fill=tk.X)
        
        # Правая колонка: списки привычек
        # Плохие привычки
        self.bad_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.RAISED, padx=15, pady=15)
        self.bad_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        tk.Label(
            self.bad_frame,
            text="Последние плохие привычки",
            font=("Arial", 12, "bold"),
            bg="white",
            fg=self.bad_color
        ).pack(pady=(0, 10))
        
        # Кастомный список с прокруткой для плохих привычек
        self.bad_canvas = tk.Canvas(self.bad_frame, bg="white", highlightthickness=0)
        self.bad_scrollbar = tk.Scrollbar(self.bad_frame, orient="vertical", command=self.bad_canvas.yview)
        self.bad_scrollable_frame = tk.Frame(self.bad_canvas, bg="white")
        
        self.bad_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.bad_canvas.configure(scrollregion=self.bad_canvas.bbox("all"))
        )
        
        self.bad_canvas.create_window((0, 0), window=self.bad_scrollable_frame, anchor="nw")
        self.bad_canvas.configure(yscrollcommand=self.bad_scrollbar.set)
        
        self.bad_canvas.pack(side="left", fill="both", expand=True)
        self.bad_scrollbar.pack(side="right", fill="y")
        
        # Хорошие привычки
        self.good_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.RAISED, padx=15, pady=15)
        self.good_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            self.good_frame,
            text="Старые хорошие привычки",
            font=("Arial", 12, "bold"),
            bg="white",
            fg=self.good_color
        ).pack(pady=(0, 10))
        
        # Кастомный список с прокруткой для хороших привычек
        self.good_canvas = tk.Canvas(self.good_frame, bg="white", highlightthickness=0)
        self.good_scrollbar = tk.Scrollbar(self.good_frame, orient="vertical", command=self.good_canvas.yview)
        self.good_scrollable_frame = tk.Frame(self.good_canvas, bg="white")
        
        self.good_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.good_canvas.configure(scrollregion=self.good_canvas.bbox("all"))
        )
        
        self.good_canvas.create_window((0, 0), window=self.good_scrollable_frame, anchor="nw")
        self.good_canvas.configure(yscrollcommand=self.good_scrollbar.set)
        
        self.good_canvas.pack(side="left", fill="both", expand=True)
        self.good_scrollbar.pack(side="right", fill="y")
    
    def create_habits_list_page(self):
        """Создаем страницу списка привычек"""
        self.habits_list_page = tk.Frame(self.main_container, bg=self.bg_color)
        
        main_frame = tk.Frame(self.habits_list_page, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Верхняя часть - форма добавления новой привычки
        form_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.RAISED, padx=20, pady=20)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            form_frame,
            text="Создать новую привычку",
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(pady=(0, 10))
        
        # Сетка для формы
        grid_frame = tk.Frame(form_frame, bg="white")
        grid_frame.pack(pady=10)
        
        # Название привычки
        tk.Label(grid_frame, text="Название:", bg="white", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=8)
        self.new_habit_name = tk.Entry(grid_frame, font=("Arial", 11), width=30)
        self.new_habit_name.grid(row=0, column=1, pady=8, padx=(10, 20))
        
        # Тип привычки
        tk.Label(grid_frame, text="Тип:", bg="white", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=8)
        
        self.habit_type_var = tk.IntVar(value=1)
        type_frame = tk.Frame(grid_frame, bg="white")
        type_frame.grid(row=1, column=1, sticky="w", pady=8, padx=(10, 0))
        
        tk.Radiobutton(type_frame, text="Хорошая", variable=self.habit_type_var, 
                      value=1, bg="white", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Radiobutton(type_frame, text="Плохая", variable=self.habit_type_var, 
                      value=0, bg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Количество звездочек
        tk.Label(grid_frame, text="Звездочек:", bg="white", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=8)
        
        self.stars_var = tk.IntVar(value=1)
        self.stars_spinbox = tk.Spinbox(grid_frame, from_=1, to=10, textvariable=self.stars_var, 
                                  font=("Arial", 11), width=10)
        self.stars_spinbox.grid(row=2, column=1, sticky="w", pady=8, padx=(10, 20))
        
        # Кнопка создания
        create_btn = tk.Button(
            form_frame,
            text="Создать привычку",
            bg=self.good_color,
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            command=self.create_habit
        )
        create_btn.pack(pady=10, fill=tk.X)
        
        # Нижняя часть - список привычек
        list_frame = tk.Frame(main_frame, bg=self.bg_color)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            list_frame,
            text="Список всех привычек",
            font=("Arial", 16, "bold"),
            bg=self.bg_color
        ).pack(pady=(0, 10))
        
        # Таблица привычек с кнопками удаления
        columns = ("ID", "Название", "Тип", "Звездочек", "Действия")
        self.habits_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.habits_tree.heading(col, text=col)
            self.habits_tree.column(col, width=80)
        
        self.habits_tree.column("Название", width=200)
        self.habits_tree.column("Действия", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.habits_tree.yview)
        self.habits_tree.configure(yscroll=scrollbar.set)
        
        self.habits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка удаления выбранной привычки
        delete_btn = tk.Button(
            list_frame,
            text="Удалить выбранную привычку",
            bg=self.bad_color,
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            command=self.delete_selected_habit
        )
        delete_btn.pack(pady=10, fill=tk.X)
    
    def create_calendar_page(self):
        """Создаем страницу календаря"""
        self.calendar_page = tk.Frame(self.main_container, bg=self.bg_color)
        
        frame = tk.Frame(self.calendar_page, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            frame,
            text="Календарь привычек",
            font=("Arial", 18, "bold"),
            bg=self.bg_color
        ).pack(pady=(0, 20))
        
        # Верхняя панель с навигацией по месяцам
        nav_frame = tk.Frame(frame, bg=self.bg_color)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.current_date = date.today()
        
        # Кнопки навигации
        self.prev_btn = tk.Button(
            nav_frame,
            text="◀ Предыдущий месяц",
            command=self.prev_month,
            bg=self.sidebar_color,
            fg="white",
            font=("Arial", 11),
            padx=15,
            pady=8
        )
        self.prev_btn.pack(side=tk.LEFT)
        
        self.month_year_label = tk.Label(
            nav_frame,
            text=self.current_date.strftime("%B %Y").upper(),
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        self.month_year_label.pack(side=tk.LEFT, expand=True)
        
        self.next_btn = tk.Button(
            nav_frame,
            text="Следующий месяц ▶",
            command=self.next_month,
            bg=self.sidebar_color,
            fg="white",
            font=("Arial", 11),
            padx=15,
            pady=8
        )
        self.next_btn.pack(side=tk.RIGHT)
        
        # Фрейм для календаря
        self.cal_frame_container = tk.Frame(frame, bg=self.bg_color)
        self.cal_frame_container.pack(fill=tk.BOTH, expand=True)
        
        # Создаем календарь
        self.create_calendar_grid()
    
    def create_calendar_grid(self):
        """Создаем сетку календаря"""
        # Очищаем старую сетку
        for widget in self.cal_frame_container.winfo_children():
            widget.destroy()
        
        # Создаем основной контейнер для календаря
        calendar_container = tk.Frame(self.cal_frame_container, bg="white", bd=2, relief=tk.RAISED)
        calendar_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Заголовки дней недели
        days = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ВОСКРЕСЕНЬЕ"]
        
        # Создаем сетку 7x8 (7 дней недели + заголовки)
        for col in range(7):
            calendar_container.columnconfigure(col, weight=1, uniform="calendar_col")
        
        for row in range(8):  # 0 - заголовки, 1-7 - недели
            calendar_container.rowconfigure(row, weight=1, uniform="calendar_row")
        
        # Заголовки дней недели
        for i, day in enumerate(days):
            day_label = tk.Label(
                calendar_container,
                text=day,
                font=("Arial", 9, "bold"),
                bg="#e0e0e0",
                fg="#333333",
                height=2,
                relief=tk.RAISED,
                bd=1
            )
            day_label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
        
        # Получаем первый и последний день месяца
        year = self.current_date.year
        month = self.current_date.month
        
        # Первый день месяца
        first_day = date(year, month, 1)
        # День недели первого дня (0 = понедельник, 6 = воскресенье)
        first_day_weekday = first_day.weekday()
        
        # Количество дней в месяце
        days_in_month = calendar.monthrange(year, month)[1]
        
        # Загружаем привычки за месяц с временем
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        
        # Получаем все логи за месяц
        start_date = date(year, month, 1)
        end_date = date(year, month, days_in_month)
        
        cursor.execute('''
            SELECT hl.date, hl.time, h.name, h.is_good
            FROM habit_logs hl
            JOIN habits h ON hl.habit_id = h.id
            WHERE date(hl.date) BETWEEN date(?) AND date(?)
            ORDER BY hl.date, hl.time DESC
        ''', (start_date, end_date))
        
        month_logs = cursor.fetchall()
        conn.close()
        
        # Группируем логи по дням
        logs_by_day = {}
        for log in month_logs:
            log_date = datetime.strptime(log[0], '%Y-%m-%d').date()
            day = log_date.day
            if day not in logs_by_day:
                logs_by_day[day] = []
            logs_by_day[day].append(log)
        
        # Заполняем календарь
        day_num = 1
        start_row = 1  # Начинаем с первой строки после заголовков
        max_weeks = 6  # Максимум 6 недель в месяце
        
        for week in range(max_weeks):
            for weekday in range(7):
                current_row = start_row + week
                
                if current_row >= 8:  # Не превышаем количество строк
                    break
                    
                if (week == 0 and weekday < first_day_weekday) or day_num > days_in_month:
                    # Пустая ячейка
                    cell = tk.Frame(
                        calendar_container,
                        bg="#f9f9f9",
                        relief=tk.SUNKEN,
                        bd=1
                    )
                    cell.grid(row=current_row, column=weekday, sticky="nsew", padx=1, pady=1)
                else:
                    # Ячейка с днем
                    cell = tk.Frame(
                        calendar_container,
                        bg="white",
                        relief=tk.RAISED,
                        bd=1
                    )
                    cell.grid(row=current_row, column=weekday, sticky="nsew", padx=1, pady=1)
                    
                    # Настраиваем сетку внутри ячейки
                    cell.rowconfigure(0, weight=0)  # Для номера дня
                    cell.rowconfigure(1, weight=1)  # Для списка привычек
                    
                    # Номер дня
                    day_bg = "#e8f4fd" if day_num == date.today().day and month == date.today().month and year == date.today().year else "white"
                    
                    day_header = tk.Frame(cell, bg=day_bg, height=25)
                    day_header.grid(row=0, column=0, sticky="ew")
                    day_header.grid_propagate(False)
                    
                    day_label = tk.Label(
                        day_header,
                        text=str(day_num),
                        font=("Arial", 10, "bold"),
                        bg=day_bg,
                        fg="#2c3e50"
                    )
                    day_label.pack(pady=3)
                    
                    # Привычки за этот день
                    if day_num in logs_by_day:
                        # Создаем кадр для привычек с прокруткой
                        habits_frame = tk.Frame(cell, bg="white")
                        habits_frame.grid(row=1, column=0, sticky="nsew")
                        
                        # Кастомный список с прокруткой
                        habits_canvas = tk.Canvas(habits_frame, bg="white", highlightthickness=0, height=100)
                        habits_scrollbar = tk.Scrollbar(habits_frame, orient="vertical", command=habits_canvas.yview)
                        habits_scrollable_frame = tk.Frame(habits_canvas, bg="white")
                        
                        habits_scrollable_frame.bind(
                            "<Configure>",
                            lambda e, canvas=habits_canvas: canvas.configure(scrollregion=canvas.bbox("all"))
                        )
                        
                        habits_canvas.create_window((0, 0), window=habits_scrollable_frame, anchor="nw")
                        habits_canvas.configure(yscrollcommand=habits_scrollbar.set)
                        
                        habits_canvas.pack(side="left", fill="both", expand=True)
                        habits_scrollbar.pack(side="right", fill="y")
                        
                        # Добавляем привычки (сортировка по времени, позже - выше)
                        logs = logs_by_day[day_num]
                        for log in logs:
                            log_date, log_time, habit_name, is_good = log
                            
                            # Форматируем время
                            try:
                                time_obj = datetime.strptime(log_time, '%H:%M')
                                time_str = time_obj.strftime('%H:%M')
                            except:
                                time_str = log_time
                            
                            habit_frame = tk.Frame(habits_scrollable_frame, bg="white")
                            habit_frame.pack(fill=tk.X, pady=2)
                            
                            # Цвет в зависимости от типа привычки
                            habit_bg = "#d5f4e6" if is_good == 1 else "#fadbd8"
                            habit_fg = "#27ae60" if is_good == 1 else "#e74c3c"
                            
                            habit_label = tk.Label(
                                habit_frame,
                                text=f"{time_str} - {habit_name}",
                                font=("Arial", 8),
                                bg=habit_bg,
                                fg=habit_fg,
                                anchor="w",
                                padx=5,
                                pady=2,
                                relief=tk.RAISED,
                                bd=1
                            )
                            habit_label.pack(fill=tk.X)
                    
                    day_num += 1
        
        # Если остались пустые строки, заполняем их
        for row in range(current_row + 1, 8):
            for col in range(7):
                empty_cell = tk.Frame(
                    calendar_container,
                    bg="#f9f9f9",
                    relief=tk.SUNKEN,
                    bd=1
                )
                empty_cell.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
    
    def create_notes_page(self):
        """Создаем страницу заметок"""
        self.notes_page = tk.Frame(self.main_container, bg=self.bg_color)
        
        frame = tk.Frame(self.notes_page, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            frame,
            text="Заметки",
            font=("Arial", 18, "bold"),
            bg=self.bg_color
        ).pack(pady=(0, 20))
        
        # Текстовое поле для заметок
        self.notes_text = tk.Text(frame, height=20, font=("Arial", 12))
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка сохранения
        self.save_notes_btn = tk.Button(
            frame,
            text="Сохранить заметки",
            bg=self.good_color,
            fg="white",
            font=("Arial", 12, "bold"),
            height=2,
            command=self.save_notes
        )
        self.save_notes_btn.pack(pady=10, fill=tk.X)
    
    def hide_all_pages(self):
        """Скрывает все страницы"""
        if hasattr(self, 'main_page'):
            self.main_page.pack_forget()
        if hasattr(self, 'habits_list_page'):
            self.habits_list_page.pack_forget()
        if hasattr(self, 'calendar_page'):
            self.calendar_page.pack_forget()
        if hasattr(self, 'notes_page'):
            self.notes_page.pack_forget()
    
    def show_main(self):
        """Показать главную страницу"""
        self.hide_all_pages()
        self.current_page = "main"
        self.main_page.pack(fill=tk.BOTH, expand=True)
        self.update_main_page()
    
    def show_habits_list(self):
        """Показать страницу списка привычек"""
        self.hide_all_pages()
        self.current_page = "habits_list"
        self.habits_list_page.pack(fill=tk.BOTH, expand=True)
        self.update_habits_table()
    
    def show_calendar(self):
        """Показать страницу календаря"""
        self.hide_all_pages()
        self.current_page = "calendar"
        self.calendar_page.pack(fill=tk.BOTH, expand=True)
        self.update_calendar()
    
    def show_notes(self):
        """Показать страницу заметок"""
        self.hide_all_pages()
        self.current_page = "notes"
        self.notes_page.pack(fill=tk.BOTH, expand=True)
        self.load_notes()
    
    def update_main_page(self):
        """Обновить главную страницу"""
        # Обновляем комбобокс с привычками
        self.update_habits_combo()
        
        # Обновляем звездочки
        self.load_stars()
        self.stars_label.config(text=f"★ {self.total_stars}")
        
        # Обновляем списки привычек
        self.update_habit_lists()
    
    def init_db(self):
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        
        # Таблица привычек
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                is_good INTEGER DEFAULT 1,
                stars INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица логов привычек (выполненные привычки)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
            )
        ''')
        
        # Таблица заметок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                content TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Добавляем тестовые данные, если таблица привычек пуста
        cursor.execute('SELECT COUNT(*) FROM habits')
        if cursor.fetchone()[0] == 0:
            test_habits = [
                ('Утренняя зарядка', 1, 2),
                ('Чтение книги', 1, 1),
                ('Медитация', 1, 1),
                ('Курение', 0, 3),
                ('Поздний отход ко сну', 0, 2),
                ('Пить воду 2л', 1, 1)
            ]
            cursor.executemany('INSERT INTO habits (name, is_good, stars) VALUES (?, ?, ?)', test_habits)
            
            # Добавляем тестовые логи с временем
            from datetime import date as dt_date, time as dt_time
            today = dt_date.today()
            
            test_logs = [
                (1, today.isoformat(), '08:30', 'утренняя зарядка'),
                (2, today.isoformat(), '20:00', 'чтение перед сном'),
                (3, (today - timedelta(days=1)).isoformat(), '09:15', 'медитация утром'),
                (4, (today - timedelta(days=2)).isoformat(), '14:30', 'перекур'),
                (6, (today - timedelta(days=3)).isoformat(), '12:00', 'выпил воду'),
                (1, (today - timedelta(days=4)).isoformat(), '07:45', 'зарядка'),
                (2, (today - timedelta(days=5)).isoformat(), '19:30', 'чтение'),
                (3, (today - timedelta(days=6)).isoformat(), '21:00', 'вечерняя медитация'),
                (4, (today - timedelta(days=7)).isoformat(), '11:00', 'сигарета'),
                (5, (today - timedelta(days=8)).isoformat(), '01:30', 'поздно лег'),
                (6, (today - timedelta(days=9)).isoformat(), '15:00', 'вода после обеда')
            ]
            
            # Удаляем последний элемент комментария из тестовых данных
            test_logs = [(log[0], log[1], log[2]) for log in test_logs]
            
            cursor.executemany('INSERT INTO habit_logs (habit_id, date, time) VALUES (?, ?, ?)', test_logs)
            
            # Добавляем тестовую заметку
            cursor.execute('INSERT INTO notes (date, content) VALUES (?, ?)', 
                         (today.isoformat(), 'Первая заметка. Стараюсь вести здоровый образ жизни.'))
        
        conn.commit()
        conn.close()
    
    def load_habits(self):
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM habits ORDER BY name')
        self.habits = cursor.fetchall()
        conn.close()
    
    def load_stars(self):
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        
        # Рассчитываем общее количество звезд
        cursor.execute('''
            SELECT SUM(CASE WHEN h.is_good = 1 THEN h.stars ELSE -h.stars END)
            FROM habit_logs hl
            JOIN habits h ON hl.habit_id = h.id
        ''')
        
        result = cursor.fetchone()
        self.total_stars = result[0] if result[0] is not None else 0
        conn.close()
    
    def update_habits_combo(self):
        """Обновить список в комбобоксе привычек"""
        self.load_habits()
        habit_names = [h[1] for h in self.habits]
        self.habit_combo['values'] = habit_names
        if habit_names:
            self.habit_combo.current(0)
    
    def update_habits_table(self):
        """Обновить таблицу привычек на странице списка"""
        if hasattr(self, 'habits_tree'):
            # Очищаем таблицу
            for item in self.habits_tree.get_children():
                self.habits_tree.delete(item)
            
            # Заполняем таблицу
            for habit in self.habits:
                habit_id, name, is_good, stars, created_at = habit
                habit_type = "Хорошая" if is_good == 1 else "Плохая"
                stars_display = f"+{stars}" if is_good == 1 else f"-{stars}"
                self.habits_tree.insert("", tk.END, values=(habit_id, name, habit_type, stars_display, "Удалить"))
    
    def update_habit_lists(self):
        """Обновить списки привычек на главной странице"""
        if not hasattr(self, 'bad_scrollable_frame') or not hasattr(self, 'good_scrollable_frame'):
            return
        
        # Очищаем списки
        for widget in self.bad_scrollable_frame.winfo_children():
            widget.destroy()
        
        for widget in self.good_scrollable_frame.winfo_children():
            widget.destroy()
        
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        
        # Последние плохие привычки (сортировка по дате и времени)
        cursor.execute('''
            SELECT h.name, hl.date, hl.time
            FROM habit_logs hl
            JOIN habits h ON hl.habit_id = h.id
            WHERE h.is_good = 0
            ORDER BY hl.date DESC, hl.time DESC
            LIMIT 10
        ''')
        
        bad_habits = cursor.fetchall()
        for habit in bad_habits:
            name, habit_date, habit_time = habit
            
            # Форматируем дату и время
            try:
                date_obj = datetime.strptime(habit_date, '%Y-%m-%d')
                date_str = date_obj.strftime('%d.%m.%Y')
            except:
                date_str = habit_date
            
            habit_frame = tk.Frame(self.bad_scrollable_frame, bg="#fadbd8")
            habit_frame.pack(fill=tk.X, pady=2, padx=2)
            
            habit_label = tk.Label(
                habit_frame,
                text=f"{date_str} {habit_time} - {name}",
                font=("Arial", 9),
                bg="#fadbd8",
                fg="#e74c3c",
                anchor="w",
                padx=5,
                pady=3
            )
            habit_label.pack(fill=tk.X)
        
        # Самые старые хорошие привычки (которые давно не делались)
        cursor.execute('''
            SELECT h.name, MAX(hl.date || ' ' || hl.time) as last_datetime
            FROM habits h
            LEFT JOIN habit_logs hl ON h.id = hl.habit_id
            WHERE h.is_good = 1
            GROUP BY h.id
            ORDER BY last_datetime ASC NULLS FIRST
            LIMIT 10
        ''')
        
        good_habits = cursor.fetchall()
        for habit in good_habits:
            name, last_datetime = habit
            
            if last_datetime:
                try:
                    # Разделяем дату и время
                    if ' ' in last_datetime:
                        date_part, time_part = last_datetime.split(' ', 1)
                        date_obj = datetime.strptime(date_part, '%Y-%m-%d')
                        date_str = date_obj.strftime('%d.%m.%Y')
                        datetime_str = f"{date_str} {time_part}"
                    else:
                        datetime_str = last_datetime
                except:
                    datetime_str = last_datetime
            else:
                datetime_str = "Никогда"
            
            habit_frame = tk.Frame(self.good_scrollable_frame, bg="#d5f4e6")
            habit_frame.pack(fill=tk.X, pady=2, padx=2)
            
            habit_label = tk.Label(
                habit_frame,
                text=f"{name}\nПоследний раз: {datetime_str}",
                font=("Arial", 9),
                bg="#d5f4e6",
                fg="#27ae60",
                anchor="w",
                padx=5,
                pady=3
            )
            habit_label.pack(fill=tk.X)
        
        conn.close()
        
        # Обновляем прокрутку
        self.bad_canvas.configure(scrollregion=self.bad_canvas.bbox("all"))
        self.good_canvas.configure(scrollregion=self.good_canvas.bbox("all"))
    
    def update_calendar(self):
        """Обновить календарь"""
        self.month_year_label.config(text=self.current_date.strftime("%B %Y").upper())
        self.create_calendar_grid()
    
    def load_notes(self):
        """Загрузить заметки из базы данных"""
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        cursor.execute('SELECT content FROM notes ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        self.notes_text.delete("1.0", tk.END)
        if result:
            self.notes_text.insert("1.0", result[0])
        conn.close()
    
    def add_habit_log(self):
        """Добавить выполненную привычку"""
        habit_name = self.habit_var.get()
        
        if not habit_name:
            messagebox.showwarning("Ошибка", "Выберите привычку!")
            return
        
        # Получаем дату и время
        selected_date = self.date_entry.get_date()
        date_str = selected_date.strftime('%Y-%m-%d')
        
        hour = self.hour_var.get().zfill(2)
        minute = self.minute_var.get().zfill(2)
        time_str = f"{hour}:{minute}"
        
        # Валидация времени
        try:
            datetime.strptime(time_str, '%H:%M')
        except ValueError:
            messagebox.showwarning("Ошибка", "Неверный формат времени!")
            return
        
        # Находим ID привычки
        habit_id = None
        for habit in self.habits:
            if habit[1] == habit_name:
                habit_id = habit[0]
                break
        
        if habit_id is None:
            messagebox.showwarning("Ошибка", "Привычка не найдена!")
            return
        
        # Сохраняем в базу
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO habit_logs (habit_id, date, time)
            VALUES (?, ?, ?)
        ''', (habit_id, date_str, time_str))
        conn.commit()
        conn.close()
        
        # Обновляем данные
        self.update_main_page()
        
        messagebox.showinfo("Успех", "Привычка добавлена!")
    
    def create_habit(self):
        """Создать новую привычку"""
        name = self.new_habit_name.get().strip()
        is_good = self.habit_type_var.get()
        stars = self.stars_var.get()
        
        if not name:
            messagebox.showwarning("Ошибка", "Введите название привычки!")
            return
        
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO habits (name, is_good, stars)
                VALUES (?, ?, ?)
            ''', (name, is_good, stars))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Ошибка", "Привычка с таким названием уже существует!")
            conn.close()
            return
        
        conn.close()
        
        # Обновляем данные
        self.load_habits()
        
        # Очищаем поле
        self.new_habit_name.delete(0, tk.END)
        
        # Обновляем комбобокс на главной странице
        if self.current_page == "main":
            self.update_habits_combo()
        
        messagebox.showinfo("Успех", "Привычка создана!")
    
    def delete_selected_habit(self):
        """Удалить выбранную привычку"""
        if not hasattr(self, 'habits_tree'):
            return
        
        selection = self.habits_tree.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите привычку для удаления!")
            return
        
        item = self.habits_tree.item(selection[0])
        habit_id = item['values'][0]
        habit_name = item['values'][1]
        
        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", f"Удалить привычку '{habit_name}'?"):
            return
        
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Привычка удалена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить привычку: {str(e)}")
        finally:
            conn.close()
        
        # Обновляем данные
        self.load_habits()
        self.update_habits_table()
        
        # Обновляем комбобокс на главной странице
        if self.current_page == "main":
            self.update_habits_combo()
    
    def save_notes(self):
        """Сохранить заметки"""
        content = self.notes_text.get("1.0", tk.END).strip()
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO notes (date, content) VALUES (?, ?)', 
                     (datetime.now().date().isoformat(), content))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Заметки сохранены!")
    
    def prev_month(self):
        """Перейти к предыдущему месяцу"""
        # Переход к предыдущему месяцу
        first_day = self.current_date.replace(day=1)
        self.current_date = first_day - timedelta(days=1)
        self.current_date = self.current_date.replace(day=1)
        self.update_calendar()
    
    def next_month(self):
        """Перейти к следующему месяцу"""
        # Переход к следующему месяцу
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()

def main():
    root = tk.Tk()
    app = HabitsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
