# 📱 بناء APK للأندرويد باستخدام Google Colab
# ===============================================
# 
# اتبع هذه الخطوات لبناء التطبيق:
#
# الخطوة 1: افتح Google Colab
# ---------------------------
# اذهب إلى: https://colab.research.google.com
# أنشئ Notebook جديد
#
# الخطوة 2: انسخ والصق الكود التالي في خلايا Colab
# ------------------------------------------------

# ============ الخلية 1: تثبيت Buildozer ============
"""
!pip install buildozer
!pip install cython==0.29.33
!sudo apt-get update
!sudo apt-get install -y python3-pip build-essential git python3 python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev libgstreamer1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good
!sudo apt-get install -y libgstreamer1.0-dev gstreamer1.0-alsa gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
!sudo apt-get install -y openjdk-17-jdk
!sudo apt-get install -y autoconf automake libtool pkg-config
"""

# ============ الخلية 2: رفع ملفات المشروع ============
"""
# ارفع الملفات التالية إلى Colab:
# - main.py
# - ui_components.py
# - score_calculator.py
# - buildozer.spec

from google.colab import files
uploaded = files.upload()  # سيفتح نافذة لرفع الملفات
"""

# ============ الخلية 3: بناء APK ============
"""
!buildozer android debug
"""

# ============ الخلية 4: تحميل APK ============
"""
from google.colab import files
files.download('bin/cccounter-1.0.0-arm64-v8a_armeabi-v7a-debug.apk')
"""

# ============================================
# ملاحظات مهمة:
# ============================================
# 
# 1. البناء يستغرق 15-30 دقيقة في المرة الأولى
# 2. بعد التحميل، انقل APK لهاتفك عبر:
#    - USB
#    - Google Drive
#    - Bluetooth
#    - أي طريقة أخرى
# 3. على الهاتف:
#    - اذهب للإعدادات > الأمان
#    - فعّل "السماح بالتثبيت من مصادر غير معروفة"
#    - افتح ملف APK وثبّته
