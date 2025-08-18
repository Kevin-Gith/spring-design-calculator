import streamlit as st
import math
from datetime import datetime

# ---------- 固定參數 ----------
G = 8000  # kgf/mm^2

# ---------- 自訂浮點範圍產生器 ----------
def frange(start, stop, step):
    while start <= stop:
        yield round(start, 2)
        start += step

# ---------- 星星得分 ----------
def score_to_stars(score):
    return '★' * score + '☆' * (4 - score)

# ---------- Streamlit 頁面設定 ----------
st.set_page_config(page_title="彈簧組合計算器", page_icon="🧮")
st.title("🧮 彈簧組合計算器")

# ---------- 密碼保護 ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("請輸入密碼", type="password")
    if password:
        if password == "admin-kipo$$$":
            st.session_state.authenticated = True
            st.success("✅ 密碼正確，請繼續操作")
            st.rerun()
        else:
            st.error("❌ 密碼錯誤，請重新輸入")
    st.stop()

# ---------- 輸入表單 ----------
with st.form("spring_form"):
    st.subheader("📌 請輸入參數")
    L = st.number_input("CPU長度 (mm)", min_value=1.0, value=25.0)
    W = st.number_input("CPU寬度 (mm)", min_value=1.0, value=25.0)
    G = st.number_input("彈簧鋼性模數 (kgf/mm²)", min_value=1.0, value=8000.0)
    SS = st.number_input("螺絲行程 (mm)", min_value=0.1, value=0.3)
    SRU = st.number_input("Spring Room Unlock (mm)", min_value=0.1, value=2.5)
    SSD = st.number_input("螺絲桿徑 (mm)", min_value=0.1, value=1.2)
    SHD = st.number_input("螺絲頭徑 (mm)", min_value=SSD + 0.01, value=2.4)
    CPSI = st.number_input("晶片承受最大負載 (lbf/in²)", min_value=1.0, value=40.0)
    SNN = st.number_input("螺絲數量 (pcs)", min_value=1, step=1, value=4)
    N = st.number_input("顯示組合數量", min_value=1, step=1, value=5)
    submitted = st.form_submit_button("🚀 開始計算")

# ---------- 計算 ----------
if submitted:
    st.subheader("📝 輸入參數確認")
    st.markdown(f"""
    - CPU長度：{L} mm  
    - CPU寬度：{W} mm  
    - 彈簧鋼性模數：{G} kgf/mm²  
    - 螺絲行程：{SS} mm  
    - Spring Room Unlock：{SRU} mm  
    - 螺絲桿徑：{SSD} mm  
    - 螺絲頭徑：{SHD} mm  
    - 晶片最大負載：{CPSI} lbf/in²  
    - 螺絲數量：{SNN} pcs  
    - 顯示組合數量：{N} 組  
    """)

    PSI_lower = CPSI * 0.9
    PSI_upper = CPSI * 1.1
    valid_combinations = []

    for WD in frange(0.2, 1.0, 0.1):
        ID_min = SSD + 0.01
        ID_max = SHD - 0.01
        for ID in frange(ID_min, ID_max, 0.1):
            for SN in frange(3, 20, 1):
                NC = SN - 2
                if NC <= 0:
                    continue
                OD = round(ID + 2*WD, 2)
                MD = round(ID + WD, 2)
                SK = round((G * WD**4) / (8 * MD**3 * NC), 2)
                SL = round((SN + 1) * WD, 2)

                FL_min = SL + 0.1
                FL_max = SRU + SL
                for FL in frange(FL_min, FL_max, 0.5):
                    SP = round(FL - SRU, 2)
                    if SP <= 0:
                        continue
                    SPP = round(FL / SN, 2)
                    ST = round(SP + SS, 2)
                    SCC = round(ST + SL, 2)
                    if SCC > FL:
                        continue
                    DF = round(ST * SK, 2)
                    TFK = round(DF * SNN, 2)
                    TFL = round(TFK * 2.2046, 2)
                    PSI = round((TFK / (L * W)) * 1421.0573, 2)

                    cond1 = PSI_lower <= PSI <= PSI_upper
                    cond2 = SP > 0
                    cond3 = SPP < 2.5
                    cond4 = SL >= FL*0.75
                    score = sum([cond1, cond2, cond3, cond4])
                    notes = []
                    if not cond1: notes.append(f"PSI超出範圍 → {PSI} lbf/in²")
                    if not cond2: notes.append(f"預壓不足 → {SP} mm")
                    if not cond3: notes.append(f"節距過大 → {SPP} mm")
                    if not cond4: notes.append(f"壓縮不足 → 自由長度：{FL} mm, 密實高度：{SL} mm")

                    if score >= 2:
                        valid_combinations.append({
                            "線徑": WD, "內徑": ID, "外徑": OD, "中心徑": MD,
                            "總圈數": SN, "有效圈數": NC, "自由長度": FL, "密實高度": SL,
                            "預壓": SP, "節距": SPP, "Spring Room Locked": SRU - SS,
                            "行程": ST, "壓縮確認": SCC, "行程壓力": DF,
                            "模組總壓力(kgf)": TFK, "模組總壓力(lbf)": TFL,
                            "晶片負載": PSI, "評分": score, "不符合原因": notes
                        })

    if not valid_combinations:
        st.warning("❌ 沒有符合條件的組合，請嘗試調整參數。")
    else:
        valid_combinations.sort(key=lambda x: -x['評分'])
        available = len(valid_combinations)
        st.success(f"✅ 找到 {available} 組符合條件的組合。顯示前 {min(N, available)} 組：")
        for i, combo in enumerate(valid_combinations[:N]):
            stars_display = score_to_stars(combo['評分'])
            with st.expander(f"第 {i+1} 組（滿足條件：{stars_display}）", expanded=True):
                for k, v in combo.items():
                    if k != "不符合原因" and k != "評分":
                        st.write(f"{k}: {v}")
                if combo["不符合原因"]:
                    st.markdown(
                        f"<div style='background-color:#fff3cd; padding:8px; border-radius:5px;'>⚠ 不符合條件：</div>",
                        unsafe_allow_html=True
                    )
                    for note in combo["不符合原因"]:
                        st.write(note)
                else:
                    st.markdown(
                        f"<div style='background-color:#d1ecf1; padding:8px; border-radius:5px;'>⚠ 不符合條件： 無</div>",
                        unsafe_allow_html=True
                    )

# ---------- 顯示最後更新時間 ----------
st.write("最後更新時間：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
