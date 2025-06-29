import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import ListProperty, StringProperty
from functools import partial
import random
import arabic_reshaper
from bidi.algorithm import get_display
from kivy.core.text import LabelBase

LabelBase.register(name='Vazir', fn_regular='./Vazirmatn-Regular.ttf')
kivy.resources.resource_add_path('.')


def fix_persian_text(text):
    reshaped_text = arabic_reshaper.reshape(str(text))
    bidi_text = get_display(reshaped_text)
    return bidi_text


class StyledScreen(Screen):
    background_color = ListProperty([1, 1, 1, 1])
    background_image = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.color_instruction = Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def on_pre_enter(self, *args):
        self._update_background()

    def _update_background(self):
        if self.background_image:
            self.rect.source = self.background_image
            self.color_instruction.rgba = (1, 1, 1, 1)
        else:
            self.rect.source = ''
            self.color_instruction.rgba = self.background_color

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Vazir'
        self.font_size = '20sp'
        self.size_hint_y = None
        self.height = 50
        self.background_normal = ''
        self.background_color = (1, 1, 1, 0.7)
        self.color = (0, 0, 0, 1)
        with self.canvas.before:
            Color(0.3, 0.6, 0.9, 1)
            self.border_rect = RoundedRectangle(radius=[15], size=self.size, pos=self.pos)
        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _update_graphics(self, *args):
        self.border_rect.pos = self.pos
        self.border_rect.size = self.size

GAME_STAGES = {
    1: {
        "environment": [
            {"q": "چند تا ماشین در اتاق بود؟", "a": ["چهارتا", "سه تا", "دو تا", "یکی"]},
            {"q": "کدام گزینه در اتاق نبود؟", "a": ["توپ", "سطل اشغال", "چراغ مظالعه", "جامدادی"]},
            {"q": "صندلی چند تا چرخ داشت؟", "a": ["سه تا", "چهار تا", "هیچی", "پنج تا"]}
        ]
    },
    2: {
        "environment": [
            {"q": "کدام گزینه در اتاق نبود؟", "a": ["زرافه", "توپ", "خرس", "بالن"]},
            {"q": "چند تا ساعت روی دیوار بود؟", "a": ["هیجی", "یکی","دو تا","سه تا"]},
            {"q": "رنگ میز چه رنگی بود؟", "a": ["سبز", "آبی", "زرد", "قرمز"]}
        ],
        "social": [
            {"q": "اگر کسی ناراحت است، چه کاری می‌کنی؟", "a": ["کمک می‌کنم", "نادیده می‌گیرم", "می‌خندم", "صحبت می‌کنم"]},
            {"q": "در صف صبر می‌کنی یا جلو می‌روی؟", "a": ["صبر می‌کنم", "جلو می‌روم", "داد می‌زنم", "قهر می‌کنم"]},
            {"q": "اگر دوستت چیزی شکسته، چه کار می‌کنی؟", "a": ["صحبت می‌کنم", "عصبانی می‌شوم", "فرار می‌کنم", "کمک می‌کنم"]}
        ]
    }
}


class GameScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lives = 3
        self.current_stage = 1


class MenuScreen(StyledScreen):
    background_image = 'images/menu_bg.jpg'

    def on_enter(self, *args):
        super().on_enter(*args)
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', spacing=15, padding=[40, 100, 40, 100])

        title_text = fix_persian_text("در بسته") 
        subtitle_text = fix_persian_text("(نسخه آزمایشی)")

        title = Label(text=title_text, font_name='Vazir', font_size='48sp',
                      color=(1, 1, 1, 1), halign='center', valign='middle')
        subtitle = Label(text=subtitle_text, font_name='Vazir', font_size='20sp',
                         color=(1, 1, 1, 0.9), halign='center', valign='middle')

        for lbl in (title, subtitle):
            lbl.bind(size=lambda lbl, val: setattr(lbl, 'text_size', val))

        start_btn = StyledButton(text=fix_persian_text("ورود به بازی"))
        start_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'room_screen'))

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(start_btn)
        self.add_widget(layout)


class RoomScreen(StyledScreen):
    stage_backgrounds = {
        1: 'images/room_bg_1.jpg',
        2: 'images/room_bg_2.jpg'
    }
    def on_enter(self, *args):
        bg = self.stage_backgrounds.get(self.manager.current_stage, 'images/room_bg_1.jpg')
        self.background_image = bg
        self._update_background() 

        super().on_enter(*args)
        self.clear_widgets()

        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        text_bg = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint=(1, None))
        text_bg.height = 150

        with text_bg.canvas.before:
            self.text_bg_color = Color(0.9, 0.9, 0.9, 0.8)
            self.text_bg_rect = Rectangle(pos=text_bg.pos, size=text_bg.size)

        def update_text_bg(instance, value):
            self.text_bg_rect.pos = instance.pos
            self.text_bg_rect.size = instance.size

        text_bg.bind(pos=update_text_bg, size=update_text_bg)

        title = Label(text=fix_persian_text(f"مرحله {self.manager.current_stage}"), font_name='Vazir',
                      font_size='30sp', color=(0, 0, 0, 1))
        detail_label = Label(
            text=fix_persian_text("به جزئیات زیر به مدت 8 ثانیه دقت کنید."),
            font_name='Vazir', font_size='18sp', color=(0, 0, 0, 1))

        text_bg.add_widget(title)
        text_bg.add_widget(detail_label)
        main_layout.add_widget(text_bg)
        self.add_widget(main_layout)

        Clock.schedule_once(self.go_to_questions, 8)

    def go_to_questions(self, dt):
        self.manager.current = 'question_screen'


class QuestionScreen(StyledScreen):
    background_image = 'images/question_bg.jpg'
    
    def on_enter(self, *args):
        super().on_enter(*args)
        self.clear_widgets()
        self.question_order = []
        self.question_index = 0

        stage = self.manager.current_stage
        stage_data = GAME_STAGES.get(stage, GAME_STAGES[1])

        # تعیین ترتیب سوال‌ها در هر مرحله طبق خواسته شما
        if stage == 1:
            # فقط یک سوال محیطی
            self.question_order = [("environment", random.choice(stage_data["environment"]))]
        elif stage == 2:
            # یک سوال محیطی و بعد یک سوال اجتماعی
            env_q = random.choice(stage_data["environment"])
            soc_q = random.choice(stage_data["social"])
            self.question_order = [("environment", env_q), ("social", soc_q)]
        else:
            # مراحل بالاتر هنوز آماده نیست
            self.manager.current = 'coming_soon_screen'
            return

        self.ask_question()

    def ask_question(self):
        self.clear_widgets()
        if self.question_index >= len(self.question_order):
            # پایان سوالات این مرحله، رفتن به مرحله بعد
            self.manager.current_stage += 1
            if self.manager.current_stage > len(GAME_STAGES):
                self.manager.current = 'coming_soon_screen'
            else:
                self.manager.current = 'room_screen'
            return

        q_type, question_set = self.question_order[self.question_index]
        question_text = question_set['q']
        answers = question_set['a'][:]
        correct_answer = answers[0]
        random.shuffle(answers)

        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        q_label = Label(text=fix_persian_text(question_text), font_name='Vazir', font_size='24sp', color=(1, 1, 1, 1))
        layout.add_widget(q_label)

        for answer in answers:
            btn = StyledButton(text=fix_persian_text(answer))
            btn.bind(on_press=partial(self.check_answer, answer, correct_answer))
            layout.add_widget(btn)

        self.add_widget(layout)

    def check_answer(self, selected, correct, instance):
        if selected == correct:
            self.question_index += 1
            self.ask_question()
        else:
            self.manager.lives -= 1
            self.manager.current = 'lose_screen'

            
class LoseScreen(StyledScreen):
    background_image = 'images/lose_bg.jpg'

    def on_enter(self, *args):
        super().on_enter(*args)
        self.clear_widgets()

        container = BoxLayout(orientation='vertical', padding=30, spacing=20,
                              size_hint=(None, None), size=(350, 400))
        container.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        lives_left = self.manager.lives
        if lives_left > 0:
            main_text = "پاسخ شما اشتباه بود!"
            sub_text = f"شما {lives_left} جان دیگر دارید."
            btn_text = "تلاش مجدد"
        else:
            main_text = "شما باختید!"
            sub_text = "GAME OVER"
            btn_text = "شروع مجدد"

        with container.canvas.before:
            Color(1, 1, 1, 0.3)  
            self.bg_rect = RoundedRectangle(radius=[15], size=container.size, pos=container.pos)
            Color(1, 1, 1, 1)
            self.border_rect = RoundedRectangle(radius=[15], size=container.size, pos=container.pos, width=2)

        def update_rect(instance, value):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
            self.border_rect.pos = instance.pos
            self.border_rect.size = instance.size

        container.bind(pos=update_rect, size=update_rect)

        main_label = Label(text=fix_persian_text(main_text),
                           font_name='Vazir', font_size='24sp',
                           halign='center', valign='middle',
                           color=(0, 0, 0, 1))  
        main_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        sub_label = Label(text=fix_persian_text(sub_text),
                          font_name='Vazir', font_size='18sp' if lives_left > 0 else '32sp',
                          halign='center', valign='middle',
                          color=(0, 0, 0, 1))  
        sub_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        retry_btn = StyledButton(text=fix_persian_text(btn_text))
        retry_btn.bind(on_press=self.retry_stage if lives_left > 0 else self.restart_game)

        container.add_widget(main_label)
        container.add_widget(sub_label)
        container.add_widget(retry_btn)

        self.add_widget(container)

    def retry_stage(self, instance):
        self.manager.current = 'room_screen'

    def restart_game(self, instance):
        self.manager.lives = 3
        self.manager.current_stage = 1
        self.manager.current = 'room_screen'


class ComingSoonScreen(StyledScreen):
    background_image = 'images/coming_soon_bg.jpg'

    def on_enter(self, *args):
        super().on_enter(*args)
        self.clear_widgets()

        container = BoxLayout(orientation='vertical', padding=30, spacing=20,
                              size_hint=(None, None), size=(350, 500))
        container.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        with container.canvas.before:
            Color(1, 1, 1, 0.25)  # پس‌زمینه سفید نیمه شفاف
            self.bg_rect = RoundedRectangle(radius=[20], size=container.size, pos=container.pos)
            Color(1, 1, 1, 1)  # حاشیه سفید
            self.border_rect = RoundedRectangle(radius=[20], size=container.size, pos=container.pos, width=2)

        def update_rect(instance, value):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
            self.border_rect.pos = instance.pos
            self.border_rect.size = instance.size

        container.bind(pos=update_rect, size=update_rect)


        title_label = Label(text=fix_persian_text("به زودی ..."), font_name='Vazir', font_size='40sp',
                            color=(0 , 0, 0, 1), halign='center', valign='middle')
        title_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        info_text = ("مراحل جدید به زودی\n"
                     "به بازی اضافه خواهند شد.\n"
                     "منتظر آیتم های جذاب تر باشید!")
        info_label = Label(text=fix_persian_text(info_text), font_name='Vazir', font_size='16sp',
                           color=(0 , 0, 0, 0.8), halign='center', valign='middle')
        info_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        restart_btn = StyledButton(text=fix_persian_text("شروع مجدد"))
        restart_btn.bind(on_press=self.restart_game)

        container.add_widget(title_label)
        container.add_widget(info_label)
        container.add_widget(restart_btn)

        self.add_widget(container)

    def restart_game(self, instance):
        self.manager.lives = 3
        self.manager.current_stage = 1
        self.manager.current = 'room_screen'


class ClosedDoorApp(App):
    def build(self):
        sm = GameScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(RoomScreen(name='room_screen'))
        sm.add_widget(QuestionScreen(name='question_screen'))
        sm.add_widget(LoseScreen(name='lose_screen'))
        sm.add_widget(ComingSoonScreen(name='coming_soon_screen'))
        sm.current = 'menu'
        return sm


if __name__ == '__main__':
    ClosedDoorApp().run()
