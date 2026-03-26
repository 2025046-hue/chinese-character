import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime

_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)

from app.auth import UserManager
from app.logger import logger
from app.progress import DATA_DIR
from app.progress import ProgressManager
from app.audio_engine import AudioEngine
from app.evaluation_engine import evaluate_character
from app.asset_loader import make_overlay_image
from streamlit_drawable_canvas import st_canvas
from app.constants import ENTER_USERNAME, BACK_TO_MENU, FILL_COLOR


@st.dialog("Confirm Logout")
def logout_dialog():
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("Yes", use_container_width=True):
            reset_audio_state()
            st.session_state.confirm_logout = False
            st.session_state.current_view = "login"
            st.rerun()
    with col_no:
        if st.button("No", use_container_width=True):
            st.session_state.confirm_logout = False
            st.rerun()


def init_session_state():
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'login'
    if 'user_manager' not in st.session_state:
        st.session_state.user_manager = UserManager()
    if 'progress' not in st.session_state:
        st.session_state.progress = ProgressManager(st.session_state.user_manager)
    if 'audio' not in st.session_state:
        st.session_state.audio = AudioEngine()
    if 'session' not in st.session_state:
        st.session_state.session = {
            "id": uuid.uuid4().hex,
            "started_at": datetime.now().isoformat()
        }
    if 'tracing_characters' not in st.session_state:
        st.session_state.tracing_characters = load_characters("tracing_characters.json")
    if 'audio_characters' not in st.session_state:
        st.session_state.audio_characters = load_characters("audio_characters.json")
    if 'current_char' not in st.session_state:
        st.session_state.current_char = None
    if 'selected_char_index' not in st.session_state:
        st.session_state.selected_char_index = None
    if 'evaluation_result' not in st.session_state:
        st.session_state.evaluation_result = None
    if 'current_evaluation_type' not in st.session_state:
        st.session_state.current_evaluation_type = None
    if 'strokes' not in st.session_state:
        st.session_state.strokes = []
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False
    if "confirm_logout" not in st.session_state:
        st.session_state.confirm_logout = False
    if "screen_width" not in st.session_state:
        st.session_state.screen_width = 1200


def capture_screen_width():
    st.markdown(
        """
        <script>
        const sendWidth = () => {
            const width = window.innerWidth;
            window.parent.postMessage(
                { type: "STREAMLIT_SCREEN_WIDTH", width },
                "*"
            );
        };
        sendWidth();
        window.addEventListener("resize", sendWidth);
        </script>
        """,
        unsafe_allow_html=True
    )
    

def load_characters(filename: str):
    p = Path(__file__).parent / "data" / filename
    if not p.exists():
        return [
            {"char": "你", "pinyin": "nǐ", "meaning": "you", "difficulty": "beginner"},
            {"char": "好", "pinyin": "hǎo", "meaning": "good", "difficulty": "beginner"},
            {"char": "水", "pinyin": "shuǐ", "meaning": "water", "difficulty": "beginner"},
        ]
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
        

def log_tracing_result(user, char, result, strokes, mode="ts"):
    try:
        logger.info(
            f"MODE={mode} | "
            f"USER={user} | "
            f"CHAR={char} | "
            f"ATTEMPT={result.get('attempt')} | "
            f"SCORE={result.get('score')} | "
            f"PASSED={result.get('score', 0) >= 60} | "
            f"STROKES_MATCH={result.get('correct_stroke_order_match')} | "
            f"FEEDBACK={result.get('feedback')} | "
            f"STROKE_COUNT={len(strokes)}"
        )
    except Exception as e:
        print("Global logging failed:", e)


def main():
    st.set_page_config(page_title="Chinese Character Recognizer", layout="wide")
    capture_screen_width()
    init_session_state()
    if st.session_state.current_view == 'login':
        render_login_screen()
    elif st.session_state.current_view == 'main_menu':
        render_main_menu()
    elif st.session_state.current_view == 'tracing':
        render_tracing_screen()
    elif st.session_state.current_view == 'audio_practice':
        render_audio_practice_screen()
    elif st.session_state.current_view == 'result':
        render_result_screen()
    elif st.session_state.current_view == 'progress':
        render_progress_screen()
    elif st.session_state.current_view == 'session_history':
        render_session_history_screen()


def render_login_screen():
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        st.markdown(
            "<p style='text-align:center; font-size: 1.8rem; font-weight: 600;'>Welcome to Chinese Character Learning</p>",
            unsafe_allow_html=True
        )
        username = st.text_input(
            "Enter Username",
            key="login_username",
            placeholder=ENTER_USERNAME,
            label_visibility="collapsed"
        ).strip()

        error_placeholder = st.empty()
        users = st.session_state.user_manager._users

        def show_error(message):
            error_placeholder.markdown(
                f"<p style='color:red;'>{message}</p>",
                unsafe_allow_html=True
            )

        if st.button("Login", use_container_width=True):
            error_placeholder.empty()

            if not username:
                show_error("Please enter a username")
            elif username not in users:
                show_error(f"User '{username}' does not exist. Please create a new user.")
            else:
                st.session_state.user_manager.current_user = username
                st.session_state.current_view = "main_menu"
                st.rerun()

        st.markdown(
            "<div style='text-align:center; font-weight:600; margin:0px 0px 12px 0px;'>OR</div>",
            unsafe_allow_html=True
        )

        if st.button("Create New User", use_container_width=True):
            error_placeholder.empty()

            if not username:
                show_error("Please enter a username")
            elif username in users:
                show_error(f"Username '{username}' is already taken. Please choose another.")
            else:
                st.session_state.user_manager.create_or_get_user(username)
                st.session_state.user_manager.current_user = username
                st.session_state.current_view = "main_menu"
                st.rerun()
                

def render_main_menu():
    st.markdown(
        "<p style='text-align:center; font-size: 1.8rem; font-weight: 600;'>Main Menu</p>",
        unsafe_allow_html=True
    )

    st.write(f"Welcome, {st.session_state.user_manager.current_user or 'Guest'}!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Tracing Module", use_container_width=True):
            st.session_state.selected_char_index = None
            st.session_state.current_char = None
            st.session_state.current_view = "tracing"
            st.rerun()
    with col2:
        if st.button("Audio Prompt Module", use_container_width=True):
            st.session_state.selected_char_index = None
            st.session_state.current_char = None
            st.session_state.current_view = "audio_practice"
            st.rerun()

    col3, col4 = st.columns(2)
    with col3:
        if st.button("View Progress", use_container_width=True):
            st.session_state.current_view = "progress"
            st.rerun()
    with col4:
        if st.button("Exit", use_container_width=True):
            st.session_state.confirm_logout = True

    if st.session_state.confirm_logout:
        logout_dialog()


def extract_stroke(obj):
    if obj.get("type") != "path" or not obj.get("path"):
        return None

    points = []
    for cmd, x, y, *_ in obj.get("path", []):
        if cmd in ("M", "L"):
            points.extend([int(x), int(y)])

    return points if points else None


def submit_result(type):
    user = st.session_state.user_manager.current_user or "guest"
    char = st.session_state.current_char
    user_stats = st.session_state.progress.get_user_stats(user)
    stats = next(
        (s for s in user_stats if s.get("character") == char),
        {}
    )

    if stats.get("total_attempts", 0) >= 2:
        st.error("This character is locked after 2 attempts.")
        return

    evaluate_and_show_result(char, st.session_state.strokes, type)
    

def render_character_info_panel(
    practice_type: str,
    canvas_width: int | None = None
):
    CONFIG = {
        "audio": {
            "characters_key": "audio_characters",
            "bold": False,
            "show_reference_image": False,
        },
        "tracing": {
            "characters_key": "tracing_characters",
            "bold": True,
            "show_reference_image": True,
        }
    }

    cfg = CONFIG[practice_type]
    char_meta = next(
        (
            c for c in st.session_state.get(cfg["characters_key"], [])
            if c.get("char") == st.session_state.current_char
        ),
        {}
    )

    if cfg["bold"]:
        st.write(f"**Pinyin:** {char_meta.get('pinyin', '')}")
        st.write(f"**Meaning:** {char_meta.get('meaning', '')}")
    else:
        st.write(f"Pinyin: {char_meta.get('pinyin', '')}")
        st.write(f"Meaning: {char_meta.get('meaning', '')}")

    if cfg["show_reference_image"] and st.session_state.current_char and canvas_width:
        img = make_overlay_image(
            st.session_state.current_char,
            size=min(240, canvas_width // 2)
        )
        st.image(img, caption="Reference Character")

        
def render_tracing_canvas_and_sidebar(canvas_width):
    col1, col2 = st.columns([80, 20])

    with col1:
        canvas_result = st_canvas(
            fill_color=FILL_COLOR,
            stroke_width=3,
            stroke_color="#333333",
            background_color="#ffffff",
            height=500,
            width=canvas_width,
            drawing_mode="freedraw",
            key="tracing_canvas",
            display_toolbar=False,
            update_streamlit=True
        )

    with col2:
        render_character_info_panel("tracing", canvas_width)

    return canvas_result


def render_practice_header(title: str):
    _, col_center, col_right = st.columns([1.5, 7, 1.5])
    with col_center:
        st.markdown(
            f"<p style='text-align:center; font-size:1.8rem; font-weight:600;'>{title}</p>",
            unsafe_allow_html=True
        )
    with col_right:
        if st.button(BACK_TO_MENU, key="back_to_menu_header"):
            reset_audio_state()
            st.session_state.current_view = "main_menu"
            st.rerun()

            
def render_practice_action_buttons(on_submit, submit_disabled):
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("Back to Grid", use_container_width=True):
            reset_character_selection()

    with col2:
        st.button("Clear", disabled=True, use_container_width=True)

    with col3:
        st.button("Undo", disabled=True, use_container_width=True)

    with col4:
        st.button("Redo", disabled=True, use_container_width=True)

    with col5:
        if st.button("Submit", disabled=submit_disabled, use_container_width=True):
            on_submit()
           

def render_practice_canvas_and_sidebar(
    canvas_width: int,
    practice_type: str
):
    CONFIG = {
        "audio": {
            "canvas_key": "audio_canvas",
            "sidebar_renderer": lambda: (
                render_character_info_panel("audio"),
                render_audio_controls()
            )
        },
        "tracing": {
            "canvas_key": "tracing_canvas",
            "sidebar_renderer": lambda: (
                render_character_info_panel("tracing", canvas_width),
            )
        }
    }

    cfg = CONFIG[practice_type]
    col1, col2 = st.columns([80, 20])
    with col1:
        canvas_result = st_canvas(
            fill_color=FILL_COLOR,
            stroke_width=3,
            stroke_color="#333333",
            background_color="#ffffff",
            height=500,
            width=canvas_width,
            drawing_mode="freedraw",
            key=cfg["canvas_key"],
            display_toolbar=True,
            update_streamlit=True
        )

    with col2:
        cfg["sidebar_renderer"]()

    return canvas_result
 

def render_tracing_screen():
    if st.session_state.selected_char_index is None:
        show_practice_grid("tracing")
        return

    render_practice_header("Tracing Practice")
    canvas_width = get_canvas_width()
    canvas_result = render_practice_canvas_and_sidebar(canvas_width, "tracing")
    update_strokes_from_canvas(canvas_result)
    render_practice_action_buttons(
        on_submit=lambda: submit_result("ts"),
        submit_disabled=not st.session_state.strokes
    )
   
 
def show_practice_grid(practice_type: str):
    CONFIG = {
        "audio": {
            "title": "Audio Practice",
            "characters_key": "audio_characters",
            "button_key_prefix": "audio_char_",
        },
        "tracing": {
            "title": "Tracing Practice",
            "characters_key": "tracing_characters",
            "button_key_prefix": "tracing_char_",
        }
    }

    cfg = CONFIG[practice_type]
    _, col_center, col_right = st.columns([1.5, 7, 1.5])
    with col_center:
        st.markdown(
            f"<p style='text-align:center; font-size: 1.8rem; font-weight: 600;'>{cfg['title']}</p>",
            unsafe_allow_html=True
        )
    with col_right:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button(BACK_TO_MENU, use_container_width=True):
            st.session_state.current_view = "main_menu"
            st.rerun()

    characters = st.session_state.get(cfg["characters_key"], [])
    grid_cols = 10
    grid_rows = (len(characters) + grid_cols - 1) // grid_cols

    for row_idx in range(grid_rows):
        cols = st.columns(grid_cols)
        for col_idx in range(grid_cols):
            char_idx = row_idx * grid_cols + col_idx
            if char_idx >= len(characters):
                break

            ch = characters[char_idx].get("char")

            with cols[col_idx]:
                if st.button(ch, key=f"{cfg['button_key_prefix']}{char_idx}"):
                    reset_audio_state()
                    st.session_state.selected_char_index = char_idx
                    st.session_state.current_char = ch
                    st.rerun()

def reset_audio_state():
    st.session_state.pop("current_audio_bytes", None)
    st.session_state.is_playing = False

def reset_character_selection():
    reset_audio_state()
    st.session_state.selected_char_index = None
    st.session_state.current_char = None
    st.rerun()


def update_strokes_from_canvas(canvas_result):
    if not canvas_result or not canvas_result.json_data:
        st.session_state.strokes = []
        return

    strokes = []
    for obj in canvas_result.json_data.get("objects", []):
        stroke = extract_stroke(obj)
        if stroke:
            strokes.append(stroke)

    st.session_state.strokes = strokes
    

def handle_audio_action(action):
    if action != "play": return
    audio = st.session_state.audio
    char = st.session_state.current_char
    if not char: return
    audio_bytes = audio.get_audio_bytes(char)
    st.session_state.current_audio_bytes = audio_bytes
    
def stop_audio():
    st.session_state.pop("current_audio_bytes", None)
    st.rerun()
    
    
def render_audio_controls():
    col1, col2 = st.columns(2)
    play_clicked = col1.button("▶ Play", use_container_width=True)
    col2.button("⏹ Stop", use_container_width=True)
    audio_placeholder = st.empty()
    if play_clicked and st.session_state.current_char:
        audio_bytes = st.session_state.audio.get_audio_bytes(
            st.session_state.current_char
        )
        audio_placeholder.audio(
            audio_bytes,
            format="audio/mp3"
        )
            

def render_canvas_and_sidebar(canvas_width):
    col1, col2 = st.columns([80, 20])
    canvas_result = None
    with col1:
        canvas_result = st_canvas(
            fill_color=FILL_COLOR,
            stroke_width=3,
            stroke_color="#333333",
            background_color="#ffffff",
            height=500,
            width=canvas_width,
            drawing_mode="freedraw",
            key="audio_canvas",
            display_toolbar=False,
            update_streamlit=True
        )
    with col2:
        render_character_info_panel("audio")
        render_audio_controls()

    return canvas_result
        

def get_canvas_width():
    screen_width = st.session_state.get("screen_width", 1200)
    canvas_width = int(screen_width * 0.75)
    MIN_WIDTH = 450
    MAX_WIDTH = 1100
    return max(MIN_WIDTH, min(canvas_width, MAX_WIDTH))


def render_audio_practice_screen():
    if st.session_state.selected_char_index is None:
        show_practice_grid("audio")
        return

    render_practice_header("Audio Practice")
    canvas_width = get_canvas_width()
    canvas_result = render_practice_canvas_and_sidebar(canvas_width, "audio")
    update_strokes_from_canvas(canvas_result)
    render_practice_action_buttons(
        on_submit=lambda: submit_result("aps"),
        submit_disabled=not st.session_state.strokes
    )


def evaluate_and_show_result(char, strokes, type):
    try:
        result = evaluate_character(char, strokes)
    except Exception as e:
        result = {
            "score": 0,
            "feedback": f"Evaluation error: {e}",
            "correct_stroke_order_match": False,
            "correct_stroke_order": []
        }

    user_stats = st.session_state.progress.get_user_stats(st.session_state.user_manager.current_user or "guest")
    stats = next((item for item in user_stats if item.get("character") == char), {})
    attempts_done = stats.get("attempts", 0) if type == "ts" else stats.get("total_attempts", 0)
    attempt_number = attempts_done + 1
    result["attempt"] = attempt_number

    if result.get("score", 0) >= 60:
        if attempt_number == 1:
            result["score"] = 100
        elif attempt_number == 2:
            result["score"] = 70

    passed = result.get("score", 0) >= 60
    strokes_match = result.get("correct_stroke_order_match", False)

    user = st.session_state.user_manager.current_user or "guest"
    st.session_state.progress.update_progress(
        user,
        char=char,
        strokes=strokes,
        correct=passed,
        type=type,
        strokes_match=strokes_match
    )
    st.session_state.progress.record_session_attempt(
        st.session_state.session["id"],
        user,
        char,
        result,
        type
    )

    st.session_state.evaluation_result = result
    st.session_state.current_evaluation_type = type
    st.session_state.current_view = 'result'
    st.rerun()


def render_result_screen():
    evaluation_type = st.session_state.current_evaluation_type
    header_map = {
        None: "Result",
        "ts": "Tracing Result",
        "aps": "Audio Prompt Result"
    }
    st.markdown(
        f"<p style='text-align:left; font-size: 1.8rem; font-weight: 600;'>{header_map.get(evaluation_type, 'Result')}</p>",
        unsafe_allow_html=True
    )

    if not st.session_state.evaluation_result:
        st.error("No evaluation result to display")
        return

    result = st.session_state.evaluation_result

    score = result.get("score", 0)
    status = "Pass" if score >= 60 else "Fail"

    st.write(f"**Score:** {score}%")
    st.write(f"**Status:** {status}")
    st.write(f"**Attempt:** {result.get('attempt', 0)}")
    st.write(f"**Character:** {st.session_state.current_char}")
    st.markdown(
        "<p style='text-align:left; font-size: 1.8rem; font-weight: 600;'>Feedback</p>",
        unsafe_allow_html=True
    )
    feedback = result.get("feedback", "No feedback available.")
    st.write(feedback)

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("Next Character", use_container_width=True):
            if st.session_state.current_evaluation_type == "ts":
                st.session_state.selected_char_index = None
                st.session_state.current_char = None
                st.session_state.current_view = 'tracing'
            elif st.session_state.current_evaluation_type == "aps":
                st.session_state.selected_char_index = None
                st.session_state.current_char = None
                st.session_state.current_view = 'audio_practice'
            else:
                st.session_state.current_view = 'main_menu'
            st.rerun()

    with col_btn2:
        if st.button("Back to Menu", use_container_width=True):
            st.session_state.current_view = 'main_menu'
            st.rerun()
            

def _render_progress_header():
    _, col_center, col_right = st.columns([1.5, 7, 1.5])
    with col_center:
        st.markdown(
            "<p style='text-align:center; font-size: 1.8rem; font-weight: 600;'>Progress</p>",
            unsafe_allow_html=True
        )
    with col_right:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("Back to Menu", key="progress_back_menu"):
            st.session_state.current_view = "main_menu"
            st.rerun()


def _calculate_overall_stats(sessions):
    total_attempts = len(sessions)
    total_correct = sum(1 for s in sessions if s.get("passed"))
    accuracy = (total_correct / total_attempts * 100) if total_attempts else 0
    return total_attempts, total_correct, accuracy


def _group_sessions_by_character(sessions):
    char_stats = {}
    for session in sessions:
        char_stats.setdefault(session.get("char", ""), []).append(session)
    return char_stats


def _render_character_progress(_, sessions):
    attempts = len(sessions)
    correct = sum(1 for s in sessions if s.get("passed"))
    accuracy = (correct / attempts * 100) if attempts else 0

    st.write(
        f"**Total Attempts:** {attempts} | "
        f"**Passed:** {correct} | "
        f"**Accuracy:** {accuracy:.1f}%"
    )

    for i, session in enumerate(sessions):
        status = "✅ Pass" if session.get("passed") else "❌ Fail"
        st.write(
            f"- Attempt {session.get('attempt', i + 1)}: "
            f"{session.get('score', 0):.1f}% ({status})"
        )


def render_progress_screen():
    _render_progress_header()
    user = st.session_state.user_manager.current_user
    if not user:
        st.warning("Please log in to view progress.")
        if st.button("Go to Login", key="progress_login"):
            st.session_state.current_view = "login"
            st.rerun()
        return

    user_sessions = st.session_state.progress.get_user_sessions(user)
    if not user_sessions:
        st.info("No progress data. Start practicing to see your progress!")
        return

    total_attempts, total_correct, accuracy = _calculate_overall_stats(user_sessions)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Attempts", total_attempts)
    col2.metric("Successful", total_correct)
    col3.metric("Accuracy", f"{accuracy:.1f}%")

    st.subheader("Progress by Character")
    char_stats = _group_sessions_by_character(user_sessions)
    for char, sessions in char_stats.items():
        with st.expander(f"Character: {char}", expanded=True):
            _render_character_progress(char, sessions)


def render_session_history_screen():
    st.header("Session History")
    if st.button("Export Sessions CSV", use_container_width=True):
        filepath = DATA_DIR / "exported_sessions.csv"
        st.session_state.progress.export_sessions_csv(str(filepath))
        st.success(f"Sessions exported to {filepath}")

    if st.button("Back", use_container_width=True):
        st.session_state.current_view = 'main_menu'
        st.rerun()

if __name__ == "__main__":
    main()