"""
واجهة المستخدم لتطبيق عداد نقاط الشدة
UI Components for CC Counter App
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.metrics import dp

import os
import tempfile

# مكتبات دعم النص العربي
import arabic_reshaper
from bidi.algorithm import get_display

# مسار الخط العربي
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansArabic.ttf')
ARABIC_FONT = 'Arabic' if os.path.exists(FONT_PATH) else None


def arabic(text):
    """تحويل النص العربي ليظهر بشكل صحيح"""
    if not text:
        return text
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


class RTLLabel(Label):
    """Label يدعم النص العربي RTL"""
    
    def __init__(self, **kwargs):
        # تحويل النص العربي
        if 'text' in kwargs:
            kwargs['text'] = arabic(kwargs['text'])
        kwargs.setdefault('halign', 'center')
        kwargs.setdefault('text_size', (None, None))
        kwargs.setdefault('font_size', dp(18))
        if ARABIC_FONT:
            kwargs.setdefault('font_name', ARABIC_FONT)
        super().__init__(**kwargs)
        self.bind(size=self._update_text_size)
    
    def _update_text_size(self, *args):
        self.text_size = (self.width, None)


class StyledButton(Button):
    """زر منسق"""
    
    def __init__(self, **kwargs):
        # تحويل النص العربي
        if 'text' in kwargs:
            kwargs['text'] = arabic(kwargs['text'])
        kwargs.setdefault('font_size', dp(18))
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(50))
        if ARABIC_FONT:
            kwargs.setdefault('font_name', ARABIC_FONT)
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(0.2, 0.6, 0.8, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class CardToggleButton(ToggleButton):
    """زر لاختيار البطاقة (مدبلة أو لا)"""
    
    card_name = StringProperty("")
    card_suit = StringProperty("")
    is_queen = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        # تحويل النص العربي
        if 'text' in kwargs:
            kwargs['text'] = arabic(kwargs['text'])
        if ARABIC_FONT:
            kwargs.setdefault('font_name', ARABIC_FONT)
        super().__init__(**kwargs)
        self.font_size = dp(16)
        self.size_hint_y = None
        self.height = dp(60)
        
        self.bind(state=self.on_state_change)
    
    def on_state_change(self, instance, value):
        if value == 'down':
            self.background_color = (0.8, 0.2, 0.2, 1)  # أحمر للمدبل
        else:
            self.background_color = (0.3, 0.3, 0.3, 1)  # رمادي للعادي


class HomeScreen(Screen):
    """الشاشة الرئيسية"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # العنوان
        title = RTLLabel(
            text="🃏 عداد الكومبلكس شراكة",
            font_size=dp(28),
            halign='center',
            size_hint_y=None,
            height=dp(100)
        )
        layout.add_widget(title)
        
        # زر التصوير
        camera_btn = StyledButton(
            text="📸 تصوير الأكلات",
            on_press=self.go_to_camera
        )
        layout.add_widget(camera_btn)
        
        # زر الإدخال اليدوي
        manual_btn = StyledButton(
            text="✍️ إدخال يدوي",
            on_press=self.go_to_manual
        )
        layout.add_widget(manual_btn)
        
        # زر السجل
        history_btn = StyledButton(
            text="📊 سجل النقاط",
            on_press=self.go_to_history
        )
        layout.add_widget(history_btn)
        
        # مساحة فارغة
        layout.add_widget(BoxLayout())
        
        # شرح القواعد
        rules_btn = StyledButton(
            text="📖 قواعد العد",
            on_press=self.show_rules
        )
        layout.add_widget(rules_btn)
        
        self.add_widget(layout)
    
    def go_to_camera(self, instance):
        self.manager.current = 'camera'
    
    def go_to_manual(self, instance):
        self.manager.current = 'manual'
    
    def go_to_history(self, instance):
        self.manager.current = 'history'
    
    def show_rules(self, instance):
        rules_text = """
📜 قواعد العدّ:

🃏 الأكلات:
• كل أكلة (4 ورقات) = -15 نقطة

♦️ الديناري:
• كل ورقة ديناري = -10 نقاط

👸 البنات (Q):
• كل بنت عادية = -25 نقطة
• كل بنت مدبلة = -50 نقطة

👑 شيخ القبة (K ♥):
• عادي = -75 نقطة
• مدبل = -150 نقطة

✨ التدبيل للخصم:
إذا دبّلت ورقة والخصم أكلها:
• بنت = +25 نقطة لك
• شيخ القبة = +75 نقطة لك
        """
        
        popup = Popup(
            title="قواعد العدّ",
            content=RTLLabel(text=rules_text, halign='right'),
            size_hint=(0.9, 0.8)
        )
        popup.open()


class CameraScreen(Screen):
    """شاشة الكاميرا - مؤقتاً تحويل للإدخال اليدوي"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'camera'
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # رسالة
        info_label = RTLLabel(
            text="📸 ميزة الكاميرا\n\nهذه الميزة تعمل على الهاتف فقط.\n\nللاختبار، استخدم الإدخال اليدوي.",
            font_size=dp(20),
            halign='center',
            size_hint_y=0.6
        )
        layout.add_widget(info_label)
        
        # زر الإدخال اليدوي
        manual_btn = StyledButton(
            text="✍️ الإدخال اليدوي",
            on_press=self.go_to_manual
        )
        layout.add_widget(manual_btn)
        
        # زر الرجوع
        back_btn = StyledButton(
            text="🔙 رجوع",
            on_press=self.go_back
        )
        layout.add_widget(back_btn)
        
        layout.add_widget(BoxLayout())  # مساحة فارغة
        
        self.add_widget(layout)
    
    def go_to_manual(self, instance):
        self.manager.current = 'manual'
    
    def go_back(self, instance):
        self.manager.current = 'home'


class ManualInputScreen(Screen):
    """شاشة الإدخال اليدوي"""
    
    total_cards = NumericProperty(0)
    diamond_count = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'manual'
        self.queen_buttons = {}
        self.king_button = None
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # العنوان
        title = RTLLabel(
            text="✍️ إدخال البطاقات",
            font_size=dp(24),
            size_hint_y=None,
            height=dp(50),
            halign='center'
        )
        main_layout.add_widget(title)
        
        # منطقة التمرير
        scroll = ScrollView(size_hint_y=0.8)
        content = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # === عدد الأوراق ===
        cards_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        cards_section.add_widget(RTLLabel(text="🃏 عدد الأوراق الكلي:", size_hint_y=None, height=dp(30)))
        
        cards_controls = BoxLayout(size_hint_y=None, height=dp(50))
        
        minus_cards_btn = StyledButton(text="-", size_hint_x=0.2, on_press=self.decrease_cards)
        self.cards_label = Label(text="0", font_size=dp(24))
        plus_cards_btn = StyledButton(text="+", size_hint_x=0.2, on_press=self.increase_cards)
        
        cards_controls.add_widget(minus_cards_btn)
        cards_controls.add_widget(self.cards_label)
        cards_controls.add_widget(plus_cards_btn)
        
        cards_section.add_widget(cards_controls)
        content.add_widget(cards_section)
        
        # === عدد الديناري ===
        diamond_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        diamond_section.add_widget(RTLLabel(text="♦️ عدد أوراق الديناري:", size_hint_y=None, height=dp(30)))
        
        diamond_controls = BoxLayout(size_hint_y=None, height=dp(50))
        
        minus_diamond_btn = StyledButton(text="-", size_hint_x=0.2, on_press=self.decrease_diamonds)
        self.diamond_label = Label(text="0", font_size=dp(24))
        plus_diamond_btn = StyledButton(text="+", size_hint_x=0.2, on_press=self.increase_diamonds)
        
        diamond_controls.add_widget(minus_diamond_btn)
        diamond_controls.add_widget(self.diamond_label)
        diamond_controls.add_widget(plus_diamond_btn)
        
        diamond_section.add_widget(diamond_controls)
        content.add_widget(diamond_section)
        
        # === البنات ===
        queens_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(250))
        queens_section.add_widget(RTLLabel(
            text="👸 البنات الموجودة (اضغط للتدبيل):",
            size_hint_y=None, height=dp(40)
        ))
        
        queens_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(180))
        
        suits = [
            ("بستوني", "♠"),
            ("ديناري", "♦"),
            ("قبة", "♥"),
            ("اسباتي", "♣")
        ]
        
        for suit_name, suit_symbol in suits:
            btn = CardToggleButton(
                text=f"Q {suit_symbol}\n{suit_name}",
                card_name=f"Q_{suit_name}",
                card_suit=suit_name
            )
            btn.group = None  # السماح باختيار متعدد
            self.queen_buttons[suit_name] = btn
            queens_grid.add_widget(btn)
        
        queens_section.add_widget(queens_grid)
        content.add_widget(queens_section)
        
        # === شيخ القبة ===
        king_section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        king_section.add_widget(RTLLabel(
            text="👑 شيخ القبة (اضغط للتدبيل):",
            size_hint_y=None, height=dp(40)
        ))
        
        self.king_button = CardToggleButton(
            text="K ♥\nشيخ القبة",
            card_name="K_قبة",
            card_suit="قبة",
            is_queen=False
        )
        self.king_button.group = None
        king_section.add_widget(self.king_button)
        content.add_widget(king_section)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        # أزرار التحكم
        controls = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        calculate_btn = StyledButton(
            text="📊 حساب النقاط",
            on_press=self.calculate_score
        )
        controls.add_widget(calculate_btn)
        
        back_btn = StyledButton(
            text="🔙 رجوع",
            on_press=self.go_back
        )
        controls.add_widget(back_btn)
        
        main_layout.add_widget(controls)
        
        self.add_widget(main_layout)
    
    def increase_cards(self, instance):
        self.total_cards += 4  # زيادة بأكلة كاملة
        self.cards_label.text = str(self.total_cards)
    
    def decrease_cards(self, instance):
        if self.total_cards >= 4:
            self.total_cards -= 4
            self.cards_label.text = str(self.total_cards)
    
    def increase_diamonds(self, instance):
        self.diamond_count += 1
        self.diamond_label.text = str(self.diamond_count)
    
    def decrease_diamonds(self, instance):
        if self.diamond_count > 0:
            self.diamond_count -= 1
            self.diamond_label.text = str(self.diamond_count)
    
    def get_input_data(self):
        """جمع بيانات الإدخال"""
        queens = []
        for suit_name, btn in self.queen_buttons.items():
            if btn.state == 'down' or hasattr(btn, 'has_queen') and btn.has_queen:
                queens.append({
                    "suit": suit_name,
                    "is_doubled": btn.state == 'down'
                })
        
        has_king = self.king_button.state == 'down' or (
            hasattr(self.king_button, 'has_king') and self.king_button.has_king
        )
        king_doubled = self.king_button.state == 'down'
        
        return {
            "total_cards": self.total_cards,
            "diamond_count": self.diamond_count,
            "queens": queens,
            "has_king_heart": has_king,
            "king_doubled": king_doubled
        }
    
    def calculate_score(self, instance):
        """حساب النقاط والانتقال لشاشة النتيجة"""
        data = self.get_input_data()
        
        # حفظ البيانات في الـ app
        app = self.manager.app
        app.current_round_data = data
        
        self.manager.current = 'doubled_selection'
    
    def go_back(self, instance):
        self.manager.current = 'home'
    
    def on_enter(self):
        """إعادة تعيين عند الدخول"""
        self.total_cards = 0
        self.diamond_count = 0
        self.cards_label.text = "0"
        self.diamond_label.text = "0"
        
        for btn in self.queen_buttons.values():
            btn.state = 'normal'
        self.king_button.state = 'normal'


class DoubledSelectionScreen(Screen):
    """شاشة اختيار البطاقات المدبلة من الخصم"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'doubled_selection'
        self.doubled_by_opponent = {}  # البطاقات التي دبلها الخصم
        self.doubled_to_opponent = {}  # البطاقات التي دبلناها للخصم
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # العنوان
        title = RTLLabel(
            text="🎯 اختيار التدبيل",
            font_size=dp(24),
            size_hint_y=None,
            height=dp(50),
            halign='center'
        )
        main_layout.add_widget(title)
        
        # منطقة التمرير
        scroll = ScrollView(size_hint_y=0.8)
        self.content = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        
        scroll.add_widget(self.content)
        main_layout.add_widget(scroll)
        
        # أزرار التحكم
        controls = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        calculate_btn = StyledButton(
            text="📊 النتيجة النهائية",
            on_press=self.show_result
        )
        controls.add_widget(calculate_btn)
        
        back_btn = StyledButton(
            text="🔙 رجوع",
            on_press=self.go_back
        )
        controls.add_widget(back_btn)
        
        main_layout.add_widget(controls)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        """بناء واجهة الاختيار عند الدخول"""
        self.content.clear_widgets()
        self.doubled_by_opponent = {}
        self.doubled_to_opponent = {}
        
        app = self.manager.app
        data = getattr(app, 'current_round_data', {})
        
        queens = data.get('queens', [])
        has_king = data.get('has_king_heart', False)
        
        # === القسم الأول: البطاقات التي دبلها الخصم (نحصل على سالب مضاعف) ===
        section1 = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(50))
        section1.add_widget(RTLLabel(
            text="❌ هل دبّل الخصم أياً من هذه؟",
            font_size=dp(18),
            halign='center',
            size_hint_y=None,
            height=dp(40)
        ))
        self.content.add_widget(section1)
        
        # عرض البنات الموجودة
        for queen_data in queens:
            suit = queen_data['suit']
            btn = ToggleButton(
                text=arabic(f"Q {suit} (مدبلة من الخصم)"),
                size_hint_y=None,
                height=dp(50),
                font_name=ARABIC_FONT if ARABIC_FONT else 'Roboto'
            )
            btn.bind(state=lambda instance, value, s=suit: self.toggle_opponent_doubled(s, value, 'queen'))
            self.content.add_widget(btn)
            self.doubled_by_opponent[f"Q_{suit}"] = False
        
        # شيخ القبة
        if has_king:
            king_btn = ToggleButton(
                text=arabic("K قبة (مدبل من الخصم)"),
                size_hint_y=None,
                height=dp(50),
                font_name=ARABIC_FONT if ARABIC_FONT else 'Roboto'
            )
            king_btn.bind(state=lambda instance, value: self.toggle_opponent_doubled('قبة', value, 'king'))
            self.content.add_widget(king_btn)
            self.doubled_by_opponent["K_قبة"] = False
        
        # === القسم الثاني: البطاقات التي دبلناها للخصم (نحصل على موجب) ===
        section2 = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60))
        section2.add_widget(RTLLabel(
            text="",
            size_hint_y=None,
            height=dp(10)
        ))
        section2.add_widget(RTLLabel(
            text="✅ هل دبّلت أنت للخصم؟ (تحصل على موجب)",
            font_size=dp(18),
            halign='center',
            size_hint_y=None,
            height=dp(40)
        ))
        self.content.add_widget(section2)
        
        # البنات الغير موجودة (التي أكلها الخصم)
        all_suits = ["بستوني", "ديناري", "قبة", "اسباتي"]
        existing_suits = [q['suit'] for q in queens]
        
        for suit in all_suits:
            if suit not in existing_suits:
                btn = ToggleButton(
                    text=arabic(f"Q {suit} (دبلتها للخصم)"),
                    size_hint_y=None,
                    height=dp(50),
                    background_color=(0.2, 0.6, 0.2, 1),
                    font_name=ARABIC_FONT if ARABIC_FONT else 'Roboto'
                )
                btn.bind(state=lambda instance, value, s=suit: self.toggle_my_doubled(s, value, 'queen'))
                self.content.add_widget(btn)
                self.doubled_to_opponent[f"Q_{suit}"] = False
        
        # شيخ القبة إذا لم يكن موجوداً
        if not has_king:
            king_btn = ToggleButton(
                text=arabic("K قبة (دبلته للخصم)"),
                size_hint_y=None,
                height=dp(50),
                background_color=(0.2, 0.6, 0.2, 1),
                font_name=ARABIC_FONT if ARABIC_FONT else 'Roboto'
            )
            king_btn.bind(state=lambda instance, value: self.toggle_my_doubled('قبة', value, 'king'))
            self.content.add_widget(king_btn)
            self.doubled_to_opponent["K_قبة"] = False
    
    def toggle_opponent_doubled(self, suit, state, card_type):
        """تبديل حالة التدبيل من الخصم"""
        key = f"{'Q' if card_type == 'queen' else 'K'}_{suit}"
        self.doubled_by_opponent[key] = (state == 'down')
    
    def toggle_my_doubled(self, suit, state, card_type):
        """تبديل حالة التدبيل للخصم"""
        key = f"{'Q' if card_type == 'queen' else 'K'}_{suit}"
        self.doubled_to_opponent[key] = (state == 'down')
    
    def show_result(self, instance):
        """عرض النتيجة النهائية"""
        app = self.manager.app
        
        # حفظ بيانات التدبيل
        app.doubled_by_opponent = self.doubled_by_opponent
        app.doubled_to_opponent = self.doubled_to_opponent
        
        self.manager.current = 'result'
    
    def go_back(self, instance):
        self.manager.current = 'manual'


class ResultScreen(Screen):
    """شاشة النتيجة"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'result'
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # العنوان
        title = RTLLabel(
            text="📊 نتيجة الجولة",
            font_size=dp(28),
            size_hint_y=None,
            height=dp(60),
            halign='center'
        )
        main_layout.add_widget(title)
        
        # منطقة النتائج
        scroll = ScrollView(size_hint_y=0.75)
        self.result_content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.result_content.bind(minimum_height=self.result_content.setter('height'))
        
        scroll.add_widget(self.result_content)
        main_layout.add_widget(scroll)
        
        # أزرار التحكم
        controls = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        new_round_btn = StyledButton(
            text="🔄 جولة جديدة",
            on_press=self.new_round
        )
        controls.add_widget(new_round_btn)
        
        home_btn = StyledButton(
            text="🏠 الرئيسية",
            on_press=self.go_home
        )
        controls.add_widget(home_btn)
        
        main_layout.add_widget(controls)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        """حساب وعرض النتيجة"""
        self.result_content.clear_widgets()
        
        app = self.manager.app
        data = getattr(app, 'current_round_data', {})
        doubled_by = getattr(app, 'doubled_by_opponent', {})
        doubled_to = getattr(app, 'doubled_to_opponent', {})
        
        # === حساب النقاط ===
        total_cards = data.get('total_cards', 0)
        diamond_count = data.get('diamond_count', 0)
        queens = data.get('queens', [])
        has_king = data.get('has_king_heart', False)
        
        # نقاط الأكلات
        tricks = total_cards // 4
        tricks_points = -tricks * 15
        
        # نقاط الديناري
        diamond_points = -diamond_count * 10
        
        # نقاط البنات
        queens_points = 0
        queens_details = []
        for queen in queens:
            suit = queen['suit']
            is_doubled = doubled_by.get(f"Q_{suit}", False)
            value = -50 if is_doubled else -25
            queens_points += value
            doubled_text = " (مدبلة)" if is_doubled else ""
            queens_details.append(f"Q {suit}{doubled_text}: {value}")
        
        # نقاط شيخ القبة
        king_points = 0
        king_detail = ""
        if has_king:
            is_doubled = doubled_by.get("K_قبة", False)
            king_points = -150 if is_doubled else -75
            doubled_text = " (مدبل)" if is_doubled else ""
            king_detail = f"K قبة{doubled_text}: {king_points}"
        
        # مكافأة التدبيل للخصم (موجب)
        bonus_points = 0
        bonus_details = []
        for key, is_doubled in doubled_to.items():
            if is_doubled:
                if key.startswith("Q_"):
                    bonus_points += 25
                    bonus_details.append(f"{key}: +25")
                elif key.startswith("K_"):
                    bonus_points += 75
                    bonus_details.append(f"{key}: +75")
        
        # المجموع
        total = tricks_points + diamond_points + queens_points + king_points + bonus_points
        
        # === عرض النتائج ===
        results = [
            ("═" * 30, None),
            (f"🃏 الأكلات: {tricks}", tricks_points),
            (f"♦️ الديناري: {diamond_count}", diamond_points),
        ]
        
        for detail in queens_details:
            results.append((f"👸 {detail}", None))
        
        if queens_details:
            results.append((f"مجموع البنات:", queens_points))
        
        if king_detail:
            results.append((f"👑 {king_detail}", None))
        
        if bonus_details:
            results.append(("─" * 30, None))
            results.append(("✨ مكافأة التدبيل:", None))
            for detail in bonus_details:
                results.append((f"   {detail}", None))
            results.append((f"مجموع المكافأة:", bonus_points))
        
        results.append(("═" * 30, None))
        
        for text, points in results:
            row = BoxLayout(size_hint_y=None, height=dp(40))
            row.add_widget(RTLLabel(text=text, halign='right'))
            if points is not None:
                row.add_widget(Label(text=str(points), font_size=dp(18), size_hint_x=0.3))
            self.result_content.add_widget(row)
        
        # === نقاط الفريقين ===
        # مجموع الجولة للفريقين يجب أن يساوي -500
        ROUND_TOTAL = -500
        team2_score = ROUND_TOTAL - total
        
        # نقاط فريقك
        team1_row = BoxLayout(size_hint_y=None, height=dp(60))
        team1_color = (0.2, 0.8, 0.2, 1) if total > -250 else (0.8, 0.2, 0.2, 1)
        team1_label = RTLLabel(
            text=f"📌 نقاط فريقك: {total}",
            font_size=dp(24),
            halign='center',
            color=team1_color
        )
        team1_row.add_widget(team1_label)
        self.result_content.add_widget(team1_row)
        
        # نقاط الخصم
        team2_row = BoxLayout(size_hint_y=None, height=dp(60))
        team2_color = (0.2, 0.8, 0.2, 1) if team2_score > -250 else (0.8, 0.2, 0.2, 1)
        team2_label = RTLLabel(
            text=f"📌 نقاط الخصم: {team2_score}",
            font_size=dp(24),
            halign='center',
            color=team2_color
        )
        team2_row.add_widget(team2_label)
        self.result_content.add_widget(team2_row)
        
        # تأكيد المجموع
        verify_row = BoxLayout(size_hint_y=None, height=dp(40))
        verify_label = RTLLabel(
            text=f"✓ المجموع: {total} + {team2_score} = {total + team2_score}",
            font_size=dp(16),
            halign='center',
            color=(0.5, 0.5, 0.5, 1)
        )
        verify_row.add_widget(verify_label)
        self.result_content.add_widget(verify_row)
        
        # حفظ في السجل
        self.save_to_history(total, team2_score, data)
    
    def save_to_history(self, team1_score, team2_score, data):
        """حفظ النتيجة في السجل"""
        app = self.manager.app
        if not hasattr(app, 'history'):
            app.history = []
        
        from datetime import datetime
        app.history.append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'team1_score': team1_score,
            'team2_score': team2_score,
            'data': data
        })
    
    def new_round(self, instance):
        self.manager.current = 'manual'
    
    def go_home(self, instance):
        self.manager.current = 'home'


class HistoryScreen(Screen):
    """شاشة السجل"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'history'
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # العنوان
        title = RTLLabel(
            text="📜 سجل النقاط",
            font_size=dp(24),
            size_hint_y=None,
            height=dp(50),
            halign='center'
        )
        main_layout.add_widget(title)
        
        # منطقة السجل
        scroll = ScrollView(size_hint_y=0.8)
        self.history_content = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        self.history_content.bind(minimum_height=self.history_content.setter('height'))
        
        scroll.add_widget(self.history_content)
        main_layout.add_widget(scroll)
        
        # المجموع الكلي
        self.total_label = RTLLabel(
            text="المجموع: 0",
            font_size=dp(22),
            size_hint_y=None,
            height=dp(50),
            halign='center'
        )
        main_layout.add_widget(self.total_label)
        
        # أزرار التحكم
        controls = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        clear_btn = StyledButton(
            text="🗑️ مسح السجل",
            on_press=self.clear_history
        )
        controls.add_widget(clear_btn)
        
        back_btn = StyledButton(
            text="🔙 رجوع",
            on_press=self.go_back
        )
        controls.add_widget(back_btn)
        
        main_layout.add_widget(controls)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        """تحديث السجل عند الدخول"""
        self.history_content.clear_widgets()
        
        app = self.manager.app
        history = getattr(app, 'history', [])
        
        team1_total = 0
        team2_total = 0
        round_count = len(history)
        
        # عنوان الجدول
        if history:
            header = BoxLayout(size_hint_y=None, height=dp(40))
            header.add_widget(RTLLabel(text="الجولة", halign='center', size_hint_x=0.3))
            header.add_widget(RTLLabel(text="فريقك", halign='center', size_hint_x=0.35))
            header.add_widget(RTLLabel(text="الخصم", halign='center', size_hint_x=0.35))
            self.history_content.add_widget(header)
        
        for i, entry in enumerate(history, 1):
            team1 = entry.get('team1_score', entry.get('total', 0))  # دعم السجل القديم
            team2 = entry.get('team2_score', -500 - team1)
            team1_total += team1
            team2_total += team2
            
            row = BoxLayout(size_hint_y=None, height=dp(50))
            
            # رقم الجولة
            row.add_widget(Label(text=f"{i}", font_size=dp(16), size_hint_x=0.3))
            
            # نقاط فريقك
            color1 = (0.2, 0.8, 0.2, 1) if team1 > -250 else (0.8, 0.2, 0.2, 1)
            row.add_widget(Label(text=str(team1), font_size=dp(18), size_hint_x=0.35, color=color1))
            
            # نقاط الخصم
            color2 = (0.2, 0.8, 0.2, 1) if team2 > -250 else (0.8, 0.2, 0.2, 1)
            row.add_widget(Label(text=str(team2), font_size=dp(18), size_hint_x=0.35, color=color2))
            
            self.history_content.add_widget(row)
        
        if not history:
            self.history_content.add_widget(RTLLabel(
                text="لا يوجد سجل بعد",
                halign='center',
                size_hint_y=None,
                height=dp(100)
            ))
        else:
            # خط فاصل
            self.history_content.add_widget(RTLLabel(
                text="─" * 40,
                halign='center',
                size_hint_y=None,
                height=dp(20)
            ))
            
            # صف المجاميع
            totals_row = BoxLayout(size_hint_y=None, height=dp(50))
            totals_row.add_widget(RTLLabel(text="المجموع:", halign='center', size_hint_x=0.3, font_size=dp(16)))
            
            color1 = (0.2, 0.8, 0.2, 1) if team1_total > team2_total else (0.8, 0.2, 0.2, 1)
            totals_row.add_widget(Label(text=str(team1_total), font_size=dp(20), size_hint_x=0.35, color=color1, bold=True))
            
            color2 = (0.2, 0.8, 0.2, 1) if team2_total > team1_total else (0.8, 0.2, 0.2, 1)
            totals_row.add_widget(Label(text=str(team2_total), font_size=dp(20), size_hint_x=0.35, color=color2, bold=True))
            
            self.history_content.add_widget(totals_row)
        
        # المجموع المتوقع
        expected_total = round_count * -500
        actual_total = team1_total + team2_total
        
        self.total_label.text = f"المجموع الكلي: {actual_total} (المتوقع: {expected_total})"
    
    def clear_history(self, instance):
        """مسح السجل"""
        app = self.manager.app
        app.history = []
        self.on_enter()
    
    def go_back(self, instance):
        self.manager.current = 'home'
