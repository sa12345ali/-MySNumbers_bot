# بوت تيليجرام للأرقام الوهمية (SMS-Activate)

هذا المشروع جاهز للرفع على منصة **Render** للعمل بشكل دائم 24/7.

## الملفات المرفقة:
1. `main.py`: الكود الأساسي للبوت.
2. `requirements.txt`: المكتبات اللازمة للتشغيل.
3. `Procfile`: ملف إعدادات التشغيل لمنصة Render.

## خطوات الرفع على Render:
1. قم بإنشاء حساب على [Render](https://render.com).
2. اربط حسابك بـ **GitHub** وارفع هذه الملفات في مستودع (Repository) جديد.
3. في لوحة تحكم Render، اختر **New +** ثم **Background Worker**.
4. اختر المستودع الذي رفعت فيه الملفات.
5. في إعدادات التشغيل:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
6. اضغط على **Create Background Worker**.

سيقوم Render الآن بتشغيل البوت وسيبقى يعمل بشكل دائم.
