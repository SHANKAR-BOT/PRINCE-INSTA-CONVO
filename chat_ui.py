import streamlit as st
import base64
from pathlib import Path
import html
import ai_guide


def init_chat_state():
    """Initialize chat session state - Call this at the top of every page"""
    if 'ai_chat_history' not in st.session_state:
        st.session_state.ai_chat_history = []
    
    if 'show_ai_assistant' not in st.session_state:
        st.session_state.show_ai_assistant = False


@st.cache_data
def load_pika_avatar():
    """Load Pika's profile picture as base64"""
    pika_image_path = Path(__file__).parent / 'attached_assets' / '1763040040342_1763040189071.jpg'
    if pika_image_path.exists():
        try:
            with open(pika_image_path, 'rb') as img_file:
                return base64.b64encode(img_file.read()).decode()
        except:
            pass
    return None


def render_chat_panel(form_key="pika_chat_form"):
    """Render Pika AI chat panel in main content area - ChatGPT style
    
    Args:
        form_key: Unique key for the chat form (default: "pika_chat_form")
    """
    
    pika_avatar = load_pika_avatar()
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="
            background: linear-gradient(135deg, rgba(255, 23, 68, 0.3), rgba(0, 217, 255, 0.3));
            padding: 1.5rem;
            border-radius: 15px;
            border: 2px solid #FF1744;
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.4);
        ">
            <h2 style="
                color: #FF1744;
                font-family: 'Orbitron', monospace;
                text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
                margin: 0;
                font-size: 1.5rem;
            ">💬 PIKA AI CHAT</h2>
            <p style="
                color: rgba(0, 217, 255, 0.9);
                margin: 0.5rem 0 0 0;
                font-size: 0.9rem;
            ">Your Personal Guide</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    chat_container = st.container()
    
    with chat_container:
        if len(st.session_state.ai_chat_history) > 0:
            st.markdown('<div style="max-height: 500px; overflow-y: auto; padding: 0.5rem;">', unsafe_allow_html=True)
            
            for msg in st.session_state.ai_chat_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                
                if role == 'user':
                    escaped_content = html.escape(content)
                    st.markdown(f"""
                    <div class="chat-message user" style="display: flex; flex-direction: row-reverse; margin-bottom: 1rem; align-items: flex-start;">
                        <div class="chat-bubble user" style="
                            background: linear-gradient(135deg, rgba(255, 23, 68, 0.3), rgba(255, 23, 68, 0.2));
                            border: 2px solid #FF1744;
                            color: #ffffff;
                            padding: 0.8rem 1rem;
                            border-radius: 15px;
                            max-width: 80%;
                            word-wrap: break-word;
                            margin-left: auto;
                        ">
                            {escaped_content}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    avatar_html = ""
                    if pika_avatar:
                        avatar_html = f'<img src="data:image/jpeg;base64,{pika_avatar}" style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid #FF1744; margin-right: 0.5rem; flex-shrink: 0;" />'
                    
                    escaped_content = html.escape(content)
                    st.markdown(f"""
                    <div class="chat-message assistant" style="display: flex; margin-bottom: 1rem; align-items: flex-start;">
                        {avatar_html}
                        <div class="chat-bubble assistant" style="
                            background: linear-gradient(135deg, rgba(0, 217, 255, 0.2), rgba(0, 217, 255, 0.1));
                            border: 2px solid rgba(0, 217, 255, 0.5);
                            color: #ffffff;
                            padding: 0.8rem 1rem;
                            border-radius: 15px;
                            max-width: 80%;
                            word-wrap: break-word;
                        ">
                            {escaped_content}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👋 Namaste! Main Pika hoon. Aap mujhse kuch bhi puch sakte ho!")
    
    with st.form(form_key, clear_on_submit=True):
        user_message = st.text_area(
            "💬 Type your message:",
            height=80,
            placeholder="E.g., Instagram cookies kaise nikaalun?",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            submit_btn = st.form_submit_button("📤 Send", use_container_width=True)
        
        with col2:
            clear_btn = st.form_submit_button("🗑️ Clear", use_container_width=True)
        
        if clear_btn:
            st.session_state.ai_chat_history = []
            st.rerun()
        
        if submit_btn and user_message.strip() and not clear_btn:
            st.session_state.ai_chat_history.append({
                'role': 'user',
                'content': user_message.strip()
            })
            
            with st.spinner("🤖 Pika is thinking..."):
                ai_response = ai_guide.get_ai_response(
                    user_message.strip(),
                    conversation_history=st.session_state.ai_chat_history
                )
            
            st.session_state.ai_chat_history.append({
                'role': 'assistant',
                'content': ai_response
            })
            
            st.rerun()
