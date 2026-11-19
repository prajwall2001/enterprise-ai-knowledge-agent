
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Enterprise AI Knowledge Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM STYLING ----------
st.markdown("""
<style>
    .stApp {
        background: #0b1120;
        color: #e5e7eb;
    }
    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263244;
    }
    .main-title {
        font-size: 2.1rem;
        font-weight: 750;
        color: #f8fafc;
        margin-bottom: 4px;
    }
    .subtitle {
        color: #94a3b8;
        margin-bottom: 25px;
    }
    .info-card {
        background: #172235;
        padding: 18px;
        border: 1px solid #29384e;
        border-radius: 12px;
        margin-bottom: 12px;
    }
    .source-card {
        background: #172235;
        border-left: 3px solid #38bdf8;
        padding: 12px;
        border-radius: 7px;
        margin: 8px 0;
    }
    div.stButton > button {
        border-radius: 9px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []


# ---------- API HEALTH ----------
def check_backend():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


# ---------- PDF UPLOAD ----------
def upload_pdf(pdf):
    try:
        response = requests.post(
            f"{API_URL}/documents/upload",
            files={
                "file": (
                    pdf.name,
                    pdf.getvalue(),
                    "application/pdf"
                )
            },
            timeout=180
        )
        response.raise_for_status()
        return response.json(), None

    except requests.exceptions.RequestException as error:
        detail = "Unable to connect to the backend."
        if error.response is not None:
            try:
                detail = error.response.json().get("detail", str(error))
            except ValueError:
                detail = error.response.text
        return None, detail


# ---------- CHAT API ----------
def ask_question(question):
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"question": question},
            timeout=180
        )
        response.raise_for_status()
        return response.json(), None

    except requests.exceptions.RequestException as error:
        detail = "Unable to connect to the AI backend."
        if error.response is not None:
            try:
                detail = error.response.json().get("detail", str(error))
            except ValueError:
                detail = error.response.text
        return None, detail


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 🤖 Knowledge Agent")
    st.caption("Enterprise document intelligence")

    st.divider()

    backend = check_backend()

    if backend:
        st.success("Backend connected")
        st.metric("Stored document chunks", backend.get("stored_chunks", 0))
    else:
        st.error("Backend offline")
        st.caption("Start the FastAPI server to continue.")

    st.divider()

    st.markdown("### Upload documents")

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("Process Documents", use_container_width=True):
        if not uploaded_files:
            st.warning("Please select at least one PDF.")
        elif not backend:
            st.error("FastAPI backend is not running.")
        else:
            progress = st.progress(0)
            success_count = 0

            for index, pdf in enumerate(uploaded_files):
                with st.spinner(f"Processing {pdf.name}..."):
                    result, error = upload_pdf(pdf)

                if result:
                    success_count += 1
                    st.session_state.uploaded_docs.append({
                        "name": result["filename"],
                        "pages": result["total_pages"],
                        "chunks": result["stored_chunks"]
                    })
                    st.success(
                        f"{pdf.name}: {result['stored_chunks']} chunks stored"
                    )
                else:
                    st.error(f"{pdf.name}: {error}")

                progress.progress((index + 1) / len(uploaded_files))

            if success_count:
                st.success(f"Successfully processed {success_count} PDF(s).")

    st.divider()

    st.markdown("### Uploaded documents")

    if st.session_state.uploaded_docs:
        for doc in st.session_state.uploaded_docs:
            st.markdown(
                f"**{doc['name']}**  \n"
                f"{doc['pages']} pages · {doc['chunks']} chunks"
            )
    else:
        st.caption("No documents uploaded in this session.")

    st.divider()

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ---------- MAIN CHAT AREA ----------
st.markdown(
    '<div class="main-title">Enterprise AI Knowledge Agent</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Ask questions, retrieve information, and get answers grounded in your PDFs.'
    '</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        '<div class="info-card">📄 <b>PDF Knowledge</b><br>'
        '<small>Upload and process documents</small></div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        '<div class="info-card">🔎 <b>Semantic Search</b><br>'
        '<small>Retrieve relevant document chunks</small></div>',
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        '<div class="info-card">🤖 <b>AI Responses</b><br>'
        '<small>Answers powered by local Ollama</small></div>',
        unsafe_allow_html=True
    )


# ---------- CHAT HISTORY ----------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            with st.expander("View document sources"):
                for source in message["sources"]:
                    st.markdown(
                        f"**{source['source']} — Page {source['page']}**"
                    )
                    st.caption(
                        f"Retrieval distance: {source.get('distance', 'N/A')}"
                    )


# ---------- CHAT INPUT ----------
question = st.chat_input("Ask a question about your uploaded documents...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating an answer..."):
            result, error = ask_question(question)

        if error:
            st.error(error)
        else:
            answer = result.get("answer", "No answer received.")
            sources = result.get("sources", [])

            st.markdown(answer)

            if sources:
                with st.expander("View document sources", expanded=True):
                    for source in sources:
                        st.markdown(
                            f"**{source['source']} — Page {source['page']}**"
                        )
                        st.caption(
                            f"Retrieval distance: {source.get('distance', 'N/A')}"
                        )

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })
