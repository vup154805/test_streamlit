import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
import threading
import time

# 記錄當前的 session
connected_users = set()
lock = threading.Lock()

def get_session_id():
    """取得當前使用者的 session ID"""
    ctx = get_script_run_ctx()
    return ctx.session_id if ctx else None

session_id = get_session_id()

if session_id:
    with lock:
        if len(connected_users) >= 5:  # 限制 5 人
            st.error("目前使用人數已滿，請稍後再試！")
            st.stop()
        else:
            connected_users.add(session_id)
            st.session_state["connected"] = True  # 標記為已連線

st.title("受限的 Streamlit 應用")
st.write(f"目前使用者數量：{len(connected_users)}")

# **監控使用者是否還在線上**
def monitor_users():
    while True:
        with lock:
            active_sessions = set(st.session_state.keys())
            disconnected_sessions = connected_users - active_sessions
            for sid in disconnected_sessions:
                connected_users.discard(sid)
        time.sleep(5)  # 每 5 秒檢查一次

# **背景執行監聽程式**
if "monitor_thread" not in st.session_state:
    monitor_thread = threading.Thread(target=monitor_users, daemon=True)
    monitor_thread.start()
    st.session_state["monitor_thread"] = True
