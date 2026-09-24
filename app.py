# 🖨️ دالة إنشاء بطاقة باركود رسمية مع ضبط النص العربي بدون مربعات
@st.cache_data(ttl=3600)
def generate_printable_card(app_url_str, logo_file_path):
    card = Image.new("RGB", (800, 1050), color="#FFFFFF")
    draw = ImageDraw.Draw(card)
    
    # رسم الإطار الخارجي الأنيق
    draw.rectangle([(20, 20), (780, 1030)], outline="#10233F", width=8)
    draw.rectangle([(30, 30), (770, 1020)], outline="#C9A227", width=3)
    
    y_offset = 50
    # 1. رسم الشعار في الأعلى
    if logo_file_path and os.path.exists(logo_file_path):
        try:
            logo = Image.open(logo_file_path).convert("RGBA")
            logo.thumbnail((180, 180))
            logo_x = (800 - logo.width) // 2
            card.paste(logo, (logo_x, y_offset), logo)
            y_offset += logo.height + 20
        except Exception:
            y_offset += 20
    else:
        y_offset += 20

    # 2. جلب ورسم الـ QR Code عالي الدقة في المنتصف
    encoded_url = urllib.parse.quote(app_url_str)
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={encoded_url}&color=10233F"
    
    try:
        req = urllib.request.urlopen(qr_api_url)
        qr_bytes_data = req.read()
        qr_img = Image.open(io.BytesIO(qr_bytes_data)).convert("RGB")
        qr_x = (800 - qr_img.width) // 2
        card.paste(qr_img, (qr_x, y_offset + 30))
    except Exception:
        pass
        
    buf = io.BytesIO()
    card.save(buf, format="PNG")
    return buf.getvalue()
