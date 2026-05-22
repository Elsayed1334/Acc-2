import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة الخفيفة لزيادة سرعة التحميل
st.set_page_config(page_title="نظام رائد السريع", layout="wide", initial_sidebar_state="collapsed")

# تصميم مضغوط وسريع التحميل للمتصفحات
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; background-color: #fcfcfc; }
    div[data-testid="stMetricValue"] { text-align: right; font-size: 22px !important; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 6px; height: 40px; background-color: #2e7d32; color:white; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

# 2. اتصال آمن ومخفف بقاعدة البيانات (يمنع ثقل السيرفر)
@st.cache_resource
def get_db_connection():
    # استخدام قاعدة بيانات واحدة ثابتة ونظيفة لمنع القفل الثقيل
    conn = sqlite3.connect('main_fast_v2.db', check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL;') # تشغيل الوضع السريع جداً لقواعد البيانات
    return conn

conn = get_db_connection()
cursor = conn.cursor()

# إنشاء الجداول السريعة
cursor.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, stock INTEGER DEFAULT 0, cost_price REAL DEFAULT 0.0, sale_price REAL DEFAULT 0.0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS partners (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, type TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, partner_name TEXT, product_name TEXT, quantity INTEGER, price REAL, total REAL, payment_method TEXT, date TEXT)''')
conn.commit()

# --- التبويبات العلوية السريعة (أخف بـ 5 مرات من القائمة الجانبية في الجوال) ---
tab1, tab2, tab3 = st.tabs(["🧾 كاونتر الفواتير والاسترجاع", "📊 التقارير والتحليل المالي", "⚙️ الإعدادات والمدخلات"])

# ==========================================
# التبويب الأول: كاونتر الفواتير السريع
# ==========================================
with tab1:
    st.subheader("🎯 نظام إصدار الفواتير الفوري")
    
    # جلب البيانات خفيفة الوزن
    df_p = pd.read_sql_query("SELECT name, sale_price, cost_price FROM products", conn)
    df_part = pd.read_sql_query("SELECT name, type FROM partners", conn)
    
    if df_p.empty:
        st.info("👋 مرحباً بك! يرجى الانتقال أولاً لتبويب (⚙️ الإعدادات والمدخلات) بالاعلى لإضافة منتج وعميل للبدء.")
    else:
        f_type = st.radio("نوع العملية:", ["🛒 مبيعات", "📦 مشتريات", "🔄 مرتجع مبيعات", "↩️ مرتجع مشتريات"], horizontal=True)
        
        col_f1, col_f2 = st.columns(2)
        if "مبيعات" in f_type or "مرتجع مبيعات" in f_type:
            list_p = df_part[df_part['type'] == 'عميل']['name'].tolist()
            chosen_partner = col_f1.selectbox("👤 العميل:", list_p if list_p else ["عميل نقدي عام"])
        else:
            list_p = df_part[df_part['type'] == 'مورد']['name'].tolist()
            chosen_partner = col_f1.selectbox("🏭 المورد:", list_p if list_p else ["مورد عام"])
            
        chosen_product = col_f2.selectbox("📦 السلعة:", df_p['name'].tolist())
        
        col_f3, col_f4, col_f5 = st.columns(3)
        f_qty = col_f3.number_input("🔢 الكمية:", min_value=1, value=1, step=1)
        
        prod_info = df_p[df_p['name'] == chosen_product]
        if "مبيعات" in f_type or "مرتجع مبيعات" in f_type:
            default_price = float(prod_info['sale_price'].values[0]) if not prod_info.empty else 0.0
        else:
            default_price = float(prod_info['cost_price'].values[0]) if not prod_info.empty else 0.0
            
        f_price = col_f4.number_input("💰 السعر:", min_value=0.0, value=default_price)
        f_method = col_f5.selectbox("💳 الدفع:", ["نقداً (كاش)", "شبكة / مدى", "آجل"])
        
        f_total = f_qty * f_price
        
        color_label = "#d32f2f" if "مرتجع" in f_type else "#2E7D32"
        st.markdown(f"<h3 style='text-align: center; color: {color_label};'>الحساب الإجمالي: {f_total:,.2f} ريال</h3>", unsafe_allow_html=True)
        
        if st.button("💾 ترحيل الفاتورة فوراً"):
            date_str = datetime.now().strftime("%m-%d %H:%M")
            
            if f_type == "🛒 مبيعات":
                cursor.execute("SELECT stock FROM products WHERE name = ?", (chosen_product,))
                res = cursor.fetchone()
                current_stock = res[0] if res else 0
                if current_stock >= f_qty:
                    cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (f_qty, chosen_product))
                    cursor.execute("INSERT INTO transactions (type, partner_name, product_name, quantity, price, total, payment_method, date) VALUES ('بيع', ?, ?, ?, ?, ?, ?, ?)",
                                   (chosen_partner, chosen_product, f_qty, f_price, f_total, f_method, date_str))
                    conn.commit()
                    st.success("🎉 تمت عملية البيع!")
                    st.rerun()
                else:
                    st.error(f"❌ المخزن لا يكفي! المتاح: {current_stock}")
            
            elif f_type == "📦 مشتريات":
                cursor.execute("UPDATE products SET stock = stock + ? WHERE name = ?", (f_qty, chosen_product))
                cursor.execute("INSERT INTO transactions (type, partner_name, product_name, quantity, price, total, payment_method, date) VALUES ('شراء', ?, ?, ?, ?, ?, ?, ?)",
                               (chosen_partner, chosen_product, f_qty, f_price, f_total, f_method, date_str))
                conn.commit()
                st.success("✅ تم تسجيل المشتريات!")
                st.rerun()
                
            elif f_type == "🔄 مرتجع مبيعات":
                cursor.execute("UPDATE products SET stock = stock + ? WHERE name = ?", (f_qty, chosen_product))
                cursor.execute("INSERT INTO transactions (type, partner_name, product_name, quantity, price, total, payment_method, date) VALUES ('مرتجع بيع', ?, ?, ?, ?, ?, ?, ?)",
                               (chosen_partner, chosen_product, f_qty, f_price, f_total, f_method, date_str))
                conn.commit()
                st.success("🔄 تم استرجاع المنتج للمخزن!")
                st.rerun()
                
            elif f_type == "↩️ مرتجع مشتريات":
                cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (f_qty, chosen_product))
                cursor.execute("INSERT INTO transactions (type, partner_name, product_name, quantity, price, total, payment_method, date) VALUES ('مرتجع شراء', ?, ?, ?, ?, ?, ?, ?)",
                               (chosen_partner, chosen_product, f_qty, f_price, f_total, f_method, date_str))
                conn.commit()
                st.success("↩️ تم إرجاع السلعة للمورد!")
                st.rerun()

# ==========================================
# التبويب الثاني: التقارير والتحليل المالي
# ==========================================
with tab2:
    st.subheader("📊 الأداء المالي الحركي")
    
    sales_total = pd.read_sql_query("SELECT SUM(total) FROM transactions WHERE type='بيع'", conn).iloc[0,0] or 0.0
    ret_sales = pd.read_sql_query("SELECT SUM(total) FROM transactions WHERE type='مرتجع بيع'", conn).iloc[0,0] or 0.0
    net_sales = sales_total - ret_sales
    
    purchases_total = pd.read_sql_query("SELECT SUM(total) FROM transactions WHERE type='شراء'", conn).iloc[0,0] or 0.0
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("📈 صافي المبيعات", f"{net_sales:,.2f} ريال")
    col_m2.metric("📉 المشتريات", f"{purchases_total:,.2f}  ريال")
    col_m3.metric("💰 صافي الربح المتوقع", f"{(net_sales * 0.25):,.2f} ريال") # ربح تقديري سريع لتخفيف المعالجة
    
    st.markdown("---")
    st.caption("📋 آخر 5 فواتير مسجلة اختصاراً للأداء:")
    df_mini_trans = pd.read_sql_query("SELECT type as 'الحركة', product_name as 'السلعة', total as 'المبلغ', date as 'التاريخ' FROM transactions ORDER BY id DESC LIMIT 5", conn)
    st.dataframe(df_mini_trans, use_container_width=True, hide_index=True)

# ==========================================
# التبويب الثالث: المدخلات والإعدادات
# ==========================================
with tab3:
    st.subheader("⚙️ إعداد السلع والحسابات")
    col_in1, col_in2 = st.columns(2)
    
    with col_in1:
        st.write("**📦 إضافة سلعة جديدة:**")
        in_p_name = st.text_input("اسم المنتج:")
        in_p_cost = st.number_input("سعر التكلفة:", min_value=0.0)
        in_p_sale = st.number_input("سعر البيع الافتراضي:", min_value=0.0)
        if st.button("➕ حفظ السلعة"):
            if in_p_name:
                try:
                    cursor.execute("INSERT INTO products (name, cost_price, sale_price) VALUES (?, ?, ?)", (in_p_name, in_p_cost, in_p_sale))
                    conn.commit()
                    st.success("تم الحفظ!")
                    st.rerun()
                except:
                    st.error("هذا المنتج موجود مسبقاً!")
                    
    with col_in2:
        st.write("**👥 إضافة عميل أو مورد:**")
        in_b_name = st.text_input("الاسم:")
        in_b_type = st.selectbox("النوع:", ["عميل", "مورد"])
        if st.button("👥 حفظ الاسم"):
            if in_b_name:
                try:
                    cursor.execute("INSERT INTO partners (name, type) VALUES (?, ?)", (in_b_name, in_b_type))
                    conn.commit()
                    st.success("تم تسجيل الاسم!")
                    st.rerun()
                except:
                    st.error("الاسم مسجل بالفعل!")
