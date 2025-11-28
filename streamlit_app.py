
import streamlit as st
try:
    from streamlit_drawable_canvas import st_canvas
    HAS_CANVAS = True
except Exception:
    HAS_CANVAS = False

try:
    from PIL import Image
except Exception:
    Image = None
try:
    import numpy as np
except Exception:
    np = None

st.set_page_config(page_title="색과 흰색의 농도 체험", layout="centered")

st.title("🖌️ 나만의 색 만들기 ")
st.write(
    "한 가지 색을 골라 흰색과의 비율을 바꾸어 색의 진하기가 어떻게 변하는지 눈으로 확인해 보세요!"
)


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple) -> str:
    return "#%02x%02x%02x" % rgb


def mix_with_white(rgb: tuple, weight_color: float, weight_white: float) -> tuple:
    """Mix an rgb color with white (#ffffff) by weights and return resulting rgb tuple."""
    total = weight_color + weight_white
    if total == 0:
        return rgb  # fallback: no change
    white = (255, 255, 255)
    r = round((rgb[0] * weight_color + white[0] * weight_white) / total)
    g = round((rgb[1] * weight_color + white[1] * weight_white) / total)
    b = round((rgb[2] * weight_color + white[2] * weight_white) / total)
    return (r, g, b)


st.header("색을 고르고 흰색과 섞어볼까요?")

col1, col2 = st.columns([2, 3])
with col1:
    chosen_color = st.color_picker("색을 골라보세요", value="#00b7ff")
with col2:
    ratio_color = st.number_input("고른 색의 값(자연수)", min_value=0, value=3, step=1, format="%d")
    ratio_white = st.number_input("흰색의 값 (자연수)", min_value=0, value=1, step=1, format="%d")

total = ratio_color + ratio_white
if total == 0:
    st.warning("비율을 0으로 두면 혼합 색을 계산할 수 없습니다. 비율을 하나 이상으로 설정해 주세요.")
    total = 1

frac_color = ratio_color / total
# Marker position on gradient: gradient goes from chosen_color (left, 0%) to white (right, 100%).
# We want the brush to be at the left side when the chosen color is stronger.
# So compute marker_pct as (1 - frac_color) * 100 so that 100% color -> marker at 0% (left), 0% color -> marker at 100% (right).
marker_pct = int(round((1 - frac_color) * 100))
color_pct_label = int(round(frac_color * 100))

rgb_chosen = hex_to_rgb(chosen_color)
mixed_rgb = mix_with_white(rgb_chosen, ratio_color, ratio_white)
mixed_hex = rgb_to_hex(mixed_rgb)

def luminance(rgb: tuple) -> float:
    r, g, b = (x / 255 for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

lum = luminance(mixed_rgb)
def darkness_label(frac: float, lum_val: float) -> str:
    # Use fraction primarily to indicate paint 'concentration', and luminance as secondary cue
    if frac >= 0.75:
        return "진함"
    elif frac >= 0.5:
        return "중간"
    elif frac >= 0.25:
        return "약간 연함"
    else:
        return "매우 연함"

dark_label = darkness_label(frac_color, lum)

st.markdown("---")
st.header("색 확인하기")
st.write("붓의 위치를 통해 내가 만든 색의 진하기를 확인해볼까요?")

# Render gradient and brush marker using HTML
ratio_label = f"{ratio_color}:{ratio_white}"
gradient_html = f"""
<div style='position:relative; width:100%; height:64px; border-radius:8px; background:linear-gradient(to right, {chosen_color}, #ffffff); box-shadow: 0 1px 6px rgba(0,0,0,0.15);'>
    <div style='position:absolute; left:{marker_pct}%; top:0; transform:translateX(-50%);'>
    <div style='font-size:28px; line-height:1'>🖌️</div>
  </div>
    <div style='position:absolute; left:{marker_pct}%; bottom:6px; transform:translateX(-50%); font-size:13px; color:#111;'> {ratio_label}</div>
</div>
"""

st.markdown(gradient_html, unsafe_allow_html=True)



st.markdown("---")
st.subheader("시각적 확인")
sw1, sw2, sw3 = st.columns([1, 1, 1])
sw1.markdown(f"<div style='height:60px;background:{chosen_color};border-radius:8px'></div>", unsafe_allow_html=True)
sw1.caption("선택 색")
sw2.markdown(f"<div style='height:60px;background:#ffffff;border-radius:8px;border:1px solid #ddd'></div>", unsafe_allow_html=True)
sw2.caption("흰색")
sw3.markdown(f"<div style='height:60px;background:{mixed_hex};border-radius:8px;border:1px solid #ddd'></div>", unsafe_allow_html=True)
sw3.caption("혼합 색")

st.markdown("---")
st.markdown("")
st.write(f"진하기 레벨: {dark_label} (명도: {lum:.2f})")


st.markdown("---")
st.header("내가 만든 색으로 직접 그림을 그려볼까요?")
if HAS_CANVAS and Image is not None and np is not None:
    st.write("붓 크기 조절")

    brush_width = st.slider("붓 크기", min_value=1, max_value=50, value=10)

    # Create a white background canvas and set stroke_color to the mixed color
    canvas_result = st_canvas(
        fill_color=None,
        stroke_width=brush_width,
        stroke_color=mixed_hex,
        background_color="#ffffff",
        height=400,
        width=800,
        drawing_mode="freedraw",
        key="canvas",
    )

    if canvas_result.image_data is not None:
        # image_data is RGBA numpy array, convert to PIL Image for download
        img_data = canvas_result.image_data
        # Convert numpy array to PIL Image
        img = Image.fromarray(img_data.astype("uint8"), "RGBA")
        img_rgb = img.convert("RGB")
        st.image(img_rgb, caption="내가 그린 그림", use_column_width=True)
        # Provide download
        buf = None
        try:
            import io
            buf = io.BytesIO()
            img_rgb.save(buf, format="PNG")
            buf.seek(0)
            st.download_button("이미지 다운로드 (PNG)", data=buf, file_name="my_painting.png", mime="image/png")
        except Exception:
            st.error("이미지 변환에 실패했습니다.")
else:
    st.info("그림판 기능은 추가 패키지(streamlit-drawable-canvas, Pillow, numpy)가 필요합니다. 설치 후 앱을 재시작하세요: `pip install -r requirements.txt`.")

# --- 게임하러가기 버튼 추가 ---
st.markdown("---")
st.write("")
col_game = st.columns([1, 2, 1])[1]
with col_game:
    game_btn = st.button("🎮 게임하러가기", key="go_to_game", use_container_width=True)

# 페이지 이동 (농도 맞추기 게임)
if game_btn:
    try:
        st.switch_page("pages/game.py")
    except Exception:
        st.warning("게임 페이지가 아직 준비되지 않았습니다. 'pages/game.py' 파일을 만들어주세요.")


