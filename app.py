import streamlit as st
from generation import getSessionID, generateResponse, getSessionHistory

st.set_page_config(page_title='InfraBuddy', layout='wide')

# Generate session id
if 'session_id' not in st.session_state:
    st.session_state.session_id = getSessionID()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

with st.sidebar:
    st.title("InfraBuddy")
    st.caption("Designed and powered by CloudByAdi Solutions.")

    selection = st.selectbox(
        label='Navigation',
        options=['InfraBuddy', 'History', 'Uploads', 'Settings'],
        index=0,
        label_visibility='hidden',
        key='selection'
    )
    st.write('Session ID:', st.session_state.session_id)

    if st.button('New Conversation'):
        st.session_state.chat_history = []
        st.session_state.session_id = getSessionID()
        getSessionHistory(st.session_state.session_id).clear()


if selection == 'InfraBuddy':
    prompt = st.chat_input('Ask anything!')

    placeholder = st.empty()
    placeholder.markdown(
        '''
        <h1 style='text-align: center; color: #ffffff;'>
            Welcome to InfraBuddy
        </h1>
        <p style='text-align: center; font-size: 16px; color: gray;'>
            Designed and powered by CloudByAdi Solutions
        </p>
        ''',
        unsafe_allow_html=True
    )

    if prompt:
        placeholder.empty()

        st.session_state.chat_history.append({'role': 'user', 'content': prompt})
        with st.chat_message('user'):
            st.markdown(prompt)

        with st.chat_message('assistant'):
            streamResponse = st.write_stream(generateResponse(prompt, st.session_state.session_id))
        st.session_state.chat_history.append({'role': 'assistant', 'content': streamResponse})

elif selection == 'History':
    st.header('📜 Interaction History')
    st.markdown(
        """
        <h1 style='text-align: center; color: #ffffff;'>
            Coming Soon ....
        </h1>
        """,
        unsafe_allow_html=True
    )

elif selection == 'Uploads':
    st.header('📤 Upload Knowledge Base PDFs')
    st.markdown(
        """
        <h1 style='text-align: center; color: #ffffff;'>
            Coming Soon ....
        </h1>
        """,
        unsafe_allow_html=True
    )

elif selection == 'Settings':
    st.header('⚙️ Settings')
    st.markdown(
        """
        <h1 style='text-align: center; color: #ffffff;'>
            Coming Soon ....
        </h1>
        """,
        unsafe_allow_html=True
    )