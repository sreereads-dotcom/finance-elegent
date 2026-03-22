import streamlit as st
import json, os, pandas as pd, plotly.graph_objects as go
from datetime import datetime
from logos import LOGOS

st.set_page_config(page_title="Finance Manager", page_icon="💎", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
* { font-family: 'Outfit', sans-serif !important; }
.stApp { background: linear-gradient(135deg,#080810 0%,#0d0820 50%,#080810 100%); }
.block-container { padding: 1.5rem 2rem 4rem; max-width: 960px; }
::-webkit-scrollbar{width:4px} ::-webkit-scrollbar-track{background:#0d0820} ::-webkit-scrollbar-thumb{background:#ff2d78;border-radius:99px}

/* HERO */
.hero-header{background:linear-gradient(135deg,#1a0825,#0d0820,#1a0525);border:1px solid rgba(255,45,120,.25);border-radius:20px;padding:28px 32px;margin-bottom:24px;position:relative;overflow:hidden}
.hero-header::before{content:'';position:absolute;top:-60px;right:-60px;width:200px;height:200px;background:radial-gradient(circle,rgba(255,45,120,.2),transparent 70%);border-radius:50%}
.hero-title{font-size:32px;font-weight:800;background:linear-gradient(135deg,#ff2d78,#ff85b3,#c020f0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0;letter-spacing:-0.5px}
.hero-sub{font-size:13px;color:rgba(255,255,255,.4);margin-top:4px;letter-spacing:.5px}

/* 3D BUTTONS */
.stButton>button{background:linear-gradient(180deg,#ff2d78 0%,#cc1f5f 100%)!important;color:white!important;border:none!important;border-radius:10px!important;font-weight:600!important;font-family:'Outfit',sans-serif!important;font-size:13px!important;padding:10px 18px!important;box-shadow:0 6px 0 #7a0f36,0 8px 20px rgba(255,45,120,.4)!important;transition:all .15s ease!important;letter-spacing:.3px!important}
.stButton>button:hover{box-shadow:0 6px 0 #7a0f36,0 12px 28px rgba(255,45,120,.5)!important;transform:translateY(-2px)!important}
.stButton>button:active{box-shadow:0 2px 0 #7a0f36,0 4px 12px rgba(255,45,120,.3)!important;transform:translateY(4px)!important}

/* METRICS */
div[data-testid="stMetric"]{background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,45,120,.15)!important;border-radius:14px!important;padding:16px!important;transition:all .3s!important}
div[data-testid="stMetric"]:hover{border-color:rgba(255,45,120,.4)!important;background:rgba(255,45,120,.05)!important}
div[data-testid="stMetricLabel"]{color:rgba(255,255,255,.45)!important;font-size:11px!important;font-weight:600!important;letter-spacing:.08em!important}
div[data-testid="stMetricValue"]{color:white!important;font-family:'JetBrains Mono',monospace!important;font-size:22px!important}

/* TABS */
.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,.03);border-radius:12px;padding:4px;border:1px solid rgba(255,45,120,.1);gap:2px}
.stTabs [data-baseweb="tab"]{border-radius:8px!important;font-weight:600!important;font-size:13px!important;color:rgba(255,255,255,.5)!important;padding:8px 18px!important}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(255,45,120,.25),rgba(160,32,240,.2))!important;color:#ff2d78!important;border:1px solid rgba(255,45,120,.3)!important}

/* INPUTS */
.stNumberInput input,.stTextInput input{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,45,120,.2)!important;border-radius:8px!important;color:white!important}
.stNumberInput input:focus,.stTextInput input:focus{border-color:rgba(255,45,120,.6)!important;box-shadow:0 0 0 3px rgba(255,45,120,.1)!important}

/* EXPANDER */
.streamlit-expanderHeader{background:rgba(255,255,255,.02)!important;border:1px solid rgba(255,45,120,.12)!important;border-radius:10px!important;color:rgba(255,255,255,.8)!important;font-weight:600!important}
.streamlit-expanderContent{background:rgba(255,255,255,.01)!important;border:1px solid rgba(255,45,120,.08)!important;border-top:none!important;border-radius:0 0 10px 10px!important}

hr{border-color:rgba(255,45,120,.12)!important}
.stSuccess{background:rgba(0,230,118,.08)!important;border-color:rgba(0,230,118,.2)!important;border-radius:10px!important}
.stWarning{background:rgba(255,171,0,.08)!important;border-color:rgba(255,171,0,.2)!important;border-radius:10px!important}
.stError{background:rgba(255,23,68,.08)!important;border-color:rgba(255,23,68,.2)!important;border-radius:10px!important}
.stInfo{background:rgba(41,121,255,.08)!important;border-color:rgba(41,121,255,.2)!important;border-radius:10px!important}
</style>
""", unsafe_allow_html=True)

# ── CONFIG ────────────────────────────────────────────────────────────
GROUPS = [
    {"name":"Rent",          "type":"expense",  "color":"#a78bfa"},
    {"name":"Loan / EMI",    "type":"savings",  "color":"#2979ff"},
    {"name":"KSFE",          "type":"savings",  "color":"#00bcd4"},
    {"name":"Credit Card",   "type":"expense",  "color":"#ff2d78"},
    {"name":"Investment",    "type":"savings",  "color":"#00e676"},
    {"name":"RD / Personal", "type":"savings",  "color":"#64b5f6"},
    {"name":"Other",         "type":"expense",  "color":"#9e9e9e"},
]
GMAP        = {g["name"]: g for g in GROUPS}
GROUP_NAMES = [g["name"] for g in GROUPS]
SAV_GROUPS  = [g["name"] for g in GROUPS if g["type"]=="savings"]
EXP_GROUPS  = [g["name"] for g in GROUPS if g["type"]=="expense"]
MONTHS      = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
DATA_FILE   = "data.json"

ITEM_LOGOS = {
    "SBI Loan":        LOGOS["sbi"],
    "KSFE 1":          LOGOS["ksfe"],
    "KSFE 2":          LOGOS["ksfe"],
    "KSFE 3":          LOGOS["ksfe"],
    "School Van":      LOGOS["school_van"],
    "SIP":             LOGOS["groww"],
    "Prabeena RD":     LOGOS["blm"],
    "Ranganswami RD":  LOGOS["india_post"],
    "SBI Credit Card": LOGOS["sbi_card"],
    "AU Credit Card":  LOGOS["au"],
    "ICICI Card 1":    LOGOS["icici1"],
    "ICICI Card 2":    LOGOS["icici2"],
    "GVR":             LOGOS["gvr"],
}

# ── DATA ──────────────────────────────────────────────────────────────
def default_data():
    return {
        "months": {
            "Apr 2026": {
                "income": [{"id":1,"name":"Salary","amt":0}],
                "dues": [
                    {"id":1,  "name":"Rent (main)",    "amt":13000,"group":"Rent",          "note":"",             "recur":True,"status":"pending"},
                    {"id":2,  "name":"Rent (2nd)",      "amt":6750, "group":"Rent",          "note":"5750+1000",    "recur":True,"status":"pending"},
                    {"id":3,  "name":"SBI Loan",        "amt":34800,"group":"Loan / EMI",    "note":"",             "recur":True,"status":"pending"},
                    {"id":4,  "name":"KSFE 1",          "amt":6400, "group":"KSFE",          "note":"",             "recur":True,"status":"pending"},
                    {"id":5,  "name":"KSFE 2",          "amt":13812,"group":"KSFE",          "note":"",             "recur":True,"status":"pending"},
                    {"id":6,  "name":"KSFE 3",          "amt":7983, "group":"KSFE",          "note":"",             "recur":True,"status":"pending"},
                    {"id":7,  "name":"School Van",      "amt":2000, "group":"Other",         "note":"",             "recur":True,"status":"pending"},
                    {"id":8,  "name":"SIP",             "amt":10000,"group":"Investment",    "note":"",             "recur":True,"status":"pending"},
                    {"id":9,  "name":"Prabeena RD",     "amt":1000, "group":"RD / Personal", "note":"RD payment",   "recur":True,"status":"pending"},
                    {"id":10, "name":"Ranganswami RD",  "amt":1000, "group":"RD / Personal", "note":"RD payment",   "recur":True,"status":"pending"},
                    {"id":11, "name":"SBI Credit Card", "amt":7254, "group":"Credit Card",   "note":"",             "recur":True,"status":"pending"},
                    {"id":12, "name":"AU Credit Card",  "amt":359,  "group":"Credit Card",   "note":"",             "recur":True,"status":"pending"},
                    {"id":13, "name":"ICICI Card 1",    "amt":3355, "group":"Credit Card",   "note":"",             "recur":True,"status":"pending"},
                    {"id":14, "name":"ICICI Card 2",    "amt":0,    "group":"Credit Card",   "note":"Update amount","recur":True,"status":"pending"},
                    {"id":15, "name":"Achan",           "amt":3000, "group":"Other",         "note":"",             "recur":True,"status":"done"},
                    {"id":16, "name":"Amma",            "amt":2500, "group":"Other",         "note":"",             "recur":True,"status":"done"},
                    {"id":17, "name":"GVR",             "amt":3000, "group":"Other",         "note":"",             "recur":True,"status":"done"},
                ]
            }
        },
        "cur_month":"Apr 2026",
        "next_id":100
    }

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            raw = open(DATA_FILE).read().strip()
            if raw and raw != "{}":
                p = json.loads(raw)
                if "months" in p and p["months"] and "cur_month" in p:
                    return p
    except Exception:
        pass
    d = default_data(); save_data(d); return d

def save_data(data):
    try:
        with open(DATA_FILE,"w") as f: json.dump(data,f,indent=2)
    except Exception as e:
        st.warning(f"Save warning: {e}")

if "data" not in st.session_state:
    st.session_state.data = load_data()

def D():    return st.session_state.data
def save(): save_data(D())
def get_id():
    D()["next_id"] = D().get("next_id",100)+1; save(); return D()["next_id"]

def cur_month():
    cm = D().get("cur_month","")
    if cm not in D()["months"]: cm=list(D()["months"].keys())[0]; D()["cur_month"]=cm
    return cm

def cur_mdata():  return D()["months"][cur_month()]
def cur_dues():   return cur_mdata()["dues"]
def cur_income(): return cur_mdata()["income"]
def fmt(n):       return f"₹{int(round(n)):,}"

def calcs():
    inc   = sum(i["amt"] for i in cur_income())
    all_d = cur_dues()
    sav   = sum(d["amt"] for d in all_d if d["group"] in SAV_GROUPS)
    exp   = sum(d["amt"] for d in all_d if d["group"] in EXP_GROUPS)
    paid  = sum(d["amt"] for d in all_d if d["status"]=="done")
    pend  = sum(d["amt"] for d in all_d if d["status"]=="pending")
    over  = sum(d["amt"] for d in all_d if d["status"]=="overdue")
    return {"inc":inc,"sav":sav,"exp":exp,"balance":inc-sav-exp,"paid":paid,"pend":pend,"over":over}

def logo_img(name, size=34):
    logo = ITEM_LOGOS.get(name)
    if logo:
        return f'<img src="{logo}" style="width:{size}px;height:{size}px;object-fit:contain;border-radius:6px;background:rgba(255,255,255,.08);padding:3px">'
    c = ["#ff2d78","#2979ff","#00e676","#ffab00","#a78bfa"][hash(name)%5]
    return f'<div style="width:{size}px;height:{size}px;border-radius:6px;background:{c}22;border:1px solid {c}44;display:flex;align-items:center;justify-content:center;font-size:{int(size*.4)}px;font-weight:700;color:{c}">{name[0].upper()}</div>'

# ── HEADER ────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-header">
  <div class="hero-title">💎 Finance Manager</div>
  <div class="hero-sub">PERSONAL WEALTH TRACKER &nbsp;·&nbsp; {cur_month().upper()}</div>
</div>
""", unsafe_allow_html=True)

hc1,hc2,hc3,hc4 = st.columns([2,2,2,1])
with hc1:
    ml  = list(D()["months"].keys())
    idx = ml.index(cur_month()) if cur_month() in ml else 0
    sel = st.selectbox("Month", ml, index=idx, label_visibility="collapsed")
    if sel != cur_month(): D()["cur_month"]=sel; save(); st.rerun()
with hc2:
    mon,yr = cur_month().split(" ")
    ni=MONTHS.index(mon)+1; ny=int(yr)
    if ni>11: ni=0; ny+=1
    nk=f"{MONTHS[ni]} {ny}"
    if st.button(f"➕ Create {nk}", use_container_width=True):
        if nk not in D()["months"]:
            rec=[dict(d,id=get_id(),status="pending") for d in cur_dues() if d["recur"]]
            inc=[dict(i,id=get_id()) for i in cur_income()]
            nm={nk:{"income":inc,"dues":rec}}; nm.update(D()["months"])
            D()["months"]=nm; D()["cur_month"]=nk; save(); st.success(f"✅ {nk} created!"); st.rerun()
        else: st.warning(f"{nk} already exists.")
with hc3:
    if st.button("✅ Mark All Paid", use_container_width=True):
        for d in cur_dues(): d["status"]="done"
        save(); st.rerun()
with hc4:
    if st.button("↺ Reset", use_container_width=True):
        for d in cur_dues(): d["status"]="pending"
        save(); st.rerun()

st.divider()

# ── TABS ──────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5 = st.tabs(["📊  Overview","📋  Dues","➕  Add Item","📈  Analysis","📑  Reports"])

# ════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.4);margin:8px 0 12px"><span style="color:#00e676">●</span> INCOME SOURCES</div>',unsafe_allow_html=True)
    changed=False
    for i,item in enumerate(cur_income()):
        c1,c2,c3=st.columns([3,2,1])
        with c1:
            st.markdown(f'<div style="display:flex;align-items:center;gap:10px;padding:8px 0"><div style="width:36px;height:36px;border-radius:8px;background:rgba(0,230,118,.1);border:1px solid rgba(0,230,118,.2);display:flex;align-items:center;justify-content:center;font-size:18px">💰</div><div><div style="font-weight:600;font-size:14px">{item["name"]}</div><div style="font-size:11px;color:rgba(255,255,255,.35)">Income source</div></div></div>',unsafe_allow_html=True)
        with c2:
            nv=st.number_input("amt",value=int(item["amt"]),min_value=0,step=1000,key=f"inc_{item['id']}",label_visibility="collapsed")
            if nv!=item["amt"]: cur_income()[i]["amt"]=nv; changed=True
        with c3:
            if st.button("🗑",key=f"di_{item['id']}"): cur_income().pop(i); save(); st.rerun()
    if changed: save()
    # custom toggle — no st.expander to avoid arrow_right bug
    if "show_add_inc" not in st.session_state: st.session_state.show_add_inc = False
    if st.button("➕  Add income source", key="toggle_add_inc", use_container_width=True):
        st.session_state.show_add_inc = not st.session_state.show_add_inc; st.rerun()
    if st.session_state.show_add_inc:
        st.markdown('<div style="background:rgba(255,255,255,.02);border:1px solid rgba(255,45,120,.15);border-radius:10px;padding:14px 16px;margin-top:4px">', unsafe_allow_html=True)
        ai1,ai2=st.columns([3,2])
        with ai1: ni_n=st.text_input("Name",key="ni_n",placeholder="Bonus, Rental...")
        with ai2: ni_a=st.number_input("Amount",min_value=0,key="ni_a",value=0,step=1000)
        if st.button("Add Source",key="add_inc"):
            if ni_n: cur_income().append({"id":get_id(),"name":ni_n,"amt":ni_a}); save(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    c=calcs()
    st.markdown('<div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.4);margin:0 0 12px"><span style="color:#ff2d78">●</span> MONTHLY TALLY</div>',unsafe_allow_html=True)
    m1,m2,m3,m4=st.columns(4)
    with m1: st.metric("💰 Income",fmt(c["inc"]))
    with m2: st.metric("💙 Savings",fmt(c["sav"]))
    with m3: st.metric("🔴 Expenses",fmt(c["exp"]))
    with m4:
        st.metric("Balance",fmt(c["balance"]),
                  delta="✅ Surplus" if c["balance"]>=0 else "⚠️ Shortfall",
                  delta_color="normal" if c["balance"]>=0 else "inverse")

    st.divider()
    st.markdown('<div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.4);margin:0 0 12px"><span style="color:#ffab00">●</span> PAYMENT STATUS</div>',unsafe_allow_html=True)
    p1,p2,p3=st.columns(3)
    with p1: st.metric("✅ Paid",fmt(c["paid"]))
    with p2: st.metric("⏳ Pending",fmt(c["pend"]))
    with p3: st.metric("⚠️ Overdue",fmt(c["over"]))

    all_d=cur_dues()
    dc=sum(1 for d in all_d if d["status"]=="done"); tc=len(all_d)
    pct=dc/tc if tc else 0
    cc="#00e676" if pct==1 else "#ffab00" if pct>=.5 else "#ff2d78"
    st.markdown(f'<div style="margin:16px 0 6px;font-size:13px;color:rgba(255,255,255,.6)">Payment progress &nbsp;<b style="color:white">{int(pct*100)}%</b> &nbsp;—&nbsp; {dc}/{tc} items paid</div><div style="height:10px;border-radius:99px;background:rgba(255,255,255,.06);overflow:hidden;margin-bottom:16px"><div style="height:100%;width:{int(pct*100)}%;border-radius:99px;background:linear-gradient(90deg,{cc},{cc}aa)"></div></div>',unsafe_allow_html=True)

    if c["inc"]>0:
        st.divider()
        st.markdown('<div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.4);margin:0 0 14px">📊 INCOME ALLOCATION</div>',unsafe_allow_html=True)
        sp=min(100,int(c["sav"]/c["inc"]*100)); ep=min(100,int(c["exp"]/c["inc"]*100)); bp=max(0,100-sp-ep)
        st.markdown(f'''
        <div style="margin-bottom:12px"><div style="display:flex;justify-content:space-between;font-size:12px;color:rgba(255,255,255,.6);margin-bottom:5px"><span>💙 Savings · {fmt(c["sav"])}</span><span>{sp}%</span></div><div style="height:8px;border-radius:99px;background:rgba(255,255,255,.06);overflow:hidden"><div style="height:100%;width:{sp}%;background:linear-gradient(90deg,#2979ff,#64b5f6);border-radius:99px"></div></div></div>
        <div style="margin-bottom:12px"><div style="display:flex;justify-content:space-between;font-size:12px;color:rgba(255,255,255,.6);margin-bottom:5px"><span>🔴 Expenses · {fmt(c["exp"])}</span><span>{ep}%</span></div><div style="height:8px;border-radius:99px;background:rgba(255,255,255,.06);overflow:hidden"><div style="height:100%;width:{ep}%;background:linear-gradient(90deg,#ff2d78,#ff85b3);border-radius:99px"></div></div></div>
        <div style="margin-bottom:12px"><div style="display:flex;justify-content:space-between;font-size:12px;color:rgba(255,255,255,.6);margin-bottom:5px"><span>🟢 Balance · {fmt(max(0,c["balance"]))}</span><span>{bp}%</span></div><div style="height:8px;border-radius:99px;background:rgba(255,255,255,.06);overflow:hidden"><div style="height:100%;width:{bp}%;background:linear-gradient(90deg,#00e676,#69f0ae);border-radius:99px"></div></div></div>
        ''',unsafe_allow_html=True)

    st.divider()
    if st.button("✅  Mark All as Paid",use_container_width=True):
        for d in cur_dues(): d["status"]="done"
        save(); st.rerun()

# ════════════════════════════════════════════════════════════════════════
# DUES
# ════════════════════════════════════════════════════════════════════════
with tab2:
    all_d=cur_dues()
    CYCLE={"pending":"done","done":"overdue","overdue":"pending"}
    BTN={"pending":"✓ Mark Paid","done":"⚠ Overdue","overdue":"↺ Pending"}

    f1,f2=st.columns(2)
    with f1: ftype=st.selectbox("Type",["All","Savings","Expenses"],key="ftype")
    with f2: fstatus=st.selectbox("Status",["All","Pending","Done","Overdue"],key="fstatus")

    for sec_type,sec_label,sec_col in [("savings","💙 Savings & Investments","#2979ff"),("expense","🔴 Expenses","#ff2d78")]:
        if ftype=="Savings"  and sec_type!="savings": continue
        if ftype=="Expenses" and sec_type!="expense": continue
        sec_g=[g["name"] for g in GROUPS if g["type"]==sec_type]
        sec_dues=[d for d in all_d if d["group"] in sec_g]
        sec_tot=sum(d["amt"] for d in sec_dues)
        filtered=sec_dues if fstatus=="All" else [d for d in sec_dues if d["status"]==fstatus.lower()]
        if not filtered: continue

        st.markdown(f'<div style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:{sec_col};margin:20px 0 4px;display:flex;align-items:center;justify-content:space-between"><span>{sec_label}</span><span style="font-family:JetBrains Mono,monospace;font-size:15px">{fmt(sec_tot)}</span></div><div style="height:1px;background:linear-gradient(90deg,{sec_col}55,transparent);margin-bottom:14px"></div>',unsafe_allow_html=True)

        for g in GROUPS:
            if g["type"]!=sec_type: continue
            gd=[d for d in filtered if d["group"]==g["name"]]
            if not gd: continue
            g_tot=sum(d["amt"] for d in gd)
            aig=[d for d in all_d if d["group"]==g["name"]]
            done_g=sum(1 for d in aig if d["status"]=="done")
            pct_g=done_g/len(aig) if aig else 0


            # ── Custom collapsible group header (no st.expander to avoid arrow_down bug) ──
            ck = f"grp_{g['name']}"
            if ck not in st.session_state: st.session_state[ck] = True
            is_open = st.session_state[ck]
            col_g = "#00e676" if pct_g==1 else g["color"]
            badge_txt = "all paid" if pct_g==1 else f"{done_g}/{len(aig)} paid"
            arrow = "▼" if is_open else "▶"

            gh1, gh2 = st.columns([5,1])
            with gh1:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);
                border-radius:12px 12px {'0 0' if is_open else '12px 12px'};padding:12px 16px;margin-top:4px">
                  <div style="display:flex;align-items:center;justify-content:space-between">
                    <div style="display:flex;align-items:center;gap:10px">
                      <div style="width:10px;height:10px;border-radius:3px;background:{g['color']}"></div>
                      <span style="font-weight:700;font-size:15px;color:white">{g['name']}</span>
                      <span style="font-size:10px;padding:2px 8px;border-radius:99px;
                      background:{col_g}22;color:{col_g};font-weight:700">{badge_txt}</span>
                    </div>
                    <span style="font-family:'JetBrains Mono',monospace;font-weight:700;font-size:15px;color:white">{fmt(g_tot)}</span>
                  </div>
                  <div style="height:4px;border-radius:99px;background:rgba(255,255,255,.06);overflow:hidden;margin-top:10px">
                    <div style="height:100%;width:{int(pct_g*100)}%;background:{col_g};border-radius:99px"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with gh2:
                st.write("")
                if st.button(arrow, key=f"tog_{g['name']}_{sec_type}", use_container_width=True):
                    st.session_state[ck] = not is_open; st.rerun()

            if is_open:
                st.markdown(f'''<div style="background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.06);
                border-top:none;border-radius:0 0 12px 12px;padding:10px 14px 14px;margin-bottom:8px">''',unsafe_allow_html=True)
                changed=False
                for due in gd:
                    ri=next(i for i,d in enumerate(all_d) if d["id"]==due["id"])
                    r1,r2,r3,r4=st.columns([3,2,2,1])
                    with r1:
                        note_h=f'<div style="font-size:11px;color:rgba(255,255,255,.35);margin-top:1px">{due["note"]}</div>' if due["note"] else ""
                        fade="opacity:.5;" if due["status"]=="done" else ""
                        st.markdown(f'<div style="display:flex;align-items:center;gap:10px;padding:6px 0;{fade}">{logo_img(due["name"],34)}<div><div style="font-weight:600;font-size:14px">{due["name"]}</div>{note_h}</div></div>',unsafe_allow_html=True)
                    with r2:
                        na=st.number_input("₹",value=int(due["amt"]),min_value=0,step=100,key=f"da_{due['id']}",label_visibility="collapsed")
                        if na!=due["amt"]: cur_dues()[ri]["amt"]=na; changed=True
                    with r3:
                        if st.button(BTN[due["status"]],key=f"ds_{due['id']}",use_container_width=True):
                            cur_dues()[ri]["status"]=CYCLE[due["status"]]; save(); st.rerun()
                    with r4:
                        if st.button("🗑",key=f"dd_{due['id']}"): cur_dues().pop(ri); save(); st.rerun()
                st.markdown('</div>',unsafe_allow_html=True)
                if changed: save()
            else:
                st.markdown("<div style='margin-bottom:8px'></div>",unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:8px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
# ADD ITEM
# ════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.4);margin:0 0 16px">➕ ADD NEW DUE ITEM</div>',unsafe_allow_html=True)
    a1,a2=st.columns(2)
    with a1:
        an=st.text_input("Name",placeholder="e.g. KSFE 4, New Loan, Car EMI")
        ag=st.selectbox("Group",GROUP_NAMES)
        ar=st.checkbox("Monthly recurring",value=True)
    with a2:
        aa=st.number_input("Amount (₹)",min_value=0,value=0,step=100)
        ant=st.text_input("Note (optional)",placeholder="e.g. 5750+1000")
        as_=st.selectbox("Initial status",["pending","done","overdue"])
    gtype=GMAP[ag]["type"]; gcol="#2979ff" if gtype=="savings" else "#ff2d78"
    st.markdown(f'<div style="background:{gcol}0d;border:1px solid {gcol}33;border-radius:10px;padding:10px 16px;margin:8px 0;font-size:13px;display:flex;align-items:center;gap:8px"><span style="width:8px;height:8px;border-radius:50%;background:{gcol};display:inline-block"></span>Categorised as &nbsp;<b style="color:{gcol}">{"SAVINGS" if gtype=="savings" else "EXPENSE"}</b> &nbsp;under <b>{ag}</b></div>',unsafe_allow_html=True)
    if st.button("✅  Add Item",use_container_width=True,type="primary"):
        if an:
            cur_dues().append({"id":get_id(),"name":an,"amt":aa,"group":ag,"note":ant,"recur":ar,"status":as_})
            save(); st.success(f"✅ '{an}' added to {ag}!"); st.rerun()
        else: st.error("Please enter a name.")

    st.divider()
    st.markdown('<div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.4);margin:0 0 12px">🔁 RECURRING ITEMS</div>',unsafe_allow_html=True)
    rec=[d for d in cur_dues() if d["recur"]]
    if rec:
        for d in rec:
            gtype2=GMAP[d["group"]]["type"]; gcol2="#2979ff" if gtype2=="savings" else "#ff2d78"
            st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;border-radius:10px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);margin-bottom:6px"><div style="display:flex;align-items:center;gap:10px">{logo_img(d["name"],28)}<div><span style="font-weight:600;font-size:13px">{d["name"]}</span><span style="font-size:11px;color:rgba(255,255,255,.35);margin-left:8px">{d["group"]}</span></div></div><div style="display:flex;align-items:center;gap:10px"><span style="font-size:10px;padding:2px 8px;border-radius:99px;background:{gcol2}1a;color:{gcol2};font-weight:700">{"SAVINGS" if gtype2=="savings" else "EXPENSE"}</span><span style="font-family:JetBrains Mono,monospace;font-weight:600;font-size:13px">{fmt(d["amt"])}</span></div></div>',unsafe_allow_html=True)
    else:
        st.info("No recurring items yet.")

# ════════════════════════════════════════════════════════════════════════
# ANALYSIS
# ════════════════════════════════════════════════════════════════════════
with tab4:
    c=calcs(); all_d=cur_dues()
    col_d,col_t=st.columns([1,1])
    with col_d:
        fig=go.Figure(data=[go.Pie(
            labels=["Savings","Expenses","Balance"],
            values=[c["sav"],c["exp"],max(0,c["balance"])],
            hole=0.68,
            marker=dict(colors=["#2979ff","#ff2d78","#00e676"],line=dict(color="#080810",width=3)),
            textinfo="label+percent",textfont=dict(family="Outfit",size=12,color="white"),
            hovertemplate="%{label}: ₹%{value:,}<extra></extra>"
        )])
        fig.update_layout(title=dict(text="Income Split",font=dict(family="Outfit",size=14,color="rgba(255,255,255,.5)")),
            showlegend=False,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",height=300,margin=dict(t=40,b=0,l=0,r=0))
        st.plotly_chart(fig,use_container_width=True)
    with col_t:
        st.markdown('<div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.4);margin-bottom:16px">MONTHLY TALLY</div>',unsafe_allow_html=True)
        for icon,label,val,col in [("💰","Income",fmt(c["inc"]),"#00e676"),("💙","Savings",fmt(c["sav"]),"#2979ff"),("🔴","Expenses",fmt(c["exp"]),"#ff2d78"),("⚖️","Balance",fmt(c["balance"]),"#00e676" if c["balance"]>=0 else "#ff1744"),("✅","Paid",fmt(c["paid"]),"#00e676"),("⏳","Pending",fmt(c["pend"]),"#ffab00")]:
            st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.05)"><span style="font-size:13px;color:rgba(255,255,255,.6)">{icon} {label}</span><span style="font-family:JetBrains Mono,monospace;font-weight:700;font-size:14px;color:{col}">{val}</span></div>',unsafe_allow_html=True)

    st.divider()
    g_data=[]
    for g in GROUPS:
        items=[d for d in all_d if d["group"]==g["name"]]
        if not items: continue
        g_data.append({"Group":g["name"],"Paid":sum(d["amt"] for d in items if d["status"]=="done"),"Pending":sum(d["amt"] for d in items if d["status"]=="pending"),"Overdue":sum(d["amt"] for d in items if d["status"]=="overdue")})
    if g_data:
        df_g=pd.DataFrame(g_data)
        fig2=go.Figure()
        for lbl,col in [("Paid","#00e676"),("Pending","#ffab00"),("Overdue","#ff1744")]:
            fig2.add_trace(go.Bar(name=lbl,x=df_g["Group"],y=df_g[lbl],marker=dict(color=col,line=dict(width=0)),opacity=0.9))
        fig2.update_layout(barmode="stack",title=dict(text="Payment by Group",font=dict(family="Outfit",size=14,color="rgba(255,255,255,.5)")),
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Outfit",color="rgba(255,255,255,.7)"),height=360,
            xaxis=dict(gridcolor="rgba(255,255,255,.04)",tickfont=dict(size=11)),
            yaxis=dict(gridcolor="rgba(255,255,255,.04)",tickprefix="₹",tickfont=dict(size=11)),
            legend=dict(orientation="h",yanchor="bottom",y=1.02,font=dict(size=11),bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=60,b=0),bargap=0.3)
        st.plotly_chart(fig2,use_container_width=True)

    st.markdown('<div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.4);margin:16px 0 14px">PAYMENT PROGRESS BY GROUP</div>',unsafe_allow_html=True)
    for g in GROUPS:
        items=[d for d in all_d if d["group"]==g["name"]]
        if not items: continue
        n=len(items); done=sum(1 for d in items if d["status"]=="done"); tot=sum(d["amt"] for d in items)
        pct=done/n if n else 0; col="#00e676" if pct==1 else g["color"]
        gtype=GMAP[g["name"]]["type"]; badge_col="#2979ff" if gtype=="savings" else "#ff2d78"; badge_bg=f"{'rgba(41,121,255,.12)' if gtype=='savings' else 'rgba(255,45,120,.12)'}"
        st.markdown(f'<div style="margin-bottom:14px"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px"><div style="display:flex;align-items:center;gap:8px"><div style="width:8px;height:8px;border-radius:2px;background:{g["color"]}"></div><span style="font-weight:600;font-size:13px">{g["name"]}</span><span style="font-size:10px;padding:2px 7px;border-radius:99px;background:{badge_bg};color:{badge_col};font-weight:700">{"SAVINGS" if gtype=="savings" else "EXPENSE"}</span></div><span style="font-size:12px;color:rgba(255,255,255,.5)">{done}/{n} · <span style="font-family:JetBrains Mono,monospace">{fmt(tot)}</span></span></div><div style="height:7px;border-radius:99px;background:rgba(255,255,255,.06);overflow:hidden"><div style="height:100%;width:{int(pct*100)}%;background:linear-gradient(90deg,{col},{col}aa);border-radius:99px"></div></div></div>',unsafe_allow_html=True)

    st.divider()
    st.markdown('<div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.4);margin:0 0 14px">💡 SMART INSIGHTS</div>',unsafe_allow_html=True)
    done_c=sum(1 for d in all_d if d["status"]=="done"); total_c=len(all_d)
    pct_d=int(done_c/total_c*100) if total_c else 0
    if pct_d==100:   st.success("🎉 All dues cleared! Excellent financial discipline this month.")
    elif pct_d>=50:  st.warning(f"⏳ {pct_d}% paid ({done_c}/{total_c} items). Keep going!")
    else:            st.error(f"🔴 Only {pct_d}% paid. {total_c-done_c} items still pending.")
    if c["inc"]>0:
        sp=int(c["sav"]/c["inc"]*100); ep=int(c["exp"]/c["inc"]*100)
        st.info(f"💙 {sp}% of income → savings ({fmt(c['sav'])})")
        st.info(f"🔴 {ep}% of income → expenses ({fmt(c['exp'])})")
        if c["balance"]>=0: st.success(f"✅ {fmt(c['balance'])} remaining after all dues!")
        else:                st.error(f"⚠️ Shortfall of {fmt(abs(c['balance']))}!")
    else: st.warning("💰 Enter your income in Overview tab to see tally.")
    overdue=[d for d in all_d if d["status"]=="overdue"]
    if overdue: st.error(f"⚠️ Overdue: {', '.join(d['name'] for d in overdue)} — Pay immediately!")
    zero_amt=[d for d in all_d if d["amt"]==0 and d["status"]!="done"]
    if zero_amt: st.warning(f"📝 No amount: {', '.join(d['name'] for d in zero_amt)} — update when bill arrives.")
    top_p=sorted([d for d in all_d if d["status"]!="done"],key=lambda x:-x["amt"])
    if top_p: st.info(f"💜 Largest pending: **{top_p[0]['name']}** — {fmt(top_p[0]['amt'])}")

    st.divider()
    st.markdown('<div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(255,255,255,.4);margin:0 0 14px">💾 BACKUP & RESTORE</div>',unsafe_allow_html=True)
    bc1,bc2=st.columns(2)
    with bc1:
        st.download_button(label="⬇️  Download Backup",data=json.dumps(D(),indent=2),
            file_name=f"finances_{datetime.now().strftime('%Y%m%d')}.json",mime="application/json",use_container_width=True)
    with bc2:
        up=st.file_uploader("⬆️ Restore from backup",type="json",key="restore")
        if up:
            try:
                restored=json.loads(up.read())
                if "months" in restored and "cur_month" in restored:
                    st.session_state.data=restored; save_data(restored); st.success("✅ Restored!"); st.rerun()
                else: st.error("Invalid backup file.")
            except Exception as e: st.error(f"Error: {e}")


# ════════════════════════════════════════════════════════════════════════
# REPORTS — Consolidated date range view
# ════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('''<div style="font-size:12px;font-weight:700;text-transform:uppercase;
    letter-spacing:.12em;color:rgba(255,255,255,.4);margin:0 0 16px">
    <span style="color:#ff2d78">●</span> CONSOLIDATED REPORT</div>''', unsafe_allow_html=True)

    all_months = list(D()["months"].keys())

    if len(all_months) < 1:
        st.info("No data yet. Add some months first.")
    else:
        # ── FILTERS ──
        f1, f2, f3 = st.columns(3)
        with f1:
            from_month = st.selectbox("From Month", all_months,
                                       index=len(all_months)-1, key="rep_from")
        with f2:
            to_month   = st.selectbox("To Month",   all_months,
                                       index=0, key="rep_to")
        with f3:
            # Build filter options: All Groups + All Items + individual items
            all_item_names = []
            for m in all_months:
                for d in D()["months"][m]["dues"]:
                    if d["name"] not in all_item_names:
                        all_item_names.append(d["name"])

            filter_options = (
                ["📊 All Items", "── By Group ──"] +
                GROUP_NAMES +
                ["── By Item ──"] +
                sorted(all_item_names)
            )
            selected_filter = st.selectbox("Filter by Group / Item", filter_options, key="rep_filter")

        # ── BUILD MONTH RANGE ──
        # Months stored newest first — reverse to get chronological
        ordered = list(reversed(all_months))
        try:
            fi = ordered.index(from_month)
            ti = ordered.index(to_month)
            if fi > ti: fi, ti = ti, fi   # swap if reversed
            selected_months = ordered[fi:ti+1]
        except ValueError:
            selected_months = all_months

        if not selected_months:
            st.warning("No months in selected range.")
        else:
            # ── COLLECT DATA ──
            rows = []
            for m in selected_months:
                mdata = D()["months"].get(m, {})
                dues  = mdata.get("dues", [])
                inc   = sum(i["amt"] for i in mdata.get("income", []))
                for d in dues:
                    # apply filter
                    if selected_filter == "📊 All Items":
                        pass
                    elif selected_filter in GROUP_NAMES:
                        if d["group"] != selected_filter: continue
                    elif selected_filter.startswith("──"):
                        pass
                    else:
                        if d["name"] != selected_filter: continue
                    rows.append({
                        "month":  m,
                        "name":   d["name"],
                        "group":  d["group"],
                        "type":   GMAP.get(d["group"], {}).get("type","expense"),
                        "amt":    d["amt"],
                        "status": d["status"],
                        "income": inc,
                    })

            if not rows:
                st.info("No data for selected filter and range.")
            else:
                import pandas as pd

                df = pd.DataFrame(rows)

                # ── SUMMARY CARDS ──
                total_amt  = df["amt"].sum()
                paid_amt   = df[df["status"]=="done"]["amt"].sum()
                pend_amt   = df[df["status"]=="pending"]["amt"].sum()
                over_amt   = df[df["status"]=="overdue"]["amt"].sum()
                n_months   = len(selected_months)

                st.markdown(f'''
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:20px">
                  <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,45,120,.15);border-radius:14px;padding:14px 16px">
                    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:rgba(255,255,255,.4);margin-bottom:6px">Total Amount</div>
                    <div style="font-size:22px;font-weight:700;font-family:JetBrains Mono,monospace;color:white">{fmt(total_amt)}</div>
                    <div style="font-size:11px;color:rgba(255,255,255,.35);margin-top:4px">{n_months} month(s)</div>
                  </div>
                  <div style="background:rgba(255,255,255,.03);border:1px solid rgba(0,230,118,.15);border-radius:14px;padding:14px 16px">
                    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:rgba(255,255,255,.4);margin-bottom:6px">Paid</div>
                    <div style="font-size:22px;font-weight:700;font-family:JetBrains Mono,monospace;color:#00e676">{fmt(paid_amt)}</div>
                    <div style="font-size:11px;color:rgba(255,255,255,.35);margin-top:4px">{len(df[df["status"]=="done"])} entries</div>
                  </div>
                  <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,171,0,.15);border-radius:14px;padding:14px 16px">
                    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:rgba(255,255,255,.4);margin-bottom:6px">Pending</div>
                    <div style="font-size:22px;font-weight:700;font-family:JetBrains Mono,monospace;color:#ffab00">{fmt(pend_amt)}</div>
                    <div style="font-size:11px;color:rgba(255,255,255,.35);margin-top:4px">{len(df[df["status"]=="pending"])} entries</div>
                  </div>
                  <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,23,68,.15);border-radius:14px;padding:14px 16px">
                    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:rgba(255,255,255,.4);margin-bottom:6px">Monthly Avg</div>
                    <div style="font-size:22px;font-weight:700;font-family:JetBrains Mono,monospace;color:#ff2d78">{fmt(total_amt/n_months if n_months else 0)}</div>
                    <div style="font-size:11px;color:rgba(255,255,255,.35);margin-top:4px">per month</div>
                  </div>
                </div>
                ''', unsafe_allow_html=True)

                st.divider()

                # ── MONTH-WISE VERTICAL TABLE ──
                st.markdown('''<div style="font-size:12px;font-weight:700;text-transform:uppercase;
                letter-spacing:.12em;color:rgba(255,255,255,.4);margin:0 0 12px">
                MONTH-WISE BREAKDOWN</div>''', unsafe_allow_html=True)

                for m in selected_months:
                    m_rows = [r for r in rows if r["month"]==m]
                    if not m_rows: continue
                    m_total = sum(r["amt"] for r in m_rows)
                    m_paid  = sum(r["amt"] for r in m_rows if r["status"]=="done")
                    m_pend  = sum(r["amt"] for r in m_rows if r["status"]=="pending")
                    m_over  = sum(r["amt"] for r in m_rows if r["status"]=="overdue")
                    m_pct   = int(m_paid/m_total*100) if m_total else 0
                    bar_col = "#00e676" if m_pct==100 else "#ffab00" if m_pct>=50 else "#ff2d78"

                    # Month header
                    st.markdown(f'''
                    <div style="background:linear-gradient(135deg,rgba(255,45,120,.08),rgba(160,32,240,.05));
                    border:1px solid rgba(255,45,120,.2);border-radius:12px;padding:12px 16px;margin-bottom:2px">
                      <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                          <span style="font-size:15px;font-weight:700;color:white">{m}</span>
                          <span style="font-size:11px;color:rgba(255,255,255,.4);margin-left:10px">{len(m_rows)} item(s)</span>
                        </div>
                        <div style="display:flex;gap:16px;align-items:center">
                          <span style="font-size:11px;color:#00e676">✓ {fmt(m_paid)}</span>
                          <span style="font-size:11px;color:#ffab00">⏳ {fmt(m_pend)}</span>
                          {"<span style=\'font-size:11px;color:#ff1744\'>⚠ " + fmt(m_over) + "</span>" if m_over>0 else ""}
                          <span style="font-family:JetBrains Mono,monospace;font-weight:700;font-size:16px;color:white">{fmt(m_total)}</span>
                        </div>
                      </div>
                      <div style="height:4px;border-radius:99px;background:rgba(255,255,255,.06);overflow:hidden;margin-top:8px">
                        <div style="height:100%;width:{m_pct}%;background:{bar_col};border-radius:99px"></div>
                      </div>
                    </div>
                    ''', unsafe_allow_html=True)

                    # Item rows for this month
                    with st.container():
                        st.markdown('<div style="background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.05);border-top:none;border-radius:0 0 12px 12px;padding:6px 14px 10px;margin-bottom:12px">', unsafe_allow_html=True)
                        for r in m_rows:
                            s_col = "#00e676" if r["status"]=="done" else "#ff1744" if r["status"]=="overdue" else "#ffab00"
                            s_lbl = "✓ Paid" if r["status"]=="done" else "⚠ Overdue" if r["status"]=="overdue" else "⏳ Pending"
                            gtype = r["type"]
                            g_col = "#2979ff" if gtype=="savings" else "#ff2d78"
                            fade  = "opacity:.5;" if r["status"]=="done" else ""
                            st.markdown(f'''
                            <div style="display:flex;align-items:center;justify-content:space-between;
                            padding:8px 0;border-bottom:1px solid rgba(255,255,255,.04);{fade}">
                              <div style="display:flex;align-items:center;gap:10px;min-width:0">
                                {logo_img(r["name"],28)}
                                <div>
                                  <div style="font-weight:600;font-size:13px">{r["name"]}</div>
                                  <div style="font-size:10px;color:rgba(255,255,255,.35)">{r["group"]}
                                    <span style="margin-left:4px;padding:1px 5px;border-radius:4px;
                                    background:{g_col}1a;color:{g_col};font-weight:700">
                                    {"SAV" if gtype=="savings" else "EXP"}</span>
                                  </div>
                                </div>
                              </div>
                              <div style="display:flex;align-items:center;gap:14px;flex-shrink:0">
                                <span style="font-size:11px;color:{s_col};font-weight:600">{s_lbl}</span>
                                <span style="font-family:JetBrains Mono,monospace;font-weight:700;font-size:14px">{fmt(r["amt"])}</span>
                              </div>
                            </div>
                            ''', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                st.divider()

                # ── TREND CHART ──
                if len(selected_months) > 1:
                    st.markdown('''<div style="font-size:12px;font-weight:700;text-transform:uppercase;
                    letter-spacing:.12em;color:rgba(255,255,255,.4);margin:0 0 12px">
                    MONTHLY TREND</div>''', unsafe_allow_html=True)

                    trend_data = []
                    for m in selected_months:
                        m_rows2 = [r for r in rows if r["month"]==m]
                        trend_data.append({
                            "Month":   m,
                            "Total":   sum(r["amt"] for r in m_rows2),
                            "Paid":    sum(r["amt"] for r in m_rows2 if r["status"]=="done"),
                            "Pending": sum(r["amt"] for r in m_rows2 if r["status"]=="pending"),
                        })
                    df_trend = pd.DataFrame(trend_data)

                    fig_t = go.Figure()
                    fig_t.add_trace(go.Bar(name="Paid",    x=df_trend["Month"], y=df_trend["Paid"],    marker_color="#00e676", opacity=0.9))
                    fig_t.add_trace(go.Bar(name="Pending", x=df_trend["Month"], y=df_trend["Pending"], marker_color="#ffab00", opacity=0.9))
                    fig_t.add_trace(go.Scatter(name="Total", x=df_trend["Month"], y=df_trend["Total"],
                                               mode="lines+markers",
                                               line=dict(color="#ff2d78", width=2, dash="dot"),
                                               marker=dict(size=7, color="#ff2d78")))
                    fig_t.update_layout(
                        barmode="stack",
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Outfit", color="rgba(255,255,255,.7)"),
                        height=320,
                        xaxis=dict(gridcolor="rgba(255,255,255,.04)", tickfont=dict(size=11)),
                        yaxis=dict(gridcolor="rgba(255,255,255,.04)", tickprefix="₹", tickfont=dict(size=11)),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                   font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
                        margin=dict(t=30,b=0), bargap=0.3
                    )
                    st.plotly_chart(fig_t, use_container_width=True)

                st.divider()

                # ── ITEM-WISE SUMMARY ──
                st.markdown('''<div style="font-size:12px;font-weight:700;text-transform:uppercase;
                letter-spacing:.12em;color:rgba(255,255,255,.4);margin:0 0 12px">
                ITEM-WISE TOTAL ACROSS SELECTED MONTHS</div>''', unsafe_allow_html=True)

                item_summary = {}
                for r in rows:
                    k = r["name"]
                    if k not in item_summary:
                        item_summary[k] = {"group":r["group"],"type":r["type"],"total":0,"paid":0,"count":0}
                    item_summary[k]["total"] += r["amt"]
                    item_summary[k]["paid"]  += r["amt"] if r["status"]=="done" else 0
                    item_summary[k]["count"] += 1

                sorted_items = sorted(item_summary.items(), key=lambda x: -x[1]["total"])
                grand_total  = sum(v["total"] for v in item_summary.values())

                for name, info in sorted_items:
                    pct_i  = int(info["paid"]/info["total"]*100) if info["total"] else 0
                    bar_c  = "#00e676" if pct_i==100 else "#ffab00" if pct_i>=50 else "#ff2d78"
                    width_pct = int(info["total"]/grand_total*100) if grand_total else 0
                    gtype  = info["type"]; g_col = "#2979ff" if gtype=="savings" else "#ff2d78"
                    st.markdown(f'''
                    <div style="margin-bottom:10px">
                      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:5px">
                        <div style="display:flex;align-items:center;gap:8px">
                          {logo_img(name, 26)}
                          <span style="font-weight:600;font-size:13px">{name}</span>
                          <span style="font-size:10px;color:rgba(255,255,255,.35)">{info["group"]}</span>
                          <span style="font-size:10px;padding:1px 6px;border-radius:4px;
                          background:{g_col}1a;color:{g_col};font-weight:700">
                          {"SAV" if gtype=="savings" else "EXP"}</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px">
                          <span style="font-size:11px;color:rgba(255,255,255,.4)">{info["count"]} month(s)</span>
                          <span style="font-family:JetBrains Mono,monospace;font-weight:700;font-size:14px">{fmt(info["total"])}</span>
                        </div>
                      </div>
                      <div style="height:6px;border-radius:99px;background:rgba(255,255,255,.06);overflow:hidden">
                        <div style="height:100%;width:{width_pct}%;background:linear-gradient(90deg,{bar_c},{bar_c}88);border-radius:99px"></div>
                      </div>
                    </div>
                    ''', unsafe_allow_html=True)

                st.divider()
                st.markdown(f'''
                <div style="display:flex;justify-content:space-between;align-items:center;
                padding:14px 18px;background:rgba(255,45,120,.06);border:1px solid rgba(255,45,120,.2);
                border-radius:12px">
                  <span style="font-weight:700;font-size:15px">Grand Total · {from_month} → {to_month}</span>
                  <span style="font-family:JetBrains Mono,monospace;font-weight:800;font-size:22px;
                  color:#ff2d78">{fmt(grand_total)}</span>
                </div>
                ''', unsafe_allow_html=True)
