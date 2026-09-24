import streamlit as st
from datetime import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import io

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="الأكاديمية المهنية للمعلمين - فرع الجيزة",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 1. تنسيقات CSS لضبط RTL وتوسيط العناوين والهيدر
st.markdown("""
    <style>
    /* تطبيق اتجاه النص RTL للواجهة كاملة */
    html, body, [class*="css"], div, h1, h2, h3, h4, h5, h6, p, label, input {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* ضبط مكان القائمة الجانبية لتكون جهة اليمين */
    [data-testid="stSidebar"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* محاذاة حقول الإدخال */
    .stTextInput input {
        text-align: right !important;
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
    }
    
    .academy-title {
        font-size: 28px !important;
        font-weight: bold !important;
        color: #10233F !important;
        text-align: center !important;
        margin-bottom: 5px !important;
    }
    
    .branch-title {
        font-size: 32px !important; /* تكبير حجم خط اسم الفرع */
        font-weight: 900 !important;
        color: #C9A227 !important;
        text-align: center !important;
        margin-top: 5px !important;
    }
    
    /* توسيط أزرار النموذج */
    .stButton button {
        width: 100%;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 🏛️ 2. العرض العلوي (الشعار واسم الأكاديمية والفرع في المنتصف)

# عرض اللوجو في المنتصف
col_left, col_logo, col_right = st.columns([2, 1, 2])
with col_logo:
    # قم باستبدال اسم الصورة باسم ملف اللوجو لديك مثل: "logo.png"
    st.image("logo.png", use_container_width=True)

# عرض اسم الأكاديمية والفرع بخط كبير وفي المنتصف
st.markdown("""
    <div class="header-box">
        <div class="academy-title">الأكاديمية المهنية للمعلمين</div>
        <div class="branch-title">📍 فرع الجيزة</div>
    </div>
""", unsafe_allow_html=True)

# إنشاء الاتصال مع Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# جلب البيانات الحالية من Google Sheets
try:
    df_existing = conn.read(ttl=0)
except Exception:
    df_existing = pd.DataFrame(columns=["كود المعلم", "اسم المعلم", "الرقم القومي", "تاريخ الدخول", "وقت الدخول"])

# 📌 القائمة الجانبية للتنقل
st.sidebar.title("📌 القائمة الرئيسية")
page = st.sidebar.radio("اختر الصفحة:", ["📝 تسجيل دخول معلم", "🔒 لوحة تحكم الإدارة"])

# ==========================================
# 1️⃣ صفحة تسجيل دخول المعلم
# ==========================================
if page == "📝 تسجيل دخول معلم":
    st.subheader("📝 تسجيل حضور المعلمين بالمقر")
    st.caption("أهلاً بك! يُرجى إدخال البيانات التالية لتسجيل حضورك اليوم.")

    with st.form(key="checkin_form", clear_on_submit=True):
        teacher_id = st.text_input("كود المعلم / رقم السجل", placeholder="أدخل كود المعلم الخاص بك")
        teacher_name = st.text_input("اسم المعلم ثلاثي / رباعي", placeholder="أدخل اسمك الكريم")
        national_id = st.text_input("الرقم القومي (اختياري)", placeholder="14 رقم")
        
        submit_button = st.form_submit_button(label="تسجيل الدخول 🚀")

    if submit_button:
        if not teacher_id or not teacher_name:
            st.error("⚠️ يُرجى إدخال كود المعلم والاسم للتمكن من التسجيل.")
        else:
            now = datetime.now()
            today_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")

            already_registered = False
            if not df_existing.empty and "كود المعلم" in df_existing.columns and "تاريخ الدخول" in df_existing.columns:
                check_record = df_existing[(df_existing["كود المعلم"].astype(str) == str(teacher_id)) & 
                                         (df_existing["تاريخ الدخول"] == today_date)]
                if not check_record.empty:
                    already_registered = True

            if already_registered:
                st.warning(f"⚠️ أهلاً أستاذ/ة {teacher_name}، لقد تم تسجيل حضورك اليوم بالفعل!")
            else:
                new_data = pd.DataFrame([{
                    "كود المعلم": teacher_id,
                    "اسم المعلم": teacher_name,
                    "الرقم القومي": national_id,
                    "تاريخ الدخول": today_date,
                    "وقت الدخول": current_time
                }])
                
                updated_df = pd.concat([df_existing, new_data], ignore_index=True)
                conn.update(data=updated_df)
                
                st.success(f"✅ تم تسجيل دخولك بنجاح يا أستاذ/ة {teacher_name} الساعة {current_time}!")
                st.balloons()

# ==========================================
# 2️⃣ صفحة لوحة تحكم الإدارة (محمية)
# ==========================================
elif page == "🔒 لوحة تحكم الإدارة":
    st.subheader("📊 لوحة تحكم الإدارة - سجل الحضور اليومي")

    password = st.text_input("🔑 أدخل كلمة السر للدخول إلى لوحة التحكم:", type="password")

    ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "123456")

    if password == ADMIN_PASSWORD:
        st.success("🔓 تم التحقق بنجاح! أهلاً بك في لوحة إدارة فرع الجيزة.")
        st.divider()

        if df_existing.empty:
            st.info("لا توجد أي بيانات مسجلة حتى الآن.")
        else:
            col1, col2 = st.columns([1, 2])
            with col1:
                selected_date = st.date_input("📅 اختر التاريخ للفلترة:", datetime.now())
                filter_date_str = selected_date.strftime("%Y-%m-%d")

            filtered_df = df_existing[df_existing["تاريخ الدخول"] == filter_date_str]

            st.metric(label=f"إجمالي الحضور يوم {filter_date_str}", value=f"{len(filtered_df)} معلم")

            st.subheader("📋 قائمة الحضور:")
            st.dataframe(filtered_df, use_container_width=True)

            st.subheader("📥 تصدير التقرير")
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='الحضور')
            excel_data = output.getvalue()

            st.download_button(
                label=f"📄 تحميل سجل يوم {filter_date_str} بصيغة Excel",
                data=excel_data,
                file_name=f"giza_academy_attendance_{filter_date_str}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    elif password != "":
        st.error("❌ كلمة السر غير صحيحة!")
