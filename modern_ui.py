"""
واجهة المستخدم المحدثة لتطبيق عداد الكومبلكس شراكة
Modern UI Components for CC Counter App - Fixed Version
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse, Triangle
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.utils import platform

import os

# مكتبات دعم النص العربي
import arabic_reshaper
from bidi.algorithm import get_display

from app_config import COLORS, SUIT_NAMES, POINTS

# مسار الخط العربي
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansArabic.ttf')
ARABIC_FONT = 'Arabic' if os.path.exists(FONT_PATH) else None


def arabic(text):
    """تحويل النص العربي ليظهر بشكل صحيح"""
    if not text:
        return text
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except:
        return str(text)


# ==================== المكونات الأساسية ====================

class ArabicTextInput(TextInput):
    """حقل إدخال مخصص للعربية - لا يعكس النص"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('halign', 'right')
        kwargs.setdefault('font_size', dp(16))
        if ARABIC_FONT:
            kwargs.setdefault('font_name', ARABIC_FONT)
        super().__init__(**kwargs)
    
    def insert_text(self, substring, from_undo=False):
        """إدخال النص بدون تحويل"""
        return super().insert_text(substring, from_undo=from_undo)
    
    def get_text(self):
        """الحصول على النص الأصلي"""
        return self.text


class ArabicLabel(Label):
    """Label مع دعم كامل للعربية"""
    
    def __init__(self, **kwargs):
        if 'text' in kwargs:
            kwargs['text'] = arabic(str(kwargs['text']))
        kwargs.setdefault('halign', 'center')
        kwargs.setdefault('valign', 'middle')
        kwargs.setdefault('font_size', dp(16))
        kwargs.setdefault('color', COLORS['text'])
        if ARABIC_FONT:
            kwargs.setdefault('font_name', ARABIC_FONT)
        super().__init__(**kwargs)
        self.bind(size=self._update)
    
    def _update(self, *args):
        self.text_size = self.size
    
    def set_text(self, text):
        self.text = arabic(str(text))


class ArabicButton(Button):
    """زر مع دعم كامل للعربية"""
    
    def __init__(self, bg_color=None, **kwargs):
        if 'text' in kwargs:
            kwargs['text'] = arabic(str(kwargs['text']))
        kwargs.setdefault('font_size', dp(16))
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(50))
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        if ARABIC_FONT:
            kwargs.setdefault('font_name', ARABIC_FONT)
        super().__init__(**kwargs)
        
        self.bg_color = bg_color or COLORS['primary']
        self._draw_bg()
        self.bind(pos=self._draw_bg, size=self._draw_bg)
    
    def _draw_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])


class CardWidget(ToggleButton):
    """بطاقة مرسومة يدوياً بدون Unicode"""
    
    suit = StringProperty('heart')
    rank = StringProperty('Q')
    
    def __init__(self, suit='heart', rank='Q', **kwargs):
        super().__init__(**kwargs)
        self.suit = suit
        self.rank = rank
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.size_hint = (None, None)
        self.size = (dp(70), dp(100))
        self.text = ''
        
        self.bind(state=self._on_state)
        self.bind(pos=self._draw, size=self._draw)
        Clock.schedule_once(lambda dt: self._draw(), 0)
    
    def _on_state(self, *args):
        self._draw()
    
    def _draw(self, *args):
        self.canvas.before.clear()
        self.canvas.after.clear()
        
        x, y = self.pos
        w, h = self.size
        
        with self.canvas.before:
            # خلفية البطاقة
            if self.state == 'down':
                Color(0.15, 0.65, 0.3, 1)  # أخضر عند الاختيار
            else:
                Color(1, 1, 1, 1)  # أبيض
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
            
            # إطار
            if self.state == 'down':
                Color(0.1, 0.5, 0.2, 1)
            else:
                Color(0.4, 0.4, 0.4, 1)
            Line(rounded_rectangle=(x, y, w, h, dp(8)), width=2)
        
        with self.canvas.after:
            # لون الرمز
            if self.suit in ['heart', 'diamond']:
                Color(0.9, 0.15, 0.15, 1)  # أحمر
            else:
                Color(0.15, 0.15, 0.15, 1)  # أسود
            
            # رسم الرمز في المنتصف
            cx = x + w / 2
            cy = y + h * 0.55
            sz = min(w, h) * 0.32
            
            if self.suit == 'heart':
                self._draw_heart(cx, cy, sz)
            elif self.suit == 'diamond':
                self._draw_diamond(cx, cy, sz)
            elif self.suit == 'spade':
                self._draw_spade(cx, cy, sz)
            elif self.suit == 'club':
                self._draw_club(cx, cy, sz)
    
    def _draw_heart(self, cx, cy, size):
        """رسم شكل قلب محسن"""
        r = size * 0.45
        # الدائرتين العلويتين
        Ellipse(pos=(cx - size*0.42 - r/2, cy + r*0.1), size=(r, r))
        Ellipse(pos=(cx + size*0.42 - r/2, cy + r*0.1), size=(r, r))
        # المثلث السفلي
        Triangle(points=[
            cx - size*0.85, cy + r*0.5,
            cx + size*0.85, cy + r*0.5,
            cx, cy - size*0.95
        ])
    
    def _draw_diamond(self, cx, cy, size):
        """رسم شكل ماسة"""
        # مثلثين
        Triangle(points=[
            cx, cy + size*0.9,
            cx - size*0.55, cy,
            cx + size*0.55, cy
        ])
        Triangle(points=[
            cx, cy - size*0.9,
            cx - size*0.55, cy,
            cx + size*0.55, cy
        ])
    
    def _draw_spade(self, cx, cy, size):
        """رسم شكل بستوني محسن"""
        r = size * 0.4
        # الدائرتين الجانبيتين
        Ellipse(pos=(cx - size*0.4 - r/2, cy - r*0.4), size=(r, r))
        Ellipse(pos=(cx + size*0.4 - r/2, cy - r*0.4), size=(r, r))
        # المثلث العلوي
        Triangle(points=[
            cx - size*0.8, cy,
            cx + size*0.8, cy,
            cx, cy + size*0.95
        ])
        # الساق
        Triangle(points=[
            cx - size*0.25, cy - size*0.3,
            cx + size*0.25, cy - size*0.3,
            cx, cy - size*0.95
        ])
    
    def _draw_club(self, cx, cy, size):
        """رسم شكل سباتي/نادي محسن"""
        r = size * 0.38
        # ثلاث دوائر
        Ellipse(pos=(cx - r/2, cy + r*0.35), size=(r, r))  # علوي
        Ellipse(pos=(cx - r/2 - size*0.42, cy - r*0.35), size=(r, r))  # يسار
        Ellipse(pos=(cx - r/2 + size*0.42, cy - r*0.35), size=(r, r))  # يمين
        # الساق
        Triangle(points=[
            cx - size*0.2, cy - size*0.2,
            cx + size*0.2, cy - size*0.2,
            cx, cy - size*0.95
        ])


class CardWithRank(BoxLayout):
    """بطاقة مع رتبة (Q أو K)"""
    
    def __init__(self, suit='heart', rank='Q', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (dp(75), dp(115))
        self.spacing = 0
        
        self.suit = suit
        self.rank = rank
        self.selected = False
        
        self._card = CardWidget(suit=suit, rank=rank)
        self._card.size = (dp(70), dp(85))
        self._card.bind(state=self._on_card_state)
        
        # رسم الرتبة أسفل البطاقة
        if suit in ['heart', 'diamond']:
            color = (0.85, 0.1, 0.1, 1)
        else:
            color = (0.1, 0.1, 0.1, 1)
        
        self._rank_lbl = Label(
            text=rank,
            font_size=dp(22),
            bold=True,
            color=color,
            size_hint_y=None,
            height=dp(28)
        )
        
        self.add_widget(self._card)
        self.add_widget(self._rank_lbl)
    
    def _on_card_state(self, inst, val):
        self.selected = (val == 'down')
        if self.selected:
            self._rank_lbl.color = (0.2, 0.7, 0.3, 1)
        elif self.suit in ['heart', 'diamond']:
            self._rank_lbl.color = (0.85, 0.1, 0.1, 1)
        else:
            self._rank_lbl.color = (0.1, 0.1, 0.1, 1)
    
    @property
    def state(self):
        return self._card.state
    
    @state.setter
    def state(self, val):
        self._card.state = val


class NumberSelector(BoxLayout):
    """عنصر اختيار الأرقام"""
    
    value = NumericProperty(0)
    min_val = NumericProperty(0)
    max_val = NumericProperty(13)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.spacing = dp(10)
        
        # زر النقصان
        minus = ArabicButton(text="-", size_hint_x=0.25, bg_color=COLORS['danger'])
        minus.bind(on_press=self._decrease)
        self.add_widget(minus)
        
        # القيمة
        self.val_label = Label(
            text="0",
            font_size=dp(32),
            color=COLORS['text'],
            size_hint_x=0.5
        )
        self.add_widget(self.val_label)
        
        # زر الزيادة
        plus = ArabicButton(text="+", size_hint_x=0.25, bg_color=COLORS['success'])
        plus.bind(on_press=self._increase)
        self.add_widget(plus)
        
        self.bind(value=self._update_label)
    
    def _update_label(self, *args):
        self.val_label.text = str(int(self.value))
    
    def _increase(self, *args):
        if self.value < self.max_val:
            self.value += 1
    
    def _decrease(self, *args):
        if self.value > self.min_val:
            self.value -= 1


class TeamScoreBox(BoxLayout):
    """صندوق نتيجة الفريق"""
    
    def __init__(self, name="", score=0, color=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(90)
        self.padding = dp(8)
        
        self._bg_color = color or COLORS['card']
        self._draw_bg()
        self.bind(pos=self._draw_bg, size=self._draw_bg)
        
        # الاسم
        self.name_lbl = ArabicLabel(
            text=name,
            font_size=dp(14),
            color=COLORS['text_secondary'],
            size_hint_y=0.35
        )
        self.add_widget(self.name_lbl)
        
        # النتيجة
        self.score_lbl = Label(
            text=str(score),
            font_size=dp(32),
            color=COLORS['text'],
            bold=True,
            size_hint_y=0.65
        )
        self.add_widget(self.score_lbl)
    
    def _draw_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
    
    def set_name(self, name):
        self.name_lbl.set_text(name)
    
    def set_score(self, score):
        self.score_lbl.text = str(score)


# ==================== الشاشات ====================

class WelcomeScreen(Screen):
    """شاشة الترحيب"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'welcome'
        Clock.schedule_once(lambda dt: self._build(), 0)
    
    def _build(self):
        with self.canvas.before:
            Color(*COLORS['background'])
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(15))
        
        # العنوان مع رموز البطاقات
        title_box = BoxLayout(orientation='vertical', size_hint_y=0.3)
        
        # رموز البطاقات المرسومة
        cards_row = BoxLayout(size_hint_y=0.55, spacing=dp(8))
        cards_row.add_widget(Widget(size_hint_x=0.15))
        for suit in ['spade', 'heart', 'diamond', 'club']:
            card = CardWidget(suit=suit, rank='')
            card.size = (dp(50), dp(65))
            card.disabled = True
            cards_row.add_widget(card)
        cards_row.add_widget(Widget(size_hint_x=0.15))
        title_box.add_widget(cards_row)
        
        title = ArabicLabel(
            text="عداد الكومبلكس شراكة",
            font_size=dp(22),
            size_hint_y=0.45
        )
        title_box.add_widget(title)
        layout.add_widget(title_box)
        
        # إدخال أسماء الفرق
        teams_box = BoxLayout(orientation='vertical', size_hint_y=0.35, spacing=dp(8))
        
        teams_box.add_widget(ArabicLabel(
            text="اسم الفريق الاول",
            font_size=dp(13),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(22)
        ))
        
        self.team1_input = ArabicTextInput(
            text="",
            hint_text="فريقنا",
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_color=COLORS['surface'],
            foreground_color=COLORS['text'],
            cursor_color=COLORS['primary']
        )
        teams_box.add_widget(self.team1_input)
        
        teams_box.add_widget(ArabicLabel(
            text="اسم الفريق الثاني",
            font_size=dp(13),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(22)
        ))
        
        self.team2_input = ArabicTextInput(
            text="",
            hint_text="الخصم",
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_color=COLORS['surface'],
            foreground_color=COLORS['text'],
            cursor_color=COLORS['primary']
        )
        teams_box.add_widget(self.team2_input)
        
        layout.add_widget(teams_box)
        
        layout.add_widget(Widget(size_hint_y=0.08))
        
        # الأزرار
        start_btn = ArabicButton(
            text="بدء لعبة جديدة",
            bg_color=COLORS['success'],
            height=dp(55),
            font_size=dp(18)
        )
        start_btn.bind(on_press=self._start_game)
        layout.add_widget(start_btn)
        
        continue_btn = ArabicButton(
            text="استكمال لعبة سابقة",
            bg_color=COLORS['primary'],
            height=dp(45)
        )
        continue_btn.bind(on_press=self._continue_game)
        layout.add_widget(continue_btn)
        
        # زر الإعدادات
        settings_btn = ArabicButton(
            text="⚙ إعدادات الكاميرا",
            bg_color=COLORS['surface'],
            height=dp(40),
            font_size=dp(14)
        )
        settings_btn.bind(on_press=self._open_settings)
        layout.add_widget(settings_btn)
        
        layout.add_widget(Widget(size_hint_y=0.05))
        
        self.add_widget(layout)
    
    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def _start_game(self, *args):
        app = self.manager.app
        app.team1_name = self.team1_input.text or "فريقنا"
        app.team2_name = self.team2_input.text or "الخصم"
        app.reset_game()
        self.manager.current = 'game'
    
    def _continue_game(self, *args):
        self.manager.current = 'game'
    
    def _open_settings(self, *args):
        self.manager.current = 'settings'


class GameScreen(Screen):
    """شاشة اللعبة الرئيسية"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'game'
        Clock.schedule_once(lambda dt: self._build(), 0)
    
    def _build(self):
        with self.canvas.before:
            Color(*COLORS['background'])
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        
        # النتائج الكلية
        scores = BoxLayout(size_hint_y=None, height=dp(95), spacing=dp(8))
        
        self.team1_box = TeamScoreBox(name="فريقنا", score=0, color=COLORS['primary_dark'])
        scores.add_widget(self.team1_box)
        
        vs_lbl = Label(text="VS", font_size=dp(16), color=COLORS['text'], size_hint_x=0.15)
        scores.add_widget(vs_lbl)
        
        self.team2_box = TeamScoreBox(name="الخصم", score=0, color=COLORS['danger'])
        scores.add_widget(self.team2_box)
        
        layout.add_widget(scores)
        
        # رقم الجولة
        self.round_lbl = ArabicLabel(
            text="الجولة: 0",
            font_size=dp(16),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(28)
        )
        layout.add_widget(self.round_lbl)
        
        # منطقة المحتوى
        scroll = ScrollView(size_hint_y=0.45)
        self.content = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        scroll.add_widget(self.content)
        layout.add_widget(scroll)
        
        # الأزرار
        buttons = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180), spacing=dp(8))
        
        # خيار الكاميرا أو اليدوي
        new_round_lbl = ArabicLabel(
            text="بدء جولة جديدة",
            font_size=dp(14),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(25)
        )
        buttons.add_widget(new_round_lbl)
        
        methods_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        
        camera_btn = ArabicButton(
            text="بالكاميرا",
            bg_color=COLORS['secondary'],
            font_size=dp(14)
        )
        camera_btn.bind(on_press=self._start_camera_round)
        methods_row.add_widget(camera_btn)
        
        manual_btn = ArabicButton(
            text="يدوي",
            bg_color=COLORS['success'],
            font_size=dp(14)
        )
        manual_btn.bind(on_press=self._start_manual_round)
        methods_row.add_widget(manual_btn)
        
        buttons.add_widget(methods_row)
        
        history_btn = ArabicButton(
            text="سجل الجولات",
            bg_color=COLORS['primary'],
            height=dp(45)
        )
        history_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'history'))
        buttons.add_widget(history_btn)
        
        home_btn = ArabicButton(
            text="الصفحة الرئيسية",
            bg_color=COLORS['surface'],
            height=dp(40)
        )
        home_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'welcome'))
        buttons.add_widget(home_btn)
        
        layout.add_widget(buttons)
        
        self.add_widget(layout)
    
    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def on_enter(self):
        self._refresh()
    
    def _refresh(self):
        app = self.manager.app
        
        self.team1_box.set_name(app.team1_name)
        self.team1_box.set_score(app.team1_total)
        self.team2_box.set_name(app.team2_name)
        self.team2_box.set_score(app.team2_total)
        
        self.round_lbl.set_text(f"الجولة: {app.round_number}")
        
        self.content.clear_widgets()
        
        if app.history:
            last = app.history[-1]
            
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), padding=dp(10))
            with box.canvas.before:
                Color(*COLORS['card'])
                RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(10)])
            
            box.add_widget(ArabicLabel(
                text=f"نتيجة الجولة {last['round']}",
                font_size=dp(14),
                color=COLORS['text_secondary']
            ))
            
            row = BoxLayout()
            t1_color = COLORS['success'] if last['team1'] > last['team2'] else COLORS['text']
            row.add_widget(ArabicLabel(text=f"{app.team1_name}: {last['team1']}", color=t1_color))
            
            t2_color = COLORS['success'] if last['team2'] > last['team1'] else COLORS['text']
            row.add_widget(ArabicLabel(text=f"{app.team2_name}: {last['team2']}", color=t2_color))
            box.add_widget(row)
            
            self.content.add_widget(box)
        else:
            self.content.add_widget(ArabicLabel(
                text="اضغط لبدء جولة جديدة",
                color=COLORS['text_secondary'],
                size_hint_y=None,
                height=dp(80)
            ))
    
    def _start_camera_round(self, *args):
        app = self.manager.app
        app.round_number += 1
        self.manager.current = 'camera'
    
    def _start_manual_round(self, *args):
        app = self.manager.app
        app.round_number += 1
        self.manager.current = 'counting'


class CameraScreen(Screen):
    """شاشة الكاميرا للتعرف على البطاقات باستخدام AI"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'camera'
        self.camera_widget = None
        self.detected_cards = {'queens': [], 'king': False}
        Clock.schedule_once(lambda dt: self._build(), 0)
    
    def _build(self):
        with self.canvas.before:
            Color(*COLORS['background'])
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # العنوان
        layout.add_widget(ArabicLabel(
            text="صور البطاقات",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40)
        ))
        
        # منطقة الكاميرا
        self.camera_box = BoxLayout(size_hint_y=0.5)
        layout.add_widget(self.camera_box)
        
        # عرض البطاقات المكتشفة
        self.detected_box = BoxLayout(orientation='vertical', size_hint_y=0.25, spacing=dp(5))
        self.detected_box.add_widget(ArabicLabel(
            text="البطاقات المكتشفة:",
            font_size=dp(14),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(25)
        ))
        self.detected_cards_row = BoxLayout(size_hint_y=None, height=dp(80))
        self.detected_box.add_widget(self.detected_cards_row)
        layout.add_widget(self.detected_box)
        
        # الأزرار
        buttons = BoxLayout(size_hint_y=None, height=dp(130), spacing=dp(8), orientation='vertical')
        
        capture_btn = ArabicButton(
            text="التقاط وتحليل",
            bg_color=COLORS['success'],
            height=dp(50)
        )
        capture_btn.bind(on_press=self._capture)
        buttons.add_widget(capture_btn)
        
        btn_row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        
        manual_btn = ArabicButton(
            text="ادخال يدوي",
            bg_color=COLORS['primary'],
            height=dp(45)
        )
        manual_btn.bind(on_press=self._go_manual)
        btn_row.add_widget(manual_btn)
        
        back_btn = ArabicButton(
            text="رجوع",
            bg_color=COLORS['surface'],
            height=dp(45)
        )
        back_btn.bind(on_press=self._go_back)
        btn_row.add_widget(back_btn)
        
        buttons.add_widget(btn_row)
        layout.add_widget(buttons)
        
        self.add_widget(layout)
    
    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def on_enter(self):
        self.detected_cards = {'queens': [], 'king': False}
        self._update_detected_display()
        
        # تشغيل الكاميرا
        if platform in ('android', 'ios'):
            self._start_camera()
        else:
            self.camera_box.clear_widgets()
            self.camera_box.add_widget(ArabicLabel(
                text="الكاميرا تعمل على الموبايل\n\nللاختبار اضغط التقاط",
                font_size=dp(14),
                color=COLORS['text_secondary']
            ))
    
    def on_leave(self):
        if self.camera_widget:
            try:
                self.camera_widget.play = False
            except:
                pass
    
    def _start_camera(self):
        try:
            from kivy.uix.camera import Camera
            self.camera_box.clear_widgets()
            self.camera_widget = Camera(play=True, resolution=(640, 480))
            self.camera_box.add_widget(self.camera_widget)
        except Exception as e:
            self.camera_box.clear_widgets()
            self.camera_box.add_widget(ArabicLabel(
                text="خطا في تشغيل الكاميرا",
                color=COLORS['danger']
            ))
    
    def _update_detected_display(self):
        self.detected_cards_row.clear_widgets()
        
        for suit in self.detected_cards['queens']:
            card = CardWidget(suit=suit, rank='Q')
            card.size = (dp(50), dp(65))
            card.disabled = True
            card.state = 'down'
            self.detected_cards_row.add_widget(card)
        
        if self.detected_cards['king']:
            card = CardWidget(suit='heart', rank='K')
            card.size = (dp(50), dp(65))
            card.disabled = True
            card.state = 'down'
            self.detected_cards_row.add_widget(card)
        
        if not self.detected_cards['queens'] and not self.detected_cards['king']:
            self.detected_cards_row.add_widget(ArabicLabel(
                text="لم يتم اكتشاف بطاقات بعد",
                font_size=dp(12),
                color=COLORS['text_secondary']
            ))
    
    def _capture(self, *args):
        """التقاط - الانتقال لشاشة اختيار البطاقات"""
        # حالياً ننتقل للاختيار اليدوي
        # الـ API يحتاج إعداد من شاشة الإعدادات
        self.manager.current = 'camera_result'
    
    def _go_manual(self, *args):
        self.manager.current = 'counting'
    
    def _go_back(self, *args):
        app = self.manager.app
        if app.round_number > 0:
            app.round_number -= 1
        self.manager.current = 'game'


class CameraResultScreen(Screen):
    """شاشة نتائج الكاميرا - اختيار البطاقات المكتشفة"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'camera_result'
        self.queen_cards = {}
        self.king_card = None
        Clock.schedule_once(lambda dt: self._build(), 0)
    
    def _build(self):
        with self.canvas.before:
            Color(*COLORS['background'])
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        layout.add_widget(ArabicLabel(
            text="حدد البطاقات التي التقطتها",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(35)
        ))
        
        scroll = ScrollView(size_hint_y=0.7)
        content = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # البنات
        queens_box = self._make_section("حدد البنات الموجودة")
        queens_row = BoxLayout(size_hint_y=None, height=dp(120), spacing=dp(5))
        self.queen_cards = {}
        for suit in ['spade', 'heart', 'diamond', 'club']:
            card = CardWithRank(suit=suit, rank='Q')
            self.queen_cards[suit] = card
            queens_row.add_widget(card)
        queens_box.add_widget(queens_row)
        content.add_widget(queens_box)
        
        # شيخ القبة
        king_box = self._make_section("شيخ القبة")
        king_row = BoxLayout(size_hint_y=None, height=dp(120))
        king_row.add_widget(Widget())
        self.king_card = CardWithRank(suit='heart', rank='K')
        king_row.add_widget(self.king_card)
        king_row.add_widget(Widget())
        king_box.add_widget(king_row)
        content.add_widget(king_box)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        
        # الأزرار
        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        
        confirm_btn = ArabicButton(
            text="تاكيد والمتابعة",
            bg_color=COLORS['success']
        )
        confirm_btn.bind(on_press=self._confirm)
        btn_row.add_widget(confirm_btn)
        
        layout.add_widget(btn_row)
        
        self.add_widget(layout)
    
    def _make_section(self, title):
        box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10))
        box.bind(minimum_height=box.setter('height'))
        
        with box.canvas.before:
            Color(*COLORS['card'])
            box._bg = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(10)])
        box.bind(pos=lambda *a: setattr(box._bg, 'pos', box.pos),
                 size=lambda *a: setattr(box._bg, 'size', box.size))
        
        box.add_widget(ArabicLabel(
            text=title,
            font_size=dp(14),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(25)
        ))
        
        return box
    
    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def on_enter(self):
        # إعادة تعيين
        for card in self.queen_cards.values():
            card.state = 'normal'
        self.king_card.state = 'normal'
    
    def _confirm(self, *args):
        """تأكيد البطاقات المكتشفة والانتقال للتدبيل"""
        app = self.manager.app
        
        selected_queens = [s for s, c in self.queen_cards.items() if c.state == 'down']
        has_king = self.king_card.state == 'down'
        
        # حفظ البيانات المكتشفة
        app.detected_from_camera = {
            'queens': selected_queens,
            'has_king': has_king
        }
        
        # الانتقال لشاشة إدخال الأكلات والديناري
        self.manager.current = 'counting_from_camera'


class CountingFromCameraScreen(Screen):
    """شاشة عد الأكلات بعد الكاميرا"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'counting_from_camera'
        Clock.schedule_once(lambda dt: self._build(), 0)
    
    def _build(self):
        with self.canvas.before:
            Color(*COLORS['background'])
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        layout.add_widget(ArabicLabel(
            text="ادخل عدد الاكلات والديناري",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(35)
        ))
        
        # عرض البطاقات المكتشفة
        self.detected_lbl = ArabicLabel(
            text="البطاقات المكتشفة",
            font_size=dp(13),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(25)
        )
        layout.add_widget(self.detected_lbl)
        
        self.detected_row = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(5))
        layout.add_widget(self.detected_row)
        
        content = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=0.5)
        
        # عدد الأكلات
        tricks_box = self._make_section("عدد الاكلات")
        self.tricks_selector = NumberSelector()
        tricks_box.add_widget(self.tricks_selector)
        content.add_widget(tricks_box)
        
        # عدد الديناري
        diamond_box = self._make_section("عدد اوراق الديناري")
        self.diamond_selector = NumberSelector()
        diamond_box.add_widget(self.diamond_selector)
        content.add_widget(diamond_box)
        
        layout.add_widget(content)
        
        # الأزرار
        next_btn = ArabicButton(
            text="التالي - اختيار التدبيل",
            bg_color=COLORS['primary'],
            height=dp(50)
        )
        next_btn.bind(on_press=self._next)
        layout.add_widget(next_btn)
        
        self.add_widget(layout)
    
    def _make_section(self, title):
        box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), padding=dp(10))
        
        with box.canvas.before:
            Color(*COLORS['card'])
            box._bg = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(10)])
        box.bind(pos=lambda *a: setattr(box._bg, 'pos', box.pos),
                 size=lambda *a: setattr(box._bg, 'size', box.size))
        
        box.add_widget(ArabicLabel(
            text=title,
            font_size=dp(14),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(25)
        ))
        
        return box
    
    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def on_enter(self):
        self.tricks_selector.value = 0
        self.diamond_selector.value = 0
        
        # عرض البطاقات المكتشفة
        self.detected_row.clear_widgets()
        app = self.manager.app
        detected = getattr(app, 'detected_from_camera', {'queens': [], 'has_king': False})
        
        for suit in detected.get('queens', []):
            card = CardWidget(suit=suit, rank='Q')
            card.size = (dp(45), dp(60))
            card.disabled = True
            card.state = 'down'
            self.detected_row.add_widget(card)
        
        if detected.get('has_king', False):
            card = CardWidget(suit='heart', rank='K')
            card.size = (dp(45), dp(60))
            card.disabled = True
            card.state = 'down'
            self.detected_row.add_widget(card)
    
    def _next(self, *args):
        app = self.manager.app
        detected = getattr(app, 'detected_from_camera', {'queens': [], 'has_king': False})
        
        app.current_round_data = {
            'tricks': int(self.tricks_selector.value),
            'diamonds': int(self.diamond_selector.value),
            'queens': detected.get('queens', []),
            'has_king': detected.get('has_king', False)
        }
        
        self.manager.current = 'doubling'


class CountingScreen(Screen):
    """شاشة العد اليدوية"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'counting'
        self.queen_cards = {}
        self.king_card = None
        Clock.schedule_once(lambda dt: self._build(), 0)
    
    def _build(self):
        with self.canvas.before:
            Color(*COLORS['background'])
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        
        # العنوان
        layout.add_widget(ArabicLabel(
            text="عد الاكلات يدويا",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(30)
        ))
        
        # التمرير
        scroll = ScrollView(size_hint_y=0.82)
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # عدد الأكلات
        tricks_box = self._make_section("عدد الاكلات", "كل اكلة 4 ورقات")
        self.tricks_selector = NumberSelector()
        tricks_box.add_widget(self.tricks_selector)
        content.add_widget(tricks_box)
        
        # عدد الديناري
        diamond_box = self._make_section("عدد اوراق الديناري", "")
        
        # رمز الديناري
        diamond_row = BoxLayout(size_hint_y=None, height=dp(55))
        diamond_row.add_widget(Widget())
        diamond_icon = CardWidget(suit='diamond', rank='')
        diamond_icon.size = (dp(40), dp(50))
        diamond_icon.disabled = True
        diamond_row.add_widget(diamond_icon)
        diamond_row.add_widget(Widget())
        diamond_box.add_widget(diamond_row)
        
        self.diamond_selector = NumberSelector()
        diamond_box.add_widget(self.diamond_selector)
        content.add_widget(diamond_box)
        
        # البنات
        queens_box = self._make_section("البنات الموجودة", "اضغط على الموجودة")
        queens_row = BoxLayout(size_hint_y=None, height=dp(120), spacing=dp(5))
        self.queen_cards = {}
        for suit in ['spade', 'heart', 'diamond', 'club']:
            card = CardWithRank(suit=suit, rank='Q')
            self.queen_cards[suit] = card
            queens_row.add_widget(card)
        queens_box.add_widget(queens_row)
        content.add_widget(queens_box)
        
        # شيخ القبة
        king_box = self._make_section("شيخ القبة", "")
        king_row = BoxLayout(size_hint_y=None, height=dp(120))
        king_row.add_widget(Widget())
        self.king_card = CardWithRank(suit='heart', rank='K')
        king_row.add_widget(self.king_card)
        king_row.add_widget(Widget())
        king_box.add_widget(king_row)
        content.add_widget(king_box)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        
        # زر التالي
        next_btn = ArabicButton(
            text="التالي",
            bg_color=COLORS['primary'],
            height=dp(50)
        )
        next_btn.bind(on_press=self._next)
        layout.add_widget(next_btn)
        
        self.add_widget(layout)
    
    def _make_section(self, title, subtitle):
        box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10))
        box.bind(minimum_height=box.setter('height'))
        
        with box.canvas.before:
            Color(*COLORS['card'])
            box._bg = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(10)])
        box.bind(pos=lambda *a: setattr(box._bg, 'pos', box.pos),
                 size=lambda *a: setattr(box._bg, 'size', box.size))
        
        box.add_widget(ArabicLabel(
            text=title,
            font_size=dp(14),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(25)
        ))
        
        if subtitle:
            box.add_widget(ArabicLabel(
                text=subtitle,
                font_size=dp(11),
                color=COLORS['text_secondary'],
                size_hint_y=None,
                height=dp(18)
            ))
        
        return box
    
    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def on_enter(self):
        # إعادة تعيين
        self.tricks_selector.value = 0
        self.diamond_selector.value = 0
        for card in self.queen_cards.values():
            card.state = 'normal'
        self.king_card.state = 'normal'
    
    def _next(self, *args):
        app = self.manager.app
        
        selected_queens = [s for s, c in self.queen_cards.items() if c.state == 'down']
        
        app.current_round_data = {
            'tricks': int(self.tricks_selector.value),
            'diamonds': int(self.diamond_selector.value),
            'queens': selected_queens,
            'has_king': self.king_card.state == 'down'
        }
        
        self.manager.current = 'doubling'


class DoublingScreen(Screen):
    """شاشة اختيار التدبيل"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'doubling'
        self.opponent_doubled = {}
        self.my_doubled = {}
        Clock.schedule_once(lambda dt: self._build(), 0)
    
    def _build(self):
        with self.canvas.before:
            Color(*COLORS['background'])
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        
        self.layout.add_widget(ArabicLabel(
            text="اختيار التدبيل",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(30)
        ))
        
        scroll = ScrollView(size_hint_y=0.82)
        self.content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        scroll.add_widget(self.content)
        self.layout.add_widget(scroll)
        
        calc_btn = ArabicButton(
            text="حساب النتيجة",
            bg_color=COLORS['success'],
            height=dp(50)
        )
        calc_btn.bind(on_press=self._calculate)
        self.layout.add_widget(calc_btn)
        
        self.add_widget(self.layout)
    
    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def on_enter(self):
        self.content.clear_widgets()
        self.opponent_doubled = {}
        self.my_doubled = {}
        
        app = self.manager.app
        data = app.current_round_data
        queens = data.get('queens', [])
        has_king = data.get('has_king', False)
        
        # ما دبله الخصم علي
        if queens or has_king:
            box1 = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10))
            box1.bind(minimum_height=box1.setter('height'))
            
            with box1.canvas.before:
                Color(0.25, 0.15, 0.15, 1)  # لون أحمر داكن
                box1._bg = RoundedRectangle(pos=box1.pos, size=box1.size, radius=[dp(10)])
            box1.bind(pos=lambda *a: setattr(box1._bg, 'pos', box1.pos),
                     size=lambda *a: setattr(box1._bg, 'size', box1.size))
            
            box1.add_widget(ArabicLabel(
                text="هل دبل الخصم اي من هذه؟",
                font_size=dp(14),
                color=COLORS['warning'],
                size_hint_y=None,
                height=dp(28)
            ))
            box1.add_widget(ArabicLabel(
                text="اختر البطاقات التي دبلها الخصم عليك",
                font_size=dp(11),
                color=COLORS['text_secondary'],
                size_hint_y=None,
                height=dp(20)
            ))
            
            row1 = BoxLayout(size_hint_y=None, height=dp(120), spacing=dp(5))
            
            for suit in queens:
                card = CardWithRank(suit=suit, rank='Q')
                card._card.bind(state=lambda inst, val, s=suit: self._set_opponent(s, 'Q', val))
                row1.add_widget(card)
                self.opponent_doubled[f"Q_{suit}"] = False
            
            if has_king:
                card = CardWithRank(suit='heart', rank='K')
                card._card.bind(state=lambda inst, val: self._set_opponent('heart', 'K', val))
                row1.add_widget(card)
                self.opponent_doubled["K_heart"] = False
            
            box1.add_widget(row1)
            self.content.add_widget(box1)
        
        # ما دبلته أنا على الخصم
        all_suits = ['spade', 'heart', 'diamond', 'club']
        missing = [s for s in all_suits if s not in queens]
        missing_king = not has_king
        
        if missing or missing_king:
            box2 = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(10))
            box2.bind(minimum_height=box2.setter('height'))
            
            with box2.canvas.before:
                Color(0.12, 0.22, 0.12, 1)  # لون أخضر داكن
                box2._bg = RoundedRectangle(pos=box2.pos, size=box2.size, radius=[dp(10)])
            box2.bind(pos=lambda *a: setattr(box2._bg, 'pos', box2.pos),
                     size=lambda *a: setattr(box2._bg, 'size', box2.size))
            
            box2.add_widget(ArabicLabel(
                text="هل دبلت انت على الخصم؟",
                font_size=dp(14),
                color=COLORS['success'],
                size_hint_y=None,
                height=dp(28)
            ))
            box2.add_widget(ArabicLabel(
                text="اختر البطاقات التي دبلتها على الخصم",
                font_size=dp(11),
                color=COLORS['text_secondary'],
                size_hint_y=None,
                height=dp(20)
            ))
            
            row2 = BoxLayout(size_hint_y=None, height=dp(120), spacing=dp(5))
            
            for suit in missing:
                card = CardWithRank(suit=suit, rank='Q')
                card._card.bind(state=lambda inst, val, s=suit: self._set_mine(s, 'Q', val))
                row2.add_widget(card)
                self.my_doubled[f"Q_{suit}"] = False
            
            if missing_king:
                card = CardWithRank(suit='heart', rank='K')
                card._card.bind(state=lambda inst, val: self._set_mine('heart', 'K', val))
                row2.add_widget(card)
                self.my_doubled["K_heart"] = False
            
            box2.add_widget(row2)
            self.content.add_widget(box2)
    
    def _set_opponent(self, suit, rank, state):
        self.opponent_doubled[f"{rank}_{suit}"] = (state == 'down')
    
    def _set_mine(self, suit, rank, state):
        self.my_doubled[f"{rank}_{suit}"] = (state == 'down')
    
    def _calculate(self, *args):
        app = self.manager.app
        data = app.current_round_data
        
        score = 0
        
        # الأكلات
        score -= data['tricks'] * POINTS['trick']
        
        # الديناري
        score -= data['diamonds'] * POINTS['diamond']
        
        # البنات
        for suit in data['queens']:
            if self.opponent_doubled.get(f"Q_{suit}", False):
                score -= POINTS['queen'] * 2
            else:
                score -= POINTS['queen']
        
        # شيخ القبة
        if data['has_king']:
            if self.opponent_doubled.get("K_heart", False):
                score -= POINTS['king_heart'] * 2
            else:
                score -= POINTS['king_heart']
        
        # مكافأة التدبيل على الخصم
        for key, val in self.my_doubled.items():
            if val:
                if key.startswith('Q_'):
                    score += POINTS['queen']
                elif key.startswith('K_'):
                    score += POINTS['king_heart']
        
        team2 = POINTS['round_total'] - score
        
        app.team1_total += score
        app.team2_total += team2
        
        app.history.append({
            'round': app.round_number,
            'team1': score,
            'team2': team2
        })
        
        self.manager.current = 'game'


class HistoryScreen(Screen):
    """شاشة السجل"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'history'
        Clock.schedule_once(lambda dt: self._build(), 0)
    
    def _build(self):
        with self.canvas.before:
            Color(*COLORS['background'])
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        
        layout.add_widget(ArabicLabel(
            text="سجل الجولات",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40)
        ))
        
        scroll = ScrollView(size_hint_y=0.75)
        self.table = BoxLayout(orientation='vertical', spacing=dp(3), size_hint_y=None)
        self.table.bind(minimum_height=self.table.setter('height'))
        scroll.add_widget(self.table)
        layout.add_widget(scroll)
        
        self.total_lbl = ArabicLabel(
            text="",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(35)
        )
        layout.add_widget(self.total_lbl)
        
        back_btn = ArabicButton(
            text="رجوع",
            bg_color=COLORS['primary'],
            height=dp(45)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'game'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def on_enter(self):
        self.table.clear_widgets()
        app = self.manager.app
        
        # العنوان
        header = BoxLayout(size_hint_y=None, height=dp(35))
        header.add_widget(Label(text="#", color=COLORS['text'], size_hint_x=0.15))
        header.add_widget(ArabicLabel(text=app.team1_name, size_hint_x=0.425, font_size=dp(13)))
        header.add_widget(ArabicLabel(text=app.team2_name, size_hint_x=0.425, font_size=dp(13)))
        self.table.add_widget(header)
        
        # الجولات
        for entry in app.history:
            row = BoxLayout(size_hint_y=None, height=dp(40))
            with row.canvas.before:
                Color(*COLORS['card'])
                RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(5)])
            
            row.add_widget(Label(text=str(entry['round']), color=COLORS['text'], size_hint_x=0.15))
            
            c1 = COLORS['success'] if entry['team1'] > entry['team2'] else COLORS['text']
            row.add_widget(Label(text=str(entry['team1']), color=c1, size_hint_x=0.425, font_size=dp(16)))
            
            c2 = COLORS['success'] if entry['team2'] > entry['team1'] else COLORS['text']
            row.add_widget(Label(text=str(entry['team2']), color=c2, size_hint_x=0.425, font_size=dp(16)))
            
            self.table.add_widget(row)
        
        if not app.history:
            self.table.add_widget(ArabicLabel(
                text="لا توجد جولات",
                color=COLORS['text_secondary'],
                size_hint_y=None,
                height=dp(80)
            ))
        
        expected = app.round_number * POINTS['round_total']
        actual = app.team1_total + app.team2_total
        self.total_lbl.set_text(f"المجموع الكلي: {app.team1_total} + {app.team2_total} = {actual}")


class SettingsScreen(Screen):
    """شاشة الإعدادات - إعداد API Key"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        Clock.schedule_once(lambda dt: self._build(), 0)
    
    def _build(self):
        with self.canvas.before:
            Color(*COLORS['background'])
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        # العنوان
        layout.add_widget(ArabicLabel(
            text="إعدادات التطبيق",
            font_size=dp(22),
            size_hint_y=None,
            height=dp(50)
        ))
        
        # قسم API
        api_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200), spacing=dp(10))
        
        with api_box.canvas.before:
            Color(*COLORS['card'])
            api_box._bg = RoundedRectangle(pos=api_box.pos, size=api_box.size, radius=[dp(15)])
        api_box.bind(pos=lambda *a: setattr(api_box._bg, 'pos', api_box.pos),
                     size=lambda *a: setattr(api_box._bg, 'size', api_box.size))
        
        api_box.add_widget(ArabicLabel(
            text="إعدادات التعرف بالكاميرا",
            font_size=dp(16),
            color=COLORS['primary'],
            size_hint_y=None,
            height=dp(35)
        ))
        
        api_box.add_widget(ArabicLabel(
            text="مفتاح Roboflow API",
            font_size=dp(13),
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=dp(25),
            halign='right'
        ))
        
        self.api_input = ArabicTextInput(
            hint_text="أدخل مفتاح API هنا",
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            halign='left',
            padding=[dp(10), dp(10)]
        )
        api_box.add_widget(self.api_input)
        
        # زر حفظ API
        save_api_btn = ArabicButton(
            text="حفظ المفتاح",
            bg_color=COLORS['success'],
            size_hint_y=None,
            height=dp(45)
        )
        save_api_btn.bind(on_press=self._save_api_key)
        api_box.add_widget(save_api_btn)
        
        layout.add_widget(api_box)
        
        # تعليمات
        help_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180), spacing=dp(5))
        
        with help_box.canvas.before:
            Color(*COLORS['surface'])
            help_box._bg = RoundedRectangle(pos=help_box.pos, size=help_box.size, radius=[dp(15)])
        help_box.bind(pos=lambda *a: setattr(help_box._bg, 'pos', help_box.pos),
                      size=lambda *a: setattr(help_box._bg, 'size', help_box.size))
        
        help_box.add_widget(ArabicLabel(
            text="كيف تحصل على مفتاح API؟",
            font_size=dp(14),
            color=COLORS['primary'],
            size_hint_y=None,
            height=dp(30)
        ))
        
        steps = [
            "1. اذهب إلى roboflow.com",
            "2. أنشئ حساب مجاني",
            "3. اذهب إلى Settings",
            "4. اختر API Keys",
            "5. انسخ المفتاح وألصقه هنا"
        ]
        
        for step in steps:
            help_box.add_widget(ArabicLabel(
                text=step,
                font_size=dp(11),
                color=COLORS['text_secondary'],
                size_hint_y=None,
                height=dp(22),
                halign='right'
            ))
        
        layout.add_widget(help_box)
        
        # حالة API
        self.status_lbl = ArabicLabel(
            text="",
            font_size=dp(13),
            size_hint_y=None,
            height=dp(35)
        )
        layout.add_widget(self.status_lbl)
        
        # مساحة فارغة
        layout.add_widget(Widget())
        
        # زر رجوع
        back_btn = ArabicButton(
            text="رجوع",
            bg_color=COLORS['primary'],
            size_hint_y=None,
            height=dp(50)
        )
        back_btn.bind(on_press=self._go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def on_enter(self):
        """عند دخول الشاشة"""
        # تحميل المفتاح المحفوظ
        app = self.manager.app
        if hasattr(app, 'api_key') and app.api_key:
            self.api_input.text = app.api_key
            self._check_api_status()
        else:
            self._load_saved_key()
    
    def _load_saved_key(self):
        """تحميل المفتاح من الملف"""
        try:
            import os
            config_path = os.path.join(os.path.dirname(__file__), 'api_config.txt')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    key = f.read().strip()
                    if key:
                        self.api_input.text = key
                        self.manager.app.api_key = key
                        self._check_api_status()
        except:
            pass
    
    def _save_api_key(self, *args):
        """حفظ مفتاح API"""
        key = self.api_input.text.strip()
        
        if not key:
            self.status_lbl.set_text("الرجاء إدخال مفتاح API")
            self.status_lbl.color = COLORS['danger']
            return
        
        # حفظ في التطبيق
        self.manager.app.api_key = key
        
        # حفظ في ملف
        try:
            import os
            config_path = os.path.join(os.path.dirname(__file__), 'api_config.txt')
            with open(config_path, 'w') as f:
                f.write(key)
        except:
            pass
        
        # تحديث card_detector
        try:
            import card_detector
            card_detector.ROBOFLOW_API_KEY = key
        except:
            pass
        
        self.status_lbl.set_text("تم حفظ المفتاح بنجاح ✓")
        self.status_lbl.color = COLORS['success']
        
        # اختبار المفتاح
        Clock.schedule_once(lambda dt: self._check_api_status(), 0.5)
    
    def _check_api_status(self):
        """التحقق من حالة API"""
        try:
            from card_detector import CardDetector
            detector = CardDetector(self.api_input.text.strip())
            
            if detector.is_ready:
                self.status_lbl.set_text("المفتاح جاهز للاستخدام ✓")
                self.status_lbl.color = COLORS['success']
            else:
                self.status_lbl.set_text("المفتاح غير صالح")
                self.status_lbl.color = COLORS['danger']
        except Exception as e:
            self.status_lbl.set_text(f"خطأ: {str(e)}")
            self.status_lbl.color = COLORS['danger']
    
    def _go_back(self, *args):
        self.manager.current = 'welcome'
