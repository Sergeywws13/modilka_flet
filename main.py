import flet as ft
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt

# Настройка SQLAlchemy
Base = declarative_base()
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)

# Модель пользователя
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(100))
    email = Column(String(100), unique=True)
    
    __table_args__ = (
        UniqueConstraint('username', name='unique_username'),
        UniqueConstraint('email', name='unique_email'),
    )

# Создание таблиц
Base.metadata.create_all(engine)

# Основное приложение
def main(page: ft.Page):
    page.title = "Эмоциональный дневник"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Элементы интерфейса
    def toggle_forms(e):
        login_form.visible = not login_form.visible
        register_form.visible = not register_form.visible
        page.update()

    # Форма входа
    login_username = ft.TextField(label="Имя пользователя", width=300)
    login_password = ft.TextField(label="Пароль", password=True, width=300)
    login_btn = ft.ElevatedButton("Войти", width=300)
    login_link = ft.TextButton("Создать аккаунт", on_click=toggle_forms)

    # Форма регистрации
    register_username = ft.TextField(label="Имя пользователя", width=300)
    register_password = ft.TextField(label="Пароль", password=True, width=300)
    register_email = ft.TextField(label="Email", width=300)
    register_btn = ft.ElevatedButton("Зарегистрироваться", width=300)
    register_link = ft.TextButton("Уже есть аккаунт", on_click=toggle_forms)

    # Обработчики событий
    def on_login(e):
        session = Session()
        try:
            user = session.query(User).filter_by(username=login_username.value).first()
            if user and bcrypt.checkpw(login_password.value.encode('utf-8'), user.password_hash.encode('utf-8')):
                page.clean()
                page.add(ft.Text(f"Добро пожаловать, {login_username.value}!"))
            else:
                show_error("Неверные учетные данные")
        finally:
            session.close()

    def on_register(e):
        session = Session()
        try:
            if session.query(User).filter_by(username=register_username.value).first():
                show_error("Пользователь уже существует")
                return

            hashed_pw = bcrypt.hashpw(register_password.value.encode('utf-8'), bcrypt.gensalt())
            new_user = User(
                username=register_username.value,
                password_hash=hashed_pw.decode('utf-8'),
                email=register_email.value
            )
            
            session.add(new_user)
            session.commit()
            show_success("Регистрация успешна!")
            toggle_forms(None)
        except Exception as ex:
            session.rollback()
            show_error(f"Ошибка: {str(ex)}")
        finally:
            session.close()

    def show_error(message):
        page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=ft.colors.RED)
        page.snack_bar.open = True
        page.update()

    def show_success(message):
        page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=ft.colors.GREEN)
        page.snack_bar.open = True
        page.update()

    # Привязка обработчиков
    login_btn.on_click = on_login
    register_btn.on_click = on_register

    # Компоновка форм
    login_form = ft.Column(
        [
            ft.Text("Вход", size=20),
            login_username,
            login_password,
            login_btn,
            login_link
        ],
        visible=True
    )

    register_form = ft.Column(
        [
            ft.Text("Регистрация", size=20),
            register_username,
            register_password,
            register_email,
            register_btn,
            register_link
        ],
        visible=False
    )

    page.add(login_form, register_form)

ft.app(target=main)
