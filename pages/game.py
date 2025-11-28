import streamlit as st
import random

st.set_page_config(page_title="물약 연구실 게임", layout="centered")

# --- 게임 상태 관리 ---
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        "step": "intro",  # intro, order, mixing, result
        "customer_order": None,
        "user_mix": {},
        "result": None,
        "character_img": None,  # 추후 그림 연동
    }

game = st.session_state.game_state

# --- 색상 및 이름 정의 ---
COLOR_LIST = [
    ("빨간색", "#ff3b30"),
    ("주황색", "#ff9500"),
    ("노란색", "#ffd60a"),
    ("초록색", "#34c759"),
    ("파란색", "#007aff"),
    ("남색", "#5856d6"),
    ("보라색", "#af52de"),
]
WHITE = ("흰색", "#ffffff")

# --- 캐릭터(내 그림) 표시 ---
st.title("🧪 물약 연구실")
st.write("내가 그린 그림이 연구실 주인 캐릭터가 되었어요!")

# (추후: streamlit_app.py에서 그림을 세션에 저장해 연동 가능)
st.image("https://em-content.zobj.net/source/microsoft-teams/363/artist-palette_1f3a8.png", width=120, caption="내 캐릭터")

st.markdown("---")

# --- 손님 받기 버튼 ---
if game["step"] == "intro":
    st.header("손님을 맞이해볼까요?")
    if st.button("👋 손님 받기", key="get_customer"):
        # 랜덤 주문 생성 (색상, 비율)
        color_name, color_hex = random.choice(COLOR_LIST)
        color_ratio = random.randint(2, 5)
        white_ratio = random.randint(1, 3)
        game["customer_order"] = {
            "color_name": color_name,
            "color_hex": color_hex,
            "color_ratio": color_ratio,
            "white_ratio": white_ratio,
        }
        game["user_mix"] = {c[0]: 0 for c in COLOR_LIST}
        game["user_mix"]["흰색"] = 0
        game["step"] = "order"
        st.experimental_rerun()

# --- 주문 등장 (말풍선) ---
if game["step"] == "order":
    order = game["customer_order"]
    st.header("손님의 주문!")
    st.markdown(f"<div style='padding:16px 24px; background:#f0f4ff; border-radius:16px; border:1px solid #bcd; font-size:20px; margin-bottom:16px;'><b>손님:</b> {order['color_name']}과 흰색이 <b>{order['color_ratio']}:{order['white_ratio']}</b>인 물약을 만들어주세요!</div>", unsafe_allow_html=True)
    st.write("아래에서 물약 재료를 드래그해서 원하는 비율로 섞어보세요!")
    game["step"] = "mixing"
    st.experimental_rerun()

# --- 물약 만들기 (드래그 인터페이스) ---
if game["step"] == "mixing":
    order = game["customer_order"]
    st.subheader("물약 재료 통")
    cols = st.columns(len(COLOR_LIST) + 1)
    color_keys = [c[0] for c in COLOR_LIST] + ["흰색"]
    color_hexes = [c[1] for c in COLOR_LIST] + [WHITE[1]]
    for i, (name, hexcode) in enumerate(zip(color_keys, color_hexes)):
        with cols[i]:
            st.markdown(f"<div style='width:48px; height:48px; background:{hexcode}; border-radius:50%; border:2px solid #aaa; margin:auto'></div>", unsafe_allow_html=True)
            st.write(name)
            if st.button(f"{name} 드래그", key=f"drag_{name}"):
                game["user_mix"][name] += 1
                st.experimental_rerun()
            st.write(f"x {game['user_mix'][name]}")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("완성!", key="submit_mix"):
        # 정답 체크
        correct = (
            game["user_mix"][order["color_name"]] == order["color_ratio"] and
            game["user_mix"]["흰색"] == order["white_ratio"] and
            sum([v for k, v in game["user_mix"].items() if k != order["color_name"] and k != "흰색"]) == 0
        )
        game["result"] = correct
        game["step"] = "result"
        st.experimental_rerun()

# --- 결과 ---
if game["step"] == "result":
    order = game["customer_order"]
    if game["result"]:
        st.success(f"정답! 손님이 만족해요 😊 ({order['color_name']}:{order['color_ratio']}, 흰색:{order['white_ratio']})")
    else:
        st.error(f"아쉬워요! 정답은 {order['color_name']}:{order['color_ratio']}, 흰색:{order['white_ratio']} 입니다.")
    if st.button("다음 손님 받기", key="next_customer"):
        game["step"] = "intro"
        st.experimental_rerun()
