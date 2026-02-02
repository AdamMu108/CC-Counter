"""
حاسبة نقاط لعبة الشدة كومبلكس كومبلكس
Score Calculator for Complex Complex Card Game
"""

from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum


class CardSuit(Enum):
    """أنواع الورق"""
    SPADE = "بستوني"      # ♠
    DIAMOND = "ديناري"    # ♦
    HEART = "قبة"         # ♥
    CLUB = "اسباتي"       # ♣


class CardRank(Enum):
    """رتب الورق"""
    QUEEN = "Q"           # بنت
    KING = "K"            # شيخ


@dataclass
class SpecialCard:
    """بطاقة خاصة (بنت أو شيخ القبة)"""
    rank: CardRank
    suit: CardSuit
    is_doubled: bool = False  # هل تم تدبيلها
    
    @property
    def base_value(self) -> int:
        """القيمة الأساسية للبطاقة"""
        if self.rank == CardRank.QUEEN:
            return 25
        elif self.rank == CardRank.KING and self.suit == CardSuit.HEART:
            return 75
        return 0
    
    @property
    def actual_value(self) -> int:
        """القيمة الفعلية بعد التدبيل"""
        return self.base_value * 2 if self.is_doubled else self.base_value
    
    def __str__(self) -> str:
        doubled_text = " (مدبلة)" if self.is_doubled else ""
        return f"{self.rank.value} {self.suit.value}{doubled_text}"


@dataclass
class RoundData:
    """بيانات الجولة"""
    total_cards: int = 0                          # عدد الأوراق الكلي
    diamond_count: int = 0                        # عدد أوراق الديناري
    queens: List[SpecialCard] = field(default_factory=list)  # البنات
    king_heart: SpecialCard = None                # شيخ القبة
    
    # البطاقات التي دبّلها الفريق للخصم (يحصل على موجب)
    doubled_to_opponent: List[SpecialCard] = field(default_factory=list)


class ScoreCalculator:
    """حاسبة النقاط الرئيسية"""
    
    # ثوابت النقاط
    POINTS_PER_TRICK = 15      # نقاط كل أكلة
    CARDS_PER_TRICK = 4        # عدد الأوراق في كل أكلة
    POINTS_PER_DIAMOND = 10    # نقاط كل ديناري
    POINTS_PER_QUEEN = 25      # نقاط كل بنت
    POINTS_KING_HEART = 75     # نقاط شيخ القبة
    ROUND_TOTAL = -500         # مجموع نقاط الفريقين في كل جولة
    
    def __init__(self):
        self.round_data = RoundData()
        self.round_number = 0           # رقم الجولة الحالية
        self.team1_total = 0            # مجموع الفريق الأول
        self.team2_total = 0            # مجموع الفريق الثاني
    
    def reset_round(self):
        """إعادة تعيين بيانات الجولة"""
        self.round_data = RoundData()
    
    def start_new_round(self):
        """بدء جولة جديدة"""
        self.round_number += 1
        self.reset_round()
    
    def reset_game(self):
        """إعادة تعيين اللعبة بالكامل"""
        self.round_number = 0
        self.team1_total = 0
        self.team2_total = 0
        self.reset_round()
    
    def calculate_team2_score(self, team1_score: int) -> int:
        """
        حساب نقاط الفريق الثاني تلقائياً
        مجموع الفريقين = -500
        
        Args:
            team1_score: نقاط الفريق الأول
        
        Returns:
            نقاط الفريق الثاني
        """
        return self.ROUND_TOTAL - team1_score
    
    def get_expected_total(self) -> int:
        """
        الحصول على المجموع الكلي المتوقع لكلا الفريقين
        = عدد الجولات × -500
        """
        return self.round_number * self.ROUND_TOTAL
    
    def finalize_round(self, team1_score: int) -> Dict:
        """
        إنهاء الجولة وحساب نقاط الفريقين
        
        Args:
            team1_score: نقاط الفريق الأول (الذي قام بالعدّ)
        
        Returns:
            قاموس بنقاط الفريقين والمجاميع
        """
        team2_score = self.calculate_team2_score(team1_score)
        
        self.team1_total += team1_score
        self.team2_total += team2_score
        
        expected_total = self.get_expected_total()
        actual_total = self.team1_total + self.team2_total
        
        return {
            "round_number": self.round_number,
            "team1_round_score": team1_score,
            "team2_round_score": team2_score,
            "team1_total": self.team1_total,
            "team2_total": self.team2_total,
            "expected_total": expected_total,
            "actual_total": actual_total,
            "is_valid": actual_total == expected_total
        }
    
    def set_cards_data(self, total_cards: int, diamond_count: int, 
                       queens: List[Dict], has_king_heart: bool):
        """
        تعيين بيانات البطاقات من معالجة الصور
        
        Args:
            total_cards: عدد الأوراق الكلي
            diamond_count: عدد أوراق الديناري
            queens: قائمة البنات [{"suit": CardSuit, "is_doubled": bool}, ...]
            has_king_heart: هل يوجد شيخ القبة
        """
        self.round_data.total_cards = total_cards
        self.round_data.diamond_count = diamond_count
        
        # إضافة البنات
        self.round_data.queens = []
        for q in queens:
            queen = SpecialCard(
                rank=CardRank.QUEEN,
                suit=q.get("suit", CardSuit.SPADE),
                is_doubled=q.get("is_doubled", False)
            )
            self.round_data.queens.append(queen)
        
        # شيخ القبة
        if has_king_heart:
            self.round_data.king_heart = SpecialCard(
                rank=CardRank.KING,
                suit=CardSuit.HEART,
                is_doubled=False
            )
    
    def set_doubled_card(self, card: SpecialCard, is_doubled: bool):
        """تعيين حالة التدبيل لبطاقة"""
        card.is_doubled = is_doubled
    
    def add_doubled_to_opponent(self, rank: CardRank, suit: CardSuit):
        """
        إضافة بطاقة تم تدبيلها للخصم (يحصل الفريق على موجب)
        """
        card = SpecialCard(rank=rank, suit=suit, is_doubled=True)
        self.round_data.doubled_to_opponent.append(card)
    
    def calculate_tricks_points(self) -> int:
        """حساب نقاط الأكلات"""
        num_tricks = self.round_data.total_cards // self.CARDS_PER_TRICK
        return -num_tricks * self.POINTS_PER_TRICK
    
    def calculate_diamond_points(self) -> int:
        """حساب نقاط الديناري"""
        return -self.round_data.diamond_count * self.POINTS_PER_DIAMOND
    
    def calculate_queens_points(self) -> int:
        """حساب نقاط البنات"""
        total = 0
        for queen in self.round_data.queens:
            total -= queen.actual_value
        return total
    
    def calculate_king_heart_points(self) -> int:
        """حساب نقاط شيخ القبة"""
        if self.round_data.king_heart:
            return -self.round_data.king_heart.actual_value
        return 0
    
    def calculate_doubled_to_opponent_points(self) -> int:
        """حساب النقاط الموجبة من التدبيل للخصم"""
        total = 0
        for card in self.round_data.doubled_to_opponent:
            # القيمة موجبة لأن الفريق دبّل والخصم أكل
            total += card.base_value  # القيمة الأساسية فقط
        return total
    
    def calculate_round_score(self) -> Dict:
        """
        حساب نقاط الجولة الكاملة
        
        Returns:
            قاموس بتفاصيل النقاط
        """
        tricks_points = self.calculate_tricks_points()
        diamond_points = self.calculate_diamond_points()
        queens_points = self.calculate_queens_points()
        king_points = self.calculate_king_heart_points()
        doubled_bonus = self.calculate_doubled_to_opponent_points()
        
        total = tricks_points + diamond_points + queens_points + king_points + doubled_bonus
        
        return {
            "tricks": {
                "count": self.round_data.total_cards // self.CARDS_PER_TRICK,
                "points": tricks_points
            },
            "diamonds": {
                "count": self.round_data.diamond_count,
                "points": diamond_points
            },
            "queens": {
                "cards": [str(q) for q in self.round_data.queens],
                "points": queens_points
            },
            "king_heart": {
                "exists": self.round_data.king_heart is not None,
                "doubled": self.round_data.king_heart.is_doubled if self.round_data.king_heart else False,
                "points": king_points
            },
            "doubled_bonus": {
                "cards": [str(c) for c in self.round_data.doubled_to_opponent],
                "points": doubled_bonus
            },
            "total": total
        }
    
    def get_special_cards_for_selection(self) -> Dict:
        """
        الحصول على البطاقات الخاصة لعرضها للمستخدم للاختيار
        
        Returns:
            قاموس بالبنات وشيخ القبة الموجودين
        """
        result = {
            "queens": [],
            "king_heart": None,
            "missing_queens": [],
            "missing_king_heart": False
        }
        
        # البنات الموجودة
        existing_suits = set()
        for queen in self.round_data.queens:
            result["queens"].append({
                "suit": queen.suit.value,
                "suit_enum": queen.suit,
                "is_doubled": queen.is_doubled
            })
            existing_suits.add(queen.suit)
        
        # شيخ القبة
        if self.round_data.king_heart:
            result["king_heart"] = {
                "suit": CardSuit.HEART.value,
                "is_doubled": self.round_data.king_heart.is_doubled
            }
        else:
            result["missing_king_heart"] = True
        
        # البنات الناقصة (للسؤال عن التدبيل للخصم)
        all_suits = [CardSuit.SPADE, CardSuit.DIAMOND, CardSuit.HEART, CardSuit.CLUB]
        for suit in all_suits:
            if suit not in existing_suits:
                result["missing_queens"].append({
                    "suit": suit.value,
                    "suit_enum": suit
                })
        
        return result


def format_score_report(score_details: Dict, round_result: Dict = None) -> str:
    """
    تنسيق تقرير النقاط للعرض
    
    Args:
        score_details: تفاصيل النقاط من calculate_round_score
        round_result: نتيجة الجولة من finalize_round (اختياري)
    
    Returns:
        نص منسق للعرض
    """
    lines = [
        "═" * 40,
        "📊 تقرير نقاط الجولة",
        "═" * 40,
        "",
        f"🃏 الأكلات: {score_details['tricks']['count']} أكلة",
        f"   النقاط: {score_details['tricks']['points']}",
        "",
        f"♦️ الديناري: {score_details['diamonds']['count']} ورقة",
        f"   النقاط: {score_details['diamonds']['points']}",
        "",
        f"👸 البنات: {', '.join(score_details['queens']['cards']) or 'لا يوجد'}",
        f"   النقاط: {score_details['queens']['points']}",
        "",
    ]
    
    if score_details['king_heart']['exists']:
        doubled_text = " (مدبل)" if score_details['king_heart']['doubled'] else ""
        lines.extend([
            f"👑 شيخ القبة: موجود{doubled_text}",
            f"   النقاط: {score_details['king_heart']['points']}",
            "",
        ])
    
    if score_details['doubled_bonus']['points'] > 0:
        lines.extend([
            f"✨ مكافأة التدبيل للخصم:",
            f"   البطاقات: {', '.join(score_details['doubled_bonus']['cards'])}",
            f"   النقاط: +{score_details['doubled_bonus']['points']}",
            "",
        ])
    
    lines.extend([
        "─" * 40,
        f"📌 نقاط فريقك: {score_details['total']}",
    ])
    
    # إضافة نقاط الفريق الثاني إذا توفرت
    if round_result:
        lines.extend([
            f"📌 نقاط الخصم: {round_result['team2_round_score']}",
            f"   (المجموع = -500)",
            "",
            "═" * 40,
            f"🏆 الجولة رقم: {round_result['round_number']}",
            f"📊 مجموعك الكلي: {round_result['team1_total']}",
            f"📊 مجموع الخصم: {round_result['team2_total']}",
            f"📊 المجموع المتوقع: {round_result['expected_total']}",
        ])
    
    lines.append("═" * 40)
    
    return "\n".join(lines)


# مثال على الاستخدام
if __name__ == "__main__":
    calc = ScoreCalculator()
    
    # === الجولة الأولى ===
    calc.start_new_round()
    print(f"\n🎮 الجولة رقم {calc.round_number}")
    
    # محاكاة بيانات من معالجة الصور
    calc.set_cards_data(
        total_cards=20,  # 5 أكلات
        diamond_count=3,
        queens=[
            {"suit": CardSuit.HEART, "is_doubled": False},
            {"suit": CardSuit.DIAMOND, "is_doubled": False},
            {"suit": CardSuit.SPADE, "is_doubled": False},
        ],
        has_king_heart=True
    )
    
    # تعيين التدبيل للبنات (من اختيار المستخدم)
    calc.round_data.queens[0].is_doubled = True  # بنت القبة مدبلة
    calc.round_data.queens[1].is_doubled = True  # بنت الديناري مدبلة
    
    # حساب النقاط
    score_details = calc.calculate_round_score()
    team1_score = score_details['total']
    
    # إنهاء الجولة وحساب نقاط الفريق الثاني
    round_result = calc.finalize_round(team1_score)
    
    print(format_score_report(score_details, round_result))
    
    # === الجولة الثانية ===
    calc.start_new_round()
    print(f"\n🎮 الجولة رقم {calc.round_number}")
    
    calc.set_cards_data(
        total_cards=16,  # 4 أكلات
        diamond_count=2,
        queens=[
            {"suit": CardSuit.CLUB, "is_doubled": False},
        ],
        has_king_heart=False
    )
    
    score_details2 = calc.calculate_round_score()
    team1_score2 = score_details2['total']
    round_result2 = calc.finalize_round(team1_score2)
    
    print(format_score_report(score_details2, round_result2))
    
    # === ملخص اللعبة ===
    print("\n" + "═" * 40)
    print("📊 ملخص اللعبة بعد جولتين:")
    print(f"   فريقك: {calc.team1_total}")
    print(f"   الخصم: {calc.team2_total}")
    print(f"   المجموع الكلي: {calc.team1_total + calc.team2_total}")
    print(f"   المتوقع: {calc.get_expected_total()}")
    print("═" * 40)
