import streamlit as st
import pandas as pd
import datetime
import os

DATA_FILE = "sales_data.csv"

# 初始化資料
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["日期", "營業額", "花費", "備註"])
    df.to_csv(DATA_FILE, index=False)

# 載入資料
df = pd.read_csv(DATA_FILE)

st.title("📒 2025年營業額記錄系統")

# 輸入區
st.subheader("每日輸入")
today = datetime.date.today()
date = st.date_input("日期", today)
sales = st.number_input("今日營業額 (NT$)", min_value=0)
expense = st.number_input("今日花費 (NT$)", min_value=0)
note = st.text_input("備註（可選）")

if st.button("💾 儲存記錄"):
    new_row = pd.DataFrame([[date, sales, expense, note]], columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("已儲存！")

# 顯示紀錄
st.subheader("📊 歷史記錄")
st.dataframe(df)

# 月統計
st.subheader("📆 每月統計")
df["日期"] = pd.to_datetime(df["日期"])
df["月份"] = df["日期"].dt.to_period("M").astype(str)
summary = df.groupby("月份")[["營業額", "花費"]].sum().reset_index()
summary["淨利"] = summary["營業額"] - summary["花費"]
st.table(summary)
