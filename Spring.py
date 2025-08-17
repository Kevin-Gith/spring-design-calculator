import itertools
import math

def frange(start, stop, step):
    while start <= stop:
        yield round(start, 2)
        start += step

# 固定參數
G = 8000  # kgf/mm^2

def get_input(prompt, input_type=float, condition=lambda x: x > 0):
    while True:
        try:
            value = input_type(input(f"{prompt}: "))
            if condition(value):
                return round(value, 2) if isinstance(value, float) else value
            else:
                print("螺絲桿徑需小於螺絲頭徑")
        except:
            print("請重新輸入數值")

# 星星顯示轉換
def score_to_stars(score):
    return '★' * score + '☆' * (4 - score)

def main():
    while True:
        print("請依序輸入以下參數：")
        L = get_input("CPU長度 (單位mm)")
        W = get_input("CPU寬度 (單位mm)")
        SS = get_input("螺絲行程 (單位mm)")
        SRU = get_input("Spring Room Unlock (單位mm)")
        SSD = get_input("螺絲桿徑 (單位mm)")
        SHD = get_input("螺絲頭徑 (單位mm)", condition=lambda x: x > SSD)
        CPSI = get_input("晶片承受最大負載 (單位lbf/in^2)")
        SNN = get_input("螺絲數量 (單位pcs)", input_type=int)
        N = get_input("顯示組合數量", input_type=int)

        print("\n目前輸入的參數如下：")
        params = {
            "L": f"{L} mm",
            "W": f"{W} mm",
            "SS": f"{SS} mm",
            "SRU": f"{SRU} mm",
            "SSD": f"{SSD} mm",
            "SHD": f"{SHD} mm",
            "CPSI": f"{CPSI} lbf/in^2",
            "SNN": f"{SNN} pcs",
            "N": f"{N} groups"
        }
        for k, v in params.items():
            print(f"{k}: {v}")

        PSI_lower = CPSI * 0.9
        PSI_upper = CPSI * 1.1
        valid_combinations = []

        for WD in [round(i, 2) for i in frange(0.2, 1.01, 0.1)]:
            ID_min = math.ceil((SSD + 0.01) * 10) / 10
            ID_max = math.floor((SHD - 0.01) * 10) / 10
            for ID in [round(i, 2) for i in frange(ID_min, ID_max, 0.1)]:
                for SN in [round(i, 2) for i in frange(3, 20.01, 1)]:
                    NC = round(SN - 2, 2)
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

                        # 計算密實長度
                        Solid_Length = round(SN * WD, 2)

                        condition_Solid_Length = Solid_Length >= FL * 0.75

                        # 計算符合條件的情況
                        within_PSI = PSI_lower < PSI < PSI_upper
                        within_SPP = SPP < 2.5
                        valid_SP = SP > 0

                        # 計算符合條件的總數
                        score = sum([within_PSI, within_SPP, valid_SP, condition_Solid_Length])

                        reasons = []
                        if not within_PSI:
                            reasons.append(f"PSI超出範圍: {PSI} lbf/in^2")
                        if not within_SPP:
                            reasons.append(f"SPP過大: {SPP} mm")
                        if not valid_SP:
                            reasons.append(f"SP預壓不足: {SP} mm")
                        if not condition_Solid_Length:
                            reasons.append(f"密實長度過小: {Solid_Length} mm，需不低於自由長度的 75%")

                        valid_combinations.append({
                            "WD": f"{WD} mm",
                            "ID": f"{ID} mm",
                            "SN": f"{SN} laps",
                            "FL": f"{FL} mm",
                            "SP": f"{SP} mm",
                            "SPP": f"{SPP} mm",
                            "SCC": f"{SCC} mm",
                            "TFK": f"{TFK} kgf",
                            "TFL": f"{TFL} lbf",
                            "PSI": f"{PSI} lbf/in^2",
                            "Solid Length": f"{Solid_Length} mm",
                            "Score": score_to_stars(score),  # 顯示星星
                            "Notes": reasons
                        })

        if len(valid_combinations) == 0:
            print("\n⚠ 無任何組合符合條件")
        else:
            valid_combinations.sort(key=lambda x: -x['Score'])
            available = len(valid_combinations)
            if available < N:
                print(f"\n⚠ 目前僅有 {available} 組合可用，請重新輸入顯示組合數量。")
            else:
                print(f"\n✅ 找到 {available} 組合，顯示前 {N} 組最佳組合如下：\n")

            for i, combo in enumerate(valid_combinations[:min(N, available)], start=1):
                print(f"--- 第 {i} 組 ---")
                for k, v in combo.items():
                    if k not in ["Score", "Notes"]:
                        print(f"{k}: {v}")
                print(f"得分: {combo['Score']}")  # 顯示星星得分
                if combo["Score"] == "☆ ☆ ☆ ☆":
                    print("⚠ 不符合條件：", "、".join(combo["Notes"]))
                print("")

        again = input("重新計算，請輸入 Y：").strip().upper()
        if again != "Y":
            print("已結束程式。")
            input("按下 Enter 鍵結束程式...")
            break

if __name__ == "__main__":
    main()