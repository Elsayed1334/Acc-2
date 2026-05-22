import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعدادات الصفحة الاحترافية
st.set_page_config(page_title="نظام المحاسبة والمخازن المحترف", layout="wide", initial_sidebar_state="expanded")

# تخصيص واجهة المستخدم وعرض النصوص من اليمين لليسار (RTL)
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    div[data-testid="stMetricValue"] { text-align: right; }
    </style>
""", unsafe_allow_html=True)

# الاتصال بقاعدة البيانات وتحديث الجداول
conn = sqlite3.connect('accounting_pro.db', check_same_thread=False)
cursor = conn.cursor()

# إنشاء الجداول الاحترافية
cursor.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, stock INTEGER DEFAULT 0, cost_price REAL DEFAULT 0.0, sale_price REAL DEFAULT 0.0, min_limit INTEGER DEFAULT 5)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS partners (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, type TEXT NOT NULL, phone TEXT, balance REAL DEFAULT 0.0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, partner_name TEXT, product_name TEXT, quantity INTEGER, price REAL, total REAL, payment_status TEXT, date TEXT)''')
conn.commit()

# --- القائمة الجانبية للتنقل بين الأقسام ---
st.sidebar.title("🏪 لوحة التحكم")
page = st.sidebar.radio("انتقل إلى:", ["📊 لوحة القيادة والتقارير", "📦 إدارة المخزن والمنتجات", "👥 العملاء والموردين", "🧾 تسجيل الفواتير"])

# ==========================================
# 1. صفحة لوحة القيادة والتقارير
# ==========================================
if page == "📊 لوحة القيادة والتقارير":
    st.title("📊 الأداء المالي والملخص العام")
    
    # حساب المؤشرات
    sales_total = pd.read_sql_query("SELECT SUM(total) FROM transactions WHERE type='بيع'", conn).iloc[0,0] or 0.0
    purchases_total = pd.read_sql_query("SELECT SUM(total) FROM transactions WHERE type='شراء'", conn).iloc[0,0] or 0.0
    
    df_sales_calc = pd.read_sql_query("SELECT t.quantity, t.total, p.cost_price FROM transactions t JOIN products p ON t.product_name = p.name WHERE t.type='بيع'", conn)
    net_profit = sales_total - (df_sales_calc['quantity'] * df_sales_calc['cost_price']).sum() if not df_sales_calc.empty else 0.0
    
    # عرض الكروت المالية
    c1, c2, c3 = st.columns(3)
    c1.metric("📈 إجمالي المبيعات", f"{sales_total:,.2f} ريال")
    c2.metric("📉 إجمالي المشتريات", f"{purchases_total:,.2f} ريال")
    c3.metric("💰 صافي الأرباح التقريبية", f"{net_profit:,.2f} ريال")
    
    st.markdown("---")
    
    # الرسوم البيانية والأداء
    st.subheader("📈 المقارنة البيانية للعمليات")
    df_chart = pd.read_sql_query("SELECT type as 'العملية', SUM(total) as 'الإجمالي' FROM transactions GROUP BY type", conn)
    if not df_chart.empty:
        st.bar_chart(data=df_chart, x='العملية', y='الإجمالي', use_container_width=True)
    
    # تنبيهات النواقص في المخزن
    st.subheader("⚠️ تنبيهات المخزون (أوشكت على النفاد)")
    df_alerts = pd.read_sql_query("SELECT name as 'المنتج', stock as 'الكمية الحالية', min_limit as 'الحد الأدنى' FROM products WHERE stock <= min_limit", conn)
    if not df_alerts.empty:
        st.warning("⚠️ المنتجات التالية وصلت للحد الأدنى أو نفدت!")
        st.dataframe(df_alerts, use_container_width=True)
    else:
        st.success("✅ جميع مستويات المخزون ممتازة!")

# ==========================================
# 2. صفحة إدارة المخزن والمنتجات
# ==========================================
elif page == "📦 إدارة المخزن والمنتجات":
    st.title("📦 مراقبة وجرد المخزن")
    
    with st.expander("✨ إضافة منتج جديد للنظام"):
        col_a, col_b, col_c = st.columns(3)
        p_name = col_a.text_input("اسم المنتج:")
        p_sale = col_b.number_input("سعر البيع الافتراضي:", min_value=0.0)
        p_min = col_c.number_input("حد الأمان المالي (أقل كمية بالمخزن):", min_value=1, value=5)
        
        if st.button("إدخال المنتج في النظام"):
            if p_name:
                cursor.execute("INSERT INTO products (name, sale_price, min_limit) VALUES (?, ?, ?)", (p_name, p_sale, p_min))
                conn.commit()
                st.success(f"تمت إضافة المنتج {p_name} بنجاح!")
                st.rerun()
                
    st.subheader("📋 قائمة جرد المستودع الحالي")
    df_inv = pd.read_sql_query("SELECT id as 'الكود', name as 'اسم المنتج', stock as 'الكمية المتاحة', cost_price as 'متوسط سعر التكلفة', sale_price as 'سعر البيع الافتراضي' FROM products", conn)
    st.dataframe(df_inv, use_container_width=True)

# ==========================================
# 3. صفحة العملاء والموردين
# ==========================================
elif page == "👥 العملاء والموردين":
    st.title("👥 إدارة الحسابات (عملاء وموردين)")
    
    with st.expander("➕ تسجيل عميل أو مورد جديد"):
        col_p1, col_p2, col_p3 = st.columns(3)
        partner_name = col_p1.text_input("الاسم الكامل:")
        partner_type = col_p2.selectbox("الصفة الحسابية:", ["عميل", "مورد"])
        partner_phone = col_p3.text_input("رقم الجوال:")
        
        if st.button("حفظ الحساب"):
            if partner_name:
                cursor.execute("INSERT INTO partners (name, type, phone) VALUES (?, ?, ?)", (partner_name, partner_type, partner_phone))
                conn.commit()
                st.success(f"تم تسجيل {partner_type}: {partner_name}")
                st.rerun()
                
    st.subheader("📊 كشف أرصدة الحسابات الحالية")
    df_partners = pd.read_sql_query("SELECT name as 'الاسم', type as 'الصفة', phone as 'الجوال', balance as 'الحساب الحالي (ريال)' FROM partners", conn)
    st.dataframe(df_partners, use_container_width=True)
    st.caption("ملاحظة: الحساب بالسالب يعني مستحقات عليك، وبالموجب يعني أموال لك في السوق.")

# ==========================================
# 4. صفحة تسجيل الفواتير
# ==========================================
elif page == "🧾 تسجيل الفواتير":
    st.title("🧾 إنشاء الفواتير (بيع وشراء)")
    
    df_p = pd.read_sql_query("SELECT name FROM products", conn)
    df_part = pd.read_sql_query("SELECT name, type FROM partners", conn)
    
    if df_p.empty or df_part.empty:
        st.info("💡 لتسجيل فاتورة، يجب أولاً إضافة منتج واحد على الأقل، وتثبيت اسم عميل أو مورد واحد على الأقل من الأقسام الجانبية.")
    else:
        f_type = st.selectbox("نوع العملية الفورية:", ["شراء من مورد", "بيع لعميل"])
        
        col_f1, col_f2 = st.columns(2)
        # فلترة الأسماء بناءً على نوع الفاتورة
        if "شراء" in f_type:
            list_partners = df_part[df_part['type'] == 'مورد']['name'].tolist()
            chosen_partner = col_f1.selectbox("اختر المورد:", list_partners if list_partners else ["لا يوجد مورد مسجل"])
        else:
            list_partners = df_part[df_part['type'] == 'عميل']['name'].tolist()
            chosen_partner = col_f1.selectbox("اختر العميل:", list_partners if list_partners else ["لا يوجد عميل مسجل"])
            
        chosen_product = col_f2.selectbox("اختر السلعة:", df_p['name'].tolist())
        
        col_f3, col_f4, col_f5 = st.columns(3)
        f_qty = col_f3.number_input("الكمية المطلوبة:", min_value=1, step=1)
        f_price = col_f4.number_input("سعر التوريد/البيع للوحدة:", min_value=0.0)
        f_pay = col_f5.selectbox("طريقة السداد المالي:", ["نقداً (كاش)", "آجل (على الحساب)"])
        
        f_total = f_qty * f_price
        st.subheader(f"💰 المبلغ الإجمالي للفاتورة: {f_total:,.2f} ريال")
        
        if st.button("💳 اعتماد وإصدار الفاتورة"):
            date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            if "شراء" in f_type:
                # تحديث مخزن وتكلفة
                cursor.execute("UPDATE products SET stock = stock + ?, cost_price = ? WHERE name = ?", (f_qty, f_price, chosen_product))
                cursor.execute("INSERT INTO transactions (type, partner_name, product_name, quantity, price, total, payment_status, date) VALUES ('شراء', ?, ?, ?, ?, ?, ?, ?)",
                               (chosen_partner, chosen_product, f_qty, f_price, f_total, f_pay, date_now))
                if f_pay == "آجل (على الحساب)":
                    cursor.execute("UPDATE partners SET balance = balance - ? WHERE name = ?", (f_total, chosen_partner))
                conn.commit()
                st.success("🧾 تم حفظ فاتورة المشتريات وتحديث الحسابات والمخازن!")
                st.rerun()
                
            else: # بيع لعميل
                cursor.execute("SELECT stock FROM products WHERE name = ?", (chosen_product,))
                current_stock = cursor.fetchone()[0]
                
                if current_stock >= f_qty:
                    cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (f_qty, chosen_product))
                    cursor.execute("INSERT INTO transactions (type, partner_name, product_name, quantity, price, total, payment_status, date) VALUES ('بيع', ?, ?, ?, ?, ?, ?, ?)",
                                   (chosen_partner, chosen_product, f_qty, f_price, f_total, f_pay, date_now))
                    if f_pay == "آجل (على الحساب)":
                        cursor.execute("UPDATE partners SET balance = balance + ? WHERE name = ?", (f_total, chosen_partner))
                    conn.commit()
                    st.success("💵 تم إصدار فاتورة البيع وخصم المخزن بنجاح!")
                    st.rerun()
                else:
                    st.error(f"❌ المخزن لا يحتوي على الكمية الكافية! (المتاح حالياً: {current_stock} فقط)")

    st.markdown("---")
    st.subheader("🧾 أرشيف آخر الفواتير الصادرة")
    df_all_trans = pd.read_sql_query("SELECT type as 'النوع', partner_name as 'الطرف الآخر', product_name as 'المنتج', quantity as 'الكمية', total as 'الإجمالي', payment_status as 'الدفع', date as 'التاريخ' FROM transactions ORDER BY id DESC", conn)
    st.dataframe(df_all_trans, use_container_width=True)
