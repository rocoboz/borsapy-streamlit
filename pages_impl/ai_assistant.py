import streamlit as st
from openai import OpenAI
import re
from utils.data_loader import get_ticker_info

def extract_symbols(text):
    # Try to find uppercase words of length 3-6 (common stock/fund symbols)
    matches = re.findall(r'\b[A-Z]{3,6}\b', text)
    # Remove common non-stock words
    stopwords = {"NASIL", "NEDI", "ALINIR", "SATILIR", "GRAFIK", "BIST", "BANKA"}
    symbols = [m for m in matches if m not in stopwords]
    return list(set(symbols))

def fetch_rag_data(symbols):
    rag_text = ""
    for sym in symbols:
        ticker = get_ticker_info(sym)
        if ticker:
            try:
                info = ticker.info
                price = info.get('last', info.get('currentPrice', info.get('regularMarketPrice', 0)))
                chg = info.get('change_percent', info.get('regularMarketChangePercent', 0))
                pe = info.get('trailingPE', 'N/A')
                pb = info.get('priceToBook', 'N/A')
                rag_text += f"- {sym}: Fiyat={price:.2f} ₺, Değişim=%{chg:.2f}, F/K={pe}, PD/DD={pb}\n"
            except:
                pass
    return rag_text

def app():
    st.markdown("""
    <div class="animate-fade-in" style="margin-bottom: 20px;">
        <h1 style="color: #00d2ff; text-align: center;">🤖 Neo-Fintech AI Asistan</h1>
        <p style="text-align: center; opacity: 0.8;">Gerçek zamanlı BorsaPY verileriyle güçlendirilmiş finansal analiz motoru.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. API Key Authentication
    if "openrouter_api_key" not in st.session_state:
        st.session_state.openrouter_api_key = ""
        
    if not st.session_state.openrouter_api_key:
        with st.container():
            st.warning("Asistanı kullanabilmek için lütfen bir OpenRouter API anahtarı girin.")
            api_key = st.text_input("OpenRouter API Anahtarı (sk-or-v1-...)", type="password")
            st.markdown("""
            > 🔒 **Gizlilik & Güvenlik:** API anahtarınız sunucularımızda veya veritabanlarımızda **asla depolanmaz**. Sadece kendi tarayıcınızın geçici hafızasında (local session) tutulur ve model işlemleri haricinde hiçbir yere gönderilmez. Sayfayı kapattığınızda otomatik olarak silinir.
            """)
            if st.button("Asistanı Başlat", use_container_width=True):
                if api_key.startswith("sk-or-"):
                    st.session_state.openrouter_api_key = api_key
                    st.rerun()
                else:
                    st.error("Lütfen geçerli bir OpenRouter anahtarı girin.")
        return

    # 2. Setup AI Client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.session_state.openrouter_api_key,
    )
    
    # Model Selection
    model = st.selectbox("Yapay Zeka Modeli Seçin", [
        "google/gemini-2.5-flash",
        "meta-llama/llama-3-8b-instruct:free",
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o"
    ], index=0)

    # Logout button
    if st.sidebar.button("🔌 API Bağlantısını Kes", key="logout"):
        st.session_state.openrouter_api_key = ""
        st.rerun()

    # 3. Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] != "system": # Hide system prompts
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Hangi hisse veya fon hakkında konuşmak istersiniz?"):
        # Add user message to chat UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # RAG Logic
        with st.spinner("Piyasa verileri taranıyor ve asistan düşünüyor..."):
            symbols = extract_symbols(prompt)
            rag_context = ""
            if symbols:
                rag_data = fetch_rag_data(symbols)
                if rag_data:
                    rag_context = f"Sistem Notu (Canlı Veriler):\n{rag_data}\nLütfen analizini yukarıdaki bu anlık verilere dayanarak, kısa ve öz yap.\n\n"
            
            # Build API messages
            api_messages = [{"role": "system", "content": "Sen profesyonel, analitik ve objektif bir Borsa İstanbul ve kripto uzmanısın. Yorumların yatırım tavsiyesi değildir uyarısını sadece gerektiğinde yap. Yanıtların markdown formatında ve çok şık olmalı."}]
            
            # We don't want to send ALL history's RAG context, just the chat history
            for m in st.session_state.messages[:-1]:
                api_messages.append(m)
                
            # Add latest message WITH RAG context hidden inside it
            api_messages.append({"role": "user", "content": rag_context + prompt})

            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    max_tokens=1000
                )
                ai_reply = response.choices[0].message.content
                
                # Show AI response
                with st.chat_message("assistant"):
                    st.markdown(ai_reply)
                    
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            except Exception as e:
                st.error(f"API Hatası: {str(e)}")
