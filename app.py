import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="住所録・注文票アプリ", layout="centered")

st.title("住所入力・Excel保存アプリ")

# セッション状態（一時的なデータ保存）の初期化
if "data_list" not in st.session_state:
    st.session_state.data_list = []

# --- 入力フォーム ---
with st.form("input_form", clear_on_submit=True):
    st.subheader("お届け先情報入力")
    name = st.text_input("お名前")
    zipcode = st.text_input("郵便番号 (7桁)", max_chars=7)
    
    # 住所取得ボタン
    submitted_zip = st.form_submit_button("住所を検索")
    address = ""
    if zipcode:
        url = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
        res = requests.get(url).json()
        if res["results"]:
            r = res["results"][0]
            address = f"{r['address1']}{r['address2']}{r['address3']}"

    # 確定用の入力欄（自動取得した住所が表示される）
    final_address = st.text_input("住所詳細（番地など）", value=address)
    
    add_data = st.form_submit_button("リストに追加")
    
    if add_data:
        if name and final_address:
            # データをリストに追加
            new_entry = {
                "登録日時": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                "お名前": name,
                "郵便番号": zipcode,
                "住所": final_address
            }
            st.session_state.data_list.append(new_entry)
            st.success(f"{name}様のデータを追加しました。")
        else:
            st.error("お名前と住所を入力してください。")

# --- 登録データ表示とダウンロード ---
if st.session_state.data_list:
    st.subheader("登録済みデータ一覧")
    df = pd.DataFrame(st.session_state.data_list)
    st.dataframe(df)

    # Excel作成
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
