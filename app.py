import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="النظام المحاسبي الذكي", layout="wide")
st.title("📊 نظام إدارة المبيعات والمشتريات والمخزون")

conn = sqlite3.connect('accounting_web.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, stock INTEGER DEFAULT 0, cost_price REAL DEFAULT 0.0, sale_price REAL DEFAULT 0.0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, product_name TEXT, quantity INTEGER, price REAL, total REAL, date TEXT)''')
conn.commit()

st.sidebar.header("📥 مدخلات النظام")
menu = st.sidebar.selectbox("اختر العملية:", ["إدارة المنتجات", "فاتورة جديدة"])

if menu == "إدارة المنتجات":
    st.sidebar.subheader("✨ إضافة منتج جديد")
    p_name = st.sidebar.text_input("اسم المنتج:")
    p_sale = st.sidebar.number_input("سعر البيع الافتراضي:", min_value=0.0, step=1.0)
    if st.sidebar.button("حفظ المنتج"):
        if p_name:
            cursor.execute("INSERT INTO products (name, sale_price) VALUES (?, ?)", (p_name, p_sale))
            conn.commit()
            st.sidebar.success(f"تم تسجيل {p_name}!")
elif menu == "فاتورة جديدة":
    st.sidebar.subheader("📝 تسجيل حركة")
    t_type = st.sidebar.selectbox("نوع الفاتورة:", ["شراء (توريد)", "بيع (صرف)"])
    df_p = pd.read_sql_query("SELECT id, name FROM products", conn)
    if not df_p.empty:
        chosen_p = st.sidebar.selectbox("اختر المنتج:", df_p['name'].tolist())
        qty = st.sidebar.number_input("الكمية:", min_value=1, step=1)
        price = st.sidebar.number_input("سعر الوحدة:", min_value=0.0, step=1.0)
        if st.sidebar.button("اعتماد الفاتورة"):
            total = qty * price
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            if t_type == "شراء (توريد)":
                cursor.execute("UPDATE products SET stock = stock + ?, cost_price = ? WHERE name = ?", (qty, price, chosen_p))
                cursor.execute("INSERT INTO transactions (type, product_name, quantity, price, total, date) VALUES ('شراء', ?, ?, ?, ?, ?)", (chosen_p, qty, price, total, date_str))
                conn.commit()
                st.sidebar.success("تم تسجيل المشتريات!")
            elif t_type == "بيع (صرف)":
                cursor.execute("SELECT stock FROM products WHERE name = ?", (chosen_p,))
                current_stock = cursor.fetchone()[0]
                if current_stock >= qty:
                    cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (qty, chosen_p))
                    cursor.execute("INSERT INTO transactions (type, product_name, quantity, price, total, date) VALUES ('بيع', ?, ?, ?, ?, ?)", (chosen_p, qty, price, total, date_str))
                    conn.commit()
                    st.sidebar.success("تم تسجيل المبيعات!")
                else:
                    st.sidebar.error(f"المخزون غير كافٍ! المتاح: {current_stock}")

sales_total = pd.read_sql_query("SELECT SUM(total) FROM transactions WHERE type='بيع'", conn).iloc[0,0] or 0.0
purchases_total = pd.read_sql_query("SELECT SUM(total) FROM transactions WHERE type='شراء'", conn).iloc[0,0] or 0.0
df_sales_calc = pd.read_sql_query("SELECT t.quantity, t.total as sales_value, p.cost_price FROM transactions t JOIN products p ON t.product_name = p.name WHERE t.type='بيع'", conn)
net_profit = sales_total - (df_sales_calc['quantity'] * df_sales_calc['cost_price']).sum() if not df_sales_calc.empty else 0.0

col1, col2, col3 = st.columns(3)
col1.metric("📈 إجمالي المبيعات", f"{sales_total:,.2f} ريال")
col2.metric("📉 إجمالي المشتريات", f"{purchases_total:,.2f} ريال")
col3.metric("💰 صافي الأرباح", f"{net_profit:,.2f} ريال")

st.markdown("---")
tab1, tab2 = st.tabs(["📦 حالة المخزن الحالي", "🧾 سجل الفواتير"])
with tab1:
    df_inventory = pd.read_sql_query("SELECT name as 'اسم المنتج', stock as 'الكمية', cost_price as 'التكلفة', sale_price as 'سعر البيع' FROM products", conn)
    st.dataframe(df_inventory if not df_inventory.empty else "المخزن فارغ حالياً.", use_container_width=True)
with tab2:
    df_trans = pd.read_sql_query("SELECT type as 'النوع', product_name as 'المنتج', quantity as 'الكمية', price as 'السعر', total as 'الإجمالي', date as 'التاريخ' FROM transactions ORDER BY id DESC", conn)
    st.dataframe(df_trans if not df_trans.empty else "لا توجد فواتير بعد.", use_container_width=True)
