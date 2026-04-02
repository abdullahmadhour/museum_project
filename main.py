# import random
# import csv
# import os
# from fastapi import FastAPI, Request, Form, HTTPException, Response
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# app = FastAPI()
# templates = Jinja2Templates(directory="templates")

# # بيانات المدير
# ADMIN_USERNAME = "abdullah"
# ADMIN_PASSWORD = "123"

# # 1. الصفحة الرئيسية
# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     artifacts = [
#         {"icon": "👑", "era": "الأسرة 18", "name": "قناع توت عنخ آمون", "desc": "الكنز الذهبي الأشهر في التاريخ المصري."},
#         {"icon": "📜", "era": "الدولة القديمة", "name": "برديات الأهرام", "desc": "نصوص جنائزية قديمة تحكي أسرار البعث."},
#         {"icon": "🦁", "era": "الدولة الحديثة", "name": "تمثال أبو الهول الصغير", "desc": "رمز القوة والحكمة عند الفراعنة."}
#     ]
#     return templates.TemplateResponse(
#         request=request, 
#         name="index.html", 
#         context={"artifacts": artifacts}
#     )

# # 2. صفحة تسجيل الدخول
# @app.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse(request=request, name="login.html")

# @app.post("/login")
# async def login(username: str = Form(...), password: str = Form(...)):
#     if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
#         response = RedirectResponse(url="/admin", status_code=303)
#         response.set_cookie(key="admin_session", value="authorized")
#         return response
#     return HTMLResponse("<h2 style='text-align:center; direction:rtl;'>❌ خطأ في اسم المستخدم أو كلمة المرور</h2>", status_code=401)

# # 3. لوحة المدير (محمية)
# @app.get("/admin", response_class=HTMLResponse)
# async def admin_dashboard(request: Request, search: str = None):
#     if request.cookies.get("admin_session") != "authorized":
#         return RedirectResponse(url="/login")

#     all_bookings = []
#     total_revenue = 0
#     search_query = search.strip() if search else ""

#     if os.path.exists("bookings.csv"):
#         with open("bookings.csv", mode="r", encoding="utf-8-sig") as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 try:
#                     total_revenue += int(float(row.get("الإجمالي", 0)))
#                 except:
#                     pass
                
#                 row_name = row.get("الاسم", "")
#                 if not search_query or search_query in row_name:
#                     all_bookings.append(row)

#     return templates.TemplateResponse(
#         request=request, 
#         name="admin.html", 
#         context={
#             "bookings": all_bookings[::-1], 
#             "revenue": total_revenue, 
#             "count": len(all_bookings), 
#             "search_query": search_query
#         }
#     )

# # 4. دالة استقبال الحجز (هذه كانت مفقودة في كودك)
# @app.post("/book", response_class=HTMLResponse)
# async def handle_booking(
#     request: Request, 
#     name: str = Form(...), 
#     date: str = Form(...), 
#     ticket_type: str = Form(...),
#     count: int = Form(...),
#     payment_method: str = Form(...)
# ):
#     # 1. حساب السعر والبيانات
#     prices = {"egyptian": 60, "foreign": 200, "student": 30}
#     price_per_ticket = prices.get(ticket_type, 0)
#     total_amount = price_per_ticket * count
    
#     serial_number = f"GEM-{random.randint(10000, 99999)}"
#     status = "مؤكد (الدفع كاش)" if payment_method == "عند الوصول" else "قيد المراجعة"
#     ticket_label = "مصري" if ticket_type == "egyptian" else "أجنبي" if ticket_type == "foreign" else "طالب"

#     # 2. محاولة الحفظ في ملف CSV (مع تجاهل الخطأ لو السيرفر منع الكتابة)
#     try:
#         file_exists = os.path.exists("bookings.csv")
#         with open("bookings.csv", mode="a", newline="", encoding="utf-8-sig") as file:
#             fieldnames = ["الرقم التسلسلي", "الاسم", "التاريخ", "النوع", "العدد", "الإجمالي", "طريقة الدفع", "الحالة"]
#             writer = csv.DictWriter(file, fieldnames=fieldnames)
#             if not file_exists:
#                 writer.writeheader()
#             writer.writerow({
#                 "الرقم التسلسلي": serial_number,
#                 "الاسم": name,
#                 "التاريخ": date,
#                 "النوع": ticket_label,
#                 "العدد": count,
#                 "الإجمالي": total_amount,
#                 "طريقة الدفع": payment_method,
#                 "الحالة": status
#             })
#     except Exception as e:
#         # هنا بنقول للسيرفر: لو مقدرتش تكتب في الملف، اطبع الخطأ في الـ Logs وكمل عادي
#         print(f"فشل الحفظ في الملف: {e}")

#     # 3. العودة لصفحة النجاح (ستعمل حتى لو لم يتم الحفظ)
#     return templates.TemplateResponse(
#         request=request, 
#         name="success.html", 
#         context={
#             "name": name, "date": date, "total": total_amount, 
#             "count": count, "serial": serial_number, "status": status
#         }
#     )



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
SHEET_URL = "ضع_هنا_الرابط_الذي_نسخته_من_جوجل"

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
    
