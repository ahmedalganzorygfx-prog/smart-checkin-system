import streamlit as st
from datetime import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import io

# ضبط إعدادات الصفحة
st.set_page_config(page_title="نظام حضور المعلمين", page_icon="🏫", layout="wide")

# إنشاء الاتصال مع Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# جلب البيانات الحالية من Google Sheets
try:
    df_existing = conn.read(ttl=0)
except Exception:
    df_existing = pd.DataFrame(columns=["كود المعلم", "اسم المعلم", "الرقم القومي", "تاريخ الدخول", "وقت الدخول"])

# 📌 القائمة الجانبية للتنقل بين الصفحات
st.sidebar.title("📌 القائمة الرئيسية")
page = st.sidebar.radio("اختر الصفحة:", ["📝 تسجيل دخول معلم", "🔒 لوحة تحكم الإدارة"])

# ==========================================
# 1️⃣ صفحة تسجيل دخول المعلم
# ==========================================
if page == "📝 تسجيل دخول معلم":
    st.title("🏫 نظام تسجيل دخول المعلمين - الفرع")
    st.write("أهلاً بك! يُرجى إدخال البيانات التالية لتسجيل حضورك اليوم.")

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
    st.title("📊 لوحة تحكم الإدارة - سجل الحضور")

    # إدخال كلمة السر
    password = st.text_input("🔑 أدخل كلمة السر للدخول إلى لوحة التحكم:", type="password")

    # ضبط كلمة السر (يمكن تغيير 123456 إلى أي كلمة سر تريدها)
    ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "123456")

    if password == ADMIN_PASSWORD:
        st.success("🔓 تم التحقق بنجاح! أهلاً بك في لوحة الإدارة.")
        st.divider()

        if df_existing.empty:
            st.info("لا توجد أي بيانات مسجلة حتى الآن.")
        else:
            # فلترة حسب التاريخ
            col1, col2 = st.columns([1, 2])
            with col1:
                selected_date = st.date_input("📅 اختر التاريخ للفلترة:", datetime.now())
                filter_date_str = selected_date.strftime("%Y-%m-%d")

            # تصفية البيانات بناءً على التاريخ المختار
            filtered_df = df_existing[df_existing["تاريخ الدخول"] == filter_date_str]

            # إحصائيات سريعة
            st.metric(label=f"إجمالي الحضور يوم {filter_date_str}", value=f"{len(filtered_df)} معلم")

            # عرض الجدول
            st.subheader("📋 قائمة الحضور:")
            st.dataframe(filtered_df, use_container_width=True)

            # 📥 تصدير البيانات إلى Excel
            st.subheader("📥 تصدير التقرير")
            
            # تحويل البيانات إلى ملف Excel في الذاكرة
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='الحضور')
            excel_data = output.getvalue()

            # زر التنزيل
            st.download_button(
                label=f"📄 تحميل سجل يوم {filter_date_str} بصيغة Excel",
                data=excel_data,
                file_name=f"attendance_{filter_date_str}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    elif password != "":
        st.error("❌ كلمة السر غير صحيحة!")
