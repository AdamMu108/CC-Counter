"""
كاشف البطاقات - نسخة بسيطة
"""

# هذا الملف للتوافق فقط - الميزة غير مفعلة حالياً

class DetectedCard:
    def __init__(self, code='', rank='', suit=''):
        self.card_code = code
        self.rank = rank
        self.suit = suit
        self.confidence = 1.0
    
    def is_diamond(self):
        return self.suit == 'D'
    
    def is_queen(self):
        return self.rank == 'Q'
    
    def is_king_of_hearts(self):
        return self.rank == 'K' and self.suit == 'H'


class CardDetector:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.is_ready = False
        self.last_error = None
    
    def detect_cards(self, image):
        return []
