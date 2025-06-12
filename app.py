#!/usr/bin/env python3

import os
import json
import streamlit as st
import datetime
from groq import Groq
from dotenv import load_dotenv

st.set_page_config(page_title="AI Melon Ripeness Bot", page_icon="🍈", layout="wide")

# โหลดตัวแปรสิ่งแวดล้อม
load_dotenv(".env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# ฟังก์ชัน: คำนวณวันคงเหลือ
def คำนวณวันคงเหลือ(จำนวนวันที่เก็บแล้ว):
    อายุรวม = 14
    try:
        วันเก็บแล้ว = int(จำนวนวันที่เก็บแล้ว)
        คงเหลือ = max(0, อายุรวม - วันเก็บแล้ว)
        return คงเหลือ
    except:
        return None

# ฟังก์ชัน: ตรวจสอบจำนวนมิติข้อมูล
def นับจำนวนมิติ(data):
    keys = ["ph", "brix", "ความแน่นเนื้อ", "สีของเนื้อเมลอน", "กลิ่นเมล่อน", "อายุการเก็บรักษาก่อนเน่าเสีย"]
    return sum(1 for k in keys if data.get(k) is not None)

# ฟังก์ชันเรียก LLM
def chatboot(question):
    system_prompt = """ 
คุณคือผู้เชี่ยวชาญการจำแนกความสุกของเมล่อน... [ย่อเพื่อความกระชับ, เหมือนเดิมที่คุณมีอยู่]
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

# UI หลัก
def main():
    st.markdown("""
        <style>
        body { background-color: #000000; }
        .stForm { background-color: #000000; padding: 2rem; border-radius: 12px; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🍈 แชตบอตเกษตรอัจฉริยะ")
    st.subheader("ช่วยวิเคราะห์ความสุกของเมลอน ด้วย AI")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "สวัสดีจ้าว น้องเป็นแชทบอตสำหรับวิเคราะห์ความสุกของเมล่อนด้วยข้อมูล 6 มิติ..."}
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

                # ✅ ตรวจจำนวนมิติที่มี
                มิติมี = นับจำนวนมิติ(data)
                if มิติมี < 3:
                    data["ripeness"] = "ไม่สามารถพิจารณาได้"
                    มิติทั้งหมด = {
                        "ph": "ค่า pH",
                        "brix": "ค่า Brix",
                        "ความแน่นเนื้อ": "ความแน่นเนื้อ",
                        "สีของเนื้อเมลอน": "สีของเนื้อเมล่อน",
                        "กลิ่นเมล่อน": "กลิ่นของเมล่อน",
                        "อายุการเก็บรักษาก่อนเน่าเสีย": "อายุการเก็บรักษา"
                    }
                    มิติที่ขาด = [ชื่อ for key, ชื่อ in มิติทั้งหมด.items() if data.get(key) is None]
                    data["reason"] = (
                        f"ข้อมูลมีเพียง {มิติมี} มิติจาก 6 มิติหลัก ไม่สามารถประเมินความสุกได้อย่างแม่นยำ "
                        f"ควรเพิ่มข้อมูลต่อไปนี้: {', '.join(มิติที่ขาด)}"
                    )

                # แสดงผล
                with st.container():
                    st.markdown("#### 🤖 ผลการวิเคราะห์เมลอน")
                    col1, col2 = st.columns(2)
                    col1.metric("ความสุก", data.get("ripeness", "ไม่ระบุ"))
                    col1.metric("ความหวาน", data.get("brix", "ไม่ระบุ"))
                    col2.metric("ความแน่นเนื้อ", data.get("ความแน่นเนื้อ", "ไม่ระบุ"))
                    col2.metric("ค่า pH", data.get("ph", "ไม่ระบุ"))
                    วันคงเหลือ = คำนวณวันคงเหลือ(data.get("อายุการเก็บรักษาก่อนเน่าเสีย"))
                    col2.metric("คงเหลือก่อนเน่าเสีย", f"{วันคงเหลือ} วัน" if วันคงเหลือ is not None else "ไม่ระบุ")
                    col2.metric("กลิ่น", data.get("กลิ่นเมล่อน", "ไม่ระบุ"))
                    col2.metric("สี", data.get("สีของเนื้อเมลอน", "ไม่ระบุ"))
                    st.info(data.get("reason", "ไม่มีคำอธิบาย"))
            except Exception:
                st.markdown(f"**🤖 อองตอง:** {msg['content']}")

    st.markdown("---")

if __name__ == "__main__":
    main()
