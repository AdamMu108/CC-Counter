"""
تطبيق عداد الكومبلكس شراكة
CC Counter - Complex Complex Card Game Score Counter
Modern Version
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.utils import platform
import os

# تسجيل الخط العربي
try:
    FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'NotoSansArabic.ttf')
    if os.path.exists(FONT_PATH):
        LabelBase.register(name='Arabic', fn_regular=FONT_PATH)
except Exception as e:
    print(f"Font error: {e}")

# استيراد الشاشات
from modern_ui import (
    WelcomeScreen,
    GameScreen,
    CameraScreen,
    CameraResultScreen,
    CountingFromCameraScreen,
    CountingScreen,
    DoublingScreen,
    HistoryScreen,
    SettingsScreen
)

from app_config import POINTS


class CCCounterApp(App):
    """التطبيق الرئيسي"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "CC Counter"
        
        # بيانات اللعبة
        self.team1_name = "فريقنا"
        self.team2_name = "الخصم"
        self.team1_total = 0
        self.team2_total = 0
        self.round_number = 0
        self.history = []
        self.current_round_data = {}
        
        # إعدادات API
        self.api_key = ""
        self._load_api_key()
    
    def build(self):
        """بناء واجهة التطبيق"""
        
        # إعدادات النافذة
        if platform not in ('android', 'ios'):
            Window.size = (400, 750)
        
        # مدير الشاشات
        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.app = self
        
        # إضافة الشاشات
        self.sm.add_widget(WelcomeScreen())
        self.sm.add_widget(GameScreen())
        self.sm.add_widget(CameraScreen())
        self.sm.add_widget(CameraResultScreen())
        self.sm.add_widget(CountingFromCameraScreen())
        self.sm.add_widget(CountingScreen())
        self.sm.add_widget(DoublingScreen())
        self.sm.add_widget(HistoryScreen())
        self.sm.add_widget(SettingsScreen())
        
        return self.sm
    
    def reset_game(self):
        """إعادة تعيين اللعبة"""
        self.team1_total = 0
        self.team2_total = 0
        self.round_number = 0
        self.history = []
        self.current_round_data = {}
    
    def get_expected_total(self):
        """المجموع المتوقع"""
        return self.round_number * POINTS['round_total']
    
    def _load_api_key(self):
        """تحميل مفتاح API من الملف"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_config.txt')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.api_key = f.read().strip()
                    if self.api_key:
                        # تحديث card_detector
                        import card_detector
                        card_detector.ROBOFLOW_API_KEY = self.api_key
        except Exception as e:
            print(f"Error loading API key: {e}")
    
    def on_start(self):
        print("=" * 50)
        print("  CC Counter - عداد الكومبلكس شراكة")
        print("=" * 50)
    
    def on_stop(self):
        print("تم إغلاق التطبيق")


def main():
    CCCounterApp().run()


if __name__ == "__main__":
    main()
