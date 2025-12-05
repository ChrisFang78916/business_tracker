import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO

st.set_page_config(page_title="每日營業額紀錄", layout="centered")

# 右上角版本資訊
st.markdown(
    """
    <div style="text-align:right; color:gray; font-size:14px;">
        2025/11/13 v4 (月度資料已新增刪除/修改功能)
    </div>
    """,
    unsafe_allow_html=True
)
st.title("📊 家用營業額記帳系統")

# ==========================
# 初始化 session_state
# ==========================
if "daily_data" not in st.session_state or not isinstance(st.session_state.daily_data, pd.DataFrame):
    # 確保日期欄位 dtype 是 datetime64[ns]，方便後續操作
    st.session_state.daily_data = pd.DataFrame(columns=["日期", "營業額", "花費"])
if "monthly_data" not in st.session_state or not isinstance(st.session_state.monthly_data, pd.DataFrame):
    # 【修改 1：新增 "員工薪資" 欄位】
    st.session_state.monthly_data = pd.DataFrame(columns=[
        "月份", "店租", "水電瓦斯費", "員工薪資", "Foodpanda", "UberEats", "賣貨便"
    ])
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
# 新增月度編輯索引
if "monthly_edit_index" not in st.session_state:
    st.session_state.monthly_edit_index = None

# ==========================
# 每日輸入區 - 處理修改時的預填邏輯 
# ==========================
st.header("🗓️ 每日資料輸入")

# 設置預設值
initial_date = date.today()
initial_revenue = 0
initial_expense = 0

# 檢查是否在修改模式，若在，則載入舊資料
if st.session_state.edit_index is not None:
    idx = st.session_state.edit_index
    try:
        row_to_edit = st.session_state.daily_data.loc[idx]

        # 處理日期：確保 st.date_input 接收 datetime.date 類型
        date_value = row_to_edit["日期"]
        if pd.isna(date_value):
            initial_date = date.today()
        elif isinstance(date_value, pd.Timestamp):
            initial_date = date_value.date()
        elif isinstance(date_value, date):
             initial_date = date_value
        else:
             initial_date = pd.to_datetime(date_value).date()

        # 處理數字：確保 number_input 接收 int/float 類型
        initial_revenue = int(row_to_edit["營業額"]) if pd.notna(row_to_edit["營業額"]) else 0
        initial_expense = int(row_to_edit["花費"]) if pd.notna(row_to_edit["花費"]) else 0
        
    except Exception as e:
        st.error(f"載入編輯資料錯誤：{e}")
        st.session_state.edit_index = None # 出錯時退出編輯模式
        st.experimental_rerun()


col1, col2, col3 = st.columns(3)
with col1:
    # 使用 value 參數預填資料
    today = st.date_input("日期", value=initial_date)
with col2:
    # 使用 value 參數預填資料
    revenue = st.number_input("營業額", min_value=0, step=100, value=initial_revenue)
with col3:
    # 使用 value 參數預填資料
    expense = st.number_input("花費", min_value=0, step=100, value=initial_expense)

if st.session_state.edit_index is not None:
    st.info(f"✏️ 正在修改第 {st.session_state.edit_index + 1} 筆資料，修改後請按『更新資料』。")

colA, colB = st.columns(2)
with colA:
    if st.button("💾 儲存今日資料"):
        # 確保日期是 date 類型，Streamlit date_input 會返回 date 對象
        new_row = pd.DataFrame([[today, revenue, expense]], columns=["日期", "營業額", "花費"])
        st.session_state.daily_data = pd.concat([st.session_state.daily_data, new_row], ignore_index=True)
        st.success("已儲存！")

with colB:
    if st.session_state.edit_index is not None:
        if st.button("✅ 更新資料"):
            idx = st.session_state.edit_index
            # 更新資料庫中的資料
            st.session_state.daily_data.at[idx, "日期"] = today
            st.session_state.daily_data.at[idx, "營業額"] = revenue
            st.session_state.daily_data.at[idx, "花費"] = expense
            st.session_state.edit_index = None
            st.success("資料已更新！")
            # 修正：移除 st.experimental_rerun()，因為按鈕點擊已觸發 Rerun
            # st.experimental_rerun() 

# ==========================
# 每日紀錄顯示 + 修改/刪除 函數
# ==========================
st.write("### 📅 每日紀錄")

def edit_row(idx):
    st.session_state.edit_index = idx
    # 此處不需 st.experimental_rerun()，因為 button 已經會觸發 rerun

def delete_row(idx):
    if "daily_data" in st.session_state and isinstance(st.session_state.daily_data, pd.DataFrame):
        # 刪除並重設索引是正確且穩健的做法
        df = st.session_state.daily_data.drop(idx).reset_index(drop=True)
        st.session_state.daily_data = df
        st.success(f"已刪除第 {idx+1} 筆資料！")
        # 刪除後若正在編輯，需要重置 edit_index
        if st.session_state.edit_index == idx:
             st.session_state.edit_index = None
        # 修正：移除 st.experimental_rerun()

if len(st.session_state.daily_data) > 0:
    # 確保日期格式一致，避免顯示問題
    df = st.session_state.daily_data.copy()
    df['日期'] = pd.to_datetime(df['日期']).dt.date # 轉換為 date 對象以便顯示
    
    for i, row in df.iterrows():
        cols = st.columns([3, 2, 2, 1, 1])
        cols[0].write(str(row["日期"]))
        # 處理可能的 NaN/None 值，確保能轉換成 int
        rev = int(row["營業額"]) if pd.notna(row["營業額"]) else 0
        exp = int(row["花費"]) if pd.notna(row["花費"]) else 0
        cols[1].write(f"💰 {rev}")
        cols[2].write(f"💸 {exp}")
        
        # 只有在非編輯模式下才允許修改，防止多個編輯按鈕被點擊
        is_current_edit = (st.session_state.edit_index == i)
        
        # 讓修改按鈕在編輯狀態下被禁用
        if cols[3].button("✏️ 修改", key=f"edit_{i}", disabled=st.session_state.edit_index is not None and not is_current_edit):
            edit_row(i)
        
        # 刪除按鈕
        if cols[4].button("🗑️ 刪除", key=f"delete_{i}"):
            delete_row(i)
else:
    st.write("目前沒有每日紀錄。")

# ==========================
# 月度收入支出 函數
# ==========================

def edit_monthly_row(idx):
    st.session_state.monthly_edit_index = idx

def delete_monthly_row(idx):
    if "monthly_data" in st.session_state and isinstance(st.session_state.monthly_data, pd.DataFrame):
        # 刪除並重設索引是正確且穩健的做法
        df = st.session_state.monthly_data.drop(idx).reset_index(drop=True)
        st.session_state.monthly_data = df
        st.success(f"已刪除第 {idx+1} 筆月度資料！")
        # 刪除後若正在編輯，需要重置 edit_index
        if st.session_state.monthly_edit_index == idx:
             st.session_state.monthly_edit_index = None

# ==========================
# 月度輸入區 - 處理修改時的預填邏輯
# ==========================
st.header("📆 月度收入支出")

monthly_df = st.session_state.monthly_data
current_monthly_edit_index = st.session_state.monthly_edit_index
is_monthly_editing = current_monthly_edit_index is not None

# 為了讓使用者更容易編輯現有月份，我們應該先找出已儲存的月份，並將其設為預設選中
monthly_options = [f"{i}月" for i in range(1, 13)]
current_months = monthly_df["月份"].tolist()
default_month_index = 0
if len(current_months) > 0:
    if current_months[-1] in monthly_options:
        default_month_index = monthly_options.index(current_months[-1])

# 預設值
month_input = ""
current_rent = 0
current_utility = 0
current_salary = 0 # 【修改 2：新增員工薪資預設值】
current_fp = 0
current_ue = 0
current_mhb = 0

# --- 1. 載入編輯模式的資料（優先） ---
if is_monthly_editing:
    try:
        monthly_row = monthly_df.loc[current_monthly_edit_index]
        month_input = monthly_row["月份"] # 使用索引對應的月份名稱
        current_rent = int(monthly_row["店租"])
        current_utility = int(monthly_row["水電瓦斯費"])
        current_salary = int(monthly_row["員工薪資"]) # 【修改 3：載入編輯模式的薪資】
        current_fp = int(monthly_row["Foodpanda"])
        current_ue = int(monthly_row["UberEats"])
        current_mhb = int(monthly_row["賣貨便"])
    except Exception as e:
        st.error(f"載入月度編輯資料錯誤：{e}")
        st.session_state.monthly_edit_index = None
        st.experimental_rerun()
        
    st.write(f"**正在編輯月份：** `{month_input}`")
    st.info(f"✏️ 正在修改第 {current_monthly_edit_index + 1} 筆月度資料，修改後請按『更新月度資料』。")

# --- 2. 載入選擇模式的資料（非編輯時） ---
else:
    month_input = st.selectbox("選擇月份", monthly_options, index=default_month_index, key="monthly_select_box")
    if month_input in monthly_df["月份"].values:
        # 嘗試預填選定月份的月度資料
        monthly_row = monthly_df.loc[monthly_df["月份"] == month_input].iloc[0]
        current_rent = int(monthly_row["店租"])
        current_utility = int(monthly_row["水電瓦斯費"])
        current_salary = int(monthly_row["員工薪資"]) # 【修改 4：載入選擇模式的薪資】
        current_fp = int(monthly_row["Foodpanda"])
        current_ue = int(monthly_row["UberEats"])
        current_mhb = int(monthly_row["賣貨便"])


# 輸入欄位
rent = st.number_input("店租", min_value=0, step=1000, key="monthly_rent", value=current_rent)
utility = st.number_input("水電瓦斯費", min_value=0, step=500, key="monthly_utility", value=current_utility)
# 【修改 5：新增員工薪資輸入欄位】
salary = st.number_input("員工薪資", min_value=0, step=1000, key="monthly_salary", value=current_salary)
fp = st.number_input("Foodpanda 收入", min_value=0, step=500, key="monthly_fp", value=current_fp)
ue = st.number_input("UberEats 收入", min_value=0, step=500, key="monthly_ue", value=current_ue)
mhb = st.number_input("賣貨便 收入", min_value=0, step=500, key="monthly_mhb", value=current_mhb)

# 儲存/更新按鈕邏輯
colC, colD = st.columns(2)

if is_monthly_editing:
    with colC:
        if st.button("✅ 更新月度資料"):
            # 更新指定索引的資料
            monthly_df.at[current_monthly_edit_index, "月份"] = month_input
            monthly_df.at[current_monthly_edit_index, "店租"] = rent
            monthly_df.at[current_monthly_edit_index, "水電瓦斯費"] = utility
            monthly_df.at[current_monthly_edit_index, "員工薪資"] = salary # 【修改 6：更新薪資欄位】
            monthly_df.at[current_monthly_edit_index, "Foodpanda"] = fp
            monthly_df.at[current_monthly_edit_index, "UberEats"] = ue
            monthly_df.at[current_monthly_edit_index, "賣貨便"] = mhb
            st.session_state.monthly_edit_index = None
            st.success(f"月度資料已更新！")
    with colD:
        if st.button("❌ 取消編輯"):
            st.session_state.monthly_edit_index = None
            # 需要強制 Rerun 讓 Selectbox 恢復
            st.experimental_rerun()
else:
    with colC:
        if st.button("💾 儲存月度資料"):
            if month_input in monthly_df["月份"].values:
                # 若月份已存在，則更新
                # 【修改 7：更新已存在月份的資料，加入薪資欄位】
                monthly_df.loc[monthly_df["月份"] == month_input,
                                          ["店租", "水電瓦斯費", "員工薪資", "Foodpanda", "UberEats", "賣貨便"]] = [rent, utility, salary, fp, ue, mhb]
                st.info(f"已更新 {month_input} 的月度資料。")
            else:
                # 否則新增
                # 【修改 8：新增資料時，加入薪資欄位】
                new_row = pd.DataFrame([[month_input, rent, utility, salary, fp, ue, mhb]], columns=[
                    "月份", "店租", "水電瓦斯費", "員工薪資", "Foodpanda", "UberEats", "賣貨便"
                ])
                st.session_state.monthly_data = pd.concat([monthly_df, new_row], ignore_index=True)
                st.success("已儲存！")

# ==========================
# 月度紀錄顯示 + 修改/刪除
# ==========================
st.write("### 📊 月度收入支出資料")

if len(st.session_state.monthly_data) > 0:
    # 設置標題欄位
    # 【修改 9：新增 "員工薪資" 標題】
    header_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 0.5, 0.5])
    headers = ["月份", "店租", "水電瓦斯費", "員工薪資", "Foodpanda", "UberEats", "賣貨便", "修改", "刪除"]
    for hc, h in zip(header_cols, headers):
        hc.markdown(f"**{h}**")
        
    st.markdown("---")

    # 迴圈顯示資料和按鈕
    df_m = st.session_state.monthly_data
    for i, row in df_m.iterrows():
        # 9個欄位：7個數據 + 2個按鈕 (欄位數需與 header_cols 一致)
        cols = st.columns([1, 1, 1, 1, 1, 1, 1, 0.5, 0.5])
        
        # 顯示數據 (使用 :,.0f 確保格式化為千位分隔且無小數)
        cols[0].write(row["月份"])
        cols[1].write(f"{int(row['店租']):,.0f}")
        cols[2].write(f"{int(row['水電瓦斯費']):,.0f}")
        cols[3].write(f"{int(row['員工薪資']):,.0f}") # 【修改 10：顯示員工薪資數據】
        cols[4].write(f"{int(row['Foodpanda']):,.0f}")
        cols[5].write(f"{int(row['UberEats']):,.0f}")
        cols[6].write(f"{int(row['賣貨便']):,.0f}")
        
        # 動作按鈕 (索引需調整)
        is_current_edit = (st.session_state.monthly_edit_index == i)
        
        # 讓修改按鈕在編輯狀態下被禁用 (確保一次只能編輯一個)
        if cols[7].button("✏️", key=f"edit_monthly_{i}", disabled=st.session_state.monthly_edit_index is not None and not is_current_edit):
            edit_monthly_row(i)
        
        # 刪除按鈕
        if cols[8].button("🗑️", key=f"delete_monthly_{i}"):
            delete_monthly_row(i)
            
else:
    st.write("目前沒有月度紀錄。")


# ==========================
# 盈餘報表
# ==========================
st.header("💰 月盈餘報表")

if len(st.session_state.daily_data) > 0:
    # 確保 daily_data 中的日期欄位是正確的 datetime 類型
    temp_daily_df = st.session_state.daily_data.copy()
    # 這裡假設日期已經是 date/datetime/Timestamp，可以直接使用 .dt 存取器
    try:
        temp_daily_df["日期"] = pd.to_datetime(temp_daily_df["日期"])
        temp_daily_df["月份"] = temp_daily_df["日期"].dt.month.astype(str) + "月"
    except Exception as e:
        st.error(f"日期格式轉換錯誤，請檢查 daily_data 中的『日期』欄位資料：{e}")
        temp_daily_df["月份"] = ""
    
    # 避免對原始 session_state DataFrame 進行不必要修改
    monthly_sum = temp_daily_df.groupby("月份", dropna=True)[["營業額", "花費"]].sum().reset_index()

    # 將每日總結與月度費用資料合併
    report = pd.merge(monthly_sum, st.session_state.monthly_data, on="月份", how="left").fillna(0)
    
    # 確保所有數字欄位都是數值類型，避免計算錯誤
    # 【修改 11：新增 "員工薪資" 到數值欄位】
    numeric_cols = ["營業額", "花費", "店租", "水電瓦斯費", "員工薪資", "Foodpanda", "UberEats", "賣貨便"]
    for col in numeric_cols:
        report[col] = pd.to_numeric(report[col], errors='coerce').fillna(0)


    report["外送收入總和"] = report["Foodpanda"] + report["UberEats"] + report["賣貨便"]
    # 【修改 12：在盈餘計算中減去 "員工薪資"】
    report["盈餘"] = report["營業額"] + report["外送收入總和"] - report["花費"] - report["店租"] - report["水電瓦斯費"] - report["員工薪資"]

    # 【修改 13：在顯示報表時加入 "員工薪資" 欄位】
    st.dataframe(report[["月份", "營業額", "花費", "店租", "水電瓦斯費", "員工薪資", "外送收入總和", "盈餘"]])

    # ==========================
    # 年度總結
    # ==========================
    st.subheader("📅 全年總結")
    total_revenue = report["營業額"].sum()
    total_expense = report["花費"].sum()
    total_rent = report["店租"].sum()
    total_utility = report["水電瓦斯費"].sum()
    total_salary = report["員工薪資"].sum() # 【修改 14：計算全年員工薪資總和】
    total_delivery = report["外送收入總和"].sum()
    total_profit = report["盈餘"].sum()

    st.write(f"**全年營業總額：** {total_revenue:,.0f} 元")
    # 【修改 15：顯示全年店租、水電瓦斯和薪資總和】
    st.write(f"**全年花費總額：** {total_expense:,.0f} 元")
    st.write(f"**全年店租＋水電瓦斯＋員工薪資：** {total_rent + total_utility + total_salary:,.0f} 元") 
    st.write(f"**全年外送平台收入：** {total_delivery:,.0f} 元")
    st.write(f"### 💵 全年總盈餘：{total_profit:,.0f} 元")

    # 下載 Excel
    def to_excel(df):
        output = BytesIO()
        try:
            # openpyxl 雖然通常預裝在 Streamlit 環境，但加上檢查是個好習慣
            import openpyxl 
        except ImportError:
            # 在 Streamlit 環境中，通常不需要使用者額外安裝
            st.error("缺少 openpyxl 函式庫，無法生成 Excel。")
            return None
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # 報表包含計算欄位，適合匯出
            df.to_excel(writer, index=False, sheet_name="月盈餘報表")
        return output.getvalue()

    excel_data = to_excel(report)
    if excel_data:
        st.download_button(
            label="⬇ 下載Excel報表",
            data=excel_data,
            file_name="monthly_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
else:
    st.write("目前尚無每日資料可生成報表。")
