#!/usr/bin/env python3

import streamlit as st
st.set_page_config(page_title="AI Melon Ripeness Bot", page_icon="🍈", layout="wide")

import os
import json
from groq import Groq
from dotenv import load_dotenv
import datetime

# โหลด env
load_dotenv(".env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# ฟังก์ชันอื่นๆ และ main() ฟังก์ชันเดียว

def main():
    st.markdown("""
        <style>
        body { background-color: #000000; }
        .stForm { background-color: #000000; padding: 2rem; border-radius: 12px; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🍈 แชตบอตเกษตรอัจฉริยะ")
    st.subheader("ช่วยวิเคราะห์ความสุกของเมลอน ด้วย AI ")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "สวัสดีจ้าว น้องเป็นแชทบอตสำหรับวิเคราะห์ความสุกของเมล่อนด้วยข้อมูล6มิติ..."}
        ]

    with st.form("chat_form"):
        query = st.text_input("🗣️ คุณ:", placeholder="พิมพ์ลักษณะของเมลอนที่ต้องการให้วิเคราะห์...").strip()
        submitted = st.form_submit_button("🚀 ส่งข้อความ")

        if submitted and query:
            answer = chatboot(query)
            st.session_state["messages"].append({"role": "user", "content": query})
            st.session_state["messages"].append({"role": "assistant", "content": answer})
        elif submitted and not query:
            st.warning("⚠️ กรุณาพิมพ์คำถามก่อนส่ง")

    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"**🧑‍🌾 คุณ:** {msg['content']}")
        else:
            try:
                data = json.loads(msg["content"])
                with st.container():
                    st.markdown("#### 🤖 ผลการวิเคราะห์เมลอน")
                    col1, col2 = st.columns(2)
                    col1.metric("ความสุก", data.get("ripeness", "ไม่ระบุ"))
                    col1.metric("ค่า Brix", data.get("brix", "ไม่ระบุ"))
                    col2.metric("ค่า pH", data.get("ph", "ไม่ระบุ"))
                    col2.metric("อายุการเก็บรักษา", data.get("อายุการเก็บรักษา","ไม่ระบุ"))
                    st.info(data.get("reason", "คำอธิบายเหตุผล..."))
            except Exception:
                st.markdown(f"**🤖 บอท:** {msg['content']}")

    st.markdown("---")
    st.caption("🌱 พัฒนาโดยทีม Sn.Guardian gen X เป็นส่วนหนึ่งของโครงการบ่มเพาะนวัตกรปัญญาประดิษฐ์ (AI Innovator) 🤖")

if __name__ == "__main__":
    main()
