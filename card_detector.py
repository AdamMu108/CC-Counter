"""
كاشف البطاقات باستخدام Roboflow API
Card Detector using Roboflow API (Online)

النموذج: Playing Cards Detection (52 cards)
الدقة: ~95%
المجاني: 1000 صورة/شهر
"""

import os
import json
import base64
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from urllib import request, error
from io import BytesIO

# محاولة استيراد PIL
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None


# ===== إعدادات API =====

# Roboflow API - نموذج البطاقات المجاني
ROBOFLOW_API_KEY = "YOUR_API_KEY_HERE"  # ← ضع مفتاحك هنا
ROBOFLOW_MODEL = "playing-cards-ow27d"
ROBOFLOW_VERSION = "4"
ROBOFLOW_API_URL = f"https://detect.roboflow.com/{ROBOFLOW_MODEL}/{ROBOFLOW_VERSION}"


# ===== الثوابت =====

SUITS = {
    'S': ('بستوني', '♠'),
    'H': ('قبة', '♥'),
    'D': ('ديناري', '♦'),
    'C': ('اسباتي', '♣'),
}

RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

RANK_NAMES = {
    'A': 'آص', '2': '2', '3': '3', '4': '4', '5': '5',
    '6': '6', '7': '7', '8': '8', '9': '9', '10': '10',
    'J': 'ولد', 'Q': 'بنت', 'K': 'شيخ'
}

# تحويل أسماء الكلاسات من Roboflow لصيغتنا
# Roboflow يستخدم: "10C", "10D", "10H", "10S", "2C", etc.
CLASS_MAPPING = {}
for suit_code in ['C', 'D', 'H', 'S']:
    for rank in RANKS:
        # Roboflow format: "10C", "2D", "QH", etc.
        rf_class = f"{rank}{suit_code}"
        CLASS_MAPPING[rf_class] = (rank, suit_code)


# ===== البطاقة المكتشفة =====

@dataclass
class DetectedCard:
    """بطاقة مكتشفة"""
    card_code: str
    rank: str
    suit: str
    confidence: float = 1.0
    box: Tuple[float, float, float, float] = None  # x, y, w, h
    
    @property
    def suit_name(self) -> str:
        return SUITS.get(self.suit, ('', ''))[0]
    
    @property
    def suit_symbol(self) -> str:
        return SUITS.get(self.suit, ('', ''))[1]
    
    @property
    def rank_name(self) -> str:
        return RANK_NAMES.get(self.rank, self.rank)
    
    @property
    def display_name(self) -> str:
        return f"{self.rank_name} {self.suit_name}"
    
    @property
    def symbol(self) -> str:
        return f"{self.rank}{self.suit_symbol}"
    
    def is_diamond(self) -> bool:
        return self.suit == 'D'
    
    def is_queen(self) -> bool:
        return self.rank == 'Q'
    
    def is_king_of_hearts(self) -> bool:
        return self.rank == 'K' and self.suit == 'H'
    
    @classmethod
    def from_code(cls, code: str, confidence: float = 1.0, box=None) -> Optional['DetectedCard']:
        """إنشاء بطاقة من الكود"""
        if len(code) < 2:
            return None
        
        suit = code[-1].upper()
        rank = code[:-1].upper()
        
        if suit not in SUITS or rank not in RANK_NAMES:
            return None
        
        return cls(
            card_code=f"{rank}{suit}",
            rank=rank,
            suit=suit,
            confidence=confidence,
            box=box
        )


# ===== كاشف البطاقات =====

class CardDetector:
    """
    كاشف البطاقات باستخدام Roboflow API
    """
    
    def __init__(self, api_key: str = None):
        """
        تهيئة الكاشف
        
        Args:
            api_key: مفتاح Roboflow API (اختياري)
        """
        self.api_key = api_key or ROBOFLOW_API_KEY
        self.is_ready = self.api_key and self.api_key != "YOUR_API_KEY_HERE"
        self.last_error = None
        
    def set_api_key(self, api_key: str):
        """تعيين مفتاح API"""
        self.api_key = api_key
        self.is_ready = bool(api_key)
    
    def _image_to_base64(self, image) -> str:
        """تحويل صورة PIL لـ base64"""
        if not PIL_AVAILABLE:
            return None
        
        # إذا كانت الصورة مسار
        if isinstance(image, str):
            with open(image, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        
        # إذا كانت صورة PIL
        buffer = BytesIO()
        
        # تحويل لـ RGB إذا لزم
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        image.save(buffer, format='JPEG', quality=85)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def _resize_image(self, image, max_size: int = 640):
        """تصغير الصورة للتحسين"""
        if not PIL_AVAILABLE:
            return image
        
        if isinstance(image, str):
            image = Image.open(image)
        
        # حساب الحجم الجديد
        w, h = image.size
        if max(w, h) > max_size:
            ratio = max_size / max(w, h)
            new_size = (int(w * ratio), int(h * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def detect_cards(self, image, confidence_threshold: float = 0.4) -> List[DetectedCard]:
        """
        اكتشاف البطاقات في الصورة
        
        Args:
            image: صورة PIL أو مسار الصورة أو bytes
            confidence_threshold: الحد الأدنى للثقة (0.0-1.0)
            
        Returns:
            قائمة البطاقات المكتشفة
        """
        self.last_error = None
        
        if not self.is_ready:
            self.last_error = "API key غير موجود"
            return []
        
        try:
            # تصغير الصورة
            if PIL_AVAILABLE and not isinstance(image, bytes):
                image = self._resize_image(image)
            
            # تحويل لـ base64
            if isinstance(image, bytes):
                img_base64 = base64.b64encode(image).decode('utf-8')
            else:
                img_base64 = self._image_to_base64(image)
            
            if not img_base64:
                self.last_error = "فشل تحويل الصورة"
                return []
            
            # إرسال الطلب
            url = f"{ROBOFLOW_API_URL}?api_key={self.api_key}&confidence={int(confidence_threshold * 100)}"
            
            req = request.Request(
                url,
                data=img_base64.encode('utf-8'),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            with request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            # تحليل النتائج
            return self._parse_response(result, confidence_threshold)
            
        except error.HTTPError as e:
            self.last_error = f"خطأ HTTP: {e.code}"
            if e.code == 401:
                self.last_error = "مفتاح API غير صالح"
            elif e.code == 429:
                self.last_error = "تجاوزت الحد المسموح (1000 صورة/شهر)"
            return []
            
        except error.URLError as e:
            self.last_error = f"خطأ اتصال: {e.reason}"
            return []
            
        except Exception as e:
            self.last_error = f"خطأ: {str(e)}"
            return []
    
    def _parse_response(self, response: dict, min_confidence: float) -> List[DetectedCard]:
        """تحليل استجابة API"""
        cards = []
        
        predictions = response.get('predictions', [])
        
        for pred in predictions:
            class_name = pred.get('class', '')
            confidence = pred.get('confidence', 0)
            
            if confidence < min_confidence:
                continue
            
            # استخراج الإحداثيات
            x = pred.get('x', 0)
            y = pred.get('y', 0)
            w = pred.get('width', 0)
            h = pred.get('height', 0)
            box = (x - w/2, y - h/2, w, h)  # تحويل من center إلى corner
            
            # إنشاء البطاقة
            card = DetectedCard.from_code(class_name, confidence, box)
            if card:
                cards.append(card)
        
        # ترتيب حسب الثقة
        cards.sort(key=lambda c: c.confidence, reverse=True)
        
        # إزالة التكرارات (نفس البطاقة مكتشفة أكثر من مرة)
        seen = set()
        unique_cards = []
        for card in cards:
            if card.card_code not in seen:
                seen.add(card.card_code)
                unique_cards.append(card)
        
        return unique_cards
    
    def detect_from_file(self, image_path: str, confidence_threshold: float = 0.4) -> List[DetectedCard]:
        """اكتشاف من ملف صورة"""
        return self.detect_cards(image_path, confidence_threshold)
    
    def detect_from_bytes(self, image_bytes: bytes, confidence_threshold: float = 0.4) -> List[DetectedCard]:
        """اكتشاف من bytes"""
        return self.detect_cards(image_bytes, confidence_threshold)
    
    def count_for_game(self, cards: List[DetectedCard]) -> Dict[str, int]:
        """حساب الإحصائيات للعبة"""
        return {
            'total': len(cards),
            'diamonds': sum(1 for c in cards if c.is_diamond()),
            'queens': sum(1 for c in cards if c.is_queen()),
            'king_of_hearts': sum(1 for c in cards if c.is_king_of_hearts()),
        }
    
    def create_cards_manual(self, diamonds: int = 0, queens: int = 0, 
                           king_of_hearts: bool = False) -> List[DetectedCard]:
        """إنشاء بطاقات يدوياً (للاختبار)"""
        cards = []
        
        for i in range(min(diamonds, 13)):
            rank = RANKS[i]
            cards.append(DetectedCard(
                card_code=f"{rank}D",
                rank=rank,
                suit='D'
            ))
        
        other_suits = ['S', 'H', 'C']
        for i in range(min(queens, 3)):
            suit = other_suits[i]
            cards.append(DetectedCard(
                card_code=f"Q{suit}",
                rank='Q',
                suit=suit
            ))
        
        if king_of_hearts:
            cards.append(DetectedCard(
                card_code='KH',
                rank='K',
                suit='H'
            ))
        
        return cards


# ===== دوال مساعدة =====

def get_detector(api_key: str = None) -> CardDetector:
    """الحصول على كاشف البطاقات"""
    return CardDetector(api_key)


def calculate_score(tricks: int = 0, diamonds: int = 0, queens: int = 0,
                   king_of_hearts: bool = False, doubled: bool = False) -> int:
    """حساب النقاط"""
    score = 0
    score -= tricks * 15
    score -= diamonds * 10
    queen_points = -50 if doubled else -25
    score += queens * queen_points
    if king_of_hearts:
        score += -150 if doubled else -75
    return score


# ===== الاختبار =====

if __name__ == "__main__":
    print("=" * 50)
    print("   كاشف البطاقات - Roboflow API")
    print("=" * 50)
    
    detector = CardDetector()
    
    print(f"\nحالة API: {'جاهز ✓' if detector.is_ready else 'يحتاج مفتاح API ✗'}")
    
    if not detector.is_ready:
        print("\n" + "-" * 50)
        print("للحصول على مفتاح API مجاني:")
        print("1. اذهب إلى: https://roboflow.com")
        print("2. أنشئ حساب مجاني")
        print("3. اذهب إلى Settings → API Keys")
        print("4. انسخ المفتاح وضعه في الكود")
        print("-" * 50)
    
    # اختبار يدوي
    print("\n--- اختبار يدوي ---")
    cards = detector.create_cards_manual(diamonds=3, queens=2, king_of_hearts=True)
    
    for card in cards:
        print(f"  {card.symbol} - {card.display_name}")
    
    stats = detector.count_for_game(cards)
    print(f"\nالإحصائيات: ديناري={stats['diamonds']}, بنات={stats['queens']}, شيخ القبة={stats['king_of_hearts']}")
