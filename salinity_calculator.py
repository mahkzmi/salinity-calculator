import customtkinter as ctk
import tkinter as tk
import math
from datetime import datetime
import json
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ============================================================
# تنظیمات ظاهری مدرن با شیشه‌ای و انیمیشن
# ============================================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# تلاش برای بارگذاری فونت فارسی
FONT_NAME = "Helvetica"
try:
    font_paths = ["Vazir.ttf", "vazir.ttf", "assets/Vazir.ttf", "fonts/Vazir.ttf"]
    for path in font_paths:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont('Vazir', path))
            FONT_NAME = 'Vazir'
            break
except:
    pass

HISTORY_FILE = "salinity_history.json"

# رنگ‌های مدرن شیشه‌ای
COLORS = {
    "primary": "#1A5D3A",
    "primary_light": "#2D6A4F",
    "secondary": "#F59E0B",
    "danger": "#DC2626",
    "warning": "#EA580C",
    "info": "#0891B2",
    "dark": "#1E293B",
    "gray": "#64748B",
    "light_gray": "#F8FAFC",
    "border": "#E2E8F0",
    "glass_bg": "rgba(255,255,255,0.85)",
    "glass_border": "rgba(255,255,255,0.5)"
}

# ============================================================
# توابع محاسباتی
# ============================================================

def get_salinity_profile(ec, crop):
    if ec < 2:
        salinity_level = "غیرشور 🌟"
        salinity_level_en = "Non-saline"
        salinity_color = "#2E7D32"
        severity = "بدون تنش"
        severity_en = "No stress"
        severity_score = 10
        fao_class = "غیرشور"
    elif ec < 4:
        salinity_level = "کم‌شور ✅"
        salinity_level_en = "Slightly saline"
        salinity_color = "#F59E0B"
        severity = "تنش ملایم"
        severity_en = "Mild stress"
        severity_score = 30
        fao_class = "کم‌شور"
    elif ec < 8:
        salinity_level = "شور ⚠️"
        salinity_level_en = "Moderately saline"
        salinity_color = "#EA580C"
        severity = "تنش متوسط"
        severity_en = "Moderate stress"
        severity_score = 60
        fao_class = "شور"
    elif ec < 12:
        salinity_level = "خیلی شور ❌"
        salinity_level_en = "Highly saline"
        salinity_color = "#DC2626"
        severity = "تنش شدید"
        severity_en = "Severe stress"
        severity_score = 85
        fao_class = "خیلی شور"
    else:
        salinity_level = "بحرانی 🚫"
        salinity_level_en = "Extremely saline"
        salinity_color = "#991B1B"
        severity = "تنش فوق‌العاده"
        severity_en = "Extreme stress"
        severity_score = 98
        fao_class = "بحرانی"
    
    crop_params = {"گندم": 0.15, "جو": 0.10, "ذرت": 0.25, "پسته": 0.08}
    a = crop_params.get(crop, 0.15)
    loss_percent = min(95, max(0, round((1 - math.exp(-a * ec)) * 100, 1)))
    
    resistant_crops = ["جو 🌾", "پسته 🌰", "کلزا 🌻", "چغندر قند 🍬"]
    if ec > 6:
        resistant_crops = ["جو 🌾 (مقاوم‌ترین)", "پسته 🌰", "کلزا 🌻"]
    if ec > 9:
        resistant_crops = ["جو 🌾", "پسته 🌰"]
    
    if ec < 2:
        soil_effect_fa = "خاک در شرایط ایده‌آل است. هیچ اثری از شوری مشاهده نمی‌شود."
        plant_effect_fa = f"محصول {crop} حداکثر پتانسیل عملکرد خود را خواهد داشت."
        leaf_status_fa = "برگ‌ها سالم، سبز و شاداب هستند."
    elif ec < 4:
        soil_effect_fa = "شوری خفیف: جذب آب و عناصر غذایی کمی کاهش می‌یابد."
        plant_effect_fa = f"عملکرد {crop} حدود ۱۰-۱۵٪ کاهش می‌یابد."
        leaf_status_fa = "نوک برگ‌ها ممکن است کمی زرد شود."
    elif ec < 8:
        soil_effect_fa = "شوری متوسط: فشار اسمزی روی ریشه، جذب آب را سخت می‌کند."
        plant_effect_fa = f"عملکرد {crop} کاهش قابل توجهی خواهد داشت."
        leaf_status_fa = "زردی گسترده برگ‌ها، حاشیه برگ‌ها قهوه‌ای می‌شود."
    elif ec < 12:
        soil_effect_fa = "شوری شدید: ساختمان خاک تخریب شده، فعالیت میکروبی متوقف می‌شود."
        plant_effect_fa = f"کشت {crop} توجیه اقتصادی ندارد."
        leaf_status_fa = "پژمردگی شدید، نکروز گسترده، ریزش برگ."
    else:
        soil_effect_fa = "شوری بحرانی: خاک شور و سدیمی شده، احیای خاک سال‌ها زمان می‌برد."
        plant_effect_fa = "کشاورزی در این خاک غیرممکن است."
        leaf_status_fa = "گیاه از بین رفته یا هرگز جوانه نمی‌زند."
    
    if ec < 2:
        free_advice_fa = ["برنامه آبیاری معمول را ادامه دهید.", "هر سال آزمایش خاک را تکرار کنید."]
    elif ec < 4:
        free_advice_fa = ["یک نوبت آبیاری عمیق (آبشویی) انجام دهید.", "از کشت محصولات حساس مانند ذرت خودداری کنید.", "هر ۶ ماه یکبار EC خاک را اندازه بگیرید."]
    elif ec < 8:
        free_advice_fa = ["دو نوبت آبیاری سنگین با فاصله ۳ روز انجام دهید", "بهترین جایگزین‌ها: جو، پسته، کلزا", "از مواد آلی برای بهبود ساختمان خاک استفاده کنید."]
    elif ec < 12:
        free_advice_fa = ["شوری بالاست. آبیاری سنگین را تا ۳ نوبت افزایش دهید.", "شستشوی شوری (Leaching) انجام دهید.", "فعلاً کشت نکنید. ابتدا خاک را اصلاح کنید."]
    else:
        free_advice_fa = ["کشت را متوقف کنید.", "با کارشناسان VARIA تماس بگیرید.", "قبل از هر اقدامی، آزمایش کامل خاک انجام دهید."]
    
    return {
        "salinity_level": salinity_level, "salinity_level_en": salinity_level_en,
        "salinity_color": salinity_color,
        "severity": severity, "severity_en": severity_en,
        "severity_score": severity_score,
        "loss_percent": loss_percent, "fao_class": fao_class,
        "resistant_crops": resistant_crops,
        "soil_effect_fa": soil_effect_fa,
        "plant_effect_fa": plant_effect_fa,
        "leaf_status_fa": leaf_status_fa,
        "free_advice_fa": free_advice_fa
    }


def save_to_history(ec, crop, result):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    history.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "ec": ec, "crop": crop,
                    "severity": result['severity'], "loss": result['loss_percent']})
    if len(history) > 20:
        history = history[-20:]
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def generate_pdf_report(ec, crop, profile, user_name="VARIA User"):
    """گزارش PDF فارسی با طراحی حرفه‌ای"""
    filename = f"VARIA_Soil_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                           rightMargin=15, leftMargin=15,
                           topMargin=18, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Normal'], fontSize=18,
                                  textColor=colors.HexColor(COLORS['primary']), spaceAfter=15,
                                  alignment=1, fontName=FONT_NAME)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=9,
                                     textColor=colors.HexColor(COLORS['gray']), spaceAfter=20,
                                     alignment=1, fontName=FONT_NAME)
    heading_style = ParagraphStyle('Heading', parent=styles['Normal'], fontSize=12,
                                    textColor=colors.HexColor(COLORS['primary_light']), spaceAfter=8,
                                    spaceBefore=12, fontName=FONT_NAME)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9,
                                 leading=12, textColor=colors.HexColor('#333333'),
                                 alignment=0, fontName=FONT_NAME)
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7,
                                  textColor=colors.HexColor(COLORS['gray']), alignment=1, fontName=FONT_NAME)
    
    story = []
    story.append(Paragraph("🌾 گزارش سلامت خاک VARIA", title_style))
    story.append(Paragraph(f"کاربر: {user_name} | تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    story.append(Paragraph("نتایج تحلیل شوری خاک", heading_style))
    
    data = [
        ["پارامتر", "مقدار", "وضعیت"],
        ["شوری خاک (EC)", f"{ec} dS/m", profile['salinity_level']],
        ["نوع محصول", crop, "-"],
        ["سطح تنش", profile['severity'], f"{profile['severity_score']}%"],
        ["کاهش عملکرد", f"{profile['loss_percent']}%", "نسبت به خاک غیرشور"],
        ["کلاس FAO", profile['fao_class'], "-"]
    ]
    table = Table(data, colWidths=[55, 35, 55])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(COLORS['light_gray'])),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS['border'])),
    ]))
    story.append(table)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("اثر شوری بر خاک و گیاه", heading_style))
    story.append(Paragraph(f"خاک: {profile['soil_effect_fa']}", body_style))
    story.append(Paragraph(f"گیاه: {profile['plant_effect_fa']}", body_style))
    story.append(Paragraph(f"علائم ظاهری: {profile['leaf_status_fa']}", body_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("محصولات مقاوم به شوری", heading_style))
    story.append(Paragraph(", ".join(profile['resistant_crops']), body_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("اقدامات فوری رایگان", heading_style))
    for advice in profile['free_advice_fa']:
        story.append(Paragraph(f"• {advice}", body_style))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("خدمات ویژه VARIA", heading_style))
    for service in ["گزارش سلامت خاک VIP با تحلیل عمیق", "برنامه گام‌به‌گام مدیریت شوری",
                    "مشاوره تخصصی با کارشناسان علوم خاک", "طراحی سیستم آبیاری هوشمند"]:
        story.append(Paragraph(f"• {service}", body_style))
    story.append(Spacer(1, 15))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("📧 varia.agtech@gmail.com | @varia_support", small_style))
    story.append(Paragraph("© استودیوی فناوری‌های کشاورزی هوشمند VARIA", small_style))
    
    doc.build(story)
    return filename


# ============================================================
# پنجره اصلی با طراحی مدرن شیشه‌ای
# ============================================================

root = ctk.CTk()
root.title("ماشین حساب شوری VARIA")
root.geometry("950x850")
root.resizable(True, True)
root.configure(fg_color="#F0F4F8")

root.grid_columnconfigure(0, weight=1)

# Header
header_frame = ctk.CTkFrame(root, fg_color=COLORS['primary'], height=90, corner_radius=0)
header_frame.pack(fill="x")

title_label = ctk.CTkLabel(
    header_frame, 
    text="🌾 VARIA | ماشین حساب حرفه‌ای شوری خاک", 
    font=("Segoe UI", 26, "bold"), 
    text_color="white"
)
title_label.pack(pady=28)

# Main Container
main_container = ctk.CTkFrame(root, fg_color="transparent")
main_container.pack(padx=30, pady=25, fill="both", expand=True)

# ستون چپ - ورودی
left_column = ctk.CTkFrame(
    main_container, 
    fg_color="white", 
    corner_radius=28, 
    width=380,
    border_width=1,
    border_color=COLORS['border']
)
left_column.pack(side="left", fill="both", expand=True, padx=(0, 18))
left_column.pack_propagate(False)

ctk.CTkLabel(
    left_column, 
    text="📊 اطلاعات ورودی", 
    font=("Segoe UI", 20, "bold"), 
    text_color=COLORS['primary']
).pack(pady=(28, 22))

# EC Entry
ec_label = ctk.CTkLabel(left_column, text="🧂 شوری خاک (EC) - dS/m", font=("Segoe UI", 14, "bold"))
ec_label.pack(anchor="center")
ec_entry = ctk.CTkEntry(
    left_column, 
    placeholder_text="مثال: 6.2", 
    width=320, 
    height=48, 
    font=("Segoe UI", 15), 
    justify="center", 
    corner_radius=16,
    border_color=COLORS['border'],
    border_width=2
)
ec_entry.pack(pady=(6, 18))

# Crop Selection
crop_label = ctk.CTkLabel(left_column, text="🌱 نوع محصول", font=("Segoe UI", 14, "bold"))
crop_label.pack(anchor="center")
crop_var = ctk.StringVar(value="گندم")
crop_menu = ctk.CTkOptionMenu(
    left_column, 
    values=["گندم", "جو", "ذرت", "پسته"], 
    variable=crop_var, 
    width=320, 
    height=48, 
    font=("Segoe UI", 14), 
    corner_radius=16,
    fg_color="green",
    button_color=COLORS['primary'],
    dropdown_fg_color="white",
    dropdown_hover_color=COLORS['light_gray']
)
crop_menu.pack(pady=(6, 22))

# Analyze Button
calc_btn = ctk.CTkButton(
    left_column, 
    text="🔍 تحلیل شوری خاک", 
    width=320, 
    height=52, 
    font=("Segoe UI", 16, "bold"), 
    corner_radius=26, 
    fg_color=COLORS['primary'],
    hover_color=COLORS['primary_light']
)
calc_btn.pack(pady=10)

# History Button
history_btn = ctk.CTkButton(
    left_column, 
    text="📜 تاریخچه تحلیل‌ها", 
    width=320, 
    height=42, 
    font=("Segoe UI", 13), 
    corner_radius=21, 
    fg_color="transparent", 
    border_width=2, 
    border_color=COLORS['primary'], 
    text_color=COLORS['primary'],
    hover_color=COLORS['light_gray']
)
history_btn.pack(pady=12)

# ستون راست اسکرول دار
right_scroll = ctk.CTkScrollableFrame(
    main_container, 
    fg_color="transparent", 
    scrollbar_button_color=COLORS['primary'], 
    scrollbar_button_hover_color=COLORS['primary_light']
)
right_scroll.pack(side="left", fill="both", expand=True, padx=(18, 0))

# Gauge Card
gauge_card = ctk.CTkFrame(
    right_scroll, 
    fg_color="white", 
    corner_radius=24, 
    border_width=1,
    border_color=COLORS['border']
)
gauge_card.pack(fill="x", pady=(0, 14))

gauge_container = ctk.CTkFrame(gauge_card, fg_color="transparent")
gauge_container.pack(side="left", padx=20, pady=18)

gauge_canvas = tk.Canvas(gauge_container, width=140, height=140, bg="white", highlightthickness=0)
gauge_canvas.pack()
gauge_canvas.create_arc(10, 10, 130, 130, start=90, extent=360, outline=COLORS['border'], width=12, style="arc")
gauge_arc = gauge_canvas.create_arc(10, 10, 130, 130, start=90, extent=0, outline=COLORS['primary'], width=12, style="arc")
gauge_text = gauge_canvas.create_text(70, 70, text="0%", font=("Segoe UI", 18, "bold"), fill=COLORS['dark'])

info_container = ctk.CTkFrame(gauge_card, fg_color="transparent")
info_container.pack(side="left", padx=12, fill="both", expand=True)

severity_label = ctk.CTkLabel(info_container, text="شدت شوری: ---", font=("Segoe UI", 16, "bold"), text_color=COLORS['dark'])
severity_label.pack(anchor="center", pady=3)
loss_label = ctk.CTkLabel(info_container, text="کاهش عملکرد: ---", font=("Segoe UI", 13), text_color=COLORS['gray'])
loss_label.pack(anchor="center", pady=3)
fao_label = ctk.CTkLabel(info_container, text="کلاس FAO: ---", font=("Segoe UI", 12), text_color=COLORS['gray'])
fao_label.pack(anchor="center", pady=3)

# Diagnosis Card
diag_card = ctk.CTkFrame(right_scroll, fg_color="white", corner_radius=24, border_width=1, border_color=COLORS['border'])
diag_card.pack(fill="x", pady=14)
ctk.CTkLabel(diag_card, text="📊 1. تشخیص شوری خاک", font=("Segoe UI", 16, "bold"), text_color=COLORS['primary']).pack(anchor="center", pady=(14, 6))
status_label = ctk.CTkLabel(diag_card, text="وضعیت: ---", font=("Segoe UI", 14))
status_label.pack(anchor="center", pady=6)

# Effect Card
effect_card = ctk.CTkFrame(right_scroll, fg_color="white", corner_radius=24, border_width=1, border_color=COLORS['border'])
effect_card.pack(fill="x", pady=14)
ctk.CTkLabel(effect_card, text="⚠️ 2. اثر شوری بر خاک و محصول", font=("Segoe UI", 16, "bold"), text_color=COLORS['warning']).pack(anchor="center", pady=(14, 6))
soil_label = ctk.CTkLabel(effect_card, text="خاک: ---", font=("Segoe UI", 12), wraplength=430)
soil_label.pack(anchor="center", pady=3)
plant_label = ctk.CTkLabel(effect_card, text="محصول: ---", font=("Segoe UI", 12), wraplength=430)
plant_label.pack(anchor="center", pady=3)
leaf_label = ctk.CTkLabel(effect_card, text="علائم ظاهری: ---", font=("Segoe UI", 12), wraplength=430)
leaf_label.pack(anchor="center", pady=3)

# Resistant Crops Card
res_card = ctk.CTkFrame(right_scroll, fg_color="#F0FDF4", corner_radius=24, border_width=1, border_color="#A7F3D0")
res_card.pack(fill="x", pady=14)
ctk.CTkLabel(res_card, text="🌿 محصولات مقاوم به شوری", font=("Segoe UI", 15, "bold"), text_color=COLORS['primary']).pack(anchor="center", pady=(12, 6))
res_label = ctk.CTkLabel(res_card, text="", font=("Segoe UI", 13))
res_label.pack(anchor="center", pady=6)

# Free Actions Card
free_card = ctk.CTkFrame(right_scroll, fg_color="white", corner_radius=24, border_width=1, border_color=COLORS['border'])
free_card.pack(fill="x", pady=14)
ctk.CTkLabel(free_card, text="🛠️ 3. اقدام فوری و رایگان", font=("Segoe UI", 16, "bold"), text_color=COLORS['info']).pack(anchor="center", pady=(14, 6))
free_label = ctk.CTkLabel(free_card, text="", font=("Segoe UI", 12), wraplength=480)
free_label.pack(anchor="center", pady=6)

# PDF Button
pdf_btn = ctk.CTkButton(
    right_scroll, 
    text="📄 دانلود گزارش (PDF)", 
    width=320, 
    height=48,
    font=("Segoe UI", 15, "bold"), 
    corner_radius=24, 
    fg_color=COLORS['primary'],
    hover_color=COLORS['primary_light']
)
pdf_btn.pack(pady=14)

# Services Card
paid_card = ctk.CTkFrame(right_scroll, fg_color="#FEF3C7", corner_radius=24, border_width=2, border_color="#F59E0B")
paid_card.pack(fill="x", pady=14)
ctk.CTkLabel(paid_card, text="🌟 4. خدمات تخصصی VARIA", font=("Segoe UI", 15, "bold"), text_color="#B45309").pack(anchor="center", pady=(12, 6))
ctk.CTkLabel(paid_card, text="📊 گزارش VIP | 🗺️ برنامه مدیریت | 👨‍🌾 مشاوره | 💧 آبیاری هوشمند", font=("Segoe UI", 12)).pack(anchor="center", pady=4)
ctk.CTkLabel(paid_card, text="📧 varia.agtech@gmail.com | @varia_support", font=("Segoe UI", 11), text_color=COLORS['primary']).pack(anchor="center", pady=(4, 12))

# Footer
footer = ctk.CTkFrame(root, fg_color="transparent", height=45)
footer.pack(fill="x")
ctk.CTkLabel(
    footer, 
    text="VARIA AgTech Studio | استودیوی فناوری‌های کشاورزی هوشمند", 
    font=("Segoe UI", 11), 
    text_color=COLORS['gray']
).pack(pady=12)


# ============================================================
# توابع
# ============================================================

current_profile = {}

def update_gauge(percent, color):
    canvas = gauge_canvas
    canvas.delete(gauge_arc)
    extent = min(360, max(0, percent * 3.6))
    new_arc = canvas.create_arc(10, 10, 130, 130, start=90, extent=-extent, outline=color, width=12, style="arc")
    canvas.itemconfig(gauge_text, text=f"{percent}%")
    return new_arc

def update_result():
    global current_profile, gauge_arc
    ec_str = ec_entry.get()
    crop = crop_var.get()
    
    if not ec_str:
        severity_label.configure(text="شدت شوری: ⚠️ لطفاً EC را وارد کنید")
        loss_label.configure(text="کاهش عملکرد: ---")
        fao_label.configure(text="کلاس FAO: ---")
        status_label.configure(text="وضعیت: ---")
        soil_label.configure(text="خاک: ---")
        plant_label.configure(text="محصول: ---")
        leaf_label.configure(text="علائم ظاهری: ---")
        free_label.configure(text="")
        res_label.configure(text="")
        gauge_arc = update_gauge(0, COLORS['border'])
        return
    
    try:
        ec = float(ec_str)
    except ValueError:
        severity_label.configure(text="شدت شوری: ❌ مقدار نامعتبر")
        return
    
    ec_clipped = min(ec, 12)
    percent = int((ec_clipped / 12) * 100)
    if percent < 20:
        color = "#2E7D32"
    elif percent < 50:
        color = "#F59E0B"
    elif percent < 80:
        color = "#EA580C"
    else:
        color = "#DC2626"
    gauge_arc = update_gauge(percent, color)
    
    profile = get_salinity_profile(ec, crop)
    current_profile = {**profile, "ec": ec, "crop": crop}
    
    severity_label.configure(text=f"شدت شوری: {profile['severity']} ({profile['severity_score']}%)", text_color=profile['salinity_color'])
    loss_label.configure(text=f"کاهش عملکرد: {profile['loss_percent']}% نسبت به خاک غیرشور", text_color=profile['salinity_color'])
    fao_label.configure(text=f"کلاس FAO: {profile['fao_class']}")
    status_label.configure(text=f"وضعیت: {profile['salinity_level']}", text_color=profile['salinity_color'])
    soil_label.configure(text=f"خاک: {profile['soil_effect_fa']}")
    plant_label.configure(text=f"محصول: {profile['plant_effect_fa']}")
    leaf_label.configure(text=f"علائم ظاهری: {profile['leaf_status_fa']}")
    res_label.configure(text=", ".join(profile['resistant_crops']))
    free_label.configure(text="\n".join([f"• {item}" for item in profile['free_advice_fa']]))
    save_to_history(ec, crop, profile)


def show_history():
    if not os.path.exists(HISTORY_FILE):
        severity_label.configure(text="شدت شوری: 📭 هنوز تحلیلی ذخیره نشده است")
        return
    
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    if not history:
        severity_label.configure(text="شدت شوری: 📭 تاریخچه خالی است")
        return
    
    win = ctk.CTkToplevel(root)
    win.title("تاریخچه تحلیل‌ها")
    win.geometry("550x450")
    win.configure(fg_color="#F0F4F8")
    
    text_box = ctk.CTkTextbox(win, font=("Segoe UI", 13), corner_radius=16)
    text_box.pack(padx=20, pady=20, fill="both", expand=True)
    
    for item in history[-10:]:
        text_box.insert("end", f"📅 {item['date']}\n")
        text_box.insert("end", f"   EC: {item['ec']} | محصول: {item['crop']}\n")
        text_box.insert("end", f"   وضعیت: {item['severity']} | کاهش: {item['loss']}%\n")
        text_box.insert("end", "─" * 45 + "\n")
    
    text_box.configure(state="disabled")


def generate_report():
    if not current_profile:
        severity_label.configure(text="شدت شوری: ⚠️ لطفاً ابتدا تحلیل را انجام دهید")
        return
    try:
        filename = generate_pdf_report(current_profile['ec'], current_profile['crop'], current_profile)
        severity_label.configure(text=f"شدت شوری: ✅ گزارش با موفقیت ذخیره شد")
        os.startfile(filename)
    except Exception as e:
        severity_label.configure(text=f"شدت شوری: ❌ خطا در ساخت گزارش: {str(e)}")


calc_btn.configure(command=update_result)
history_btn.configure(command=show_history)
pdf_btn.configure(command=generate_report)


if __name__ == "__main__":
    root.mainloop()