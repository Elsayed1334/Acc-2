import { useState, useEffect, useCallback } from "react";

// ========== DATABASE (localStorage) ==========
const DB = {
  get: (key) => JSON.parse(localStorage.getItem(key) || "[]"),
  set: (key, val) => localStorage.setItem(key, JSON.stringify(val)),
  nextId: (arr) => arr.length ? Math.max(...arr.map(x => x.id)) + 1 : 1,
};

const initDB = () => {
  if (!localStorage.getItem("products")) DB.set("products", []);
  if (!localStorage.getItem("partners")) DB.set("partners", []);
  if (!localStorage.getItem("transactions")) DB.set("transactions", []);
};

// ========== ICONS ==========
const Icon = ({ name, size = 20 }) => {
  const icons = {
    dashboard: "M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z",
    inventory: "M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z",
    partners: "M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z",
    invoice: "M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z",
    plus: "M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z",
    alert: "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z",
    check: "M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z",
    close: "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z",
    print: "M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z",
    money: "M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z",
    chart: "M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z",
    search: "M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z",
    trash: "M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z",
    edit: "M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z",
  };
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} fill="currentColor">
      <path d={icons[name] || ""} />
    </svg>
  );
};

// ========== TOAST ==========
const Toast = ({ msg, type, onClose }) => (
  <div style={{
    position: "fixed", bottom: 24, left: "50%", transform: "translateX(-50%)",
    background: type === "error" ? "#ef4444" : type === "warn" ? "#f59e0b" : "#10b981",
    color: "#fff", padding: "12px 24px", borderRadius: 12, zIndex: 9999,
    fontFamily: "Tajawal, sans-serif", fontSize: 15, fontWeight: 600,
    boxShadow: "0 8px 32px rgba(0,0,0,0.25)", display: "flex", gap: 10, alignItems: "center",
    animation: "slideUp 0.3s ease",
  }}>
    {msg}
    <button onClick={onClose} style={{ background: "none", border: "none", color: "#fff", cursor: "pointer" }}>✕</button>
  </div>
);

// ========== MODAL ==========
const Modal = ({ title, onClose, children }) => (
  <div style={{
    position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", zIndex: 1000,
    display: "flex", alignItems: "center", justifyContent: "center", padding: 20,
    backdropFilter: "blur(4px)",
  }}>
    <div style={{
      background: "#1a1f2e", borderRadius: 20, width: "100%", maxWidth: 560,
      boxShadow: "0 24px 80px rgba(0,0,0,0.5)", border: "1px solid #2d3447",
      direction: "rtl",
    }}>
      <div style={{ padding: "20px 24px", borderBottom: "1px solid #2d3447", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ margin: 0, color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", fontSize: 18 }}>{title}</h3>
        <button onClick={onClose} style={{ background: "#2d3447", border: "none", color: "#94a3b8", borderRadius: 8, width: 32, height: 32, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Icon name="close" size={16} />
        </button>
      </div>
      <div style={{ padding: 24 }}>{children}</div>
    </div>
  </div>
);

// ========== STYLED INPUT ==========
const Input = ({ label, ...props }) => (
  <div style={{ marginBottom: 16 }}>
    {label && <label style={{ display: "block", color: "#94a3b8", fontSize: 13, marginBottom: 6, fontFamily: "Tajawal, sans-serif" }}>{label}</label>}
    <input {...props} style={{
      width: "100%", background: "#0f1219", border: "1px solid #2d3447", borderRadius: 10,
      color: "#f1f5f9", padding: "10px 14px", fontSize: 14, fontFamily: "Tajawal, sans-serif",
      outline: "none", boxSizing: "border-box", direction: "rtl",
      transition: "border-color 0.2s",
      ...props.style,
    }}
      onFocus={e => e.target.style.borderColor = "#6366f1"}
      onBlur={e => e.target.style.borderColor = "#2d3447"}
    />
  </div>
);

const Select = ({ label, options, ...props }) => (
  <div style={{ marginBottom: 16 }}>
    {label && <label style={{ display: "block", color: "#94a3b8", fontSize: 13, marginBottom: 6, fontFamily: "Tajawal, sans-serif" }}>{label}</label>}
    <select {...props} style={{
      width: "100%", background: "#0f1219", border: "1px solid #2d3447", borderRadius: 10,
      color: "#f1f5f9", padding: "10px 14px", fontSize: 14, fontFamily: "Tajawal, sans-serif",
      outline: "none", boxSizing: "border-box", direction: "rtl",
      ...props.style,
    }}>
      {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  </div>
);

const Btn = ({ children, variant = "primary", icon, ...props }) => {
  const styles = {
    primary: { background: "linear-gradient(135deg, #6366f1, #8b5cf6)", color: "#fff" },
    success: { background: "linear-gradient(135deg, #10b981, #059669)", color: "#fff" },
    danger: { background: "linear-gradient(135deg, #ef4444, #dc2626)", color: "#fff" },
    ghost: { background: "#2d3447", color: "#94a3b8" },
  };
  return (
    <button {...props} style={{
      ...styles[variant], border: "none", borderRadius: 10, padding: "10px 20px",
      fontFamily: "Tajawal, sans-serif", fontSize: 14, fontWeight: 700, cursor: "pointer",
      display: "inline-flex", alignItems: "center", gap: 8, transition: "opacity 0.2s, transform 0.1s",
      ...props.style,
    }}
      onMouseEnter={e => { e.currentTarget.style.opacity = "0.88"; e.currentTarget.style.transform = "translateY(-1px)"; }}
      onMouseLeave={e => { e.currentTarget.style.opacity = "1"; e.currentTarget.style.transform = "translateY(0)"; }}
    >
      {icon && <Icon name={icon} size={16} />}
      {children}
    </button>
  );
};

// ========== METRIC CARD ==========
const MetricCard = ({ label, value, color, icon }) => (
  <div style={{
    background: "linear-gradient(135deg, #1a1f2e, #161b27)", borderRadius: 16,
    padding: "20px 24px", border: `1px solid ${color}33`,
    boxShadow: `0 4px 24px ${color}15`, direction: "rtl",
  }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
      <div>
        <p style={{ margin: 0, color: "#64748b", fontSize: 13, fontFamily: "Tajawal, sans-serif" }}>{label}</p>
        <p style={{ margin: "8px 0 0", color, fontSize: 22, fontWeight: 800, fontFamily: "Tajawal, sans-serif" }}>{value}</p>
      </div>
      <div style={{ background: `${color}22`, borderRadius: 12, padding: 10, color }}><Icon name={icon} size={22} /></div>
    </div>
  </div>
);

// ========== TABLE ==========
const Table = ({ cols, rows, emptyMsg = "لا توجد بيانات" }) => (
  <div style={{ overflowX: "auto" }}>
    <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: "Tajawal, sans-serif", direction: "rtl" }}>
      <thead>
        <tr>
          {cols.map(c => (
            <th key={c} style={{ padding: "12px 16px", background: "#0f1219", color: "#64748b", fontSize: 13, fontWeight: 600, textAlign: "right", borderBottom: "1px solid #2d3447" }}>{c}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.length === 0 ? (
          <tr><td colSpan={cols.length} style={{ padding: 32, textAlign: "center", color: "#475569", fontFamily: "Tajawal, sans-serif" }}>{emptyMsg}</td></tr>
        ) : rows.map((row, i) => (
          <tr key={i} style={{ borderBottom: "1px solid #1e2535" }}
            onMouseEnter={e => e.currentTarget.style.background = "#1e2535"}
            onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
            {row.map((cell, j) => (
              <td key={j} style={{ padding: "12px 16px", color: "#cbd5e1", fontSize: 14, textAlign: "right" }}>{cell}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

// ========== PAGES ==========

// Dashboard
const Dashboard = ({ products, partners, transactions }) => {
  const sales = transactions.filter(t => t.type === "بيع");
  const purchases = transactions.filter(t => t.type === "شراء");
  const salesTotal = sales.reduce((s, t) => s + t.total, 0);
  const purchasesTotal = purchases.reduce((s, t) => s + t.total, 0);
  const inventoryValue = products.reduce((s, p) => s + p.stock * p.cost_price, 0);

  // Net profit calc
  const netProfit = sales.reduce((profit, t) => {
    const prod = products.find(p => p.name === t.product_name);
    const cost = prod ? prod.cost_price * t.quantity : 0;
    return profit + (t.total - cost);
  }, 0);

  // Payment method summary
  const byMethod = transactions.reduce((acc, t) => {
    acc[t.payment_method] = (acc[t.payment_method] || 0) + t.total;
    return acc;
  }, {});

  // Recent transactions
  const recent = [...transactions].reverse().slice(0, 8);

  return (
    <div>
      <h2 style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", marginBottom: 24 }}>لوحة القيادة المالية</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginBottom: 32 }}>
        <MetricCard label="إجمالي المبيعات" value={`${salesTotal.toLocaleString("ar")} ر.س`} color="#10b981" icon="chart" />
        <MetricCard label="إجمالي المشتريات" value={`${purchasesTotal.toLocaleString("ar")} ر.س`} color="#6366f1" icon="money" />
        <MetricCard label="قيمة المخزون" value={`${inventoryValue.toLocaleString("ar")} ر.س`} color="#f59e0b" icon="inventory" />
        <MetricCard label="صافي الأرباح" value={`${netProfit.toLocaleString("ar")} ر.س`} color={netProfit >= 0 ? "#10b981" : "#ef4444"} icon="money" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        {/* Payment Methods */}
        <div style={{ background: "#1a1f2e", borderRadius: 16, padding: 24, border: "1px solid #2d3447" }}>
          <h3 style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", margin: "0 0 20px", fontSize: 16 }}>💳 توزيع طرق الدفع</h3>
          {Object.keys(byMethod).length === 0 ? (
            <p style={{ color: "#475569", fontFamily: "Tajawal, sans-serif", textAlign: "center", padding: 20 }}>لا توجد بيانات بعد</p>
          ) : Object.entries(byMethod).map(([method, total]) => {
            const pct = Math.round(total / (salesTotal + purchasesTotal) * 100) || 0;
            return (
              <div key={method} style={{ marginBottom: 14 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6, direction: "rtl" }}>
                  <span style={{ color: "#94a3b8", fontFamily: "Tajawal, sans-serif", fontSize: 13 }}>{method}</span>
                  <span style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", fontSize: 13, fontWeight: 700 }}>{total.toLocaleString("ar")} ر.س</span>
                </div>
                <div style={{ height: 8, background: "#0f1219", borderRadius: 4, overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${pct}%`, background: "linear-gradient(90deg, #6366f1, #8b5cf6)", borderRadius: 4, transition: "width 0.6s ease" }} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Low Stock Alerts */}
        <div style={{ background: "#1a1f2e", borderRadius: 16, padding: 24, border: "1px solid #2d3447" }}>
          <h3 style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", margin: "0 0 20px", fontSize: 16 }}>🚨 تنبيهات المخزون</h3>
          {products.filter(p => p.stock <= p.min_limit).length === 0 ? (
            <div style={{ textAlign: "center", padding: 20 }}>
              <div style={{ color: "#10b981", fontSize: 32, marginBottom: 8 }}>✅</div>
              <p style={{ color: "#10b981", fontFamily: "Tajawal, sans-serif" }}>المخزون في وضع ممتاز</p>
            </div>
          ) : products.filter(p => p.stock <= p.min_limit).map(p => (
            <div key={p.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 14px", background: "#ef444415", borderRadius: 10, marginBottom: 8, direction: "rtl", border: "1px solid #ef444430" }}>
              <span style={{ color: "#fca5a5", fontFamily: "Tajawal, sans-serif", fontSize: 14 }}>{p.name}</span>
              <span style={{ color: "#ef4444", fontFamily: "Tajawal, sans-serif", fontSize: 13, fontWeight: 700 }}>متبقي: {p.stock}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Transactions */}
      <div style={{ background: "#1a1f2e", borderRadius: 16, padding: 24, border: "1px solid #2d3447", marginTop: 24 }}>
        <h3 style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", margin: "0 0 20px", fontSize: 16 }}>📜 آخر العمليات</h3>
        <Table
          cols={["رقم", "النوع", "الطرف", "المنتج", "الكمية", "الإجمالي", "الدفع", "التاريخ"]}
          rows={recent.map(t => [
            `#${t.id}`,
            <span style={{ color: t.type === "بيع" ? "#10b981" : "#6366f1", fontWeight: 700 }}>{t.type}</span>,
            t.partner_name, t.product_name, t.quantity,
            `${t.total.toLocaleString("ar")} ر.س`, t.payment_method,
            t.date
          ])}
        />
      </div>
    </div>
  );
};

// Inventory
const Inventory = ({ products, setProducts, toast }) => {
  const [showModal, setShowModal] = useState(false);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState({ barcode: "", name: "", cost_price: "", sale_price: "", min_limit: "5" });

  const save = () => {
    if (!form.name.trim()) return toast("أدخل اسم المنتج", "error");
    const prods = DB.get("products");
    const newProd = { id: DB.nextId(prods), barcode: form.barcode, name: form.name, stock: 0, cost_price: +form.cost_price || 0, sale_price: +form.sale_price || 0, min_limit: +form.min_limit || 5 };
    const updated = [...prods, newProd];
    DB.set("products", updated);
    setProducts(updated);
    setShowModal(false);
    setForm({ barcode: "", name: "", cost_price: "", sale_price: "", min_limit: "5" });
    toast("تم حفظ المنتج بنجاح ✅", "success");
  };

  const del = (id) => {
    if (!confirm("هل تريد حذف هذا المنتج؟")) return;
    const updated = products.filter(p => p.id !== id);
    DB.set("products", updated);
    setProducts(updated);
    toast("تم الحذف", "warn");
  };

  const filtered = products.filter(p => p.name.includes(search) || p.barcode?.includes(search));

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24, direction: "rtl" }}>
        <h2 style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", margin: 0 }}>إدارة المخزون والمنتجات</h2>
        <Btn icon="plus" onClick={() => setShowModal(true)}>إضافة منتج</Btn>
      </div>

      <div style={{ background: "#1a1f2e", borderRadius: 16, padding: 24, border: "1px solid #2d3447", marginBottom: 16 }}>
        <Input label="🔍 بحث عن منتج" placeholder="اسم المنتج أو الباركود..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      <div style={{ background: "#1a1f2e", borderRadius: 16, border: "1px solid #2d3447", overflow: "hidden" }}>
        <Table
          cols={["الباركود", "اسم السلعة", "الكمية", "سعر التكلفة", "سعر البيع", "قيمة المخزون", "الحد الأدنى", "الحالة", "حذف"]}
          rows={filtered.map(p => [
            p.barcode || "—",
            <strong style={{ color: "#f1f5f9" }}>{p.name}</strong>,
            <span style={{ color: p.stock <= p.min_limit ? "#ef4444" : "#10b981", fontWeight: 700 }}>{p.stock}</span>,
            `${p.cost_price.toFixed(2)} ر.س`,
            `${p.sale_price.toFixed(2)} ر.س`,
            `${(p.stock * p.cost_price).toFixed(2)} ر.س`,
            p.min_limit,
            p.stock <= p.min_limit
              ? <span style={{ color: "#ef4444", fontSize: 12, background: "#ef444415", padding: "3px 8px", borderRadius: 6 }}>نفذ</span>
              : <span style={{ color: "#10b981", fontSize: 12, background: "#10b98115", padding: "3px 8px", borderRadius: 6 }}>متوفر</span>,
            <button onClick={() => del(p.id)} style={{ background: "#ef444420", border: "none", color: "#ef4444", borderRadius: 8, padding: "4px 10px", cursor: "pointer" }}>حذف</button>
          ])}
        />
      </div>

      {showModal && (
        <Modal title="إضافة منتج جديد" onClose={() => setShowModal(false)}>
          <Input label="الباركود (اختياري)" value={form.barcode} onChange={e => setForm({ ...form, barcode: e.target.value })} placeholder="مثال: 628..." />
          <Input label="اسم المنتج *" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="اسم السلعة أو الخدمة" />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <Input label="سعر الشراء (التكلفة)" type="number" value={form.cost_price} onChange={e => setForm({ ...form, cost_price: e.target.value })} placeholder="0.00" />
            <Input label="سعر البيع" type="number" value={form.sale_price} onChange={e => setForm({ ...form, sale_price: e.target.value })} placeholder="0.00" />
          </div>
          <Input label="حد التنبيه (الحد الأدنى للمخزون)" type="number" value={form.min_limit} onChange={e => setForm({ ...form, min_limit: e.target.value })} />
          <div style={{ display: "flex", gap: 12, justifyContent: "flex-start" }}>
            <Btn variant="success" icon="check" onClick={save}>حفظ المنتج</Btn>
            <Btn variant="ghost" onClick={() => setShowModal(false)}>إلغاء</Btn>
          </div>
        </Modal>
      )}
    </div>
  );
};

// Partners
const Partners = ({ partners, setPartners, toast }) => {
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: "", type: "عميل", phone: "" });

  const save = () => {
    if (!form.name.trim()) return toast("أدخل اسم الحساب", "error");
    const list = DB.get("partners");
    const newP = { id: DB.nextId(list), ...form, balance: 0 };
    const updated = [...list, newP];
    DB.set("partners", updated);
    setPartners(updated);
    setShowModal(false);
    setForm({ name: "", type: "عميل", phone: "" });
    toast(`تم إنشاء حساب ${form.type}: ${form.name}`, "success");
  };

  const del = (id) => {
    if (!confirm("حذف هذا الحساب؟")) return;
    const updated = partners.filter(p => p.id !== id);
    DB.set("partners", updated);
    setPartners(updated);
    toast("تم الحذف", "warn");
  };

  const clients = partners.filter(p => p.type === "عميل");
  const suppliers = partners.filter(p => p.type === "مورد");

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24, direction: "rtl" }}>
        <h2 style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", margin: 0 }}>العملاء والموردون</h2>
        <Btn icon="plus" onClick={() => setShowModal(true)}>فتح حساب جديد</Btn>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        {/* Clients */}
        <div style={{ background: "#1a1f2e", borderRadius: 16, border: "1px solid #2d3447", overflow: "hidden" }}>
          <div style={{ padding: "16px 20px", borderBottom: "1px solid #2d3447", display: "flex", alignItems: "center", gap: 10, direction: "rtl" }}>
            <span style={{ color: "#10b981" }}>👤</span>
            <h3 style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", margin: 0, fontSize: 16 }}>العملاء ({clients.length})</h3>
          </div>
          <Table
            cols={["الاسم", "الجوال", "الرصيد", "حذف"]}
            rows={clients.map(p => [
              <strong style={{ color: "#f1f5f9" }}>{p.name}</strong>,
              p.phone || "—",
              <span style={{ color: p.balance >= 0 ? "#10b981" : "#ef4444", fontWeight: 700 }}>{p.balance.toFixed(2)} ر.س</span>,
              <button onClick={() => del(p.id)} style={{ background: "#ef444420", border: "none", color: "#ef4444", borderRadius: 8, padding: "4px 10px", cursor: "pointer" }}>حذف</button>
            ])}
          />
        </div>

        {/* Suppliers */}
        <div style={{ background: "#1a1f2e", borderRadius: 16, border: "1px solid #2d3447", overflow: "hidden" }}>
          <div style={{ padding: "16px 20px", borderBottom: "1px solid #2d3447", display: "flex", alignItems: "center", gap: 10, direction: "rtl" }}>
            <span style={{ color: "#6366f1" }}>🏭</span>
            <h3 style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", margin: 0, fontSize: 16 }}>الموردون ({suppliers.length})</h3>
          </div>
          <Table
            cols={["الاسم", "الجوال", "الرصيد", "حذف"]}
            rows={suppliers.map(p => [
              <strong style={{ color: "#f1f5f9" }}>{p.name}</strong>,
              p.phone || "—",
              <span style={{ color: p.balance >= 0 ? "#10b981" : "#ef4444", fontWeight: 700 }}>{p.balance.toFixed(2)} ر.س</span>,
              <button onClick={() => del(p.id)} style={{ background: "#ef444420", border: "none", color: "#ef4444", borderRadius: 8, padding: "4px 10px", cursor: "pointer" }}>حذف</button>
            ])}
          />
        </div>
      </div>

      {showModal && (
        <Modal title="فتح حساب جديد" onClose={() => setShowModal(false)}>
          <Input label="الاسم / اسم الشركة *" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
          <Select label="نوع الحساب" value={form.type} onChange={e => setForm({ ...form, type: e.target.value })}
            options={[{ value: "عميل", label: "👤 عميل" }, { value: "مورد", label: "🏭 مورد" }]} />
          <Input label="رقم الجوال" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} placeholder="05xxxxxxxx" />
          <div style={{ display: "flex", gap: 12 }}>
            <Btn variant="success" icon="check" onClick={save}>إنشاء الحساب</Btn>
            <Btn variant="ghost" onClick={() => setShowModal(false)}>إلغاء</Btn>
          </div>
        </Modal>
      )}
    </div>
  );
};

// Invoice (Counter)
const Invoice = ({ products, setProducts, partners, setPartners, transactions, setTransactions, toast }) => {
  const [type, setType] = useState("بيع");
  const [partner, setPartner] = useState("");
  const [product, setProduct] = useState("");
  const [qty, setQty] = useState(1);
  const [price, setPrice] = useState(0);
  const [method, setMethod] = useState("نقداً (كاش)");
  const [lastInvoice, setLastInvoice] = useState(null);

  const partnerList = partners.filter(p => p.type === (type === "بيع" ? "عميل" : "مورد"));
  const total = qty * price;

  useEffect(() => {
    if (partnerList.length > 0) setPartner(partnerList[0].name);
  }, [type]);

  useEffect(() => {
    if (product) {
      const prod = products.find(p => p.name === product);
      if (prod) setPrice(type === "بيع" ? prod.sale_price : prod.cost_price);
    }
  }, [product, type]);

  useEffect(() => {
    if (products.length > 0) setProduct(products[0].name);
  }, [products]);

  const submit = () => {
    if (!partner || !product) return toast("اختر الطرف والمنتج", "error");
    if (qty < 1) return toast("الكمية يجب أن تكون 1 على الأقل", "error");
    if (price <= 0) return toast("أدخل سعر صحيح", "error");

    const allProds = DB.get("products");
    const allPartners = DB.get("partners");
    const allTx = DB.get("transactions");

    if (type === "بيع") {
      const prod = allProds.find(p => p.name === product);
      if (!prod || prod.stock < qty) return toast(`المخزون غير كافٍ! المتاح: ${prod?.stock || 0}`, "error");
      const updatedProds = allProds.map(p => p.name === product ? { ...p, stock: p.stock - qty } : p);
      DB.set("products", updatedProds);
      setProducts(updatedProds);
      if (method === "آجل (على الحساب)") {
        const updP = allPartners.map(p => p.name === partner ? { ...p, balance: p.balance + total } : p);
        DB.set("partners", updP);
        setPartners(updP);
      }
    } else {
      const updatedProds = allProds.map(p => p.name === product ? { ...p, stock: p.stock + qty, cost_price: price } : p);
      DB.set("products", updatedProds);
      setProducts(updatedProds);
      if (method === "آجل (على الحساب)") {
        const updP = allPartners.map(p => p.name === partner ? { ...p, balance: p.balance - total } : p);
        DB.set("partners", updP);
        setPartners(updP);
      }
    }

    const date = new Date().toLocaleString("ar-SA");
    const newTx = { id: DB.nextId(allTx), type, partner_name: partner, product_name: product, quantity: qty, price, total, payment_method: method, date };
    const updatedTx = [...allTx, newTx];
    DB.set("transactions", updatedTx);
    setTransactions(updatedTx);
    setLastInvoice(newTx);
    toast(`تم اعتماد الفاتورة #${newTx.id} بنجاح 🎉`, "success");
    setQty(1);
  };

  const printInvoice = (tx) => {
    const win = window.open("", "_blank");
    const label = tx.type === "بيع" ? "العميل" : "المورد";
    win.document.write(`
      <html dir="rtl"><head><meta charset="utf-8">
      <style>body{font-family:Tajawal,Arial;padding:30px;direction:rtl;max-width:380px;margin:auto}
      .logo{text-align:center;font-size:22px;font-weight:800;margin-bottom:4px}
      .sub{text-align:center;color:#666;margin-bottom:16px}
      table{width:100%;border-collapse:collapse}td,th{padding:8px;border-bottom:1px solid #eee;font-size:14px}
      .total{font-size:18px;font-weight:800;text-align:center;margin-top:16px;padding:10px;background:#f5f5f5;border-radius:8px}
      .footer{text-align:center;color:#999;font-size:12px;margin-top:16px}
      </style></head><body>
      <div class="logo">🏪 شركة رائد للتجارة</div>
      <div class="sub">${tx.type === "بيع" ? "فاتورة مبيعات" : "فاتورة مشتريات"} | ${tx.date}</div>
      <hr>
      <table>
        <tr><td><b>${label}</b></td><td>${tx.partner_name}</td></tr>
        <tr><td><b>طريقة الدفع</b></td><td>${tx.payment_method}</td></tr>
        <tr><td><b>المنتج</b></td><td>${tx.product_name}</td></tr>
        <tr><td><b>الكمية</b></td><td>${tx.quantity}</td></tr>
        <tr><td><b>سعر الوحدة</b></td><td>${tx.price.toFixed(2)} ر.س</td></tr>
      </table>
      <div class="total">الإجمالي: ${tx.total.toFixed(2)} ريال سعودي</div>
      <div class="footer">فاتورة رقم #${tx.id} — نظام رائد المحاسبي<br>شكراً لتعاملكم معنا 🤝</div>
      </body></html>`);
    win.document.close();
    setTimeout(() => win.print(), 400);
  };

  if (products.length === 0 || partnerList.length === 0) {
    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 60, gap: 16 }}>
        <div style={{ fontSize: 48 }}>⚠️</div>
        <h3 style={{ color: "#f59e0b", fontFamily: "Tajawal, sans-serif", textAlign: "center" }}>
          {products.length === 0 ? "أضف منتجاً واحداً على الأقل أولاً" : `أضف ${type === "بيع" ? "عميلاً" : "مورداً"} أولاً من قسم الحسابات`}
        </h3>
      </div>
    );
  }

  return (
    <div>
      <h2 style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", marginBottom: 24 }}>كاونتر الفواتير الذكي</h2>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        {/* Form */}
        <div style={{ background: "#1a1f2e", borderRadius: 16, padding: 28, border: "1px solid #2d3447", direction: "rtl" }}>
          <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
            {["بيع", "شراء"].map(t => (
              <button key={t} onClick={() => setType(t)} style={{
                flex: 1, padding: "12px", border: "2px solid", borderRadius: 12,
                cursor: "pointer", fontFamily: "Tajawal, sans-serif", fontSize: 15, fontWeight: 700, transition: "all 0.2s",
                background: type === t ? (t === "بيع" ? "#10b98120" : "#6366f120") : "transparent",
                borderColor: type === t ? (t === "بيع" ? "#10b981" : "#6366f1") : "#2d3447",
                color: type === t ? (t === "بيع" ? "#10b981" : "#6366f1") : "#64748b",
              }}>
                {t === "بيع" ? "🛒 فاتورة بيع" : "📥 فاتورة شراء"}
              </button>
            ))}
          </div>

          <Select label={type === "بيع" ? "العميل" : "المورد"} value={partner} onChange={e => setPartner(e.target.value)}
            options={partnerList.map(p => ({ value: p.name, label: p.name }))} />

          <Select label="المنتج" value={product} onChange={e => setProduct(e.target.value)}
            options={products.map(p => ({ value: p.name, label: `${p.name} (متوفر: ${p.stock})` }))} />

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <Input label="الكمية" type="number" min="1" value={qty} onChange={e => setQty(+e.target.value)} />
            <Input label="سعر الوحدة" type="number" step="0.5" value={price} onChange={e => setPrice(+e.target.value)} />
          </div>

          <Select label="طريقة السداد" value={method} onChange={e => setMethod(e.target.value)}
            options={[
              { value: "نقداً (كاش)", label: "💵 نقداً (كاش)" },
              { value: "بطاقة مدى / شبكة", label: "💳 بطاقة مدى / شبكة" },
              { value: "تحويل بنكي مباشر", label: "🏦 تحويل بنكي" },
              { value: "آجل (على الحساب)", label: "📋 آجل (على الحساب)" },
            ]} />

          <div style={{ background: "#0f1219", borderRadius: 12, padding: "16px 20px", marginBottom: 20, direction: "rtl", border: "1px solid #2d3447" }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "#64748b", fontFamily: "Tajawal, sans-serif" }}>الإجمالي:</span>
              <span style={{ color: "#f59e0b", fontFamily: "Tajawal, sans-serif", fontSize: 22, fontWeight: 800 }}>{total.toFixed(2)} ر.س</span>
            </div>
          </div>

          <Btn variant="success" icon="check" onClick={submit} style={{ width: "100%", justifyContent: "center", padding: "14px" }}>
            اعتماد الفاتورة وترحيلها
          </Btn>
        </div>

        {/* Last Invoice Preview */}
        <div style={{ background: "#1a1f2e", borderRadius: 16, padding: 28, border: "1px solid #2d3447", direction: "rtl" }}>
          <h3 style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", margin: "0 0 20px", fontSize: 16 }}>🧾 الفاتورة الأخيرة</h3>
          {!lastInvoice ? (
            <div style={{ textAlign: "center", padding: 40 }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>🧾</div>
              <p style={{ color: "#475569", fontFamily: "Tajawal, sans-serif" }}>لم يتم إصدار فاتورة بعد</p>
            </div>
          ) : (
            <div>
              <div style={{ background: "#0f1219", borderRadius: 12, padding: 20, marginBottom: 16 }}>
                <div style={{ textAlign: "center", marginBottom: 16 }}>
                  <div style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", fontSize: 18, fontWeight: 800 }}>🏪 شركة رائد للتجارة</div>
                  <div style={{ color: "#64748b", fontSize: 13, fontFamily: "Tajawal, sans-serif" }}>
                    {lastInvoice.type === "بيع" ? "فاتورة مبيعات" : "فاتورة مشتريات"} #{lastInvoice.id}
                  </div>
                </div>
                {[
                  [lastInvoice.type === "بيع" ? "العميل" : "المورد", lastInvoice.partner_name],
                  ["المنتج", lastInvoice.product_name],
                  ["الكمية", lastInvoice.quantity],
                  ["سعر الوحدة", `${lastInvoice.price.toFixed(2)} ر.س`],
                  ["طريقة الدفع", lastInvoice.payment_method],
                  ["التاريخ", lastInvoice.date],
                ].map(([k, v]) => (
                  <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #1e2535" }}>
                    <span style={{ color: "#64748b", fontFamily: "Tajawal, sans-serif", fontSize: 14 }}>{k}</span>
                    <span style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", fontSize: 14, fontWeight: 600 }}>{v}</span>
                  </div>
                ))}
                <div style={{ marginTop: 16, background: "#f59e0b15", borderRadius: 10, padding: "14px", textAlign: "center", border: "1px solid #f59e0b40" }}>
                  <span style={{ color: "#64748b", fontFamily: "Tajawal, sans-serif", fontSize: 13 }}>الإجمالي</span>
                  <div style={{ color: "#f59e0b", fontFamily: "Tajawal, sans-serif", fontSize: 26, fontWeight: 800 }}>{lastInvoice.total.toFixed(2)} ر.س</div>
                </div>
              </div>
              <Btn variant="ghost" icon="print" onClick={() => printInvoice(lastInvoice)} style={{ width: "100%", justifyContent: "center" }}>
                طباعة الفاتورة
              </Btn>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ========== APP ==========
export default function App() {
  const [page, setPage] = useState("dashboard");
  const [products, setProducts] = useState([]);
  const [partners, setPartners] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [toastMsg, setToastMsg] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    initDB();
    setProducts(DB.get("products"));
    setPartners(DB.get("partners"));
    setTransactions(DB.get("transactions"));
  }, []);

  const toast = useCallback((msg, type = "success") => {
    setToastMsg({ msg, type });
    setTimeout(() => setToastMsg(null), 3500);
  }, []);

  const nav = [
    { id: "dashboard", label: "لوحة القيادة", icon: "dashboard", color: "#6366f1" },
    { id: "inventory", label: "إدارة المخزون", icon: "inventory", color: "#f59e0b" },
    { id: "partners", label: "العملاء والموردون", icon: "partners", color: "#10b981" },
    { id: "invoice", label: "كاونتر الفواتير", icon: "invoice", color: "#ef4444" },
  ];

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0f1219; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0f1219; }
        ::-webkit-scrollbar-thumb { background: #2d3447; border-radius: 3px; }
        @keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }
        input[type=number]::-webkit-inner-spin-button { opacity: 0.5; }
      `}</style>

      <div style={{ display: "flex", minHeight: "100vh", background: "#0f1219", direction: "rtl" }}>
        {/* Sidebar */}
        <div style={{
          width: sidebarOpen ? 240 : 64, minHeight: "100vh", background: "#13182a",
          borderLeft: "1px solid #1e2535", transition: "width 0.3s ease", flexShrink: 0,
          display: "flex", flexDirection: "column",
        }}>
          {/* Logo */}
          <div style={{ padding: sidebarOpen ? "24px 20px 20px" : "24px 12px 20px", display: "flex", alignItems: "center", gap: 12, borderBottom: "1px solid #1e2535" }}>
            <div style={{ width: 40, height: 40, background: "linear-gradient(135deg,#6366f1,#8b5cf6)", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, fontSize: 20 }}>🏪</div>
            {sidebarOpen && <div>
              <div style={{ color: "#f1f5f9", fontFamily: "Tajawal, sans-serif", fontSize: 15, fontWeight: 800 }}>نظام رائد</div>
              <div style={{ color: "#64748b", fontFamily: "Tajawal, sans-serif", fontSize: 11 }}>المحاسبي المتكامل</div>
            </div>}
          </div>

          {/* Nav */}
          <nav style={{ padding: "12px 8px", flex: 1 }}>
            {nav.map(n => {
              const active = page === n.id;
              return (
                <button key={n.id} onClick={() => setPage(n.id)} style={{
                  width: "100%", display: "flex", alignItems: "center", gap: 12, padding: sidebarOpen ? "12px 14px" : "12px",
                  borderRadius: 12, border: "none", cursor: "pointer", marginBottom: 4, transition: "all 0.2s", justifyContent: sidebarOpen ? "flex-start" : "center",
                  background: active ? `${n.color}20` : "transparent",
                  borderRight: active ? `3px solid ${n.color}` : "3px solid transparent",
                }}>
                  <span style={{ color: active ? n.color : "#475569", flexShrink: 0 }}><Icon name={n.icon} size={20} /></span>
                  {sidebarOpen && <span style={{ color: active ? n.color : "#64748b", fontFamily: "Tajawal, sans-serif", fontSize: 14, fontWeight: active ? 700 : 500 }}>{n.label}</span>}
                </button>
              );
            })}
          </nav>

          {/* Toggle */}
          <button onClick={() => setSidebarOpen(v => !v)} style={{
            margin: "12px 8px", padding: "10px", background: "#1e2535", border: "1px solid #2d3447",
            borderRadius: 10, cursor: "pointer", color: "#64748b", fontFamily: "Tajawal, sans-serif",
            fontSize: 13, display: "flex", alignItems: "center", justifyContent: "center", gap: 8
          }}>
            {sidebarOpen ? "◀ طي" : "▶"}
          </button>
        </div>

        {/* Main */}
        <main style={{ flex: 1, padding: "32px 28px", overflowY: "auto" }}>
          {page === "dashboard" && <Dashboard products={products} partners={partners} transactions={transactions} />}
          {page === "inventory" && <Inventory products={products} setProducts={setProducts} toast={toast} />}
          {page === "partners" && <Partners partners={partners} setPartners={setPartners} toast={toast} />}
          {page === "invoice" && <Invoice products={products} setProducts={setProducts} partners={partners} setPartners={setPartners} transactions={transactions} setTransactions={setTransactions} toast={toast} />}
        </main>
      </div>

      {toastMsg && <Toast msg={toastMsg.msg} type={toastMsg.type} onClose={() => setToastMsg(null)} />}
    </>
  );
}
