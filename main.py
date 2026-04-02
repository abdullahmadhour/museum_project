import random
import csv
import os
import httpx  # مكتبة إرسال البيانات لجوجل شيت
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# بيانات المدير
ADMIN_USERNAME = "abdullah"
ADMIN_PASSWORD = "123"

# رابط Google Sheets (ضع الرابط الذي نسخته من Apps Script هنا)
SHEET_URL = "https://script.google.com/macros/s/AKfycbzEl7jlhTLeN0SO5XYRjOu6ILnEaYrZEFFPINtvsyKsA9A-_JkYzejnmVSyaHl9OGxddA/exec"

# 1. الصفحة الرئيسية
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    artifacts = [
        {"icon": "👑", "era": "الأسرة 18", "name": "قناع توت عنخ آمون", "desc": "الكنز الذهبي الأشهر في التاريخ المصري."},
        {"icon": "📜", "era": "الدولة القديمة", "name": "برديات الأهرام", "desc": "نصوص جنائزية قديمة تحكي أسرار البعث."},
        {"icon": "🦁", "era": "الدولة الحديثة", "name": "تمثال أبو الهول الصغير", "desc": "رمز القوة والحكمة عند الفراعنة."}
    ]
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"artifacts": artifacts}
    )

# 2. صفحة تسجيل الدخول
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="admin_session", value="authorized")
        return response
    return HTMLResponse("<h2 style='text-align:center; direction:rtl;'>❌ خطأ في اسم المستخدم أو كلمة المرور</h2>", status_code=401)

# 3. لوحة المدير
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    if request.cookies.get("admin_session") != "authorized":
        return RedirectResponse(url="/login")
    
    # تنبيه: في Vercel، صفحة المدير ستعرض فقط البيانات المخزنة مؤقتاً
    # يفضل مستقبلاً سحب البيانات من Google Sheets مباشرة لعرضها هنا
    return HTMLResponse("<h2 style='text-align:center;'>البيانات محفوظة الآن في Google Sheets بنجاح!</h2>")

# 4. دالة استقبال الحجز والربط مع Google Sheets
@app.post("/book", response_class=HTMLResponse)
async def handle_booking(
    request: Request, 
    name: str = Form(...), 
    date: str = Form(...), 
    ticket_type: str = Form(...),
    count: int = Form(...),
    payment_method: str = Form(...)
):
    # حساب السعر
    prices = {"egyptian": 60, "foreign": 200, "student": 30}
    total_amount = prices.get(ticket_type, 0) * count
    serial_number = f"GEM-{random.randint(10000, 99999)}"
    status = "مؤكد (كاش)" if payment_method == "عند الوصول" else "قيد المراجعة"
    ticket_label = "مصري" if ticket_type == "egyptian" else "أجنبي" if ticket_type == "foreign" else "طالب"

    # تجهيز البيانات للإرسال لجوجل
    payload = {
        "serial": serial_number,
        "name": name,
        "date": date,
        "type": ticket_label,
        "count": count,
        "total": total_amount,
        "payment": payment_method,
        "status": status
    }

    # الإرسال الفعلي لـ Google Sheets
    try:
        async with httpx.AsyncClient() as client:
            await client.post(SHEET_URL, json=payload)
    except Exception as e:
        print(f"فشل الربط مع جوجل: {e}")

    return templates.TemplateResponse(
        request=request, 
        name="success.html", 
        context={
            "name": name, "date": date, "total": total_amount, 
            "count": count, "serial": serial_number, "status": status
        }
    )
    
