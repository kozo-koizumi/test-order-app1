import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="住所録・注文票アプリ", layout="centered")
st.title("住所入力・Excel保存アプリ")

# データ保存用のセッション
if "data_list" not in st.session_state:
    st.session_state.data_list = []
if "address_found" not in st.session_state:
    st.session_state.address_found = ""

# --- 入力エリア（フォームの外に出す） ---
st.subheader("お届け先情報入力")
name = st.text_input("お名前")
zipcode = st.text_input("郵便番号 (7桁)", max_chars=7)

# 1. 住所検索ボタン（ここをフォームから出しました）
if st.button("住所を検索"):
    if len(zipcode) == 7:
        url = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
        res = requests.get(url).json()
        if res["results"]:
            r = res["results"][0]
            st.session_state.address_found = f"{r['address1']}{r['address2']}{r['address3']}"
        else:
            st.error("住所が見つかりませんでした。")
    else:
        st.warning("郵便番号を7桁で入力してください。")

# 2. 住所の確定入力
final_address = st.text_input("住所詳細（番地など）", value=st.session_state.address_found)

# 3. 登録ボタン（ここだけフォームにするか、単独ボタンにする）
if st.button("リストに追加"):
    if name and final_address:
        new_entry = {
            "登録日時": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            "お名前": name,
            "郵便番号": zipcode,
            "住所": final_address
        }
        st.session_state.data_list.append(new_entry)
        st.success(f"{name}様のデータを追加しました。")
        # 追加後に住所をリセット
        st.session_state.address_found = ""
    else:
        st.error("お名前と住所を入力してください。")

# --- 登録データ表示とダウンロード（変更なし） ---
if st.session_state.data_list:
    st.divider()
    st.subheader("登録済みデータ一覧")
    df = pd.DataFrame(st.session_state.data_list)
    st.dataframe(df)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Orders')
    
    st.download_button(
        label="Excel形式で全データをダウンロード",
        data=output.getvalue(),
        file_name="address_list.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("リストをリセット"):
        st.session_state.data_list = []
        st.rerun()
