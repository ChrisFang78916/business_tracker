import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO

st.set_page_config(page_title="每日營業額紀錄", layout="centered")

# 右上角版本資訊
st.markdown(
    """
    <div style="text-align:right; color:gray; font-size:14px;">
        2025/11/13 v1
    </div>
    """,
    unsafe_allow_html=True
)
st.title("📊 家用營業額記帳系統")

# 初始化資料表
if "daily_data" not in st.session_state:
    st.session_state.daily_data = pd.DataFrame(columns=["日期", "營業額", "花費"])
if "monthly_data" not in st.session_state:
    st.session_state.monthly_data = pd.DataFrame(columns=[
        "月份", "店租", "水電瓦斯費", "Foodpanda", "UberEats", "賣貨便"
    ])
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ==========================
# 每日輸入區
# ==========================
st.header("🗓️ 每日資料輸入")

col1, col2, col3 = st.columns(3)
with col1:
    today = st.date_input("日期", value=date.today())
with col2:
    revenue = st.number_input("營業額", min_value=0, step=100)
with col3:
    expense = st.number_input("花費", min_value=0, step=100)

if st.session_state.edit_index is not None:
    st.info(f"✏️ 正在修改第 {st.session_state.edit_index + 1} 筆資料，修改後請按『更新資料』。")

colA, colB = st.columns(2)
with colA:
    if st.button("💾 儲存今日資料"):
        new_row = pd.DataFrame([[today, revenue, expense]], columns=["日期", "營業額", "花費"])
        st.session_state.daily_data = pd.concat([st.session_state.daily_data, new_row], ignore_index=True)
        st.success("已儲存！")

with colB:
    if st.session_state.edit_index is not None:
        if st.button("✅ 更新資料"):
            idx = st.session_state.edit_index
            st.session_state.daily_data.at[idx, "日期"] = today
            st.session_state.daily_data.at[idx, "營業額"] = revenue
            st.session_state.daily_data.at[idx, "花費"] = expense
            st.session_state.edit_index = None
            st.success("資料已更新！")

st.write("### 📅 每日紀錄")

if len(st.session_state.daily_data) > 0:
    df = st.session_state.daily_data.reset_index(drop=True)
    for i, row in df.iterrows():
        cols = st.columns([3, 2, 2, 1, 1])
        cols[0].write(str(row["日期"]))
        cols[1].write(f"💰 {int(row['營業額'])}")
        cols[2].write(f"💸 {int(row['花費'])}")
        if cols[3].button("✏️ 修改", key=f"edit_{i}"):
            st.session_state.edit_index = i
            st.experimental_rerun()
        if cols[4].button("🗑️ 刪除", key=f"delete_{i}"):
            st.session_state.daily_data = st.session_state.daily_data.drop(i).reset_index(drop=True)
            st.success(f"已刪除第 {i+1} 筆資料！")
            st.experimental_rerun()
else:
    st.write("目前沒有每日紀錄。")

# ==========================
# 月度收入支出
# ==========================
st.header("📆 月度收入支出")

month = st.selectbox("選擇月份", [f"{i}月" for i in range(1, 13)])
rent = st.number_input("店租", min_value=0, step=1000)
utility = st.number_input("水電瓦斯費", min_value=0, step=500)
fp = st.number_input("Foodpanda 收入", min_value=0, step=500)
ue = st.number_input("UberEats 收入", min_value=0, step=500)
mhb = st.number_input("賣貨便 收入", min_value=0, step=500)

if st.button("💾 儲存月度資料"):
    if month in st.session_state.monthly_data["月份"].values:
        st.session_state.monthly_data.loc[st.session_state.monthly_data["月份"] == month,
                                          ["店租", "水電瓦斯費", "Foodpanda", "UberEats", "賣貨便"]] = [rent, utility, fp, ue, mhb]
        st.info(f"已更新 {month} 的月度資料。")
    else:
        new_row = pd.DataFrame([[month, rent, utility, fp, ue, mhb]], columns=[
            "月份", "店租", "水電瓦斯費", "Foodpanda", "UberEats", "賣貨便"
        ])
        st.session_state.monthly_data = pd.concat([st.session_state.monthly_data, new_row], ignore_index=True)
        st.success("已儲存！")

st.write("### 📊 月度收入支出資料")
st.dataframe(st.session_state.monthly_data)

# ==========================
# 盈餘報表
# ==========================
st.header("💰 月盈餘報表")

if len(st.session_state.daily_data) > 0:
    st.session_state.daily_data["月份"] = pd.to_datetime(st.session_state.daily_data["日期"]).dt.month.astype(str) + "月"
    monthly_sum = st.session_state.daily_data.groupby("月份")[["營業額", "花費"]].sum().reset_index()

    report = pd.merge(monthly_sum, st.session_state.monthly_data, on="月份", how="left").fillna(0)
    report["外送收入總和"] = report["Foodpanda"] + report["UberEats"] + report["賣貨便"]
    report["盈餘"] = report["營業額"] + report["外送收入總和"] - report["花費"] - report["店租"] - report["水電瓦斯費"]

    st.dataframe(report[["月份", "營業額", "花費", "店租", "水電瓦斯費", "外送收入總和", "盈餘"]])

    # ==========================
    # 年度總結
    # ==========================
    st.subheader("📅 全年總結")
    total_revenue = report["營業額"].sum()
    total_expense = report["花費"].sum()
    total_rent = report["店租"].sum()
    total_utility = report["水電瓦斯費"].sum()
    total_delivery = report["外送收入總和"].sum()
    total_profit = report["盈餘"].sum()

    st.write(f"**全年營業總額：** {total_revenue:,.0f} 元")
    st.write(f"**全年花費總額：** {total_expense:,.0f} 元")
    st.write(f"**全年店租＋水電瓦斯：** {total_rent + total_utility:,.0f} 元")
    st.write(f"**全年外送平台收入：** {total_delivery:,.0f} 元")
    st.write(f"### 💵 全年總盈餘：{total_profit:,.0f} 元")

    # 下載 Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="營業報表")
        return output.getvalue()

    excel_data = to_excel(report)
    st.download_button(
        label="⬇ 下載Excel報表",
        data=excel_data,
        file_name="monthly_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.write("目前尚無每日資料可生成報表。")

