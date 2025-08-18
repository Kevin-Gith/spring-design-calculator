import streamlit as st
import math
from datetime import datetime

# ---------- 固定參數 ----------
def frange(start, stop, step):
    while start <= stop:
        yield round(start, 2)
        start += step

# ---------- Streamlit 頁面設定 ----------
st.set_page_config(page_title="彈簧組合計算器", page_icon="🧮")
st.title("🧮 彈簧組合計算器")

# ---------- 密碼保護 ----------
if "password_verified" not in st.session_state:
    st.session_state.password_verified = False

if not st.session_state.password_verified:
    password = st.text_input("請輸入密碼", type="password", key="pw_input")
    if st.button("🔓 登入"):
        if password == "admin-kipo$$$":
            st.session_state.password_verified = True
            st.success("密碼正確！")
            st.rerun()  # ✅ 新版 Streamlit 用法
        else:
            st.error("密碼錯誤，請重新輸入")
else:
    # ---------- 表單輸入 ----------
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
        st.subheader("📝 目前輸入參數")
        st.write(f"CPU長度：{L} mm  \nCPU寬度：{W} mm  \n彈簧鋼性模數：{G} kgf/mm²  \n螺絲行程：{SS} mm  \nSpring Room Unlock：{SRU} mm  \n螺絲桿徑：{SSD} mm  \n螺絲頭徑：{SHD} mm  \n晶片最大負載：{CPSI} lbf/in²  \n螺絲數量：{SNN} pcs  \n顯示組合數量：{N} 組")

        PSI_lower = CPSI * 0.9
        PSI_upper = CPSI * 1.1
        valid_combinations = []

        for WD in frange(0.2, 1.0, 0.1):
            ID_min = round(SSD + 0.01, 2)
            ID_max = round(SHD - 0.01, 2)
            for ID in frange(ID_min, ID_max, 0.1):
                for SN in frange(3, 20, 1):
                    NC = round(SN - 2, 2)
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

                        within_PSI = PSI_lower <= PSI <= PSI_upper
                        within_SPP = SPP < 2.5
                        valid_SP = SP > 0
                        compress_ok = SL >= FL*0.75

                        score = sum([within_PSI, valid_SP, within_SPP, compress_ok])
                        notes = []
                        if not within_PSI:
                            notes.append(f"PSI超出範圍 → {PSI} lbf/in²")
                        if not valid_SP:
                            notes.append(f"預壓不足 → {SP} mm")
                        if not within_SPP:
                            notes.append(f"節距過大 → {SPP} mm")
                        if not compress_ok:
                            notes.append(f"壓縮不足 → 自由長度：{FL} mm, 密實高度：{SL} mm")

                        if score >= 2:
                            valid_combinations.append({
                                "線徑": WD, "內徑": ID, "外徑": OD, "中心徑": MD,
                                "總圈數": SN, "有效圈數": NC, "自由長度": FL, "密實高度": SL,
                                "預壓": SP, "節距": SPP, "Spring Room Locked": SRU - SS,
                                "行程": ST, "壓縮確認": SCC, "行程壓力": DF,
                                "模組總壓力(kgf)": TFK, "模組總壓力(lbf)": TFL,
                                "晶片負載": PSI, "評分": score, 
                                "不符合原因": notes if notes else ["無"]
                            })

        if not valid_combinations:
            st.warning("❌ 沒有符合條件的組合，請嘗試調整參數。")
        else:
            valid_combinations.sort(key=lambda x: -x['評分'])
            available = len(valid_combinations)
            st.success(f"✅ 找到 {available} 組符合條件的組合。顯示前 {min(N, available)} 組：")

            for i, combo in enumerate(valid_combinations[:N]):
                stars_display = "★" * combo['評分']
                with st.expander(f"第 {i+1} 組組合（滿足條件：{stars_display}）", expanded=True):
                    st.write(f"線徑 (WD)：{combo['線徑']} mm")
                    st.write(f"內徑 (ID)：{combo['內徑']} mm")
                    st.write(f"外徑 (OD)：{combo['外徑']} mm")
                    st.write(f"中心徑 (MD)：{combo['中心徑']} mm")
                    st.write(f"總圈數 (SN)：{combo['總圈數']} laps")
                    st.write(f"有效圈數 (NC)：{combo['有效圈數']} laps")
                    st.write(f"自由長度 (FL)：{combo['自由長度']} mm")
                    st.write(f"密實高度 (SL)：{combo['密實高度']} mm")
                    st.write(f"預壓 (SP)：{combo['預壓']} mm")
                    st.write(f"節距 (SPP)：{combo['節距']} mm")
                    st.write(f"Spring Room Locked：{combo['Spring Room Locked']} mm")
                    st.write(f"行程 (ST)：{combo['行程']} mm")
                    st.write(f"壓縮確認 (SCC)：{combo['壓縮確認']} mm")
                    st.write(f"行程壓力 (DF)：{combo['行程壓力']} kgf")
                    st.write(f"模組總壓力 (TFK)：{combo['模組總壓力(kgf)']} kgf")
                    st.write(f"模組總壓力 (TFL)：{combo['模組總壓力(lbf)']} lbf")
                    st.write(f"晶片負載 (PSI)：{combo['晶片負載']} lbf/in²")

                    # ---------- 不符合條件顯示 ----------
                    if combo["不符合原因"] == ["無"]:
                        html = '<div style="background-color:#d4edda; padding:5px; border-radius:5px;">⚠ 不符合條件： 無</div>'
                    else:
                        html = f'<div style="background-color:#f8d7da; padding:5px; border-radius:5px;">⚠ 不符合條件： {"、".join(combo["不符合原因"])} </div>'
                    st.markdown(html, unsafe_allow_html=True)

        st.write("最後更新時間：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
