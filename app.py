import streamlit as st
from google import genai
from google.genai import types

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="기상 알람 챗봇",
    page_icon="🌦️",
    layout="centered"
)

st.title("🌦️ 기상 알람 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반")

# -----------------------------
# API 키 확인
# -----------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error(
        "GEMINI_API_KEY가 Secrets에 설정되지 않았습니다."
    )
    st.stop()

# Gemini 클라이언트
client = genai.Client(api_key=api_key)

# -----------------------------
# 채팅 기록 초기화
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요! 🌤️\n\n"
                "저는 기상 알람 도우미입니다.\n"
                "비, 폭염, 한파, 태풍, 미세먼지 등에 대한 "
                "알람 설정 아이디어나 안내를 도와드릴 수 있습니다."
            )
        }
    ]

# -----------------------------
# 기존 대화 출력
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# 사용자 입력
# -----------------------------
prompt = st.chat_input("질문을 입력하세요")

if prompt:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:

        # 대화 이력 구성
        conversation = []

        system_prompt = """
        당신은 기상 알람 앱의 AI 챗봇입니다.

        역할:
        - 날씨 알림 기능 설명
        - 비, 눈, 폭염, 한파, 태풍 관련 안내
        - 사용자 친화적인 답변 제공
        - 한국어로 답변

        실제 기상청 데이터가 연결되지 않은 경우
        실시간 정보를 아는 척하지 마세요.
        """

        conversation.append(
            f"시스템 지침:\n{system_prompt}\n"
        )

        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                conversation.append(f"사용자: {content}")
            elif role == "assistant":
                conversation.append(f"챗봇: {content}")

        full_prompt = "\n".join(conversation)

        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):

                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=1000,
                    )
                )

                answer = response.text

                st.markdown(answer)

        # 응답 저장
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    except Exception as e:

        error_msg = (
            "⚠️ 답변 생성 중 오류가 발생했습니다.\n\n"
            f"오류 내용: {str(e)}"
        )

        with st.chat_message("assistant"):
            st.error(error_msg)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_msg
            }
        )
