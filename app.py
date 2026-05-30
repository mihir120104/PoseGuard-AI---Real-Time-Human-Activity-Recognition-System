# """
# app.py  —  HAR AI Platform  (Production)
# Run: streamlit run app.py
# """
# import streamlit as st
# import numpy as np
# import matplotlib
# matplotlib.use("Agg")
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
# import seaborn as sns
# import pandas as pd
# import subprocess, sys, os, sqlite3
# from datetime import datetime, timedelta
# from auth        import login, register, init_db, list_users, delete_user, change_password
# from history_db  import get_history, init_history_db, delete_record, update_record, clear_all
# from report_generator import generate_pdf_report

# init_db(); init_history_db()

# st.set_page_config(page_title="HAR AI Platform", page_icon="🎯",
#                    layout="wide", initial_sidebar_state="expanded")

# # ═══════════════════════════════════════
# # GLOBAL CSS
# # ═══════════════════════════════════════
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');
# *{box-sizing:border-box;}
# html,body,[class*="css"]{font-family:'Inter',sans-serif !important; color-scheme: dark;}
# .main,.block-container{background:#070A0F !important; padding:0 1.5rem 2rem !important; max-width:100% !important;}
# section[data-testid="stSidebar"]{background:#040608 !important; border-right:1px solid #0F1923;}
# section[data-testid="stSidebar"] > div{padding:0 !important;}
# /* Hide default streamlit chrome */
# #MainMenu,footer,header{visibility:hidden;}
# /* Inputs */
# .stTextInput input,.stNumberInput input,.stSelectbox select{
#   background:#0D1520 !important; border:1px solid #1A2535 !important;
#   color:#C8D4E3 !important; border-radius:8px !important;}
# .stTextInput input:focus{border-color:#14B8A6 !important; box-shadow:0 0 0 3px rgba(20,184,166,.15) !important;}
# /* Buttons */
# .stButton>button{
#   background:#0D1520 !important; border:1px solid #1A2535 !important;
#   color:#8A9BB5 !important; border-radius:8px !important; font-size:13px !important;
#   font-family:'Inter',sans-serif !important; transition:all .15s !important; padding:8px 16px !important;}
# .stButton>button:hover{background:#1A2535 !important; color:#C8D4E3 !important; border-color:#2A3F5A !important;}
# .stButton>button[kind="primary"]{background:#0F3D30 !important; border-color:#14B8A6 !important; color:#14B8A6 !important;}
# .stButton>button[kind="primary"]:hover{background:#145C46 !important;}
# /* Tabs */
# .stTabs [data-baseweb="tab-list"]{background:#0D1520; border-radius:10px; padding:4px; gap:2px;}
# .stTabs [data-baseweb="tab"]{border-radius:7px !important; color:#4A5C74 !important; font-size:13px !important; padding:8px 16px !important;}
# .stTabs [aria-selected="true"]{background:#1A2535 !important; color:#C8D4E3 !important;}
# /* Dataframe */
# [data-testid="stDataFrame"]{border-radius:10px; overflow:hidden;}
# /* Slider */
# .stSlider [data-baseweb="slider"]{padding:0 !important;}
# /* Expander */
# .streamlit-expanderHeader{background:#0D1520 !important; border-radius:8px !important; color:#8A9BB5 !important;}
# /* Cards */
# .kpi{background:#0D1520;border:1px solid #1A2535;border-radius:12px;padding:18px 20px;position:relative;overflow:hidden;}
# .kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--a,#14B8A6);}
# .kpi-l{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:#2D3E55;margin-bottom:8px;}
# .kpi-v{font-family:'Syne',sans-serif;font-size:26px;font-weight:700;color:var(--a,#14B8A6);line-height:1;margin-bottom:5px;}
# .kpi-s{font-size:10px;color:#2D3E55;}
# .kpi-d{font-size:11px;color:#4A5C74;margin-top:4px;}
# /* Section header */
# .sh{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.2em;text-transform:uppercase;
#     color:#2D3E55;border-bottom:1px solid #0F1923;padding-bottom:8px;margin:24px 0 14px;}
# /* Alerts */
# .alert-r{background:#0E0507;border:1px solid #4A1020;border-left:3px solid #EF4444;border-radius:8px;padding:14px 18px;margin:10px 0;}
# .alert-w{background:#0D0A04;border:1px solid #4A3800;border-left:3px solid #F59E0B;border-radius:8px;padding:12px 16px;margin:8px 0;}
# .alert-g{background:#040E09;border:1px solid #0A4A25;border-left:3px solid #22C55E;border-radius:8px;padding:12px 16px;margin:8px 0;}
# @keyframes si{0%,100%{opacity:1}50%{opacity:.6}}
# .si{animation:si .6s ease-in-out infinite;}
# /* Live badge */
# @keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,.4)}50%{box-shadow:0 0 0 6px rgba(34,197,94,0)}}
# .live-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#22C55E;animation:pulse 1.5s infinite;margin-right:6px;}
# /* Page header */
# .phead{background:#070A0F;border-bottom:1px solid #0F1923;padding:12px 0 10px;margin-bottom:18px;position:sticky;top:0;z-index:99;}
# .ptitle{font-family:'Syne',sans-serif;font-size:19px;font-weight:800;color:#DDE6F0;letter-spacing:-.3px;}
# .pmeta{font-family:'JetBrains Mono',monospace;font-size:9px;color:#2D3E55;}
# .pbadge{background:#072218;border:1px solid #0A4A2C;color:#22C55E;font-family:'JetBrains Mono',monospace;font-size:9px;padding:3px 10px;border-radius:20px;}
# /* Nav button active state */
# div[data-testid="stVerticalBlock"] .stButton>button.nav-active{background:#0A2040 !important;border-color:#1A5080 !important;color:#60A5FA !important;}
# </style>
# """, unsafe_allow_html=True)

# SIREN = """<script>(function(){try{
#   const c=new(window.AudioContext||window.webkitAudioContext)();
#   [[440,880,'sawtooth'],[220,440,'square']].forEach(([lo,hi,t])=>{
#     const o=c.createOscillator(),g=c.createGain();
#     o.connect(g);g.connect(c.destination);o.type=t;
#     [0,.4,.8,1.2,1.6].forEach((s,i)=>o.frequency.setValueAtTime(i%2?hi:lo,c.currentTime+s));
#     g.gain.setValueAtTime(.25,c.currentTime);
#     g.gain.exponentialRampToValueAtTime(.001,c.currentTime+2);
#     o.start();o.stop(c.currentTime+2);
#   });
# }catch(e){}})();</script>"""

# DN  = {
#     "no":          "No Activity",
#     "no_activity": "No Activity",
#     "No Activity": "No Activity",
#     "no activity": "No Activity",
#     "Drinking":    "Drinking",
#     "drinking":    "Drinking",
#     "eating":      "Eating",
#     "Eating":      "Eating",
#     "exercise":    "Exercise",
#     "Exercise":    "Exercise",
#     "fighting":    "Fighting",
#     "Fighting":    "Fighting",
#     "Typing":      "Typing",
#     "typing":      "Typing",
#     "WritingOnBoard": "Writing on Board",
#     "writingonboard": "Writing on Board",
# }
# RISK= ["fighting","Fighting","Fighting","falling"]

# for k,v in [("logged_in",False),("page","dashboard"),("cam_pid",None),("username",""),("theme","dark")]:
#     if k not in st.session_state: st.session_state[k]=v

# # ═══════════════════════════════════════
# # HELPERS
# # ═══════════════════════════════════════
# # ── Canonical label normalizer — single source of truth ──
# _NORMALIZE = {
#     "no": "No Activity",  "no_activity": "No Activity",
#     "No Activity": "No Activity",  "no activity": "No Activity",
#     "No_Activity": "No Activity",
#     "Drinking": "Drinking",  "drinking": "Drinking",
#     "eating": "Eating",  "Eating": "Eating",
#     "exercise": "Exercise",  "Exercise": "Exercise",
#     "fighting": "Fighting",  "Fighting": "Fighting",
#     "Typing": "Typing",  "typing": "Typing",
#     "WritingOnBoard": "Writing on Board",  "writingonboard": "Writing on Board",
#     "Writing on Board": "Writing on Board",
# }

# def normalize_label(x: str) -> str:
#     return _NORMALIZE.get(x, x)

# def load_df():
#     raw=get_history()
#     if not raw: return pd.DataFrame(columns=["ID","Activity","Confidence","Time"])
#     df=pd.DataFrame(raw,columns=["ID","Activity","Confidence","Time"])
#     df=df[~df["Activity"].isin(["Unknown","No Person","...","Warming up..."])]
#     # Normalize ALL labels to canonical names — eliminates duplicate "No Activity" etc.
#     df["Activity"]=df["Activity"].apply(normalize_label)
#     df["Time"]=pd.to_datetime(df["Time"]); return df.sort_values("Time")

# def dark_fig(figsize=(7,3.5)):
#     fig,ax=plt.subplots(figsize=figsize)
#     fig.patch.set_facecolor("#0D1520"); ax.set_facecolor("#0D1520")
#     return fig,ax

# PAL=["#14B8A6","#22C55E","#60A5FA","#A78BFA","#F59E0B","#F43F5E","#FB923C"]

# def style_ax(ax):
#     ax.tick_params(colors="#2D3E55",labelsize=8)
#     for sp in ax.spines.values(): sp.set_color("#1A2535")
#     ax.set_facecolor("#0D1520")

# def read_metrics():
#     m={}
#     if os.path.exists("metrics.txt"):
#         try:
#             for line in open("metrics.txt"):
#                 k,v=line.strip().split(":")
#                 m[k.strip()]=float(v.strip())
#         except: pass
#     return m

# # ═══════════════════════════════════════
# # LOGIN PAGE
# # ═══════════════════════════════════════
# if not st.session_state.logged_in:
#     _,col,_=st.columns([1,1.2,1])
#     with col:
#         st.markdown("""
#         <div style="text-align:center;padding:50px 0 36px">
#           <div style="width:64px;height:64px;border-radius:16px;background:linear-gradient(135deg,#0F3D30,#0A2840);
#                border:1px solid #1A5040;display:inline-flex;align-items:center;justify-content:center;
#                font-size:28px;margin-bottom:22px;box-shadow:0 8px 32px rgba(20,184,166,.15);">🎯</div>
#           <div style="font-family:'Syne',sans-serif;font-size:30px;font-weight:800;
#                background:linear-gradient(135deg,#E8EDF5,#14B8A6);-webkit-background-clip:text;
#                -webkit-text-fill-color:transparent;letter-spacing:-.5px;margin-bottom:6px;">
#                HAR AI Platform</div>
#           <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#2D3E55;
#                letter-spacing:.15em;margin-bottom:10px;">HUMAN ACTIVITY RECOGNITION</div>
#           <div style="font-size:12px;color:#2D3E55;font-style:italic;margin-bottom:36px;">
#                "Every movement tells a story — we decode it."</div>
#         </div>
#         """, unsafe_allow_html=True)

#         with st.container():
#             # st.markdown('<div style="background:#0D1520;border:1px solid #1A2535;border-radius:16px;padding:32px 28px;">', unsafe_allow_html=True)
#             # st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;letter-spacing:.18em;color:#2D3E55;margin-bottom:20px;">SECURE ACCESS</div>', unsafe_allow_html=True)
#             st.markdown('<div style="font-size:11px;color:#2D3E55;margin-bottom:4px;">Username</div>', unsafe_allow_html=True)
#             uname = st.text_input("Username", placeholder="Enter username", label_visibility="collapsed", key="li_u")
#             st.markdown('<div style="font-size:11px;color:#2D3E55;margin-bottom:16px;">Password</div>', unsafe_allow_html=True)
#             passw = st.text_input("Password", type="password", placeholder="Enter password", label_visibility="collapsed", key="li_p")
#             st.markdown("<br>", unsafe_allow_html=True)
#             if st.button("Login  →", use_container_width=True, type="primary", key="li_btn"):
#                 if login(uname, passw):
#                     st.session_state.logged_in=True; st.session_state.username=uname
#                     st.session_state.page="dashboard"; st.rerun()
#                 else:
#                     st.error("Invalid credentials. Contact your administrator.")
#             st.markdown("</div>", unsafe_allow_html=True)

#         st.markdown("""
#         <div style="text-align:center;margin-top:18px;">
#           <div style="font-size:11px;color:#1A2535;">Access is granted by administrators only</div>
#           <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#161E2A;margin-top:6px;">
#             CNN + BiLSTM + Attention  ·  99.61% F1</div>
#         </div>
#         """, unsafe_allow_html=True)
#     st.stop()

# # ═══════════════════════════════════════
# # SIDEBAR
# # ═══════════════════════════════════════
# with st.sidebar:
#     is_admin = st.session_state.username == "admin"
#     st.markdown(f"""
#     <div style="padding:22px 20px 16px">
#       <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
#         <div style="width:36px;height:36px;border-radius:10px;background:#0A2040;
#              border:1px solid #1A4060;display:flex;align-items:center;justify-content:center;
#              font-size:15px;flex-shrink:0;">{"👑" if is_admin else "👤"}</div>
#         <div>
#           <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:#DDE6F0;">
#             {st.session_state.username}</div>
#           <div style="font-size:10px;color:#2D3E55;">{"Administrator" if is_admin else "Viewer"}</div>
#         </div>
#       </div>
#       {"<div style='display:inline-block;background:#160A30;border:1px solid #3A1A80;color:#A78BFA;font-family:JetBrains Mono,monospace;font-size:9px;padding:2px 8px;border-radius:10px;'>ADMIN</div>" if is_admin else ""}
#     </div>
#     """, unsafe_allow_html=True)

#     st.markdown('<div style="height:1px;background:#0F1923;margin:0 16px 12px;"></div>', unsafe_allow_html=True)

#     nav = [("dashboard","Overview","🏠"),("performance","Model Performance","📊"),
#            ("live","Live Detection","📹"),("history","History & Analytics","📋"),
#            ("admin","Admin Panel","⚙️")]
#     for key,label,icon in nav:
#         active = st.session_state.page == key
#         bg  = "background:#0A1E35;border-color:#1A4060;color:#60A5FA;" if active else ""
#         if st.button(f"{icon}  {label}", use_container_width=True,
#                      type="primary" if active else "secondary", key=f"nav_{key}"):
#             st.session_state.page=key; st.rerun()

#     st.markdown('<div style="height:1px;background:#0F1923;margin:12px 16px;"></div>', unsafe_allow_html=True)

#     m=read_metrics()
#     if m:
#         st.markdown(f"""
#         <div style="padding:0 16px 16px">
#           <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.15em;
#                color:#2D3E55;margin-bottom:10px;">MODEL STATUS</div>
#           <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
#             <span style="font-size:11px;color:#2D3E55;">Accuracy</span>
#             <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#22C55E;">
#               {m.get('Accuracy',0)*100:.1f}%</span>
#           </div>
#           <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
#             <span style="font-size:11px;color:#2D3E55;">F1 Score</span>
#             <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#14B8A6;">
#               {m.get('F1',0)*100:.1f}%</span>
#           </div>
#           <div style="background:#0A1520;border-radius:6px;height:4px;margin-top:8px;overflow:hidden">
#             <div style="background:linear-gradient(90deg,#14B8A6,#22C55E);height:4px;
#                  width:{m.get('F1',0)*100:.0f}%;border-radius:6px;"></div>
#           </div>
#         </div>
#         """, unsafe_allow_html=True)

#     st.markdown('<div style="height:1px;background:#0F1923;margin:0 16px 12px;"></div>', unsafe_allow_html=True)
#     if st.button("⏻  Logout", use_container_width=True, key="logout_btn"):
#         st.session_state.logged_in=False; st.session_state.username=""; st.rerun()

# # ═══════════════════════════════════════
# # PAGE HEADER
# # ═══════════════════════════════════════
# PTITLES = {"dashboard":("Overview","System at a glance"),
#            "performance":("Model Performance","Accuracy · F1 · Confusion Matrix"),
#            "live":("Live Detection","Real-time activity recognition"),
#            "history":("History & Analytics","Activity log and trends"),
#            "admin":("Admin Panel","User and data management")}
# pt,ps = PTITLES.get(st.session_state.page,("Dashboard",""))
# st.markdown(f"""
# <div class="phead">
#   <div style="display:flex;align-items:center;justify-content:space-between;">
#     <div>
#       <div class="ptitle">{pt}</div>
#       <div class="pmeta">{ps}</div>
#     </div>
#     <div style="display:flex;gap:10px;align-items:center;">
#       <span class="pbadge">99.61% F1</span>
#       <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#1A2535;">
#         {datetime.now().strftime('%d %b %Y  %H:%M')}</span>
#     </div>
#   </div>
# </div>
# """, unsafe_allow_html=True)

# page = st.session_state.page

# # ═══════════════════════════════════════
# # OVERVIEW
# # ═══════════════════════════════════════
# if page == "dashboard":
#     df = load_df()
#     m  = read_metrics()

#     # ── KPI row ──
#     c1,c2,c3,c4,c5 = st.columns(5)
#     kpis = []
#     if m:
#         kpis = [(c1,"MODEL ACCURACY",f"{m.get('Accuracy',0)*100:.2f}%","#22C55E",
#                  f"+{(m.get('Accuracy',0)-.73)*100:.1f}% vs baseline"),
#                 (c2,"WEIGHTED F1",f"{m.get('F1',0)*100:.2f}%","#14B8A6","Final reported score")]
#     if not df.empty:
#         kpis += [(c3,"TOTAL RECORDS",f"{len(df):,}","#60A5FA","All time"),
#                  (c4,"AVG CONFIDENCE",f"{df['Confidence'].mean()*100:.1f}%","#F59E0B","Across all records"),
#                  (c5,"UNIQUE ACTIVITIES",str(df["Activity"].nunique()),"#A78BFA","Active classes")]
#     for col,lbl,val,color,sub in kpis:
#         col.markdown(f"""<div class="kpi" style="--a:{color}">
#         <div class="kpi-l">{lbl}</div><div class="kpi-v">{val}</div>
#         <div class="kpi-s">{sub}</div></div>""", unsafe_allow_html=True)

#     # ── Risk siren ──
#     if not df.empty:
#         risk = df[df["Activity"].isin(RISK)]
#         if not risk.empty:
#             st.components.v1.html(SIREN,height=0)
#             st.markdown(f"""<div class="alert-r si">
#             <span style="color:#EF4444;font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;">
#             ⚠  RISK ACTIVITY DETECTED — {len(risk)} records
#             ({", ".join(risk["Activity"].unique())}) — Latest: {risk["Time"].max().strftime("%H:%M:%S")}
#             </span></div>""", unsafe_allow_html=True)

#     st.markdown('<div class="sh">Activity Overview</div>', unsafe_allow_html=True)

#     if df.empty:
#         st.markdown("""<div class="alert-w">
#         <span style="color:#F59E0B;font-size:13px;">📷  No data yet.
#         Go to <b>Live Detection</b> and start the camera to collect activity data.</span></div>""",
#         unsafe_allow_html=True)
#     else:
#         cl,cr = st.columns([3,2])
#         with cl:
#             st.markdown("**Activity distribution**")
#             counts = df["Activity"].value_counts()
#             counts.index = [normalize_label(x) for x in counts.index]
#             fig,ax = dark_fig((7,3.8))
#             bars = ax.barh(counts.index[::-1], counts.values[::-1],
#                            color=PAL[:len(counts)], height=0.6, edgecolor="none")
#             style_ax(ax)
#             for bar,val in zip(bars, counts.values[::-1]):
#                 ax.text(val+0.5, bar.get_y()+bar.get_height()/2,
#                         str(val), va="center", color="#2D3E55", fontsize=8)
#             ax.set_xlabel("Count", color="#2D3E55", fontsize=8)
#             plt.tight_layout(); st.pyplot(fig); plt.close(fig)

#         with cr:
#             st.markdown("**Last 10 detections**")
#             rec = df.tail(10)[["Time","Activity","Confidence"]].copy()
#             rec = rec.sort_values("Time",ascending=False)
#             rec["Activity"] = rec["Activity"].apply(normalize_label)
#             rec["Conf%"]    = (rec["Confidence"]*100).round(1)
#             rec["Time"]     = rec["Time"].dt.strftime("%H:%M:%S")
#             rec = rec.drop(columns="Confidence")
#             st.dataframe(rec, use_container_width=True, hide_index=True, height=260,
#                 column_config={"Conf%": st.column_config.ProgressColumn(
#                     "Conf%", min_value=0, max_value=100, format="%.1f%%")})

#     # ── Today stats ──
#     if not df.empty:
#         st.markdown('<div class="sh">Today\'s Summary</div>', unsafe_allow_html=True)
#         today = df[df["Time"]>=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)]
#         ts1,ts2,ts3,ts4 = st.columns(4)
#         for col,lbl,val,c in [
#             (ts1,"Today Records",str(len(today)),"#22C55E"),
#             (ts2,"Most Active",today["Activity"].mode()[0] if not today.empty else "—","#14B8A6"),
#             (ts3,"High Confidence",str((today["Confidence"]>0.85).sum()) if not today.empty else "0","#F59E0B"),
#             (ts4,"Risk Events",str(today[today["Activity"].isin(RISK)]["Activity"].count()) if not today.empty else "0","#EF4444"),
#         ]:
#             col.markdown(f'<div class="kpi" style="--a:{c}"><div class="kpi-l">{lbl}</div><div class="kpi-v" style="font-size:20px">{DN.get(val,val)}</div></div>', unsafe_allow_html=True)

#     # ── Pipeline cards ──
#     st.markdown('<div class="sh">System Pipeline</div>', unsafe_allow_html=True)
#     pc = st.columns(6)
#     for col,icon,label,sub,color in [
#         (pc[0],"📹","Camera","Webcam input","#14B8A6"),
#         (pc[1],"🦴","MediaPipe","33 keypoints","#60A5FA"),
#         (pc[2],"📐","Normalize","Hip-center","#14B8A6"),
#         (pc[3],"🔷","CNN","Conv1D feat.","#A78BFA"),
#         (pc[4],"🔄","BiLSTM","Temporal seq.","#A78BFA"),
#         (pc[5],"🏷","Classify","+ Confidence","#22C55E"),
#     ]:
#         col.markdown(f"""<div style="background:#0D1520;border:1px solid #1A2535;border-top:2px solid {color};
#         border-radius:10px;padding:14px 10px;text-align:center;">
#         <div style="font-size:20px;margin-bottom:6px;">{icon}</div>
#         <div style="font-size:11px;font-weight:500;color:#8A9BB5;">{label}</div>
#         <div style="font-size:9px;color:#2D3E55;font-family:'JetBrains Mono',monospace;">{sub}</div>
#         </div>""", unsafe_allow_html=True)

# # ═══════════════════════════════════════
# # MODEL PERFORMANCE
# # ═══════════════════════════════════════
# elif page == "performance":
#     m = read_metrics()
#     if not m:
#         st.warning("Run `python test_model.py` to generate metrics.")
#     else:
#         c = st.columns(5)
#         for col,lbl,key,color,sub in [
#             (c[0],"ACCURACY","Accuracy","#22C55E","Test set"),
#             (c[1],"WEIGHTED F1","F1","#14B8A6","Final score"),
#             (c[2],"MACRO F1","F1_macro","#14B8A6","Equal weight"),
#             (c[3],"TOP-2 ACC","Top2_accuracy","#F59E0B","In top 2"),
#             (c[4],"AVG CONF","Avg_confidence","#F59E0B","Mean conf"),
#         ]:
#             val = m.get(key,0)
#             col.markdown(f'<div class="kpi" style="--a:{color}"><div class="kpi-l">{lbl}</div><div class="kpi-v">{val*100:.2f}%</div><div class="kpi-s">{sub}</div></div>', unsafe_allow_html=True)

#     st.markdown('<div class="sh">Confusion Matrix  ·  Per-Class Stats</div>', unsafe_allow_html=True)
#     cl,cr = st.columns([3,2])
#     with cl:
#         try:
#             cm      = np.load("confusion.npy")
#             classes = np.load("classes.npy",allow_pickle=True)
#             disp_cls= [DN.get(c,c) for c in classes]
#             cm_n    = cm.astype(float)/(cm.sum(axis=1,keepdims=True)+1e-8)
#             fig,ax  = plt.subplots(figsize=(7,5.5))
#             fig.patch.set_facecolor("#0D1520"); ax.set_facecolor("#0D1520")
#             sns.heatmap(cm_n, annot=cm, fmt="d",
#                         cmap=sns.color_palette("rocket_r",as_cmap=True),
#                         xticklabels=disp_cls, yticklabels=disp_cls,
#                         linewidths=0.5, linecolor="#070A0F",
#                         ax=ax, vmin=0, vmax=1, cbar_kws={"shrink":.75,"pad":.02})
#             ax.set_xlabel("Predicted",color="#2D3E55",fontsize=10)
#             ax.set_ylabel("Actual",color="#2D3E55",fontsize=10)
#             ax.tick_params(colors="#2D3E55",labelsize=8,rotation=30)
#             plt.tight_layout(); st.pyplot(fig); plt.close(fig)
#         except: st.info("Run test_model.py to generate confusion matrix.")

#     with cr:
#         try:
#             classes = np.load("classes.npy",allow_pickle=True)
#             cm      = np.load("confusion.npy")
#             rows=[]
#             for i,cls in enumerate(classes):
#                 tp=cm[i,i]; fn=cm[i,:].sum()-tp; fp=cm[:,i].sum()-tp
#                 pr=tp/(tp+fp+1e-8); rc=tp/(tp+fn+1e-8); f1c=2*pr*rc/(pr+rc+1e-8)
#                 rows.append({"Class":DN.get(cls,cls),"Prec":f"{pr:.3f}","Rec":f"{rc:.3f}","F1":f"{f1c:.3f}"})
#             st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True,height=220)
#             f1s=[float(r["F1"]) for r in rows]
#             fig2,ax2 = plt.subplots(figsize=(5,2.8))
#             fig2.patch.set_facecolor("#0D1520"); ax2.set_facecolor("#0D1520")
#             colors=["#22C55E" if v>=0.99 else "#F59E0B" if v>=0.95 else "#EF4444" for v in f1s]
#             bars=ax2.barh([DN.get(c,c)[:12] for c in classes],f1s,color=colors,height=0.6)
#             ax2.set_xlim(0.85,1.01); ax2.axvline(1.0,color="#1A2535",linewidth=0.5)
#             style_ax(ax2)
#             for bar,val in zip(bars,f1s):
#                 ax2.text(val+.001,bar.get_y()+bar.get_height()/2,
#                          f"{val:.3f}",va="center",color="#2D3E55",fontsize=7)
#             plt.tight_layout(); st.pyplot(fig2); plt.close(fig2)
#         except: pass

#     st.markdown('<div class="sh">Model Architecture</div>', unsafe_allow_html=True)
#     arch = pd.DataFrame([
#         {"Layer":"Input",         "Shape":"(60, 132)","Params":"—",       "Purpose":"60 frames × 132 pose features (33 landmarks × 4 values)"},
#         {"Layer":"Conv1D 64",     "Shape":"(60, 64)", "Params":"8,512",   "Purpose":"Extract local spatial patterns across adjacent frames"},
#         {"Layer":"Conv1D 128",    "Shape":"(60, 128)","Params":"24,704",  "Purpose":"Deeper spatial features + BatchNorm + Dropout 0.2"},
#         {"Layer":"BiLSTM 128",    "Shape":"(60, 256)","Params":"263,168", "Purpose":"Bidirectional temporal modeling (forward + backward)"},
#         {"Layer":"BiLSTM 64",     "Shape":"(60, 128)","Params":"164,352", "Purpose":"Higher-level temporal abstraction"},
#         {"Layer":"SoftAttention", "Shape":"(128,)",   "Params":"129",     "Purpose":"Learns which frames matter most in the 60-frame window"},
#         {"Layer":"Dense 128",     "Shape":"(128,)",   "Params":"16,512",  "Purpose":"Classification head with Dropout 0.4"},
#         {"Layer":"Softmax 7",     "Shape":"(7,)",     "Params":"903",     "Purpose":"Probability distribution over 7 activity classes"},
#     ])
#     st.dataframe(arch,use_container_width=True,hide_index=True)
#     st.markdown(f"""<div class="alert-g">
#     <span style="color:#22C55E;font-size:11px;">Total parameters: <b>497,480</b>  ·  Model size: <b>1.90 MB</b>
#     ·  Training: 5-fold CV, 80 epochs max, EarlyStopping patience=12</span></div>""",
#     unsafe_allow_html=True)

# # ═══════════════════════════════════════
# # LIVE DETECTION
# # ═══════════════════════════════════════
# elif page == "live":
#     cl,cr = st.columns([3,2])
#     with cl:
#         st.markdown('<div class="sh">Camera Control</div>', unsafe_allow_html=True)
#         cam_running = st.session_state.cam_pid is not None
#         if cam_running:
#             st.markdown('<div class="alert-g"><span class="live-dot"></span><span style="color:#22C55E;font-size:12px;font-weight:600;">Camera is RUNNING</span></div>', unsafe_allow_html=True)
#         cc1,cc2,cc3 = st.columns(3)
#         with cc1:
#             if st.button("▶  Start Camera", type="primary", use_container_width=True):
#                 proc = subprocess.Popen([sys.executable,"real_time.py"])
#                 st.session_state.cam_pid = proc.pid
#                 st.success(f"Camera started — PID {proc.pid}")
#         with cc2:
#             if st.button("⏹  Stop Camera", use_container_width=True):
#                 if st.session_state.cam_pid:
#                     try:
#                         import signal
#                         os.kill(st.session_state.cam_pid,signal.SIGTERM)
#                         st.session_state.cam_pid=None; st.success("Camera stopped")
#                     except: st.warning("Press Q in the camera window to stop")
#         with cc3:
#             if st.button("↻  Refresh Feed", use_container_width=True):
#                 st.rerun()

#         st.markdown('<div class="sh">How to Get Accurate Predictions</div>', unsafe_allow_html=True)
#         tips=[
#             ("🍹 Drinking vs Eating","Hold the activity for 4+ seconds. Drinking = wrist near lips, elbow pointing DOWN. Eating = wrist near mouth, elbow pointing OUTWARD to side. Make the elbow angle as clear as possible."),
#             ("🏃 Exercise vs Fighting","Ensure your FULL body is visible from head to hip. Exercise = repetitive symmetrical motion. Stand 1.5–2.5m from camera. Rapid random arm movement triggers fighting — do exercise slowly at first."),
#             ("💤 No Activity showing wrong","Sit or stand completely still for 5+ seconds. Make sure both shoulders and hips are visible. Partial body detection = unreliable predictions."),
#             ("📷 Camera setup tips","Distance: 1.5–3m from camera. Height: roughly eye level. Lighting: bright front-facing light. Avoid strong backlight (window behind you). Wear fitted clothing for better landmark detection."),
#             ("🎯 Confidence threshold","The model only shows a label when 80%+ confident AND 65%+ of last 20 frames agree. If it shows '...' that means it's uncertain — hold the pose more clearly."),
#         ]
#         for title,body in tips:
#             st.markdown(f'<div class="alert-w" style="margin-bottom:8px;"><div style="color:#F59E0B;font-size:11px;font-weight:600;margin-bottom:4px;">{title}</div><div style="color:#5A7090;font-size:11px;line-height:1.6;">{body}</div></div>', unsafe_allow_html=True)

#     with cr:
#         st.markdown('<div class="sh">Detection Settings</div>', unsafe_allow_html=True)
#         settings=[
#             ("Global confidence threshold","80%"),
#             ("Smoothing window","20 frames (majority vote)"),
#             ("Prediction stride","Every 5 frames"),
#             ("Minimum vote ratio","65% of buffer must agree"),
#             ("Save interval","Once per 3 seconds"),
#             ("Drinking threshold","88% (most over-predicted)"),
#             ("Exercise/Fighting","85% each"),
#             ("Eating threshold","83%"),
#         ]
#         for k,v in settings:
#             st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
#             padding:8px 12px;background:#0D1520;border-radius:6px;margin-bottom:4px;border:1px solid #1A2535;">
#             <span style="font-size:11px;color:#2D3E55;">{k}</span>
#             <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#14B8A6;">{v}</span>
#             </div>""", unsafe_allow_html=True)

#         if os.path.exists("classes.npy"):
#             classes=np.load("classes.npy",allow_pickle=True)
#             st.markdown('<div class="sh">Detectable Activities</div>', unsafe_allow_html=True)
#             for cls in classes:
#                 label=DN.get(cls,cls); is_risk=cls.lower() in ["fighting","falling"]
#                 color="#EF4444" if is_risk else "#14B8A6"
#                 badge=f"<span style='font-size:9px;background:#200A0A;color:#EF4444;font-family:JetBrains Mono,monospace;padding:1px 6px;border-radius:10px;border:1px solid #5B1B1B;margin-left:6px;'>RISK</span>" if is_risk else ""
#                 st.markdown(f'<div style="display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid #0F1923;"><div style="width:6px;height:6px;border-radius:50%;background:{color};flex-shrink:0;"></div><span style="font-size:12px;color:#5A7090;">{label}</span>{badge}</div>', unsafe_allow_html=True)

# # ═══════════════════════════════════════
# # HISTORY & ANALYTICS
# # ═══════════════════════════════════════
# elif page == "history":
#     df = load_df()
#     if df.empty:
#         st.markdown('<div class="alert-w"><span style="color:#F59E0B;">No activity data yet. Start the camera to collect data.</span></div>', unsafe_allow_html=True)
#         st.stop()

#     # ── Filters ──
#     with st.expander("🔍  Filters", expanded=True):
#         fc1,fc2,fc3,fc4 = st.columns(4)
#         raw_acts  = sorted(df["Activity"].unique().tolist())
#         disp_acts = ["All"]+[DN.get(a,a) for a in raw_acts]
#         sel_disp  = fc1.selectbox("Activity",disp_acts)
#         min_conf  = fc2.slider("Min Confidence %",0,100,0,5)
#         date_rng  = fc3.selectbox("Time Range",["All time","Today","Last 7 days","Last 30 days"])
#         sort_by   = fc4.selectbox("Sort by",["Newest first","Oldest first","Highest confidence","Lowest confidence"])

#     df_f = df.copy()
#     if sel_disp!="All":
#         rk={v:k for k,v in DN.items()}.get(sel_disp,sel_disp)
#         df_f=df_f[df_f["Activity"].isin([sel_disp,rk])]
#     df_f=df_f[df_f["Confidence"]>=min_conf/100]
#     if date_rng=="Today":      df_f=df_f[df_f["Time"]>=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)]
#     elif date_rng=="Last 7 days":  df_f=df_f[df_f["Time"]>=datetime.now()-timedelta(days=7)]
#     elif date_rng=="Last 30 days": df_f=df_f[df_f["Time"]>=datetime.now()-timedelta(days=30)]
#     sort_map={"Newest first":("Time",False),"Oldest first":("Time",True),
#               "Highest confidence":("Confidence",False),"Lowest confidence":("Confidence",True)}
#     sc,sa=sort_map[sort_by]; df_f=df_f.sort_values(sc,ascending=sa)
#     if df_f.empty: st.warning("No records match the current filters."); st.stop()

#     # ── KPIs ──
#     k1,k2,k3,k4,k5 = st.columns(5)
#     for col,lbl,val,c in [
#         (k1,"TOTAL RECORDS",f"{len(df_f):,}","#22C55E"),
#         (k2,"AVG CONFIDENCE",f"{df_f['Confidence'].mean()*100:.1f}%","#14B8A6"),
#         (k3,"PEAK HOUR",f"{df_f['Time'].dt.hour.mode()[0]:02d}:00","#60A5FA"),
#         (k4,"ACTIVITIES",str(df_f["Activity"].nunique()),"#A78BFA"),
#         (k5,"LATEST",df_f["Time"].max().strftime("%H:%M"),"#F59E0B"),
#     ]:
#         col.markdown(f'<div class="kpi" style="--a:{c}"><div class="kpi-l">{lbl}</div><div class="kpi-v" style="font-size:22px">{val}</div></div>', unsafe_allow_html=True)

#     risk_df=df_f[df_f["Activity"].isin(RISK)]
#     if not risk_df.empty:
#         st.components.v1.html(SIREN,height=0)
#         st.markdown(f'<div class="alert-r si"><span style="color:#EF4444;font-family:\'JetBrains Mono\',monospace;font-size:12px;font-weight:700;">⚠  RISK — {len(risk_df)} records ({", ".join(risk_df["Activity"].unique())}) — Latest: {risk_df["Time"].max().strftime("%H:%M:%S")}</span></div>', unsafe_allow_html=True)

#     # ── Charts ──
#     st.markdown('<div class="sh">Analytics Charts</div>', unsafe_allow_html=True)
#     t1,t2,t3 = st.tabs(["Distribution","Confidence Trend","Hourly Heatmap"])

#     with t1:
#         ch1,ch2 = st.columns(2)
#         with ch1:
#             counts=df_f["Activity"].value_counts(); counts.index=[normalize_label(x) for x in counts.index]
#             fig,ax=dark_fig((5.5,3.2))
#             ax.bar(counts.index,counts.values,color=PAL[:len(counts)],edgecolor="none",width=0.6)
#             style_ax(ax); ax.tick_params(rotation=25,labelsize=8)
#             for p in ax.patches:
#                 ax.text(p.get_x()+p.get_width()/2,p.get_height()+0.2,str(int(p.get_height())),
#                         ha="center",color="#2D3E55",fontsize=8)
#             plt.tight_layout(); st.pyplot(fig); plt.close(fig)
#         with ch2:
#             # Pie chart
#             fig2,ax2=plt.subplots(figsize=(5.5,3.2))
#             fig2.patch.set_facecolor("#0D1520"); ax2.set_facecolor("#0D1520")
#             wedges,texts,autotexts=ax2.pie(counts.values,labels=None,
#                 autopct="%1.1f%%",colors=PAL[:len(counts)],startangle=90,
#                 pctdistance=0.7,wedgeprops=dict(width=0.6,edgecolor="#070A0F",linewidth=1.5))
#             for at in autotexts: at.set_fontsize(8); at.set_color("#DDE6F0")
#             ax2.legend(counts.index,loc="center left",bbox_to_anchor=(1,.5),
#                       fontsize=8,facecolor="#0D1520",labelcolor="#5A7090",framealpha=0)
#             plt.tight_layout(); st.pyplot(fig2); plt.close(fig2)

#     with t2:
#         fig3,ax3=dark_fig((10,3.2))
#         ds=df_f.sort_values("Time")
#         ax3.plot(ds["Time"],ds["Confidence"],color="#14B8A6",linewidth=0.8,alpha=0.7)
#         ax3.fill_between(ds["Time"],ds["Confidence"],alpha=0.06,color="#14B8A6")
#         ax3.axhline(0.80,color="#F59E0B",linestyle="--",linewidth=0.8,label="Threshold 80%")
#         ax3.set_ylim(0,1.05); style_ax(ax3)
#         ax3.tick_params(rotation=20,labelsize=7)
#         ax3.legend(facecolor="#0D1520",labelcolor="#2D3E55",fontsize=8)
#         # Highlight risk events
#         for _,row in df_f[df_f["Activity"].isin(RISK)].iterrows():
#             ax3.axvline(row["Time"],color="#EF4444",linewidth=0.6,alpha=0.5)
#         plt.tight_layout(); st.pyplot(fig3); plt.close(fig3)

#     with t3:
#         tmp=df_f.copy(); tmp["Hour"]=tmp["Time"].dt.hour; tmp["Date"]=tmp["Time"].dt.date
#         pivot=tmp.groupby(["Date","Hour"]).size().unstack(fill_value=0)
#         if not pivot.empty and len(pivot)>0:
#             fig4,ax4=plt.subplots(figsize=(12,max(2,len(pivot)*0.55+1)))
#             fig4.patch.set_facecolor("#0D1520"); ax4.set_facecolor("#0D1520")
#             sns.heatmap(pivot,ax=ax4,cmap="YlOrRd",linewidths=0.3,linecolor="#070A0F",
#                         cbar_kws={"shrink":.6})
#             ax4.tick_params(colors="#2D3E55",labelsize=8)
#             plt.tight_layout(); st.pyplot(fig4); plt.close(fig4)
#         else: st.info("Need data from multiple hours to show heatmap.")

#     # ── Full records table ──
#     st.markdown('<div class="sh">All Records</div>', unsafe_allow_html=True)
#     disp=df_f[["ID","Time","Activity","Confidence"]].copy()
#     disp["Activity"]=disp["Activity"].apply(normalize_label)
#     disp["Conf%"]=(disp["Confidence"]*100).round(1)
#     disp["Time"]=disp["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
#     disp=disp.drop(columns="Confidence")
#     st.dataframe(disp,use_container_width=True,hide_index=True,height=500,
#         column_config={
#             "Conf%":st.column_config.ProgressColumn("Conf%",min_value=0,max_value=100,format="%.1f%%"),
#             "Activity":st.column_config.TextColumn("Activity",width="medium"),
#             "Time":st.column_config.TextColumn("Time",width="large"),
#         })
#     st.caption(f"Showing {len(disp):,} records · activity={sel_disp} · min_conf={min_conf}% · {date_rng} · {sort_by}")

#     # ── Export ──
#     st.markdown('<div class="sh">Export</div>', unsafe_allow_html=True)
#     e1,e2,e3 = st.columns(3)
#     with e1:
#         st.download_button("📥  Download CSV",df_f.to_csv(index=False).encode(),
#             "har_history.csv",use_container_width=True,mime="text/csv")
#     with e2:
#         if st.button("📄  Generate PDF Report",use_container_width=True,type="primary"):
#             with st.spinner("Building PDF..."):
#                 try:
#                     pdf=generate_pdf_report(df_f)
#                     st.download_button("⬇️  Download PDF",pdf,
#                         f"har_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
#                         mime="application/pdf",use_container_width=True)
#                     st.success("PDF ready!")
#                 except Exception as e: st.error(f"PDF error: {e}")
#     with e3:
#         st.download_button("📊  Download JSON",df_f.to_json(orient="records",indent=2).encode(),
#             "har_history.json",use_container_width=True,mime="application/json")

# # ═══════════════════════════════════════
# # ADMIN PANEL
# # ═══════════════════════════════════════
# elif page == "admin":
#     if st.session_state.username != "admin":
#         st.markdown('<div class="alert-r"><span style="color:#EF4444;font-size:13px;">⛔  Admin access required. Login as \'admin\'.</span></div>', unsafe_allow_html=True)
#         st.stop()

#     tab1,tab2,tab3,tab4,tab5 = st.tabs(["👥 Users","📋 Records","🔑 Change Password","🔁 Retrain","🖥 System"])

#     with tab1:
#         st.markdown('<div class="sh">User Management</div>', unsafe_allow_html=True)
#         try:
#             conn=sqlite3.connect("users.db")
#             udf=pd.read_sql("SELECT id,username FROM users",conn); conn.close()
#             st.dataframe(udf,use_container_width=True,hide_index=True,height=200)
#         except Exception as e: st.warning(f"Could not load users: {e}")
#         st.divider()
#         ua1,ua2 = st.columns(2)
#         with ua1:
#             st.markdown("**Add new user**")
#             nu=st.text_input("New Username",key="nu"); np_=st.text_input("New Password",type="password",key="np_")
#             if st.button("✅  Create User",type="primary",key="cu"):
#                 if nu and np_:
#                     if register(nu,np_): st.success(f"User '{nu}' created"); st.rerun()
#                     else: st.error(f"Username '{nu}' already exists")
#                 else: st.warning("Fill both fields")
#         with ua2:
#             st.markdown("**Remove user**")
#             ulist=[u for u in list_users() if u!="admin"]
#             if ulist:
#                 du=st.selectbox("Select user to remove",ulist,key="du")
#                 if st.button("🗑  Remove User",type="primary",key="ru"):
#                     if delete_user(du): st.success(f"User '{du}' removed"); st.rerun()
#             else: st.info("No non-admin users to remove")

#     with tab2:
#         st.markdown('<div class="sh">Activity Records</div>', unsafe_allow_html=True)
#         raw=get_history()
#         if raw:
#             da=pd.DataFrame(raw,columns=["ID","Activity","Confidence","Time"])
#             st.dataframe(da,use_container_width=True,hide_index=True,height=260)
#             st.divider()
#             da1,da2,da3 = st.columns(3)
#             with da1:
#                 st.markdown("**Delete record by ID**")
#                 did=st.number_input("Record ID",min_value=1,step=1,key="did")
#                 if st.button("🗑  Delete",type="primary",key="dr"):
#                     delete_record(int(did)); st.success("Deleted"); st.rerun()
#             with da2:
#                 st.markdown("**Edit record by ID**")
#                 eid=st.number_input("Record ID",min_value=1,step=1,key="eid")
#                 na=st.text_input("New Activity Label",key="na")
#                 nc=st.number_input("New Confidence",0.0,1.0,0.8,0.01,key="nc")
#                 if st.button("✏️  Update",key="ur"):
#                     update_record(int(eid),na,nc); st.success("Updated"); st.rerun()
#             with da3:
#                 st.markdown("**Bulk actions**")
#                 st.markdown('<div class="alert-r">', unsafe_allow_html=True)
#                 if st.button("🗑  Clear ALL Records",key="ca"):
#                     clear_all(); st.success("All records cleared"); st.rerun()
#                 st.markdown("</div>", unsafe_allow_html=True)
#         else: st.info("No records yet.")

#     with tab3:
#         st.markdown('<div class="sh">Change Password</div>', unsafe_allow_html=True)
#         cp_user=st.selectbox("User",list_users(),key="cp_user")
#         cp_new =st.text_input("New Password",type="password",key="cp_new")
#         cp_con =st.text_input("Confirm Password",type="password",key="cp_con")
#         if st.button("🔑  Change Password",type="primary",key="chpw"):
#             if cp_new!=cp_con: st.error("Passwords do not match")
#             elif len(cp_new)<6: st.error("Password must be at least 6 characters")
#             else:
#                 if change_password(cp_user,cp_new): st.success(f"Password changed for '{cp_user}'")
#                 else: st.error("Failed to change password")

#     with tab4:
#         st.warning("Re-runs the full training pipeline. Takes 10–30 minutes.")
#         st.markdown('<div class="sh">Pipeline Steps</div>', unsafe_allow_html=True)
#         r1,r2,r3,r4=st.columns(4)
#         if r1.button("1 — Extract Pose",use_container_width=True):
#             with st.spinner("Extracting poses..."): subprocess.run([sys.executable,"extract_pose.py"])
#             st.success("Done")
#         if r2.button("2 — Create Dataset",use_container_width=True):
#             with st.spinner("Building dataset..."): subprocess.run([sys.executable,"create_dataset.py"])
#             st.success("Done")
#         if r3.button("3 — Train Model",use_container_width=True):
#             subprocess.Popen([sys.executable,"train_lstm.py"]); st.info("Training started in background")
#         if r4.button("4 — Evaluate",use_container_width=True):
#             with st.spinner("Evaluating..."): subprocess.run([sys.executable,"test_model.py"])
#             st.success("Done — metrics updated")

#     with tab5:
#         st.markdown('<div class="sh">File Status</div>', unsafe_allow_html=True)
#         files=["features.npy","labels.npy","classes.npy","confusion.npy","metrics.txt",
#                "metrics_detailed.txt","models/activity_model.keras","history.db","users.db",
#                "report_generator.py","model_utils.py","pose_landmarker.task"]
#         rows=[]
#         for f in files:
#             ok=os.path.exists(f)
#             rows.append({"File":f,"Status":"OK" if ok else "❌ MISSING",
#                          "Size":f"{os.path.getsize(f)/1024:.1f} KB" if ok else "—",
#                          "Modified":datetime.fromtimestamp(os.path.getmtime(f)).strftime("%H:%M %d/%m/%y") if ok else "—"})
#         st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
#         st.markdown('<div class="sh">Environment</div>', unsafe_allow_html=True)
#         env=[{"Key":"Python","Value":sys.version.split()[0]},
#              {"Key":"Platform","Value":sys.platform},
#              {"Key":"Working Dir","Value":os.getcwd()}]
#         try:
#             import tensorflow as tf
#             env.append({"Key":"TensorFlow","Value":tf.__version__})
#         except: pass
#         st.dataframe(pd.DataFrame(env),use_container_width=True,hide_index=True)

"""
app.py — HAR AI Platform (Production)
Admin sees all users + activity data. Users see only their own data.
Run: streamlit run app.py
"""
import streamlit as st
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import requests
import subprocess, sys, os, sqlite3
from datetime import datetime, timedelta
from auth        import login, register, init_db, list_users, delete_user, change_password
from history_db  import (get_history, get_history_with_users, get_user_summary,
                          get_registered_users, init_history_db,
                          delete_record, update_record, clear_all, clear_user)
from report_generator import generate_pdf_report

init_db()
init_history_db()

st.set_page_config(page_title="HAR AI Platform", page_icon="🎯",
                   layout="wide", initial_sidebar_state="expanded")


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif !important;}
.main,.block-container{background:#070A0F !important;padding:0 1.5rem 2rem !important;max-width:100% !important;}
section[data-testid="stSidebar"]{background:#040608 !important;border-right:1px solid #0F1923;}
#MainMenu,footer,header{visibility:hidden;}
.stTextInput input,.stNumberInput input{background:#0D1520 !important;border:1px solid #1A2535 !important;color:#C8D4E3 !important;border-radius:8px !important;}
.stButton>button{background:#0D1520 !important;border:1px solid #1A2535 !important;color:#8A9BB5 !important;border-radius:8px !important;font-size:13px !important;transition:all .15s !important;}
.stButton>button:hover{background:#1A2535 !important;color:#C8D4E3 !important;}
.stButton>button[kind="primary"]{background:#0F3D30 !important;border-color:#14B8A6 !important;color:#14B8A6 !important;}
.stButton>button[kind="primary"]:hover{background:#145C46 !important;}
.stTabs [data-baseweb="tab-list"]{background:#0D1520;border-radius:10px;padding:4px;}
.stTabs [data-baseweb="tab"]{border-radius:7px !important;color:#4A5C74 !important;font-size:13px !important;}
.stTabs [aria-selected="true"]{background:#1A2535 !important;color:#C8D4E3 !important;}
.kpi{background:#0D1520;border:1px solid #1A2535;border-radius:12px;padding:18px 20px;position:relative;overflow:hidden;}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--a,#14B8A6);}
.kpi-l{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:#2D3E55;margin-bottom:8px;}
.kpi-v{font-family:'Syne',sans-serif;font-size:26px;font-weight:700;color:var(--a,#14B8A6);line-height:1;}
.kpi-s{font-size:10px;color:#2D3E55;margin-top:4px;}
.sh{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:#2D3E55;border-bottom:1px solid #0F1923;padding-bottom:8px;margin:24px 0 14px;}
.alert-r{background:#0E0507;border:1px solid #4A1020;border-left:3px solid #EF4444;border-radius:8px;padding:14px 18px;margin:10px 0;}
.alert-g{background:#040E09;border:1px solid #0A4A25;border-left:3px solid #22C55E;border-radius:8px;padding:12px 16px;margin:8px 0;}
.alert-w{background:#0D0A04;border:1px solid #4A3800;border-left:3px solid #F59E0B;border-radius:8px;padding:12px 16px;margin:8px 0;}
.phead{background:#070A0F;border-bottom:1px solid #0F1923;padding:12px 0 10px;margin-bottom:18px;position:sticky;top:0;z-index:99;}
.ptitle{font-family:'Syne',sans-serif;font-size:19px;font-weight:800;color:#DDE6F0;}
.pmeta{font-family:'JetBrains Mono',monospace;font-size:9px;color:#2D3E55;}
.pbadge{background:#072218;border:1px solid #0A4A2C;color:#22C55E;font-family:'JetBrains Mono',monospace;font-size:9px;padding:3px 10px;border-radius:20px;}
@keyframes si{0%,100%{opacity:1}50%{opacity:.6}}.si{animation:si .6s ease-in-out infinite;}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,.4)}50%{box-shadow:0 0 0 6px rgba(34,197,94,0)}}
.live-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#22C55E;animation:pulse 1.5s infinite;margin-right:6px;}
</style>
""", unsafe_allow_html=True)

SIREN = """<script>(function(){try{const c=new(window.AudioContext||window.webkitAudioContext)();[[440,880,'sawtooth'],[220,440,'square']].forEach(([lo,hi,t])=>{const o=c.createOscillator(),g=c.createGain();o.connect(g);g.connect(c.destination);o.type=t;[0,.4,.8,1.2,1.6].forEach((s,i)=>o.frequency.setValueAtTime(i%2?hi:lo,c.currentTime+s));g.gain.setValueAtTime(.25,c.currentTime);g.gain.exponentialRampToValueAtTime(.001,c.currentTime+2);o.start();o.stop(c.currentTime+2);});}catch(e){}})();</script>"""

DN  = {"no":"No Activity","no_activity":"No Activity","No Activity":"No Activity",
       "drinking":"Drinking","Drinking":"Drinking","eating":"Eating","Eating":"Eating",
       "exercise":"Exercise","Exercise":"Exercise","fighting":"Fighting","Fighting":"Fighting",
       "Typing":"Typing","typing":"Typing","WritingOnBoard":"Writing on Board",
       "Writing on Board":"Writing on Board"}
RISK = ["fighting","Fighting","falling"]
PAL  = ["#14B8A6","#22C55E","#60A5FA","#A78BFA","#F59E0B","#F43F5E","#FB923C"]

def norm(x): return DN.get(x, x)

for k,v in [("logged_in",False),("page","dashboard"),("cam_pid",None),
             ("username",""),("cam_started",False)]:
    if k not in st.session_state: st.session_state[k]=v

def load_df(username=None):
    raw = get_history(None if username=="admin" else username)
    if not raw: return pd.DataFrame(columns=["ID","Activity","Confidence","Time"])
    df  = pd.DataFrame(raw, columns=["ID","Activity","Confidence","Time"])
    df  = df[~df["Activity"].isin(["Unknown","...","Warming up...","Show full body..."])]
    df["Activity"] = df["Activity"].apply(norm)
    df["Time"]     = pd.to_datetime(df["Time"])
    return df.sort_values("Time")

def dark_fig(figsize=(7,3.5)):
    fig,ax=plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#0D1520"); ax.set_facecolor("#0D1520")
    return fig,ax

def style_ax(ax):
    ax.tick_params(colors="#2D3E55",labelsize=8)
    for sp in ax.spines.values(): sp.set_color("#1A2535")

def read_metrics():
    m={}
    if os.path.exists("metrics.txt"):
        try:
            for line in open("metrics.txt"):
                k,v=line.strip().split(":")
                m[k.strip()]=float(v.strip())
        except: pass
    return m

# ═══ LOGIN ═══
if not st.session_state.logged_in:
    _,col,_=st.columns([1,1.2,1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:50px 0 36px">
          <div style="width:64px;height:64px;border-radius:16px;background:linear-gradient(135deg,#0F3D30,#0A2840);
               border:1px solid #1A5040;display:inline-flex;align-items:center;justify-content:center;font-size:28px;margin-bottom:22px;">🎯</div>
          <div style="font-family:'Syne',sans-serif;font-size:30px;font-weight:800;
               background:linear-gradient(135deg,#E8EDF5,#14B8A6);-webkit-background-clip:text;
               -webkit-text-fill-color:transparent;margin-bottom:6px;">HAR AI Platform</div>
          <div style="font-size:12px;color:#2D3E55;font-style:italic;margin-bottom:36px;">"Every movement tells a story — we decode it."</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div style="font-size:11px;color:#2D3E55;margin-bottom:4px;">Username</div>',unsafe_allow_html=True)
        uname=st.text_input("u",placeholder="Enter username",label_visibility="collapsed",key="li_u")
        st.markdown('<div style="font-size:11px;color:#2D3E55;margin-bottom:4px;">Password</div>',unsafe_allow_html=True)
        passw=st.text_input("p",type="password",placeholder="Enter password",label_visibility="collapsed",key="li_p")
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("Login  →",use_container_width=True,type="primary"):
            if login(uname,passw):
                st.session_state.logged_in=True; st.session_state.username=uname
                st.session_state.page="dashboard"; st.rerun()
            else: st.error("Invalid credentials.")
    st.stop()

uname    = st.session_state.username
is_admin = (uname=="admin")

# ═══ SIDEBAR ═══
with st.sidebar:
    st.markdown(f"""
    <div style="padding:22px 20px 16px">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
        <div style="width:36px;height:36px;border-radius:10px;background:#0A2040;border:1px solid #1A4060;
             display:flex;align-items:center;justify-content:center;font-size:15px;">{"👑" if is_admin else "👤"}</div>
        <div>
          <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:#DDE6F0;">{uname}</div>
          <div style="font-size:10px;color:#2D3E55;">{"Administrator" if is_admin else "User"}</div>
        </div>
      </div>
      {"<div style='display:inline-block;background:#160A30;border:1px solid #3A1A80;color:#A78BFA;font-size:9px;padding:2px 8px;border-radius:10px;font-family:monospace;'>ADMIN</div>" if is_admin else ""}
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#0F1923;margin:0 16px 12px;"></div>',unsafe_allow_html=True)

    nav=[("dashboard","🏠  Overview"),("live","📹  Live Detection"),("history","📋  My Activity")]
    if is_admin:
        nav+=[("users","👥  User Monitor"),("performance","📊  Model Performance"),("admin","⚙️  Admin Panel")]
    else:
        nav+=[("performance","📊  Model Performance")]

    for key,label in nav:
        active=st.session_state.page==key
        if st.button(label,use_container_width=True,
                     type="primary" if active else "secondary",key=f"nav_{key}"):
            st.session_state.page=key; st.rerun()

    st.markdown('<div style="height:1px;background:#0F1923;margin:12px 16px;"></div>',unsafe_allow_html=True)
    m=read_metrics()
    if m:
        st.markdown(f"""<div style="padding:0 16px 16px">
        <div style="font-family:monospace;font-size:9px;letter-spacing:.15em;color:#2D3E55;margin-bottom:8px;">MODEL STATUS</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
          <span style="font-size:11px;color:#2D3E55;">Accuracy</span>
          <span style="font-family:monospace;font-size:11px;color:#22C55E;">{m.get('Accuracy',0)*100:.1f}%</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
          <span style="font-size:11px;color:#2D3E55;">F1 Score</span>
          <span style="font-family:monospace;font-size:11px;color:#14B8A6;">{m.get('F1',0)*100:.1f}%</span>
        </div></div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#0F1923;margin:0 16px 12px;"></div>',unsafe_allow_html=True)
    if st.button("⏻  Logout",use_container_width=True):
        st.session_state.logged_in=False; st.session_state.username=""
        st.session_state.cam_pid=None; st.session_state.cam_started=False; st.rerun()

PTITLES={"dashboard":("Overview","System at a glance"),
          "live":("Live Detection","Start camera and detect activities"),
          "history":("My Activity","Your personal activity history"),
          "users":("User Monitor","All registered users — Admin only"),
          "performance":("Model Performance","Accuracy · F1 · Confusion Matrix"),
          "admin":("Admin Panel","User and data management")}
pt,ps=PTITLES.get(st.session_state.page,("Dashboard",""))
st.markdown(f"""<div class="phead"><div style="display:flex;align-items:center;justify-content:space-between;">
<div><div class="ptitle">{pt}</div><div class="pmeta">{ps}</div></div>
<div style="display:flex;gap:10px;align-items:center;">
  <span class="pbadge">99.61% F1</span>
  <span style="font-family:monospace;font-size:9px;color:#1A2535;">{datetime.now().strftime('%d %b %Y  %H:%M')}</span>
  <span style="font-size:11px;color:#4A5C74;">👤 {uname}</span>
</div></div></div>""", unsafe_allow_html=True)

page=st.session_state.page

# ═══ OVERVIEW ═══
if page=="dashboard":
    df=load_df(uname); m=read_metrics()
    c1,c2,c3,c4=st.columns(4)
    kpis=[]
    if m:
        kpis=[(c1,"MODEL F1","99.61%","#22C55E","Weighted F1"),
              (c2,"ACCURACY","99.61%","#14B8A6","Test set")]
    if not df.empty:
        kpis+=[(c3,"MY RECORDS",f"{len(df):,}","#60A5FA",f"By {uname}"),
               (c4,"AVG CONFIDENCE",f"{df['Confidence'].mean()*100:.1f}%","#F59E0B","All records")]
    for col,lbl,val,color,sub in kpis:
        col.markdown(f'<div class="kpi" style="--a:{color}"><div class="kpi-l">{lbl}</div><div class="kpi-v">{val}</div><div class="kpi-s">{sub}</div></div>',unsafe_allow_html=True)

    if not df.empty:
        risk=df[df["Activity"].isin(RISK)]
        if not risk.empty:
            st.components.v1.html(SIREN,height=0)
            st.markdown(f'<div class="alert-r si"><span style="color:#EF4444;font-family:monospace;font-size:12px;font-weight:700;">⚠ RISK — {len(risk)} records ({", ".join(risk["Activity"].unique())})</span></div>',unsafe_allow_html=True)

    st.markdown('<div class="sh">Your Recent Activity</div>',unsafe_allow_html=True)
    if df.empty:
        st.markdown('<div class="alert-w"><span style="color:#F59E0B;font-size:13px;">📷 No activity yet. Open <a href="https://har-ai-platform.vercel.app" target="_blank" style="color:#14B8A6;">camera page</a> or go to Live Detection.</span></div>',unsafe_allow_html=True)
    else:
        cl,cr=st.columns([3,2])
        with cl:
            counts=df["Activity"].value_counts()
            fig,ax=dark_fig((6,3.5))
            ax.barh(counts.index[::-1],counts.values[::-1],color=PAL[:len(counts)],height=0.6,edgecolor="none")
            style_ax(ax)
            for i,val in enumerate(counts.values[::-1]):
                ax.text(val+0.3,i,str(val),va="center",color="#2D3E55",fontsize=8)
            plt.tight_layout(); st.pyplot(fig); plt.close(fig)
        with cr:
            rec=df.tail(10)[["Time","Activity","Confidence"]].copy().sort_values("Time",ascending=False)
            rec["Conf%"]=(rec["Confidence"]*100).round(1)
            rec["Time"]=rec["Time"].dt.strftime("%H:%M:%S")
            st.dataframe(rec.drop(columns="Confidence"),use_container_width=True,hide_index=True,height=260,
                column_config={"Conf%":st.column_config.ProgressColumn("Conf%",min_value=0,max_value=100,format="%.1f%%")})

    st.markdown('<div class="sh">System Pipeline</div>',unsafe_allow_html=True)
    pc=st.columns(6)
    for col,icon,label,sub,color in [
        (pc[0],"📹","Camera","Browser WebRTC","#14B8A6"),(pc[1],"🦴","MediaPipe","33 keypoints","#60A5FA"),
        (pc[2],"📐","Normalize","Hip-center","#14B8A6"),(pc[3],"🔷","CNN","Conv1D","#A78BFA"),
        (pc[4],"🔄","BiLSTM","Temporal","#A78BFA"),(pc[5],"🏷","Classify","+ Confidence","#22C55E")]:
        col.markdown(f'<div style="background:#0D1520;border:1px solid #1A2535;border-top:2px solid {color};border-radius:10px;padding:14px 10px;text-align:center;"><div style="font-size:20px;margin-bottom:6px;">{icon}</div><div style="font-size:11px;font-weight:500;color:#8A9BB5;">{label}</div><div style="font-size:9px;color:#2D3E55;font-family:monospace;">{sub}</div></div>',unsafe_allow_html=True)

# ═══ LIVE DETECTION ═══
elif page=="live":
    st.markdown(f'<div class="alert-g"><span class="live-dot"></span><span style="color:#22C55E;font-size:12px;font-weight:600;">Logged in as: <b>{uname}</b> — detections saved under your account</span></div>',unsafe_allow_html=True)
    cl,cr=st.columns([3,2])
    with cl:
        st.markdown('<div class="sh">Camera Controls</div>',unsafe_allow_html=True)
        cam_running=st.session_state.cam_pid is not None
        if cam_running:
            st.markdown('<div class="alert-g"><span class="live-dot"></span><span style="color:#22C55E;font-size:12px;">Camera RUNNING</span></div>',unsafe_allow_html=True)
        cc1,cc2=st.columns(2)
        with cc1:
            if st.button("▶  Start Camera",type="primary",use_container_width=True,disabled=cam_running):
                if not st.session_state.cam_started:
                    st.session_state.cam_started=True
                    env=os.environ.copy(); env["HAR_USERNAME"]=uname
                    proc=subprocess.Popen([sys.executable,"real_time.py"],env=env)
                    st.session_state.cam_pid=proc.pid
                    st.success(f"Camera started for: {uname}"); st.rerun()
        with cc2:
            if st.button("⏹  Stop Camera",use_container_width=True,disabled=not cam_running):
                try:
                    import signal; os.kill(st.session_state.cam_pid,signal.SIGTERM)
                except: pass
                st.session_state.cam_pid=None; st.session_state.cam_started=False
                st.success("Camera stopped"); st.rerun()

        st.markdown(f"""<div class="alert-w" style="margin-top:16px;">
        <div style="color:#F59E0B;font-size:12px;font-weight:600;margin-bottom:6px;">🌐 Browser Camera (Recommended)</div>
        <div style="color:#5A7090;font-size:12px;">For best results on any device, use the browser camera page:<br>
        <a href="https://har-ai-platform.vercel.app" target="_blank" style="color:#14B8A6;">har-ai-platform.vercel.app →</a></div>
        </div>""",unsafe_allow_html=True)

        for title,body in [
            ("📷 Camera position","Stand 1.5–3m away. Full body head to hip must be visible."),
            ("🍹 Drinking vs Eating","Hold pose 4+ seconds. Drinking = elbow down. Eating = elbow out."),
            ("⏳ First prediction","Takes 4–5 seconds — model needs 60 frames before predicting.")]:
            st.markdown(f'<div class="alert-w" style="margin-bottom:6px;"><div style="color:#F59E0B;font-size:11px;font-weight:600;margin-bottom:3px;">{title}</div><div style="color:#5A7090;font-size:11px;">{body}</div></div>',unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="sh">Detection Settings</div>',unsafe_allow_html=True)
        for k,v in [("Confidence threshold","80%"),("Smoothing window","20 frames"),
                    ("Drinking threshold","90%"),("Exercise / Fighting","85%"),
                    ("First prediction delay","~4 seconds"),("Save interval","Every 3 sec")]:
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:7px 12px;background:#0D1520;border-radius:6px;margin-bottom:3px;border:1px solid #1A2535;"><span style="font-size:11px;color:#2D3E55;">{k}</span><span style="font-family:monospace;font-size:10px;color:#14B8A6;">{v}</span></div>',unsafe_allow_html=True)

# ═══ MY ACTIVITY ═══
elif page=="history":
    df=load_df(uname)
    if df.empty:
        st.markdown('<div class="alert-w"><span style="color:#F59E0B;">No activity recorded yet.</span></div>',unsafe_allow_html=True)
        st.stop()

    k1,k2,k3,k4=st.columns(4)
    for col,lbl,val,c in [(k1,"RECORDS",f"{len(df):,}","#22C55E"),
                           (k2,"AVG CONF",f"{df['Confidence'].mean()*100:.1f}%","#14B8A6"),
                           (k3,"ACTIVITIES",str(df["Activity"].nunique()),"#A78BFA"),
                           (k4,"LATEST",df["Time"].max().strftime("%H:%M"),"#F59E0B")]:
        col.markdown(f'<div class="kpi" style="--a:{c}"><div class="kpi-l">{lbl}</div><div class="kpi-v" style="font-size:22px">{val}</div></div>',unsafe_allow_html=True)

    ch1,ch2=st.columns(2)
    with ch1:
        counts=df["Activity"].value_counts()
        fig,ax=dark_fig((5.5,3.2))
        ax.bar(counts.index,counts.values,color=PAL[:len(counts)],edgecolor="none",width=0.6)
        style_ax(ax); ax.tick_params(rotation=25,labelsize=8)
        plt.tight_layout(); st.pyplot(fig); plt.close(fig)
    with ch2:
        fig2,ax2=dark_fig((5.5,3.2))
        ds=df.sort_values("Time")
        ax2.plot(ds["Time"],ds["Confidence"],color="#14B8A6",linewidth=1,alpha=0.8)
        ax2.fill_between(ds["Time"],ds["Confidence"],alpha=0.06,color="#14B8A6")
        ax2.axhline(0.80,color="#F59E0B",linestyle="--",linewidth=0.8)
        ax2.set_ylim(0,1.05); style_ax(ax2); ax2.tick_params(rotation=20,labelsize=7)
        plt.tight_layout(); st.pyplot(fig2); plt.close(fig2)

    st.markdown('<div class="sh">All My Records</div>',unsafe_allow_html=True)
    disp=df[["ID","Time","Activity","Confidence"]].copy()
    disp["Conf%"]=(disp["Confidence"]*100).round(1)
    disp["Time"]=disp["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    disp=disp.drop(columns="Confidence").sort_values("Time",ascending=False)
    st.dataframe(disp,use_container_width=True,hide_index=True,height=400,
        column_config={"Conf%":st.column_config.ProgressColumn("Conf%",min_value=0,max_value=100,format="%.1f%%")})

    e1,e2=st.columns(2)
    with e1:
        st.download_button("📥 Download CSV",df.to_csv(index=False).encode(),
            f"activity_{uname}.csv",use_container_width=True,mime="text/csv")
    with e2:
        if st.button("📄 Generate PDF",use_container_width=True,type="primary"):
            with st.spinner("Building PDF..."):
                try:
                    pdf=generate_pdf_report(df)
                    st.download_button("⬇️ Download PDF",pdf,
                        f"report_{uname}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",use_container_width=True)
                except Exception as e: st.error(f"PDF error: {e}")

# ═══ USER MONITOR (admin only) ═══
elif page=="users":
    if not is_admin: st.error("Admin access required."); st.stop()

    tab1,tab2=st.tabs(["📋 Registered Users (from Vercel)","📊 Activity by User"])

    with tab1:
        st.markdown('<div class="sh">Users who registered on Vercel camera page</div>',unsafe_allow_html=True)
        reg=get_registered_users()
        if reg:
            rdf=pd.DataFrame(reg,columns=["ID","Name","Mobile","Registered","Last Seen"])
            # KPIs
            ka,kb,kc=st.columns(3)
            ka.markdown(f'<div class="kpi" style="--a:#60A5FA"><div class="kpi-l">TOTAL REGISTERED</div><div class="kpi-v" style="font-size:24px">{len(rdf)}</div></div>',unsafe_allow_html=True)
            # active today
            today=datetime.now().strftime("%Y-%m-%d")
            active_today=rdf[rdf["Last Seen"].str.startswith(today)].shape[0]
            kb.markdown(f'<div class="kpi" style="--a:#22C55E"><div class="kpi-l">ACTIVE TODAY</div><div class="kpi-v" style="font-size:24px">{active_today}</div></div>',unsafe_allow_html=True)
            kc.markdown(f'<div class="kpi" style="--a:#F59E0B"><div class="kpi-l">LATEST USER</div><div class="kpi-v" style="font-size:18px">{rdf.iloc[0]["Name"] if len(rdf)>0 else "—"}</div></div>',unsafe_allow_html=True)
            st.markdown('<div class="sh">All Registered Users</div>',unsafe_allow_html=True)
            st.dataframe(rdf,use_container_width=True,hide_index=True,height=400)
            st.download_button("📥 Download Users CSV",rdf.to_csv(index=False).encode(),
                "registered_users.csv",use_container_width=True,mime="text/csv")
        else:
            st.markdown('<div class="alert-w"><span style="color:#F59E0B;">No users registered yet. Share the Vercel link for users to register.</span></div>',unsafe_allow_html=True)
            st.markdown(f"""<div style="background:#0D1520;border:1px solid #14B8A6;border-radius:10px;padding:16px 20px;margin-top:12px;">
            <div style="font-size:12px;color:#2D3E55;margin-bottom:6px;">Share this link with users:</div>
            <div style="font-family:monospace;font-size:14px;color:#14B8A6;">https://har-ai-platform.vercel.app</div>
            </div>""",unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="sh">Activity records grouped by user</div>',unsafe_allow_html=True)
        raw_all=get_history_with_users()
        if raw_all:
            df_all=pd.DataFrame(raw_all,columns=["ID","Username","Mobile","Activity","Confidence","Time"])
            df_all["Activity"]=df_all["Activity"].apply(norm)
            df_all=df_all[~df_all["Activity"].isin(["Show full body...","..."])]
            df_all["Time"]=pd.to_datetime(df_all["Time"])

            # Risk check
            risk_all=df_all[df_all["Activity"].isin(RISK)]
            if not risk_all.empty:
                st.components.v1.html(SIREN,height=0)
                st.markdown(f'<div class="alert-r si"><span style="color:#EF4444;font-family:monospace;font-size:12px;font-weight:700;">⚠ RISK — Users: {", ".join(risk_all["Username"].unique())}</span></div>',unsafe_allow_html=True)

            # Summary KPIs
            ka,kb,kc,kd=st.columns(4)
            for col,lbl,val,c in [
                (ka,"TOTAL RECORDS",f"{len(df_all):,}","#22C55E"),
                (kb,"UNIQUE USERS",str(df_all["Username"].nunique()),"#60A5FA"),
                (kc,"UNIQUE MOBILES",str(df_all["Mobile"].nunique()),"#A78BFA"),
                (kd,"AVG CONFIDENCE",f"{df_all['Confidence'].mean()*100:.1f}%","#F59E0B")]:
                col.markdown(f'<div class="kpi" style="--a:{c}"><div class="kpi-l">{lbl}</div><div class="kpi-v" style="font-size:22px">{val}</div></div>',unsafe_allow_html=True)

            # Per-user expanders
            summary=get_user_summary()
            for row in summary:
                su_name,su_mobile,su_count,su_last=row
                with st.expander(f"👤 {su_name}  |  📱 {su_mobile}  |  {su_count} records  |  Last: {su_last}",expanded=False):
                    su_df=df_all[df_all["Mobile"]==su_mobile].copy() if su_mobile else df_all[df_all["Username"]==su_name].copy()
                    if not su_df.empty:
                        sc1,sc2,sc3=st.columns(3)
                        sc1.metric("Records",len(su_df))
                        sc2.metric("Avg Confidence",f"{su_df['Confidence'].mean()*100:.1f}%")
                        sc3.metric("Most Common",su_df["Activity"].mode()[0])
                        counts=su_df["Activity"].value_counts()
                        fig,ax=dark_fig((6,2.2))
                        ax.barh(counts.index[::-1],counts.values[::-1],color=PAL[:len(counts)],height=0.5,edgecolor="none")
                        style_ax(ax); plt.tight_layout(); st.pyplot(fig); plt.close(fig)
                        disp=su_df[["Time","Activity","Confidence"]].copy()
                        disp["Conf%"]=(disp["Confidence"]*100).round(1)
                        disp["Time"]=disp["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
                        st.dataframe(disp.drop(columns="Confidence").sort_values("Time",ascending=False),
                                    use_container_width=True,hide_index=True,height=220)

            # Full table
            st.markdown('<div class="sh">All Records — All Users</div>',unsafe_allow_html=True)
            disp_all=df_all[["Time","Username","Mobile","Activity","Confidence"]].copy()
            disp_all["Conf%"]=(disp_all["Confidence"]*100).round(1)
            disp_all["Time"]=disp_all["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
            st.dataframe(disp_all.drop(columns="Confidence").sort_values("Time",ascending=False),
                        use_container_width=True,hide_index=True,height=400,
                column_config={"Conf%":st.column_config.ProgressColumn("Conf%",min_value=0,max_value=100,format="%.1f%%")})
            st.download_button("📥 Download All CSV",df_all.to_csv(index=False).encode(),
                "all_users_activity.csv",use_container_width=True,mime="text/csv")
        else:
            st.info("No activity data yet.")

# ═══ MODEL PERFORMANCE ═══
elif page=="performance":
    m=read_metrics()
    if not m: st.warning("Run `python test_model.py` to generate metrics.")
    else:
        cols=st.columns(5)
        for col,lbl,key,color,sub in [
            (cols[0],"ACCURACY","Accuracy","#22C55E","Test set"),
            (cols[1],"WEIGHTED F1","F1","#14B8A6","Final"),
            (cols[2],"MACRO F1","F1_macro","#14B8A6","Equal weight"),
            (cols[3],"TOP-2 ACC","Top2_accuracy","#F59E0B","In top 2"),
            (cols[4],"AVG CONF","Avg_confidence","#F59E0B","Mean")]:
            col.markdown(f'<div class="kpi" style="--a:{color}"><div class="kpi-l">{lbl}</div><div class="kpi-v">{m.get(key,0)*100:.2f}%</div><div class="kpi-s">{sub}</div></div>',unsafe_allow_html=True)
    try:
        cm=np.load("confusion.npy"); classes=np.load("classes.npy",allow_pickle=True)
        cl,cr=st.columns([3,2])
        with cl:
            fig,ax=plt.subplots(figsize=(7,5.5))
            fig.patch.set_facecolor("#0D1520"); ax.set_facecolor("#0D1520")
            cm_n=cm.astype(float)/(cm.sum(axis=1,keepdims=True)+1e-8)
            sns.heatmap(cm_n,annot=cm,fmt="d",cmap=sns.color_palette("rocket_r",as_cmap=True),
                        xticklabels=[norm(c) for c in classes],yticklabels=[norm(c) for c in classes],
                        linewidths=0.5,linecolor="#070A0F",ax=ax,vmin=0,vmax=1,
                        cbar_kws={"shrink":.75,"pad":.02})
            ax.set_xlabel("Predicted",color="#2D3E55",fontsize=10)
            ax.set_ylabel("Actual",color="#2D3E55",fontsize=10)
            ax.tick_params(colors="#2D3E55",labelsize=8,rotation=30)
            plt.tight_layout(); st.pyplot(fig); plt.close(fig)
        with cr:
            rows=[]
            for i,cls in enumerate(classes):
                tp=cm[i,i]; fn=cm[i,:].sum()-tp; fp=cm[:,i].sum()-tp
                pr=tp/(tp+fp+1e-8); rc=tp/(tp+fn+1e-8); f1c=2*pr*rc/(pr+rc+1e-8)
                rows.append({"Class":norm(cls),"Prec":f"{pr:.3f}","Rec":f"{rc:.3f}","F1":f"{f1c:.3f}"})
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True,height=260)
    except: st.info("Run test_model.py to generate confusion matrix.")

# ═══ ADMIN PANEL ═══
elif page=="admin":
    if not is_admin: st.error("Admin access required."); st.stop()
    tab1,tab2,tab3,tab4=st.tabs(["👥 Users","📋 Records","🔑 Passwords","🖥 System"])

    with tab1:
        st.markdown('<div class="sh">Dashboard Users (login accounts)</div>',unsafe_allow_html=True)
        try:
            conn=sqlite3.connect("users.db")
            udf=pd.read_sql("SELECT id,username FROM users",conn); conn.close()
            st.dataframe(udf,use_container_width=True,hide_index=True,height=180)
        except Exception as e: st.warning(f"Could not load users: {e}")
        st.divider()
        ua1,ua2=st.columns(2)
        with ua1:
            st.markdown("**Add user**")
            nu=st.text_input("Username",key="nu"); np_=st.text_input("Password",type="password",key="np_")
            if st.button("✅ Create",type="primary",key="cu"):
                if nu and np_:
                    if register(nu,np_): st.success(f"'{nu}' created"); st.rerun()
                    else: st.error(f"'{nu}' exists")
                else: st.warning("Fill both fields")
        with ua2:
            st.markdown("**Remove user**")
            ulist=[u for u in list_users() if u!="admin"]
            if ulist:
                du=st.selectbox("Select",ulist,key="du")
                if st.button("🗑 Remove",type="primary",key="ru"):
                    if delete_user(du): st.success(f"Removed '{du}'"); st.rerun()
            else: st.info("No non-admin users")

    with tab2:
        st.markdown('<div class="sh">Activity Records</div>',unsafe_allow_html=True)
        raw=get_history_with_users()
        if raw:
            da=pd.DataFrame(raw,columns=["ID","Username","Mobile","Activity","Confidence","Time"])
            st.dataframe(da,use_container_width=True,hide_index=True,height=250)
            st.divider()
            da1,da2,da3=st.columns(3)
            with da1:
                did=st.number_input("Delete ID",min_value=1,step=1,key="did")
                if st.button("🗑 Delete",type="primary",key="dr"):
                    delete_record(int(did)); st.success("Deleted"); st.rerun()
            with da2:
                clu=st.selectbox("Clear user records",["— select —"]+list_users(),key="clu")
                if st.button("🗑 Clear User",key="clu_btn"):
                    if clu!="— select —":
                        clear_user(clu); st.success(f"Cleared '{clu}'"); st.rerun()
            with da3:
                if st.button("🗑 Clear ALL Records",key="ca"):
                    clear_all(); st.success("All cleared"); st.rerun()
        else: st.info("No records yet.")

    with tab3:
        cp_u=st.selectbox("User",list_users(),key="cp_u")
        cp_n=st.text_input("New Password",type="password",key="cp_n")
        cp_c=st.text_input("Confirm",type="password",key="cp_c")
        if st.button("🔑 Change",type="primary",key="chpw"):
            if cp_n!=cp_c: st.error("Mismatch")
            elif len(cp_n)<6: st.error("Min 6 chars")
            else:
                if change_password(cp_u,cp_n): st.success(f"Changed for '{cp_u}'")

    with tab4:
        files=["classes.npy","confusion.npy","metrics.txt",
               "models/activity_model.keras","pose_landmarker.task",
               "history.db","users.db","model_utils.py","api.py"]
        rows=[{"File":f,"Status":"✅ OK" if os.path.exists(f) else "❌ MISSING",
               "Size":f"{os.path.getsize(f)/1024:.1f} KB" if os.path.exists(f) else "—"}
              for f in files]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
        env=[{"Key":"Python","Value":sys.version.split()[0]},
             {"Key":"Platform","Value":sys.platform},
             {"Key":"User","Value":uname}]
        try:
            import tensorflow as tf; env.append({"Key":"TensorFlow","Value":tf.__version__})
        except: pass
        st.dataframe(pd.DataFrame(env),use_container_width=True,hide_index=True)
        
HF_API = "https://mihir1201-poseguard-api.hf.space"

def get_history_from_api(username=None):
    """Read activity data from HF API instead of local DB"""
    try:
        url = f"{HF_API}/latest_activity"
        if username:
            url += f"?username={username}"
        r = requests.get(url, timeout=5)
        return r.json()
    except:
        return {}