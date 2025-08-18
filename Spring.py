import math

# **自訂浮點範圍產生器**
def frange(start, stop, step):
    while start <= stop:
        yield round(start, 2)
        start += step

# **取得使用者輸入，並檢查是否合理**
def get_input(prompt, input_type=float, condition=lambda x: x > 0):
    while True:
        try:
            value = input_type(input(f"{prompt}: "))
            if condition(value):
                return round(value, 2) if isinstance(value, float) else value
            else:
                print("請重新輸入數值")
        except:
            print("請重新輸入數值")

def main():
    while True:
        print("請依序輸入以下參數：")
        L = get_input("CPU長度 (mm)")
        W = get_input("CPU寬度 (mm)")
        G = get_input("彈簧鋼性模數 (kgf/mm^2)")
        SS = get_input("螺絲行程 (mm)")
        SRU = get_input("Spring Room Unlock (mm)")
        SSD = get_input("螺絲桿徑 (mm)")
        while True:
            SHD = get_input("螺絲頭徑 (mm)", condition=lambda x: x > 0)
            if SHD > SSD:
                break
            else:
                print("螺絲桿徑需小於螺絲頭徑，請重新輸入")
        CPSI = get_input("晶片承受最大負載 (lbf/in^2)")
        SNN = get_input("螺絲數量 (pcs)", input_type=int)
        N = get_input("顯示組合數量 (groups)", input_type=int)

        # **顯示輸入參數**
        print("\n目前輸入的參數如下：")
        params = {
            "CPU長度": f"{L} mm",
            "CPU寬度": f"{W} mm",
            "彈簧鋼性模數": f"{G} kgf/mm^2",
            "螺絲行程": f"{SS} mm",
            "Spring Room Unlock": f"{SRU} mm",
            "螺絲桿徑": f"{SSD} mm",
            "螺絲頭徑": f"{SHD} mm",
            "晶片承受最大負載": f"{CPSI} lbf/in^2",
            "螺絲數量": f"{SNN} pcs",
            "顯示組合數量": f"{N} groups"
        }
        for k, v in params.items():
            print(f"{k}: {v}")

        PSI_lower = CPSI * 0.9
        PSI_upper = CPSI * 1.1
        valid_combinations = []

        # **開始遍歷各種可能的設計組合**
        for WD in [round(i, 2) for i in frange(0.2, 1.0, 0.1)]:
            ID_min = round(SSD + 0.01, 2)
            ID_max = round(SHD - 0.01, 2)
            for ID in [round(i, 2) for i in frange(ID_min, ID_max, 0.1)]:
                for SN in [round(i, 1) for i in frange(3, 20.0, 0.5)]:
                    NC = round(SN - 2, 1)
                    if NC <= 0:
                        continue

                    OD = round(ID + 2 * WD, 2)
                    MD = round(ID + WD, 2)
                    SK = round((G * (WD**4)) / (8 * (MD**3) * NC), 2)
                    SL = round((SN + 1) * WD, 2)

                    FL_min = SL + 0.1
                    FL_max = SRU + SL
                    for FL in [round(i, 2) for i in frange(FL_min, FL_max, 0.5)]:
                        SP = round(FL - SRU, 2)
                        if SP <= 0:
                            continue
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

                        # **條件檢查**
                        cond1 = (PSI_lower < PSI < PSI_upper)
                        cond2 = (SP > 0)
                        cond3 = (SPP < 2.5)
                        cond4 = (FL > SL > FL * 0.75)

                        stars = sum([cond1, cond2, cond3, cond4])
                        if stars >= 2:
                            notes = []
                            if not cond1: notes.append(f"PSI超出範圍 → {PSI} lbf/in^2")
                            if not cond2: notes.append(f"SP預壓不足 → {SP} mm")
                            if not cond3: notes.append(f"SPP過大 → {SPP} mm")
                            if not cond4: notes.append(f"壓縮不足 → 自由長度：{FL} mm, 密實高度：{SL} mm")

                            valid_combinations.append({
                                "線徑": f"{WD} mm",
                                "內徑": f"{ID} mm",
                                "外徑": f"{OD} mm",
                                "中心徑": f"{MD} mm",
                                "總圈數": f"{SN} laps",
                                "有效圈數": f"{NC} laps",
                                "自由長度": f"{FL} mm",
                                "密實高度": f"{SL} mm",
                                "預壓": f"{SP} mm",
                                "節距": f"{SPP} mm",
                                "Spring Room Locked": f"{SRL} mm",
                                "行程": f"{ST} mm",
                                "壓縮確認": f"{SCC} mm",
                                "行程壓力": f"{DF} kgf",
                                "模組總壓力(kgf)": f"{TFK} kgf",
                                "模組總壓力(lbf)": f"{TFL} lbf",
                                "晶片負載": f"{PSI} lbf/in^2",
                                "評分": "★" * stars,
                                "不符合原因": notes
                            })

        # **輸出結果**
        if len(valid_combinations) == 0:
            print("\n⚠ 無任何組合符合條件")
        else:
            valid_combinations.sort(key=lambda x: len(x["評分"]), reverse=True)
            available = len(valid_combinations)
            if available < N:
                print(f"\n⚠ 目前僅有 {available} 組合可用，請重新輸入顯示組合數量。")
            else:
                print(f"\n✅ 找到 {available} 組組合，顯示前 {N} 組最佳組合如下：\n")

            for i, combo in enumerate(valid_combinations[:min(N, available)], start=1):
                print(f"--- 第 {i} 組 ---")
                for k, v in combo.items():
                    if k != "不符合原因":
                        print(f"{k}: {v}")
                if combo["不符合原因"]:
                    print("⚠ 不符合條件：")
                    for note in combo["不符合原因"]:
                        print(note)
                else:
                    print("⚠ 不符合條件：無")
                print("")

        again = input("重新計算，請輸入 Y：").strip().upper()
        if again != "Y":
            print("已結束程式。")
            input("按下 Enter 鍵結束程式...")
            break

if __name__ == "__main__":
    main()