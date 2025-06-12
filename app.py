#!/usr/bin/env python3

import os
import json
import datetime
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# โหลด API KEY
load_dotenv(".env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# คำนวณวันคงเหลือ
def คงเหลือก่อนเน่าเสีย(วันที่เริ่มสุก):
    วันนี้ = datetime.date.today()
    วันผ่านไป = (วันนี้ - วันที่เริ่มสุก).days
    รวมวันก่อนเน่า = 13 + 7
    return max(0, รวมวันก่อนเน่า - วันผ่านไป)

# แชตฟังก์ชันหลัก
def chatboot(question):
    system_prompt = """
คุณคือผู้เชี่ยวชาญการจำแนกความสุกของเมล่อน...

[...เดิมทั้งหมด...]

ตัวอย่าง:
User: "ค่า pH 6.2, ค่าบริกซ์ 12, ความแน่น 35N, เนื้อสีเขียว, กลิ่นหอมแรง, เก็บมาแล้ว 2 วัน"
Answer:
{
  "ripeness": "เริ่มสุก",
  "brix": 12,
  "ph": 6.2,
  "ความแน่นเนื้อ": 35,
  "อายุการเก็บรักษาก่อนเน่าเสีย": 16,
  "reason": "ข้อมูลครบทั้ง 6 มิติ พบว่า pH, Brix และความแน่นอยู่ในช่วงเริ่มสุก และเก็บมาเพียง 2 วันจึงยังมีอายุการเก็บรักษาเหลืออีก 16 วัน"
}
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()

# ----------------- UI -------------------
def main():
    st.set_page_config(page_title="AI Melon Ripeness Bot", page_icon="🍈", layout="wide")
    st.title("🍈 แชตบอตเกษตรอัจฉริยะ")
    st.subheader("ช่วยวิเคราะห์ความสุกของเมลอน ด้วย AI")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "ยินดีต้อนรับ... บรรยายลักษณะเมล่อนให้ครบ 6 มิติเพื่อประเมินความสุกได้อย่างแม่นยำ!"}
        ]

    with st.form("chat_form"):
        query = st.text_input("🗣️ คุณ:", placeholder="พิมพ์ลักษณะของเมลอน เช่น pH 6.2, Brix 10, ...").strip()
        submitted = st.form_submit_button("🚀 ส่งข้อความ")

        if submitted and query:
            answer = chatboot(query)
            st.session_state["messages"].append({"role": "user", "content": query})
            st.session_state["messages"].append({"role": "assistant", "content": answer})
        elif submitted and not query:
            st.warning("⚠️ กรุณาพิมพ์คำบรรยายก่อนส่ง")

    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"**🧑‍🌾 คุณ:** {msg['content']}")
        else:
            try:
                data = json.loads(msg["content"])
                st.markdown("#### 🤖 ผลการวิเคราะห์เมลอน")
                col1, col2 = st.columns(2)
                col1.metric("ความสุก", data.get("ripeness", "ไม่ระบุ"))
                col1.metric("ค่า Brix", data.get("brix", "ไม่ระบุ"))
                col2.metric("pH", data.get("ph", "ไม่ระบุ"))
                col2.metric("อายุเก็บรักษา", data.get("อายุการเก็บรักษาก่อนเน่าเสีย", "ไม่ระบุ"))

                if data.get("ripeness") == "ไม่สามารถพิจารณาได้":
                    st.warning("⚠️ ข้อมูลไม่ครบ: " + data.get("reason", ""))
                else:
                    st.info(data.get("reason", "ไม่มีคำอธิบาย"))
            except Exception:
                st.markdown(f"**🤖 บอท:** {msg['content']}")

    st.markdown("---")
    st.caption("🌱 พัฒนาโดยทีม Sn.Guardian gen X")

if __name__ == "__main__":
    main()
