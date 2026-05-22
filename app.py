import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة الاحترافية
st.set_page_config(page_title="نظام رائد المحاسبي المطوّر", layout="wide", initial_sidebar_state="expanded")

# ضبط التصميم ليدعم اللغة العربية من اليمين لليسار (RTL)
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { text-align: right; font-size: 26px !important; font-weight: bold; }
    .report-card { padding: 20px; border-radius: 10px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('accounting_analytics.db', check_same_thread=False)
cursor = conn.cursor()

# إنشاء وتحديث الجداول
cursor.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, stock INTEGER DEFAULT 0, cost_price REAL DEFAULT 0.0, sale_price REAL DEFAULT 0.0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS partners (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, type TEXT NOT NULL, balance REAL DEFAULT 0.0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, partner_name TEXT, product_name TEXT, quantity INTEGER, price REAL, total REAL, payment_method TEXT, date TEXT)''')
conn.commit()

# --- القائمة الجانبية للتنقل ---
st.sidebar.title("🗂️ القائمة الرئيسية")
page = st.sidebar.radio("اختر الشاشة:", ["📊 التقارير والتحليل المالي", "🧾 كاونتر الفواتير والاسترجاع", "⚙️ مدخلات النظام (منتجات وحسابات)"])

# ==========================================
# 1. شاشة التقارير والتحليل المالي
# ==========================================
if page == "📊 التقارير والتحليل المالي":
    st.title("📊 مركز التقارير والتحليل المالي المتقدم")
    
    # جلب الحسابات مع الأخذ في الاعتبار المرتجعات
    sales_total = pd.read_sql_query("SELECT SUM(total) FROM transactions WHERE type='بيع'", conn).iloc[0,0] or 0.0
    ret_sales_total = pd.read_sql_query("SELECT SUM(total) FROM transactions WHERE type='مرتجع بيع'", conn).iloc[0,0] or 0.0
    net_sales = sales_total - ret_sales_total # صافي المبيعات الحقيقي بعد الاسترجاع
    
    purchases_total = pd.read_sql_query("SELECT SUM(total) FROM transactions WHERE type='شراء'", conn).iloc[0,0] or 0.0
    ret_purch_total = pd.read_sql_query("SELECT SUM(total) FROM transactions WHERE type='مرتجع شراء'", conn).iloc[0,0] or 0.0
    net_purchases = purchases_total - ret_purch_total # صافي المشتريات
    
    # حساب تكلفة البضاعة المباعة (COGS) والصافي
    df_cogs = pd.read_sql_query("SELECT t.quantity, p.cost_price, t.type FROM transactions t JOIN products p ON t.product_name = p.name WHERE t.type IN ('بيع', 'مرتجع بيع')", conn)
    cogs_total = 0.0
    if not df_cogs.empty:
        for idx, row in df_cogs.iterrows():
            if row['type'] == 'بيع':
                cogs_total += row['quantity'] * row['cost_price']
            else:
                cogs_total -= row['quantity'] * row['cost_price'] # خصم التكلفة عند الاسترجاع
                
    net_profit = net_sales - cogs_total
    profit_margin = (net_profit / net_sales * 100) if net_sales > 0 else 0.0

    # عرض كروت الأداء المالي
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("📈 إجمالي مبيعاتك (صافي)", f"{net_sales:,.2f} ريال", help="المبيعات مطروح منها المسترجع")
    col_m2.metric("📉 إجمالي مشترياتك (صافي)", f"{net_purchases:,.2f} ريال")
    col_m3.metric("💰 صافي الأرباح الدقيقة", f"{net_profit:,.2f} ريال")
    col_m4.metric("📊 هامش الربح الصافي", f"{profit_margin:.1f} %")
    
    st.markdown("---")
    
    tab_an1, tab_an2 = st.tabs(["💵 تحليل السيولة وطرق الدفع", "📜 دفتر القيود وفواتير الاسترجاع"])
    
    with tab_an1:
        st.subheader("💳 توزيع السيولة والحركات")
        df_pay_split = pd.read_sql_query("SELECT type as 'نوع الحركة', SUM(total) as 'المجموع' FROM transactions GROUP BY type", conn)
        if not df_pay_split.empty:
            st.bar_chart(data=df_pay_split, x='نوع الحركة', y='المجموع', use_container_width=True)
            
    with tab_an2:
        st.subheader("📜 كشف حساب الحركات الشامل")
        df_ledger = pd.read_sql_query("SELECT id as 'رقم القيد', type as 'نوع الحركة', partner_name as 'العميل/المورد', product_name as 'السلعة', quantity as 'الكمية', total as 'الإجمالي', payment_method as 'الطريقة', date as 'التاريخ' FROM transactions ORDER BY id DESC", conn)
        st.dataframe(df_ledger, use_container_width=True, hide_index=True)
