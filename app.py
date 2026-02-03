# -*- coding: utf-8 -*-
import streamlit as st
from google import genai
from PIL import Image
import sys
import io

# 1. 인코딩 에러 방지 (한글 출력 보장)
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

st.set_page_config(page_title="Civil AI Assistant", page_icon="🏗️")

# --- 사이드바 설정 ---
with st.sidebar:
    st.title("⚙️ 설정 및 보안")
    
    # 1. API 키 입력창
    user_api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...")
    st.info("입력하신 키는 서버에 저장되지 않으며 현재 세션에서만 사용됩니다.")

    # 2. API 키 발급 방법 안내 (접기/펼치기 기능)
    with st.expander("🔑 API 키 발급 방법 안내"):
        st.markdown("""        
        1. [Google AI Studio](https://aistudio.google.com/)에 접속합니다.
        2. **Get API key** 버튼을 클릭합니다.
        3. **Create API key in new project**를 선택합니다.
        4. 생성된 키를 복사하여 위 칸에 붙여넣으세요.
        """)

# --- 메인 화면 ---
st.title("🏗️ 윤동헌과 AI 조교")
st.write("문제를 업로드하세요. 풀이를 제공합니다.")

uploaded_file = st.file_uploader("문제 이미지 업로드", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='업로드된 이미지', use_container_width=True)

    if st.button("풀이"):
        if not user_api_key:
            st.warning("왼쪽 사이드바에서 API Key를 먼저 입력해 주세요!")
        else:
            try:
                # 2. 지정하신 gemini-3-flash-preview 모델로 클라이언트 설정
                client = genai.Client(api_key=user_api_key)
                
                with st.spinner("...AI는 부정확한 답변을 제공할 수 있습니다..."):
                    prompt = """
                    당신은 토목공학 기술사입니다. 
                    이미지에 포함된 문제를 분석하여 아래의 엄격한 형식을 지켜 답변하세요.

                    1. [핵심개념]: 
                    - 문제 풀이에 필요한 핵심 이론 및 공식을 요약하여 제시하세요.
                    - 핵심개념은 2문장 이내로 요약하세요.
                    - 한 문장이 끝날 때마다 줄바꿈을 하세요.
                    
                    2. [단계별 풀이]: 
                    - 각 단계는 아래의 형식을 반드시 지키며, 한 문장이 끝날 때마다 줄바꿈을 하세요.
                    
                    <1단계> 단계 제목 
                    - 단계에 대한 첫 번째 설명 문장입니다.
                    - 수식이나 계산이 포함된 두 번째 문장입니다. ($...$ 기호의 LaTeX 사용)
                    
                    <2단계> 단계 제목
                    - 다음 단계에 대한 설명입니다.
                    - 계산 과정을 한 줄씩 분리하여 작성하세요.

                    3. [최종 답]: 
                    최종 결과값을 굵은 글씨로 단위를 포함하여 제시하세요. (예: **150.50 kN/m²**)

                    주의사항:
                    - 모든 수식은 $...$ 기호를 사용하여 LaTeX 형식으로 작성하세요.
                    - 답변은 반드시 한국어로 작성하세요.
                    - 모든 답변에서 각 문장은 가독성을 위해 짧고 명확하게 끊어서 작성하세요.
                    - "~합니다.", "~입니다."로 끝나는 문장을 사용하지 마세요.
                    - "~이다.", "~다."로 끝나는 문장을 사용하세요.
                    - "<n단계>"와 "단계 제목"은 볼드체로 작성하세요.

                    """
                    
                    # 지시하신 모델명 고정
                    response = client.models.generate_content(
                        model="gemini-3-flash-preview",
                        contents=[prompt, image]
                    )
                    
                    st.success("풀이가 완료되었습니다!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error("풀이 중 오류가 발생했습니다.")
                # 모델명이 존재하지 않거나 권한이 없을 경우 에러 메시지 출력
                st.caption(f"상세 에러 내용: {e}")

# --- 하단 안내 ---
st.caption("© 2026 Civil AI TA - Powered by Gemini 3 Flash Preview")