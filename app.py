import os
import io
from datetime import datetime
import pandas as pd
import streamlit as st
from PIL import Image
import urllib.parse

# 🖼️ 1. تحديد أيقونة التبويب (Favicon)
logo_path = None
if os.path.exists("Logo.png"):
    logo_path = "Logo.png"
elif os.path.exists("logo.png"):
    logo_path = "logo.png"

page_icon_val = Image.open(logo_path) if logo_path else "🏫"

# ⚙️ 2. ضبط إعدادات الصفحة
st.set_page_config(
    page_title="الأكاديمية المهنية للمعلمين - فرع الجيزة",
    page_icon=page_icon_val,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 3. تنسيقات CSS لضبط RTL وتوسيط العناوين والجدول
st.markdown("""
    <style>
    /* تطبيق اتجاه النص RTL للواجهة الرئيسية فقط بشكل آمن */
    .stMainBlockContainer, [data-testid="stForm"] {
        direction: rtl;
        text-align: right;
    }
    
    /* محاذاة عناصر الإدخال لليمين */
    .stTextInput input, .stDateInput input {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* تنسيق القائمة الجانبية */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        text-align: right;
    }
    
    /* توسيط عنصر الهيدر بالكامل */
    .header-box {
        text-align: center !important;
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        border-bottom: 5px solid #10233F;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        direction: rtl;
    }
    
    .academy-title {
        font-size: 26px !important;
        font-weight: bold !important;
        color: #10233F !important;
        text-align: center !important;
        margin-bottom: 5px !important;
    }
    
    .branch-title {
        font-size: 30px !important;
        font-weight: 900 !important;
        color: #C9A227 !important;
        text-align: center !important;
        margin-top: 5px !important;
    }
    
    .qr-card {
        background-color: #ffffff;
        border: 2px dashed #C9A227;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        margin-bottom: 20px;
    }

    /* توسيط عناوين قسم الإدارة وقائمة الحضور */
    .section-title {
        text-align: center !important;
        color: #10233F;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* ضبط زري التسجيل والدخول */
    .stButton button {
        width: 100%;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 📲 رابط توليد الـ QR بدون حزم إضافية
def get_qr_url(url):
    encoded_url = urllib.parse.quote(url)
    return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_url}&color=10233F"

# 🏛️ 4. العرض العلوي (الشعار واسم الأكاديمية والفرع في المنتصف)
col_left, col_logo, col_right = st.columns([2, 1, 2])
with col_logo:
    if logo_path:
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 60px; margin: 0;'>🏫</h1>", unsafe_allow_html=True)

st.markdown("""
    <div class="header-box">
        <div class="academy-title">الأكاديمية المهنية للمعلمين</div>
        <div class="branch-title">📍 فرع الجيزة</div>
    </div>
""", unsafe_allow_html=True)

# 📂 5. دالة تنظيف البيانات وتنقيتها بالأعمدة الجديدة المطلوبة
EXCEL_FILE = "attendance.xlsx"
EXPECTED_COLUMNS = [
    "كود المعلم",
    "اسم المعلم رباعي",
    "الرقم القومي",
    "الإدارة",
    "مكان العمل",
    "رقم الموبايل",
    "تاريخ الدخول",
    "وقت الدخول"
]

def load_data():
    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE, dtype=str)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
            df = df.dropna(how='all')
            for col in EXPECTED_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df[EXPECTED_COLUMNS]
        except Exception:
            return pd.DataFrame(columns=EXPECTED_COLUMNS)
    else:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

df_existing = load_data()

# 📌 6. القائمة الجانبية للتنقل وعرض الـ QR
st.sidebar.title("📌 القائمة الرئيسية")
page = st.sidebar.radio("اختر الصفحة:", ["📝 تسجيل دخول معلم", "🔒 لوحة تحكم الإدارة"])

st.sidebar.divider()
st.sidebar.markdown("### 📲 رمز QR الخاص بالفرع")

# 🔴 ضع رابط تطبيقك الحقيقي والمنشور على Streamlit Cloud هنا:
app_url = "https://giza-teachers-checkin.streamlit.app"
qr_image_url = get_qr_url(app_url)

st.sidebar.image(qr_image_url, caption="امسح الرمز بدوران هاتف المعلم للتسجيل", use_container_width=True)

# ==========================================
# 1️⃣ صفحة تسجيل دخول المعلم
# ==========================================
if page == "📝 تسجيل دخول معلم":
    col_main, col_qr_view = st.columns([3, 1])
    
    with col_main:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #10233F; margin-bottom: 8px;">📝 تسجيل حضور المعلمين بالمقر</h2>
                <p style="color: #555; font-size: 16px; margin: 0;">أهلاً بك! يُرجى إدخال البيانات التالية لتسجيل حضورك اليوم.</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form(key="checkin_form", clear_on_submit=True):
            teacher_id = st.text_input("كود المعلم / رقم السجل *", placeholder="أدخل كود المعلم الخاص بك")
            teacher_name = st.text_input("اسم المعلم رباعي *", placeholder="أدخل اسمك رباعياً")
            national_id = st.text_input("الرقم القومي (إجباري) *", placeholder="أدخل الرقم القومي المكون من 14 رقم", max_chars=14)
            
            col_adm, col_work = st.columns(2)
            with col_adm:
                administration = st.text_input("الإدارة التعليمية", placeholder="مثال: إدارة جنوب الجيزة")
            with col_work:
                workplace = st.text_input("مكان العمل (المدرسة / الجهة)", placeholder="أدخل اسم المدرسة أو جهة العمل")
                
            mobile_num = st.text_input("رقم الموبايل", placeholder="مثال: 01012345678")
            
            submit_button = st.form_submit_button(label="تسجيل الدخول 🚀")

    with col_qr_view:
        st.markdown("""
            <div class="qr-card">
                <h4 style="color: #10233F; margin-top: 0;">📲 باركود الحضور</h4>
                <p style="font-size: 12px; color: #666;">للتسجيل المباشر من هاتف المعلم</p>
            </div>
        """, unsafe_allow_html=True)
        st.image(qr_image_url, use_container_width=True)

    if submit_button:
        if not teacher_id or not teacher_name or not national_id:
            st.error("⚠️ يُرجى ملء الحقول الإجبارية: (كود المعلم، اسم المعلم رباعي، والرقم القومي).")
        elif len(national_id.strip()) != 14 or not national_id.strip().isdigit():
            st.error("⚠️ يُرجى التأكد من إدخال رقم قومي صحيح مكون من 14 رقماً.")
        else:
            now = datetime.now()
            today_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")

            already_registered = False
            if not df_existing.empty:
                check_record = df_existing[
                    ((df_existing["كود المعلم"].astype(str).str.strip() == str(teacher_id).strip()) |
                     (df_existing["الرقم القومي"].astype(str).str.strip() == str(national_id).strip())) & 
                    (df_existing["تاريخ الدخول"].astype(str) == today_date)
                ]
                if not check_record.empty:
                    already_registered = True

            if already_registered:
                st.warning(f"⚠️ أهلاً أستاذ/ة {teacher_name}، لقد تم تسجيل حضورك اليوم بالفعل!")
            else:
                new_data = pd.DataFrame([{
                    "كود المعلم": str(teacher_id).strip(),
                    "اسم المعلم رباعي": str(teacher_name).strip(),
                    "الرقم القومي": str(national_id).strip(),
                    "الإدارة": str(administration).strip() if administration else "-",
                    "مكان العمل": str(workplace).strip() if workplace else "-",
                    "رقم الموبايل": str(mobile_num).strip() if mobile_num else "-",
                    "تاريخ الدخول": str(today_date),
                    "وقت الدخول": str(current_time)
                }])
                
                updated_df = pd.concat([df_existing, new_data], ignore_index=True)
                updated_df = updated_df[EXPECTED_COLUMNS]
                updated_df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
                
                st.success(f"✅ تم تسجيل دخولك بنجاح يا أستاذ/ة {teacher_name} الساعة {current_time}!")
                st.balloons()

# ==========================================
# 2️⃣ صفحة لوحة تحكم الإدارة
# ==========================================
elif page == "🔒 لوحة تحكم الإدارة":
    st.markdown("<h2 class='section-title'>📊 لوحة تحكم الإدارة - سجل الحضور اليومي</h2>", unsafe_allow_html=True)

    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        col_s1, col_form, col_s2 = st.columns([1, 2, 1])
        with col_form:
            with st.form(key="admin_login_form"):
                password = st.text_input("🔑 أدخل كلمة السر للدخول إلى لوحة التحكم:", type="password")
                login_button = st.form_submit_button(label="دخول 🔓")
            
            ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "123456")

            if login_button:
                if password == ADMIN_PASSWORD:
                    st.session_state["admin_logged_in"] = True
                    st.rerun()
                else:
                    st.error("❌ كلمة السر غير صحيحة!")

    if st.session_state["admin_logged_in"]:
        col_title, col_logout = st.columns([4, 1])
        with col_logout:
            if st.button("تسجيل الخروج 🔒"):
                st.session_state["admin_logged_in"] = False
                st.rerun()

        st.success("🔓 تم التحقق بنجاح! أهلاً بك في لوحة إدارة فرع الجيزة.")
        st.divider()

        if df_existing.empty:
            st.info("لا توجد أي بيانات مسجلة حتى الآن.")
        else:
            col_space1, col_filter, col_space2 = st.columns([1, 2, 1])
            with col_filter:
                selected_date = st.date_input("📅 اختر التاريخ للفلترة:", datetime.now())
                filter_date_str = selected_date.strftime("%Y-%m-%d")

            filtered_df = df_existing[df_existing["تاريخ الدخول"] == filter_date_str]

            m_col1, m_col2, m_col3 = st.columns([1, 2, 1])
            with m_col2:
                st.metric(label=f"إجمالي الحضور يوم {filter_date_str}", value=f"{len(filtered_df)} معلم")

            st.markdown("<h3 class='section-title'>📋 قائمة الحضور</h3>", unsafe_allow_html=True)
            
            st.dataframe(
                filtered_df[EXPECTED_COLUMNS],
                use_container_width=True,
                hide_index=True
            )

            st.markdown("<h3 class='section-title'>📥 تصدير التقرير</h3>", unsafe_allow_html=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df[EXPECTED_COLUMNS].to_excel(writer, index=False, sheet_name='الحضور')
            excel_data = output.getvalue()

            b_col1, b_col2, b_col3 = st.columns([1, 2, 1])
            with b_col2:
                st.download_button(
                    label=f"📄 تحميل سجل يوم {filter_date_str} بصيغة Excel",
                    data=excel_data,
                    file_name=f"giza_academy_attendance_{filter_date_str}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
