from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.core.text import LabelBase
from kivy.metrics import dp
from functools import partial
import random
import arabic_reshaper
from bidi.algorithm import get_display
import os

# ---------------- فونت فارسی ----------------
try:
    # اول سعی می‌کنیم فونت Vazir رو ثبت کنیم
    LabelBase.register(name='Vazir', fn_regular='Vazir.ttf')
    FONT_NAME = 'Vazir'
except:
    try:
        # اگر فونت Vazir وجود نداشت، از فونت پیش‌فرض سیستم استفاده می‌کنیم
        LabelBase.register(name='PersianFont', fn_regular='arial.ttf')
        FONT_NAME = 'PersianFont'
        print("استفاده از فونت جایگزین")
    except:
        FONT_NAME = None
        print("استفاده از فونت پیش‌فرض")

def fix(text):
    """تابع برای اصلاح متن فارسی"""
    try:
        if not text:
            return ""
        # reshape متن فارسی
        reshaped_text = arabic_reshaper.reshape(text)
        # اصلاح جهت متن
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"خطا در پردازش متن: {e}")
        return text

def footer_into(layout):
    layout.add_widget(Label(text=fix("سازنده: احسان محمودی | نسخه 1.00"), font_name=FONT_NAME, font_size=14, size_hint_y=None, height=dp(30)))

# ---------------- نقش ها ----------------
ROLE_COUNTS = [
    ("شهروند ساده", 2),
    ("دکتر", 2),
    ("کارآگاه", 1),
    ("بازپرس", 1),
    ("بادیگارد", 2),
    ("پدر", 1),
    ("محقق", 1),
    ("پارانوید", 1),
    ("ردگیر", 1),
    ("تیزبین", 1),
    ("شهردار", 1),
    ("اسنایپ", 2),
    ("مافیا", 2),
    ("پدرخوانده", 1),
    ("مذاکره کننده", 1),
    ("شیاد", 1),
    ("پاک ساز", 1),
    ("هکر", 1),
    ("قاتل سریالی", 1),
    ("گرگینه", 1),
]

def build_flat_roles():
    flat = []
    for name, cnt in ROLE_COUNTS:
        for i in range(cnt):
            label = name if cnt == 1 else f"{name} {i+1}"
            flat.append(label)
    return flat

# ---------------- Main Menu ----------------
class MainMenu(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', spacing=20, padding=40)
        
        # اسپیسر برای بالا بردن محتوا
        layout.add_widget(Label(size_hint_y=0.3))
        
        welcome_label = Label(
            text=fix("به بازی رندوم خوش آمدید"), 
            font_name=FONT_NAME, 
            font_size=36, 
            size_hint_y=None, 
            height=dp(80)
        )
        layout.add_widget(welcome_label)
        
        btn_dice = Button(
            text=fix("بازی تاس"), 
            font_name=FONT_NAME, 
            font_size=20,
            size_hint_y=None, 
            height=dp(60)
        )
        btn_mafia = Button(
            text=fix("شهروند و مافیا"), 
            font_name=FONT_NAME, 
            font_size=20,
            size_hint_y=None, 
            height=dp(60)
        )
        
        btn_dice.bind(on_press=lambda _: setattr(self.manager, 'current', "dice_menu"))
        btn_mafia.bind(on_press=lambda _: setattr(self.manager, 'current', "mafia_builder"))
        
        layout.add_widget(btn_dice)
        layout.add_widget(btn_mafia)
        
        # اسپیسر برای پر کردن فضای خالی
        layout.add_widget(Label(size_hint_y=0.4))
        
        footer_into(layout)
        self.add_widget(layout)

# ---------------- Mafia Builder ----------------
class MafiaBuilder(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', spacing=8, padding=12)
        
        # عنوان با فونت و سایز مناسب
        title_label = Label(
            text=fix("انتخاب نقش ها"), 
            font_name=FONT_NAME, 
            font_size=24, 
            size_hint_y=None, 
            height=dp(50),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(title_label)
        
        subtitle_label = Label(
            text=fix("روی نقش کلیک کنید تا فعال یا غیرفعال شود"), 
            font_name=FONT_NAME, 
            font_size=16, 
            size_hint_y=None, 
            height=dp(30),
            color=(0.8, 0.8, 0.8, 1)
        )
        layout.add_widget(subtitle_label)

        # لیست نقش‌ها
        flat = build_flat_roles()
        scroll = ScrollView(size_hint=(1, 0.6))
        grid = GridLayout(cols=3, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        self.role_buttons = []
        for role_name in flat:
            # استفاده از تابع fix برای متن دکمه‌ها
            display_text = fix(role_name)
            b = Button(
                text=display_text, 
                font_name=FONT_NAME,
                font_size=14,
                size_hint_y=None, 
                height=dp(48),
                background_normal='', 
                background_color=(0.2, 0.2, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            b.bind(on_press=partial(self.toggle_role, role_name))
            grid.add_widget(b)
            self.role_buttons.append({"name": role_name, "btn": b, "selected": False})

        scroll.add_widget(grid)
        layout.add_widget(scroll)

        # بخش کاستوم
        custom_title = Label(
            text=fix("نقش های سفارشی"), 
            font_name=FONT_NAME, 
            font_size=18, 
            size_hint_y=None, 
            height=dp(40),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(custom_title)

        scroll_custom = ScrollView(size_hint=(1, 0.3))
        grid_custom = GridLayout(cols=2, spacing=8, size_hint_y=None)
        grid_custom.bind(minimum_height=grid_custom.setter("height"))
        
        self.custom_entries = []
        for i in range(6):
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=6)
            
            ti = TextInput(
                hint_text=fix(f"نقش سفارشی {i+1}"), 
                font_name=FONT_NAME,
                size_hint_y=None, 
                height=dp(44),
                background_color=(0.1, 0.1, 0.1, 1),
                foreground_color=(1, 1, 1, 1)
            )
            
            tb = ToggleButton(
                text=fix("انتخاب"), 
                font_name=FONT_NAME,
                size_hint_x=None, 
                width=dp(100)
            )
            
            box.add_widget(ti)
            box.add_widget(tb)
            grid_custom.add_widget(box)
            self.custom_entries.append({"ti": ti, "tb": tb})

        scroll_custom.add_widget(grid_custom)
        layout.add_widget(scroll_custom)

        # دکمه‌های پایین
        btn_start = Button(
            text=fix("شروع بازی"), 
            font_name=FONT_NAME, 
            font_size=18,
            size_hint_y=None, 
            height=dp(50),
            background_color=(0, 0.5, 0, 1)
        )
        btn_start.bind(on_press=self.start_mafia_game)
        layout.add_widget(btn_start)

        btn_back = Button(
            text=fix("بازگشت به منوی اصلی"), 
            font_name=FONT_NAME,
            size_hint_y=None, 
            height=dp(44)
        )
        btn_back.bind(on_press=self.back_to_main)
        layout.add_widget(btn_back)

        footer_into(layout)
        self.add_widget(layout)

    def toggle_role(self, role_name, instance):
        for entry in self.role_buttons:
            if entry["name"] == role_name and entry["btn"] is instance:
                entry["selected"] = not entry["selected"]
                if entry["selected"]:
                    entry["btn"].background_color = (0, 0.5, 0, 1) # سبز
                else:
                    entry["btn"].background_color = (0.2, 0.2, 0.2, 1) # خاکستری تیره
                break

    def start_mafia_game(self, _):
        selected = []
        for entry in self.role_buttons:
            if entry["selected"]:
                selected.append(entry["name"])
        
        for c in self.custom_entries:
            text = c["ti"].text.strip()
            if text and c["tb"].state == "down":
                selected.append(text)
        
        if not selected:
            # اگر هیچ نقشی انتخاب نشده، پیام نمایش بده
            print(fix("لطفا حداقل یک نقش انتخاب کنید"))
            return
        
        print(fix(f"تعداد نقش های انتخاب شده: {len(selected)}"))
        self.manager.get_screen("mafia_game").setup_players(selected)
        self.manager.current = "mafia_game"

    def back_to_main(self, _):
        self.clear_widgets()
        self.manager.current = "main"

# ---------------- Mafia Game ----------------
class MafiaGame(Screen):
    def _build_empty(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', spacing=12, padding=12)
        
        self.label = Label(
            text=fix("برای شروع روی دکمه نمایش بعدی کلیک کنید"), 
            font_name=FONT_NAME, 
            font_size=24, 
            size_hint_y=None, 
            height=dp(100),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.label)
        
        self.btn_next = Button(
            text=fix("نمایش نقش بعدی"), 
            font_name=FONT_NAME,
            size_hint_y=None, 
            height=dp(50),
            background_color=(0, 0.3, 0.6, 1)
        )
        self.btn_next.bind(on_press=self.next_player)
        layout.add_widget(self.btn_next)
        
        self.btn_restart = Button(
            text=fix("شروع مجدد"), 
            font_name=FONT_NAME,
            size_hint_y=None, 
            height=dp(44)
        )
        self.btn_restart.bind(on_press=self.restart)
        layout.add_widget(self.btn_restart)
        
        self.btn_back = Button(
            text=fix("بازگشت به انتخاب نقش"), 
            font_name=FONT_NAME,
            size_hint_y=None, 
            height=dp(44)
        )
        self.btn_back.bind(on_press=self.back_to_builder)
        layout.add_widget(self.btn_back)
        
        footer_into(layout)
        self.add_widget(layout)
        self.btn_restart.disabled = True

    def setup_players(self, players):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', spacing=12, padding=12)
        
        self.roles_original = players.copy()
        self.roles_remaining = players.copy()
        
        # نمایش تعداد نقش‌های انتخاب شده
        count_label = Label(
            text=fix(f"تعداد نقش ها: {len(players)}"), 
            font_name=FONT_NAME, 
            font_size=20, 
            size_hint_y=None, 
            height=dp(40),
            color=(0.8, 0.8, 0.8, 1)
        )
        layout.add_widget(count_label)
        
        self.label = Label(
            text=fix("برای نمایش اولین نقش روی دکمه زیر کلیک کنید"), 
            font_name=FONT_NAME, 
            font_size=26, 
            size_hint_y=None, 
            height=dp(100),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.label)
        
        self.btn_next = Button(
            text=fix("نمایش نقش بعدی"), 
            font_name=FONT_NAME,
            size_hint_y=None, 
            height=dp(50),
            background_color=(0, 0.3, 0.6, 1)
        )
        self.btn_next.bind(on_press=self.next_player)
        layout.add_widget(self.btn_next)
        
        self.btn_restart = Button(
            text=fix("شروع مجدد بازی"), 
            font_name=FONT_NAME,
            size_hint_y=None, 
            height=dp(44)
        )
        self.btn_restart.bind(on_press=self.restart)
        layout.add_widget(self.btn_restart)
        
        self.btn_back = Button(
            text=fix("بازگشت به انتخاب نقش"), 
            font_name=FONT_NAME,
            size_hint_y=None, 
            height=dp(44)
        )
        self.btn_back.bind(on_press=self.back_to_builder)
        layout.add_widget(self.btn_back)
        
        footer_into(layout)
        self.add_widget(layout)
        self.btn_restart.disabled = True

    def next_player(self, _):
        if not hasattr(self, "roles_remaining") or not self.roles_remaining:
            return
            
        if self.roles_remaining:
            sel = random.choice(self.roles_remaining)
            self.roles_remaining.remove(sel)
            
            # استفاده از تابع fix برای نمایش صحیح فارسی
            display_text = fix(f"نقش نمایش داده شده: {sel}")
            self.label.text = display_text
            
            if not self.roles_remaining:
                self.btn_next.disabled = True
                self.btn_restart.disabled = False
                self.label.text = fix("همه نقش ها نمایش داده شدند!")

    def restart(self, _):
        if hasattr(self, "roles_original"):
            self.roles_remaining = self.roles_original.copy()
            self.label.text = fix("بازی از نو شروع شد. برای نمایش نقش ها کلیک کنید.")
            self.btn_next.disabled = False
            self.btn_restart.disabled = True

    def back_to_builder(self, _):
        self.clear_widgets()
        self.manager.current = "mafia_builder"

    def on_pre_enter(self):
        if not self.children:
            self._build_empty()

# ---------------- بقیه کلاس‌ها (DiceMenu, DiceRoll, etc.) ----------------
# این بخش‌ها بدون تغییر می‌مانند یا می‌تونید از نسخه قبلی استفاده کنید

class DiceMenu(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        layout.add_widget(Label(text=fix("انتخاب حالت تاس"), font_name=FONT_NAME, font_size=30, size_hint_y=None, height=dp(48)))
        btn_classic = Button(text=fix("کلاسیک"), font_name=FONT_NAME, size_hint_y=None, height=dp(44))
        btn_multi = Button(text=fix("چند نفره"), font_name=FONT_NAME, size_hint_y=None, height=dp(44))
        btn_classic.bind(on_press=lambda _: (self.manager.get_screen("dice_roll").setup_mode("کلاسیک"), setattr(self.manager, 'current', "dice_roll")))
        btn_multi.bind(on_press=lambda _: setattr(self.manager, 'current', "dice_multi_menu"))
        layout.add_widget(btn_classic)
        layout.add_widget(btn_multi)
        btn_back = Button(text=fix("بازگشت به منو اصلی"), font_name=FONT_NAME, size_hint_y=None, height=dp(44))
        btn_back.bind(on_press=lambda _: setattr(self.manager, 'current', "main"))
        layout.add_widget(btn_back)
        footer_into(layout)
        self.add_widget(layout)

class DiceRoll(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        self.label = Label(text="", font_name=FONT_NAME, font_size=60, size_hint_y=None, height=dp(120))
        layout.add_widget(self.label)
        btn_roll = Button(text=fix("ریختن تاس"), font_name=FONT_NAME, size_hint_y=None, height=dp(48))
        btn_roll.bind(on_press=self.roll_dice)
        layout.add_widget(btn_roll)
        btn_back = Button(text=fix("بازگشت"), font_name=FONT_NAME, size_hint_y=None, height=dp(44))
        btn_back.bind(on_press=self.back_to_menu)
        layout.add_widget(btn_back)
        footer_into(layout)
        self.add_widget(layout)

    def setup_mode(self, mode):
        self.mode = mode

    def roll_dice(self, _):
        n = random.randint(1, 6)
        self.label.text = str(n)

    def back_to_menu(self, _):
        self.manager.current = "dice_menu"

# ---------------- App ----------------
class RandomApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="main"))
        sm.add_widget(DiceMenu(name="dice_menu"))
        sm.add_widget(DiceRoll(name="dice_roll"))
        sm.add_widget(MafiaBuilder(name="mafia_builder"))
        sm.add_widget(MafiaGame(name="mafia_game"))
        return sm

if __name__ == "__main__":
    RandomApp().run()