import itertools
import math
import streamlit as st

# 👉 密碼登入驗證
def check_password():
    def password_entered():
        if st.session_state["password"] == "admin_kipo":  # 設定密碼
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("請輸入密碼", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("請輸入密碼", type="password", on_change=password_entered, key="password")
        st.error("密碼錯誤，請再試一次。")
        st.stop()

check_password()  # ⬅️ 密碼驗證加在這裡

# 固定參數
G = 8000  # kgf/mm^2

def frange(start, stop, step):
    while start <= stop:
        yield round(start, 2)
        start += step

st.set_page_config(page_title="彈簧組合計算器", page_icon="🧮")
st.title("🧮 彈簧組合計算器")

with st.form("spring_form"):
    st.subheader("📌 請輸入參數")
    L = st.number_input("CPU 長度", min_value=1.0, value=25.0)
    W = st.number_input("CPU 寬度", min_value=1.0, value=25.0)
    SS = st.number_input("螺絲行程", min_value=0.1, value=0.3)
    SRU = st.number_input("Spring Room Unlock", min_value=0.1, value=2.5)
    SSD = st.number_input("螺絲桿徑", min_value=0.1, value=1.2)
    SHD = st.number_input("螺絲頭徑", min_value=SSD + 0.01, value=2.4)
    CPSI = st.number_input("晶片承受最大負載 (lbf/in²)", min_value=1.0, value=40.0)
    SNN = st.number_input("螺絲數量", min_value=1, step=1, value=4)
    N = st.number_input("顯示組合數量", min_value=1, step=1, value=5)

    submitted = st.form_submit_button("🚀 開始計算")

def score_to_stars(score):
    # 確保得分範圍為 0 到 4
    score = max(0, min(score, 4))
    return '★' * score + '☆' * (4 - score)

if submitted:
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
                OD = round(ID + 2 * WD, 2)
                MD = round(ID + WD, 2)
                SK = round((G * (WD**4)) / (8 * (MD**3) * NC), 2)
                SL = round((SN + 1) * WD, 2)

                FL_min = SL + 0.1
                FL_max = SRU + SL
                for FL in frange(FL_min, FL_max, 0.5):
                    SP = round(FL - SRU, 2)
                    if SP <= 0:
                        continue  # 只處理正數的 SP
                    SPP = round(FL / SN, 2)
                    SRL = round(SRU - SS, 2)
                    ST = round(SP + SS, 2)
                    SCC = round(ST + SL, 2)
                    if SCC > FL:
                        continue
                    DF = round(ST * SK, 2)
                    TFK = round(DF * SNN, 2)
                    TFL = round(TFK * 2.2046, 2)
                    PSI = round((TFK / (L * W)) * 1421.0573, 2)

                    # 檢查條件
                    within_PSI = PSI_lower < PSI < PSI_upper
                    within_SPP = SPP < 2.5
                    valid_SP = SP > 0

                    score = sum([within_PSI, within_SPP, valid_SP])

                    if score >= 2:
                        notes = []
                        if not within_PSI:
                            notes.append(f"⚠ PSI超出範圍：{PSI} lbf/in²")
                        if not within_SPP:
                            notes.append(f"⚠ SPP過大：{SPP} mm")
                        if not valid_SP:
                            notes.append(f"⚠ SP不足：{SP} mm")

                        valid_combinations.append({
                            "線徑": f"{WD} mm",
                            "內徑": f"{ID} mm",
                            "圈數": f"{SN} laps",
                            "彈簧長": f"{FL} mm",
                            "預壓縮": f"{SP} mm",
                            "Pitch": f"{SPP} mm",
                            "螺絲佔空間": f"{SCC} mm",
                            "總彈力": f"{TFK} kgf",
                            "總彈力": f"{TFL} lbf",  # 修改這行為 "總彈力"
                            "PSI": f"{PSI} lbf/in²",
                            "Score": score,  # 直接存儲數字得分
                            "備註": notes
                        })

    if not valid_combinations:
        st.warning("❌ 沒有符合條件的組合，請嘗試調整參數。")
    else:
        # 排序：確保得分是數字，並且能正常進行排序
        valid_combinations.sort(key=lambda x: -x['Score'])

        available = len(valid_combinations)
        st.success(f"✅ 找到 {available} 組合，顯示前 {min(N, available)} 組最佳組合：")

        for i, combo in enumerate(valid_combinations[:N]):
            with st.expander(f"第 {i+1} 組組合（得分：{score_to_stars(combo['Score'])}）", expanded=True):
                st.write(f"線徑: {combo['線徑']}")
                st.write(f"內徑: {combo['內徑']}")
                st.write(f"圈數: {combo['圈數']}")
                st.write(f"彈簧長: {combo['彈簧長']}")
                st.write(f"預壓縮: {combo['預壓縮']}")
                st.write(f"Pitch: {combo['Pitch']}")
                st.write(f"螺絲佔空間: {combo['螺絲佔空間']}")
                st.write(f"總彈力: {combo['總彈力']} kgf")
                st.write(f"總彈力: {combo['總彈力']} lbf")
                st.write(f"PSI: {combo['PSI']}")
                if combo["Score"] != 4:
                    st.warning("⚠ 備註：" + "｜".join(combo["備註"]))
