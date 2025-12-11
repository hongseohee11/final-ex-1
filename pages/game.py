import streamlit as st
import random
import json
import streamlit.components.v1 as components

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

# --- 난이도 설정 ---
DIFFICULTY_OPTIONS = ["하", "중", "상"]
DIFFICULTY_SETTINGS = {
    "하": {"color_min": 2, "color_max": 4, "white_min": 1, "white_max": 2},
    "중": {"color_min": 3, "color_max": 6, "white_min": 1, "white_max": 3},
    "상": {"color_min": 4, "color_max": 8, "white_min": 2, "white_max": 6},
}

# --- 캐릭터(내 그림) 표시 ---
st.title("🧪 물약 연구실")
st.write("내가 그린 그림이 연구실 주인 캐릭터가 되었어요!")

# 저장된 사용자 그림이 있으면 표시, 없으면 기본 팔레트 이미지 표시
if st.session_state.get("user_drawing"):
    st.image(st.session_state.user_drawing, width=200, caption="내 캐릭터")
else:
    st.image("https://em-content.zobj.net/source/microsoft-teams/363/artist-palette_1f3a8.png", width=200, caption="내 캐릭터")
st.write("**상점 주인**")

st.markdown("---")

# --- 현재 손님 주문을 항상 표시 (드래그 중에도 유지되도록)
if game.get("customer_order"):
    order = game["customer_order"]
    st.header("손님의 주문!")
    st.markdown(
        f"<div style='padding:16px 24px; background:#f0f4ff; border-radius:16px; border:1px solid #bcd; font-size:20px; margin-bottom:16px;'><b>손님:</b> {order['color_name']}과 흰색의 비율을 <b>{order['color_ratio']}:{order['white_ratio']}</b>으로 물약을 만들어주세요! (난이도: {game.get('difficulty','중')})</div>",
        unsafe_allow_html=True,
    )

# --- 손님 받기 버튼 ---
if game["step"] == "intro":
    st.header("손님을 맞이해볼까요?")
    # 난이도 선택
    if "difficulty" not in game:
        game["difficulty"] = "중"
    game["difficulty"] = st.radio("난이도", DIFFICULTY_OPTIONS, index=DIFFICULTY_OPTIONS.index(game["difficulty"]))
    if st.button("👋 손님 받기", key="get_customer"):
        # 랜덤 주문 생성 (색상, 비율) — 난이도에 따라 범위를 조절
        color_name, color_hex = random.choice(COLOR_LIST)
        diff = game.get("difficulty", "중")
        settings = DIFFICULTY_SETTINGS.get(diff, DIFFICULTY_SETTINGS["중"])
        color_ratio = random.randint(settings["color_min"], settings["color_max"])
        white_ratio = random.randint(settings["white_min"], settings["white_max"])
        game["customer_order"] = {
            "color_name": color_name,
            "color_hex": color_hex,
            "color_ratio": color_ratio,
            "white_ratio": white_ratio,
        }
        game["user_mix"] = {c[0]: 0 for c in COLOR_LIST}
        game["user_mix"]["흰색"] = 0
        # 주문을 즉시 화면에 표시하고 바로 믹싱 단계로 진입
        game["step"] = "mixing"
        st.header("손님의 주문!")
        st.markdown(
            f"<div style='padding:16px 24px; background:#f0f4ff; border-radius:16px; border:1px solid #bcd; font-size:20px; margin-bottom:16px;'><b>손님:</b> {color_name}과 흰색의 비율을 <b>{color_ratio}:{white_ratio}</b>으로 물약을 만들어주세요! (난이도: {game.get('difficulty','중')})</div>",
            unsafe_allow_html=True,
        )

# (order 단계는 즉시 믹싱으로 넘어가게 처리함)
# --- 물약 만들기 (드래그 인터페이스) ---
if game["step"] == "mixing":
    # 주문 카드가 항상 보이도록 여기서도 표시

    
    st.subheader("물약 재료 통")
    st.write("색 아래의 좌측 버튼을 클릭하여 물감을 담고, 우츨 버튼을 클릭하여 물감을 뺄 수 있습니다")

    cols = st.columns(len(COLOR_LIST) + 1)
    color_keys = [c[0] for c in COLOR_LIST] + ["흰색"]
    color_hexes = [c[1] for c in COLOR_LIST] + [WHITE[1]]
    for i, (name, hexcode) in enumerate(zip(color_keys, color_hexes)):
        with cols[i]:
            swatch_html = f"""
            <div style='position:relative; width:48px; height:48px; margin:auto;'>
              <div style='width:48px; height:48px; background:{hexcode}; border-radius:50%; border:2px solid #aaa;'></div>
              <div style='position:absolute; right:-6px; top:-6px; background:#ffffff; border-radius:50%; width:20px; height:20px; display:flex; align-items:center; justify-content:center; font-size:12px; box-shadow:0 1px 2px rgba(0,0,0,0.12);'>+</div>
              <div style='position:absolute; right:-6px; bottom:-6px; background:#ffffff; border-radius:50%; width:20px; height:20px; display:flex; align-items:center; justify-content:center; font-size:12px; box-shadow:0 1px 2px rgba(0,0,0,0.12);'>-</div>
            </div>
            """
            st.markdown(swatch_html, unsafe_allow_html=True)
            st.write(name)
            # 추가/제거 버튼을 함께 배치
            btns = st.columns([1, 1])
            add_key = f"add_{name}"
            rem_key = f"rem_{name}"
            if btns[0].button("+", key=add_key):
                game["user_mix"][name] = game["user_mix"].get(name, 0) + 1
            if btns[1].button("-", key=rem_key):
                if game["user_mix"].get(name, 0) > 0:
                    game["user_mix"][name] -= 1
            st.write(f"x {game['user_mix'].get(name, 0)}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 간단한 믹스 요약: 드래그 영역 제거, 클릭 기반 조작만 유지
    st.subheader("현재 믹스")
    total_items = 0
    for name in color_keys:
        cnt = game["user_mix"].get(name, 0)
        if cnt > 0:
            hexcode = dict(zip(color_keys, color_hexes)).get(name, "#ffffff")
            st.markdown(f"<div style='display:flex; align-items:center; gap:8px; margin-bottom:6px'><div style='width:24px; height:24px; background:{hexcode}; border-radius:4px; border:1px solid #999'></div><div style='flex:1'>{name}</div><div style='min-width:48px'>x {cnt}</div></div>", unsafe_allow_html=True)
            total_items += cnt
    if total_items == 0:
        st.info("아직 물감을 넣지 않았습니다. 밑에 좌측 버튼을 눌러 물감을 추가해보세요")
    else:
        # 선택된 색들을 요약 형식으로 출력: 색1:색2=cnt1:cnt2
        selected = [name for name in color_keys if game["user_mix"].get(name, 0) > 0]
        if selected:
            counts = [str(game["user_mix"][n]) for n in selected]
            summary = "선택된 색--> " + ":".join(selected) + "=" + ":".join(counts)
            st.info(summary)
    st.write("---")

    if st.button("완성!", key="submit_mix"):
        # 정답 체크
        correct = (
            game["user_mix"][order["color_name"]] == order["color_ratio"] and
            game["user_mix"]["흰색"] == order["white_ratio"] and
            sum([v for k, v in game["user_mix"].items() if k != order["color_name"] and k != "흰색"]) == 0
        )
        game["result"] = correct
        game["step"] = "result"

# --- 결과 ---
if game["step"] == "result":
    order = game["customer_order"]
    if game["result"]:
        st.success(f"정답! 손님이 만족해요 😊 {order['color_name']}과 흰색의 비율을 {order['color_ratio']}:{order['white_ratio']}으로 맞추셨어요.")
    else:
        st.error(f"아쉬워요! 정답은 {order['color_name']}과 흰색의 비율을 {order['color_ratio']}:{order['white_ratio']}으로 만드는 것입니다.")
    if st.button("다음 손님 받기", key="next_customer"):
        game["step"] = "intro"
        game["customer_order"] = None
