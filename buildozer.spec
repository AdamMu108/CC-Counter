[app]
# عنوان التطبيق
title = CC Counter

# اسم الحزمة
package.name = cccounter

# نطاق الحزمة (يجب أن يكون فريداً)
package.domain = org.cccounter

# الملف الرئيسي
source.main = main.py

# مجلد المصدر
source.dir = .

# الإصدار
version = 1.0.0

# المتطلبات
requirements = python3,kivy,opencv,numpy,pillow

# الأيقونة
#icon.filename = %(source.dir)s/data/icon.png

# شاشة البداية
#presplash.filename = %(source.dir)s/data/presplash.png

# الاتجاه
orientation = portrait

# وضع ملء الشاشة
fullscreen = 0

# إصدار Android API
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31

# الصلاحيات المطلوبة
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# الأنظمة المستهدفة
android.archs = arm64-v8a, armeabi-v7a

# السماح بالنسخ الاحتياطي
android.allow_backup = True

# تمكين AndroidX
android.enable_androidx = True

# الحزم المضمنة
#android.add_jars = 

# logcat filter
android.logcat_filters = *:S python:D

# تحذيرات
[buildozer]
log_level = 2
warn_on_root = 1
