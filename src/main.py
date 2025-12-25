import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import os

class HabitsTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Habits Tracker")
        self.root.geometry("1200x700")
        
        # Инициализация БД
        self.init_db()
        
        # Переменные
        self.stars = tk.IntVar(value=self.get_total_stars())
        
        # Стили
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("Header.TLabel", font=("Arial", 16, "bold"))
        
        # Главный контейнер
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Хедер
        self.create_header()
        
        # Основное содержимое
        self.create_content()
        
        # Загрузка данных
        self.refresh_all()

    def init_db(self):
        """Инициализация базы данных"""
        self.conn = sqlite3.connect('habits.db')
        self.cursor = self.conn.cursor()
        
        # Таблица привычек
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT CHECK(type IN ('good', 'bad')) NOT NULL,
                stars INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица выполненных привычек
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS completed_habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )
        ''')
        
        # Таблица заметок
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()

    def create_header(self):
        """Создание хедера"""
        header_frame = ttk.Frame(self.main_container, height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        ttk.Label(header_frame, text="Habits Tracker", 
                 style="Header.TLabel").pack(side=tk.LEFT, padx=10)

    def create_content(self):
        """Создание основного содержимого"""
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Сайдбар
        self.create_sidebar(content_frame)
        
        # Основная область
        self.create_main_area(content_frame)

    def create_sidebar(self, parent):
        """Создание бокового меню"""
        sidebar = ttk.Frame(parent, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        ttk.Label(sidebar, text="Меню", font=("Arial", 12, "bold")).pack(pady=10)
        
        buttons = [
            ("Главная", self.show_main),
            ("Список привычек", self.show_habits_list),
            ("Заметки", self.show_notes),
            ("Календарь", self.show_calendar)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(sidebar, text=text, command=command)
            btn.pack(fill=tk.X, pady=2)

    def create_main_area(self, parent):
        """Создание основной области"""
        self.main_area = ttk.Frame(parent)
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Контейнер для страниц
        self.pages = {}
        
        # Главная страница
        self.create_main_page()
        
        # Страница списка привычек
        self.create_habits_page()
        
        # Страница заметок
        self.create_notes_page()
        
        # Страница календаря
        self.create_calendar_page()
        
        # Показать главную страницу
        self.show_main()

    def create_main_page(self):
        """Создание главной страницы"""
        page = ttk.Frame(self.main_area)
        self.pages["main"] = page
        
        # Верхняя часть - звезды
        top_frame = ttk.Frame(page)
        top_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(top_frame, text="Ваши звезды:", 
                 font=("Arial", 14)).pack(side=tk.LEFT, padx=10)
        
        star_label = ttk.Label(top_frame, textvariable=self.stars,
                              font=("Arial", 24, "bold"), foreground="gold")
        star_label.pack(side=tk.LEFT, padx=10)
        
        # Основное содержимое
        main_content = ttk.Frame(page)
        main_content.pack(fill=tk.BOTH, expand=True)
        
        # Левая колонка
        left_frame = ttk.Frame(main_content, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Форма добавления привычки
        form_frame = ttk.LabelFrame(left_frame, text="Добавить выполненную привычку")
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Привычка:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.habit_var = tk.StringVar()
        self.habit_combo = ttk.Combobox(form_frame, textvariable=self.habit_var, state="readonly")
        self.habit_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Комментарий:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.comment_entry = ttk.Entry(form_frame)
        self.comment_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Button(form_frame, text="Добавить", 
                  command=self.add_completed_habit).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Правая колонка
        right_frame = ttk.Frame(main_content, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Последние плохие привычки
        bad_frame = ttk.LabelFrame(right_frame, text="Последние плохие привычки")
        bad_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.bad_listbox = tk.Listbox(bad_frame, height=8)
        self.bad_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Самые старые хорошие привычки
        good_frame = ttk.LabelFrame(right_frame, text="Старые хорошие привычки")
        good_frame.pack(fill=tk.BOTH, expand=True)
        
        self.good_listbox = tk.Listbox(good_frame, height=8)
        self.good_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_habits_page(self):
        """Создание страницы списка привычек"""
        page = ttk.Frame(self.main_area)
        self.pages["habits"] = page
        
        # Заголовок
        ttk.Label(page, text="Список привычек", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Таблица привычек
        columns = ("#1", "#2", "#3")
        self.habits_tree = ttk.Treeview(page, columns=columns, show="headings", height=15)
        
        self.habits_tree.heading("#1", text="Название")
        self.habits_tree.heading("#2", text="Тип")
        self.habits_tree.heading("#3", text="Звезды")
        
        self.habits_tree.column("#1", width=300)
        self.habits_tree.column("#2", width=100)
        self.habits_tree.column("#3", width=100)
        
        scrollbar = ttk.Scrollbar(page, orient=tk.VERTICAL, command=self.habits_tree.yview)
        self.habits_tree.configure(yscrollcommand=scrollbar.set)
        
        self.habits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Форма добавления привычки
        form_frame = ttk.LabelFrame(page, text="Добавить новую привычку")
        form_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5)
        self.new_habit_name = ttk.Entry(form_frame, width=30)
        self.new_habit_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Тип:").grid(row=0, column=2, padx=5, pady=5)
        self.new_habit_type = ttk.Combobox(form_frame, values=["good", "bad"], state="readonly")
        self.new_habit_type.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Звезды:").grid(row=0, column=4, padx=5, pady=5)
        self.new_habit_stars = ttk.Spinbox(form_frame, from_=1, to=10, width=10)
        self.new_habit_stars.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Добавить", 
                  command=self.add_new_habit).grid(row=0, column=6, padx=10, pady=5)
        
        # Кнопка удаления
        ttk.Button(page, text="Удалить выбранную", 
                  command=self.delete_habit).pack(pady=5)

    def create_notes_page(self):
        """Создание страницы заметок"""
        page = ttk.Frame(self.main_area)
        self.pages["notes"] = page
        
        ttk.Label(page, text="Заметки", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        self.notes_text = tk.Text(page, height=20, width=60)
        scrollbar = ttk.Scrollbar(page, command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=scrollbar.set)
        
        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(page, text="Сохранить", 
                  command=self.save_note).pack(pady=10)

    def create_calendar_page(self):
        """Создание страницы календаря"""
        page = ttk.Frame(self.main_area)
        self.pages["calendar"] = page
        
        ttk.Label(page, text="Календарь привычек", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Простой текстовый календарь
        self.calendar_text = tk.Text(page, height=25, width=70)
        scrollbar = ttk.Scrollbar(page, command=self.calendar_text.yview)
        self.calendar_text.configure(yscrollcommand=scrollbar.set)
        
        self.calendar_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(page, text="Обновить", 
                  command=self.update_calendar).pack(pady=10)

    def show_main(self):
        """Показать главную страницу"""
        self.show_page("main")
        self.refresh_main_page()

    def show_habits_list(self):
        """Показать список привычек"""
        self.show_page("habits")
        self.refresh_habits_list()

    def show_notes(self):
        """Показать заметки"""
        self.show_page("notes")
        self.load_notes()

    def show_calendar(self):
        """Показать календарь"""
        self.show_page("calendar")
        self.update_calendar()

    def show_page(self, page_name):
        """Показать указанную страницу"""
        for page in self.pages.values():
            page.pack_forget()
        self.pages[page_name].pack(fill=tk.BOTH, expand=True)

    def refresh_all(self):
        """Обновить все данные"""
        self.stars.set(self.get_total_stars())
        self.refresh_main_page()
        self.refresh_habits_list()

    def refresh_main_page(self):
        """Обновить главную страницу"""
        # Обновить список привычек в комбобоксе
        self.cursor.execute("SELECT id, name FROM habits ORDER BY name")
        habits = self.cursor.fetchall()
        self.habit_combo['values'] = [h[1] for h in habits]
        
        # Обновить списки плохих и хороших привычек
        self.update_bad_habits_list()
        self.update_good_habits_list()

    def update_bad_habits_list(self):
        """Обновить список плохих привычек"""
        self.bad_listbox.delete(0, tk.END)
        
        self.cursor.execute('''
            SELECT h.name, ch.created_at 
            FROM completed_habits ch
            JOIN habits h ON ch.habit_id = h.id
            WHERE h.type = 'bad'
            ORDER BY ch.created_at DESC
            LIMIT 10
        ''')
        
        for habit, date in self.cursor.fetchall():
            self.bad_listbox.insert(tk.END, f"{habit} - {date[:10]}")

    def update_good_habits_list(self):
        """Обновить список старых хороших привычек"""
        self.good_listbox.delete(0, tk.END)
        
        self.cursor.execute('''
            SELECT h.name, MAX(ch.created_at) as last_date
            FROM habits h
            LEFT JOIN completed_habits ch ON h.id = ch.habit_id
            WHERE h.type = 'good'
            GROUP BY h.id
            ORDER BY last_date ASC NULLS FIRST
            LIMIT 10
        ''')
        
        for habit, last_date in self.cursor.fetchall():
            if last_date:
                self.good_listbox.insert(tk.END, f"{habit} - {last_date[:10]}")
            else:
                self.good_listbox.insert(tk.END, f"{habit} - никогда")

    def add_completed_habit(self):
        """Добавить выполненную привычку"""
        habit_name = self.habit_var.get()
        comment = self.comment_entry.get()
        
        if not habit_name:
            messagebox.showwarning("Внимание", "Выберите привычку!")
            return
        
        # Найти ID привычки
        self.cursor.execute("SELECT id, type, stars FROM habits WHERE name = ?", (habit_name,))
        result = self.cursor.fetchone()
        
        if result:
            habit_id, habit_type, stars_change = result
            
            # Добавить запись о выполнении
            self.cursor.execute(
                "INSERT INTO completed_habits (habit_id, comment) VALUES (?, ?)",
                (habit_id, comment)
            )
            
            # Обновить звезды
            current_stars = self.stars.get()
            if habit_type == 'good':
                self.stars.set(current_stars + stars_change)
            else:
                self.stars.set(current_stars - stars_change)
            
            self.conn.commit()
            self.comment_entry.delete(0, tk.END)
            self.refresh_main_page()
            
            messagebox.showinfo("Успех", "Привычка добавлена!")
        else:
            messagebox.showerror("Ошибка", "Привычка не найдена!")

    def refresh_habits_list(self):
        """Обновить список всех привычек"""
        for item in self.habits_tree.get_children():
            self.habits_tree.delete(item)
        
        self.cursor.execute("SELECT name, type, stars FROM habits ORDER BY type, name")
        for habit in self.cursor.fetchall():
            self.habits_tree.insert("", tk.END, values=habit)

    def add_new_habit(self):
        """Добавить новую привычку"""
        name = self.new_habit_name.get()
        habit_type = self.new_habit_type.get()
        stars = self.new_habit_stars.get()
        
        if not all([name, habit_type, stars]):
            messagebox.showwarning("Внимание", "Заполните все поля!")
            return
        
        try:
            stars_int = int(stars)
            self.cursor.execute(
                "INSERT INTO habits (name, type, stars) VALUES (?, ?, ?)",
                (name, habit_type, stars_int)
            )
            self.conn.commit()
            
            self.new_habit_name.delete(0, tk.END)
            self.new_habit_type.set('')
            self.new_habit_stars.delete(0, tk.END)
            self.new_habit_stars.insert(0, "1")
            
            self.refresh_all()
            messagebox.showinfo("Успех", "Привычка добавлена!")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число звезд!")

    def delete_habit(self):
        """Удалить выбранную привычку"""
        selection = self.habits_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите привычку для удаления!")
            return
        
        item = self.habits_tree.item(selection[0])
        habit_name = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить привычку '{habit_name}'?"):
            self.cursor.execute("DELETE FROM habits WHERE name = ?", (habit_name,))
            self.conn.commit()
            self.refresh_all()
            messagebox.showinfo("Успех", "Привычка удалена!")

    def load_notes(self):
        """Загрузить заметки"""
        self.notes_text.delete(1.0, tk.END)
        
        self.cursor.execute("SELECT content FROM notes ORDER BY created_at DESC LIMIT 1")
        result = self.cursor.fetchone()
        
        if result:
            self.notes_text.insert(1.0, result[0])

    def save_note(self):
        """Сохранить заметку"""
        content = self.notes_text.get(1.0, tk.END).strip()
        
        if content:
            self.cursor.execute(
                "INSERT INTO notes (content) VALUES (?)",
                (content,)
            )
            self.conn.commit()
            messagebox.showinfo("Успех", "Заметка сохранена!")

    def update_calendar(self):
        """Обновить календарь"""
        self.calendar_text.delete(1.0, tk.END)
        
        # Получить данные за последние 30 дней
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        self.cursor.execute('''
            SELECT h.name, ch.created_at, h.type
            FROM completed_habits ch
            JOIN habits h ON ch.habit_id = h.id
            WHERE ch.created_at >= ?
            ORDER BY ch.created_at DESC
        ''', (start_date.strftime('%Y-%m-%d'),))
        
        habits_by_date = {}
        for name, date_str, habit_type in self.cursor.fetchall():
            date = date_str[:10]
            if date not in habits_by_date:
                habits_by_date[date] = []
            
            symbol = "✓" if habit_type == "good" else "✗"
            habits_by_date[date].append(f"{symbol} {name}")
        
        # Отобразить календарь
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            self.calendar_text.insert(tk.END, f"{date_str}:\n")
            
            if date_str in habits_by_date:
                for habit in habits_by_date[date_str]:
                    self.calendar_text.insert(tk.END, f"  {habit}\n")
            else:
                self.calendar_text.insert(tk.END, "  (нет привычек)\n")
            
            self.calendar_text.insert(tk.END, "\n")
            current_date += timedelta(days=1)

    def get_total_stars(self):
        """Получить общее количество звезд"""
        self.cursor.execute('''
            SELECT 
                SUM(CASE WHEN h.type = 'good' THEN h.stars ELSE -h.stars END) as total
            FROM completed_habits ch
            JOIN habits h ON ch.habit_id = h.id
        ''')
        
        result = self.cursor.fetchone()
        return result[0] if result[0] is not None else 0

    def __del__(self):
        """Закрыть соединение с БД при удалении объекта"""
        if hasattr(self, 'conn'):
            self.conn.close()

def init_database():
    """Инициализация базы данных (отдельный скрипт)"""
    if not os.path.exists('habits.db'):
        conn = sqlite3.connect('habits.db')
        cursor = conn.cursor()
        
        # Создание таблиц (как в основном приложении)
        cursor.execute('''
            CREATE TABLE habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT CHECK(type IN ('good', 'bad')) NOT NULL,
                stars INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE completed_habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Добавление примеров привычек
        sample_habits = [
            ("Утренняя зарядка", "good", 3),
            ("Чтение книги", "good", 2),
            ("Прогулка на свежем воздухе", "good", 2),
            ("Курение", "bad", 5),
            ("Поздний отход ко сну", "bad", 3),
            ("Пропуск завтрака", "bad", 2)
        ]
        
        cursor.executemany(
            "INSERT INTO habits (name, type, stars) VALUES (?, ?, ?)",
            sample_habits
        )
        
        conn.commit()
        conn.close()
        print("База данных создана с примерами привычек!")
    else:
        print("База данных уже существует.")

if __name__ == "__main__":
    # Инициализировать БД (только если её нет)
    init_database()
    
    # Запуск приложения
    root = tk.Tk()
    app = HabitsTracker(root)
    root.mainloop()
