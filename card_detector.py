"""
كاشف البطاقات باستخدام معالجة الصور
Card Detector using Image Processing (OpenCV)
"""

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class CardSuit(Enum):
    """أنواع الورق"""
    SPADE = "بستوني"      # ♠
    DIAMOND = "ديناري"    # ♦
    HEART = "قبة"         # ♥
    CLUB = "اسباتي"       # ♣


class CardRank(Enum):
    """رتب الورق"""
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"


@dataclass
class DetectedCard:
    """بطاقة مكتشفة"""
    rank: Optional[CardRank]
    suit: Optional[CardSuit]
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    contour: np.ndarray = None


class CardDetector:
    """
    كاشف البطاقات باستخدام معالجة الصور
    
    يستخدم OpenCV لاكتشاف البطاقات وتحديد نوعها ورتبتها
    """
    
    # ألوان الأنواع للتعرف
    RED_SUITS = [CardSuit.HEART, CardSuit.DIAMOND]
    BLACK_SUITS = [CardSuit.SPADE, CardSuit.CLUB]
    
    # أبعاد البطاقة القياسية (نسبة العرض للطول)
    CARD_ASPECT_RATIO = 0.7  # تقريباً
    
    # حدود المساحة للبطاقة
    MIN_CARD_AREA = 5000
    MAX_CARD_AREA = 500000
    
    def __init__(self):
        self.detected_cards: List[DetectedCard] = []
        self.processed_image = None
        
        # قوالب الرموز (يمكن تحميلها من ملفات)
        self.rank_templates = {}
        self.suit_templates = {}
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        معالجة مسبقة للصورة
        
        Args:
            image: الصورة الأصلية (BGR)
        
        Returns:
            صورة معالجة (تدرج رمادي مع تحسين التباين)
        """
        # تحويل لتدرج رمادي
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # تحسين التباين
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # تنعيم خفيف لإزالة الضوضاء
        blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
        
        return blurred
    
    def find_card_contours(self, image: np.ndarray) -> List[np.ndarray]:
        """
        إيجاد حدود البطاقات في الصورة
        
        Args:
            image: الصورة المعالجة (تدرج رمادي)
        
        Returns:
            قائمة بحدود البطاقات
        """
        # تحويل ثنائي (Thresholding)
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # إيجاد الحدود
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        card_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # تصفية حسب المساحة
            if self.MIN_CARD_AREA < area < self.MAX_CARD_AREA:
                # تقريب الحدود لمضلع
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                
                # البطاقة يجب أن تكون مستطيلة (4 زوايا تقريباً)
                if len(approx) == 4:
                    card_contours.append(contour)
        
        return card_contours
    
    def extract_card_image(self, image: np.ndarray, contour: np.ndarray) -> np.ndarray:
        """
        استخراج صورة البطاقة وتصحيح المنظور
        
        Args:
            image: الصورة الأصلية
            contour: حدود البطاقة
        
        Returns:
            صورة البطاقة المصححة
        """
        # إيجاد الزوايا الأربع
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        
        if len(approx) != 4:
            # إذا لم نجد 4 زوايا، نستخدم المستطيل المحيط
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            approx = np.int32(box)
        
        # ترتيب النقاط (أعلى-يسار، أعلى-يمين، أسفل-يمين، أسفل-يسار)
        pts = approx.reshape(4, 2)
        rect = self._order_points(pts)
        
        # حساب أبعاد البطاقة الجديدة
        (tl, tr, br, bl) = rect
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_width = max(int(width_a), int(width_b))
        
        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_height = max(int(height_a), int(height_b))
        
        # تصحيح المنظور
        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]
        ], dtype="float32")
        
        matrix = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
        
        return warped
    
    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """ترتيب نقاط المستطيل"""
        rect = np.zeros((4, 2), dtype="float32")
        
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # أعلى-يسار
        rect[2] = pts[np.argmax(s)]  # أسفل-يمين
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # أعلى-يمين
        rect[3] = pts[np.argmax(diff)]  # أسفل-يسار
        
        return rect
    
    def detect_suit_color(self, card_image: np.ndarray) -> str:
        """
        تحديد لون البطاقة (أحمر أو أسود)
        
        Args:
            card_image: صورة البطاقة
        
        Returns:
            "red" أو "black"
        """
        # تحويل لـ HSV
        hsv = cv2.cvtColor(card_image, cv2.COLOR_BGR2HSV)
        
        # نطاق الأحمر في HSV
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        
        red_pixels = cv2.countNonZero(red_mask)
        total_pixels = card_image.shape[0] * card_image.shape[1]
        
        # إذا كان أكثر من 5% أحمر، فالبطاقة حمراء
        if red_pixels / total_pixels > 0.05:
            return "red"
        return "black"
    
    def identify_rank(self, corner_image: np.ndarray) -> Optional[CardRank]:
        """
        تحديد رتبة البطاقة من صورة الزاوية
        
        Args:
            corner_image: صورة زاوية البطاقة
        
        Returns:
            رتبة البطاقة أو None
        """
        # هنا يمكن استخدام Template Matching أو ML
        # للتبسيط، سنستخدم OCR بسيط أو مقارنة القوالب
        
        # تحويل لثنائي
        gray = cv2.cvtColor(corner_image, cv2.COLOR_BGR2GRAY) if len(corner_image.shape) == 3 else corner_image
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
        
        # إيجاد الحدود في الزاوية
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # أكبر حدود هي الرقم/الحرف
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        
        # نسبة العرض للطول تساعد في التعرف
        aspect_ratio = w / h if h > 0 else 0
        
        # تحليل بسيط (يمكن تحسينه بـ ML)
        # هذا مجرد مثال - في التطبيق الحقيقي تحتاج نموذج مدرب
        
        return None  # placeholder
    
    def identify_suit(self, corner_image: np.ndarray, color: str) -> Optional[CardSuit]:
        """
        تحديد نوع البطاقة من صورة الزاوية واللون
        
        Args:
            corner_image: صورة زاوية البطاقة (الجزء السفلي من الزاوية)
            color: لون البطاقة ("red" أو "black")
        
        Returns:
            نوع البطاقة أو None
        """
        # تحويل لثنائي
        gray = cv2.cvtColor(corner_image, cv2.COLOR_BGR2GRAY) if len(corner_image.shape) == 3 else corner_image
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
        
        # إيجاد الحدود
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # أكبر حدود هي رمز النوع
        largest = max(contours, key=cv2.contourArea)
        
        # تحليل شكل الرمز
        # ♠ بستوني - أسود، شكل مدبب
        # ♦ ديناري - أحمر، شكل ماسي
        # ♥ قبة - أحمر، شكل قلب
        # ♣ اسباتي - أسود، شكل ثلاثي الفصوص
        
        # تحليل بسيط حسب اللون وخصائص الشكل
        area = cv2.contourArea(largest)
        perimeter = cv2.arcLength(largest, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        if color == "red":
            # التمييز بين القبة والديناري
            if circularity > 0.7:  # الماسة أكثر دائرية
                return CardSuit.DIAMOND
            else:
                return CardSuit.HEART
        else:
            # التمييز بين البستوني والاسباتي
            hull = cv2.convexHull(largest)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            
            if solidity > 0.8:  # البستوني أكثر صلابة
                return CardSuit.SPADE
            else:
                return CardSuit.CLUB
    
    def detect_cards(self, image: np.ndarray) -> List[DetectedCard]:
        """
        اكتشاف جميع البطاقات في الصورة
        
        Args:
            image: الصورة الأصلية (BGR)
        
        Returns:
            قائمة بالبطاقات المكتشفة
        """
        self.detected_cards = []
        
        # معالجة مسبقة
        processed = self.preprocess_image(image)
        self.processed_image = processed
        
        # إيجاد حدود البطاقات
        contours = self.find_card_contours(processed)
        
        for contour in contours:
            # استخراج صورة البطاقة
            card_image = self.extract_card_image(image, contour)
            
            if card_image.size == 0:
                continue
            
            # تحديد اللون
            color = self.detect_suit_color(card_image)
            
            # استخراج منطقة الزاوية (حيث الرقم والرمز)
            h, w = card_image.shape[:2]
            corner = card_image[0:int(h*0.25), 0:int(w*0.2)]
            
            # تحديد الرتبة والنوع
            rank = self.identify_rank(corner)
            suit = self.identify_suit(corner, color)
            
            # إيجاد المستطيل المحيط
            x, y, w, h = cv2.boundingRect(contour)
            
            detected = DetectedCard(
                rank=rank,
                suit=suit,
                confidence=0.5,  # placeholder
                bounding_box=(x, y, w, h),
                contour=contour
            )
            
            self.detected_cards.append(detected)
        
        return self.detected_cards
    
    def draw_detections(self, image: np.ndarray) -> np.ndarray:
        """
        رسم البطاقات المكتشفة على الصورة
        
        Args:
            image: الصورة الأصلية
        
        Returns:
            صورة مع رسومات البطاقات المكتشفة
        """
        result = image.copy()
        
        for card in self.detected_cards:
            x, y, w, h = card.bounding_box
            
            # رسم المستطيل
            color = (0, 255, 0)  # أخضر
            cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)
            
            # كتابة المعلومات
            text = ""
            if card.rank:
                text += card.rank.value
            if card.suit:
                text += " " + card.suit.value
            
            if text:
                cv2.putText(result, text, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return result
    
    def get_detection_summary(self) -> Dict:
        """
        الحصول على ملخص الاكتشاف
        
        Returns:
            قاموس بملخص البطاقات المكتشفة
        """
        summary = {
            "total_cards": len(self.detected_cards),
            "diamonds": [],
            "queens": [],
            "king_heart": None,
            "diamond_count": 0
        }
        
        for card in self.detected_cards:
            # عد الديناري
            if card.suit == CardSuit.DIAMOND:
                summary["diamond_count"] += 1
                summary["diamonds"].append(card)
            
            # البنات
            if card.rank == CardRank.QUEEN:
                summary["queens"].append({
                    "suit": card.suit,
                    "is_doubled": False
                })
            
            # شيخ القبة
            if card.rank == CardRank.KING and card.suit == CardSuit.HEART:
                summary["king_heart"] = True
        
        return summary


class ManualCardInput:
    """
    إدخال البطاقات يدوياً كبديل عن معالجة الصور
    للاستخدام عندما لا تعمل معالجة الصور بشكل جيد
    """
    
    @staticmethod
    def create_detection_summary(
        total_cards: int,
        diamond_count: int,
        queens: List[str],  # قائمة بأنواع البنات ["قبة", "ديناري", ...]
        has_king_heart: bool
    ) -> Dict:
        """
        إنشاء ملخص من إدخال يدوي
        
        Args:
            total_cards: عدد الأوراق الكلي
            diamond_count: عدد أوراق الديناري
            queens: قائمة بأنواع البنات
            has_king_heart: هل يوجد شيخ القبة
        
        Returns:
            ملخص بنفس تنسيق CardDetector.get_detection_summary()
        """
        suit_map = {
            "بستوني": CardSuit.SPADE,
            "ديناري": CardSuit.DIAMOND,
            "قبة": CardSuit.HEART,
            "اسباتي": CardSuit.CLUB
        }
        
        summary = {
            "total_cards": total_cards,
            "diamond_count": diamond_count,
            "queens": [],
            "king_heart": has_king_heart
        }
        
        for queen_suit in queens:
            suit = suit_map.get(queen_suit)
            if suit:
                summary["queens"].append({
                    "suit": suit,
                    "is_doubled": False
                })
        
        return summary


# مثال على الاستخدام
if __name__ == "__main__":
    # اختبار الكاشف
    detector = CardDetector()
    
    # محاكاة صورة (في التطبيق الحقيقي تأتي من الكاميرا)
    # test_image = cv2.imread("test_cards.jpg")
    # if test_image is not None:
    #     cards = detector.detect_cards(test_image)
    #     print(f"تم اكتشاف {len(cards)} بطاقة")
    #     
    #     result = detector.draw_detections(test_image)
    #     cv2.imshow("Detected Cards", result)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    
    # اختبار الإدخال اليدوي
    manual = ManualCardInput()
    summary = manual.create_detection_summary(
        total_cards=20,
        diamond_count=3,
        queens=["قبة", "ديناري", "بستوني"],
        has_king_heart=True
    )
    print("ملخص الإدخال اليدوي:")
    print(summary)
