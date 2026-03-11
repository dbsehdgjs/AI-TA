# -*- coding: utf-8 -*-
from google.genai.types import GenerationConfig
import google.genai._interactions.types.generation_config_param
import streamlit as st
from google import genai
from PIL import Image
import sys
import io
import datetime

AImodel = "gemini-3-flash-preview"

# --- 비밀번호 설정 ---
def check_password():
    """비밀번호가 맞는지 확인하고 결과를 세션 상태에 저장합니다."""
    def password_entered():
        """입력된 비밀번호를 검증합니다."""
        if st.session_state["password"] == "3534":  # <--- 여기에 원하는 비밀번호를 입력하세요
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 보안을 위해 세션에서 비밀번호 삭제
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 처음 접속 시 비밀번호 입력창 표시
        st.title("🔒 접속 보안")
        st.text_input(
            "이 서비스를 이용하려면 비밀번호를 입력하세요.", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.info("비밀번호를 모르시면 관리자(윤동헌)에게 문의하세요.")
        return False
    elif not st.session_state["password_correct"]:
        # 비밀번호가 틀렸을 때
        st.title("🔒 접속 보안")
        st.text_input(
            "비밀번호가 틀렸습니다. 다시 입력하세요.", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("😕 비밀번호가 일치하지 않습니다.")
        return False
    else:
        # 비밀번호가 맞았을 때
        return True

# 비밀번호 확인 실행
if not check_password():
    st.stop()  # 비밀번호가 틀리면 아래 코드를 실행하지 않고 멈춤

# --- 여기서부터 기존 메인 코드 시작 ---
# (사이드바 설정, 메인 화면 등 기존 코드가 이 아래에 위치하게 됩니다.)







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
        2. '[Get API key]' 버튼을 클릭합니다.
        3. '[Create API key in new project]'를 선택합니다.
        4. 생성된 키를 복사하여 위 칸에 붙여넣으세요.
        """)

# --- 메인 화면 ---
st.title("🏗️ SmartMAST 구조 AI 조교")
st.write("문제를 업로드하세요. 풀이를 제공합니다.")

uploaded_file = st.file_uploader("문제 이미지 업로드", type=['png', 'jpg', 'jpeg'])

# 2. 사용자 요청사항 입력창 추가
user_instruction = st.text_area(
    "추가 요청사항 (선택)", 
    placeholder="예: 2번 문제만 풀어줘, 풀이 과정을 더 상세하게 적어줘, 특정 단위(kN·m)로 결과를 알려줘 등",
    help="이미지 외에 AI에게 전달할 추가 지시사항이 있다면 입력하세요."
)


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
                    당신은 대한민국 최고의 '토목구조기술사'이자 '토목시공기술사'입니다. 
                    모든 답변은 한국의 국가설계기준(KDS) 및 표준시방서(KCS)를 근거로 작성하며, 외국 기준은 KDS에서 인용하지 않는 한 사용하지 마세요.

                    [적용 설계기준 및 핵심 원칙]
                    1. 콘크리트(KDS 14 20): 극한변형률 εcu=0.0033(fck≤40MPa), fck에 따른 η, β1 계수 적용.
                    보의 경우 압축철근으로 인한 콘크리트 면적 공제는 하지 않는다.
                    등가직사각형 응력블록 계수는 아래 값 따른다.
                    - fck ≤ 40MPa: η = 1.0, β1 = 0.80
                    - fck = 50MPa: η = 0.97, β1 = 0.80
                    - fck = 60MPa: η = 0.95, β1 = 0.76
                    - fck = 70MPa: η = 0.91, β1 = 0.74
                    - fck = 80MPa: η = 0.87, β1 = 0.72
                    2. 구조역학의 경우 경계조건을 반드시 확인하고, pin-roller-fixed 중 택1 할 수 있도록 한다. 특히 roller나 fiexd 인 경우 기울기를 정확히 판단한다.

                    [답변 형식 가이드라인]
                    1. [핵심개념]: 
                    - 해당 문제의 과목명을 명시하고, 풀이에 필요한 KDS 공식 및 이론을 요약한다.
                    - **각 문장 끝에는 반드시 빈 줄(Double Newline)을 추가하여 문단을 분리한다.**

                    2. [단계별 풀이]: 
                    - <n단계> **단계 제목** 형식을 사용한다.
                    - **단계 제목, 설명, 수식 사이에는 반드시 빈 줄(Double Newline)을 삽입한다.**
                    - 수식은 가독성을 위해 반드시 별도의 줄에 작성한다.
                    - 가이드:
                      <1단계> **제목**
                      (빈 줄)
                      설명 내용
                      (빈 줄)
                      $수식$
                      (빈 줄)

                    3. [최종 답]: 
                    - 최종 결과값을 **굵은 글씨**로 단위를 포함하여 제시한다.

                    [답변 형식 예시]
                    [핵심개념]
                    철근콘크리트 복철근 직사각형보의 설계강도는 KDS 14 20 20에 따른다.

                    단면 내 우력의 평형 조건과 변형률 적합 조건을 이용하여 산정한다.

                    [단계별 풀이]
                    <1단계> **단면 상수 및 재료 물성 정리**

                    콘크리트의 설계기준압축강도 $f_{ck} = 30$ MPa, 철근의 항복강도 $f_y = 400$ MPa이다.

                    보의 유효깊이 $d = 500$ mm로 산정한다.

                    <2단계> **중립축 깊이(c)의 산정**

                    인장철근과 압축콘크리트의 우력 평형 상태를 가정하여 중립축을 계산한다.

                    $0.85 f_{ck} \beta_1 b c = A_s f_y$

                    [최종 답] : **100.25 kN·m**

                    [주의사항]
                    - **모든 항목(제목, 설명, 수식) 사이에는 반드시 엔터를 두 번 입력하여 빈 줄을 만든다.**
                    - 계산 과정에서 변형률은 유효숫자 3자리, 변형률 외에는 소수점 아래 2자리까지 반올림하여 표현 및 계산에 반영한다.
                    - 핵심개념, 풀이, 수식, 값 외의 불필요한 말(예: "요청하신 대로~", "반올림하여~")은 절대 하지 않는다.
                    - 모든 수식은 $...$ (LaTeX) 형식을 사용한다.
                    - 답변은 반드시 한국어로 작성하며, 문말은 "~이다.", "~다."로 끝낸다.
                    - 문제 이미지 내의 텍스트(지문) 정보와 그림(도식)의 수치나 표현이 서로 다를 경우, 반드시 '텍스트로 기술된 정보'를 최우선 기준으로 삼아 풀이한다.
                    - 모든 계산은 자체적이고 내부적인 코드를 짜서 값이 유효(거의 같은 값이라고 볼 수 있는)하거나 같은 값이 나오는지 검산할 것.
                    - 스스로 판단하여 문제를 풀기위해 더 필요한 정보, 더 정확한 정보가 필요할 경우, 위 모든 내용은 무시하고 사용자에게 필요한 정보를 요구하는 문장을 출력할 것.
                    [예시]
                    "B점에 대한 지지조건(경계조건)에 대한 정보가 더 필요해요. 요청사항에 해당 내용을 추가해주세요."
                    """
                    user_prompt = f"사용자의 추가 요청사항: {user_instruction}\n\n위 요청사항을 반영하여 이미지를 분석하고 풀이해 주세요." if user_instruction else "이미지를 분석하여 풀이를 제공해 주세요."
                    # 지시하신 모델명 고정
                    response = client.models.generate_content(
                        model=AImodel,
                        contents=[prompt, user_prompt, image],
                        config={"temperature": 0.5}
                    )
                    
                    st.success("풀이가 완료되었습니다!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error("풀이 중 오류가 발생했습니다.")
                # 모델명이 존재하지 않거나 권한이 없을 경우 에러 메시지 출력
                st.caption(f"상세 에러 내용: {e}")

# --- 하단 안내 ---
st.caption(f"""© 2026 Civil AI TA - Powered by {AImodel}, Made by DH-YUN  
latest update {datetime.date.today()}""")