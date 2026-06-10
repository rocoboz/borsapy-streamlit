import streamlit as st
from openai import OpenAI
import json
import re

def app():
    import os
    st.markdown("""
    <div class="animate-fade-in" style="margin-bottom: 5px;">
        <h3 style="color: #00d2ff; text-align: center; margin-bottom: 0;">🤖 Neo-Fintech Süper Ajan</h3>
        <p style="text-align: center; opacity: 0.8; font-size: 0.9em; margin-top: 5px;">BorsaPY fonksiyonlarını kullanarak profesyonel analiz yapan Ajan.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. AI Provider Selection
    st.sidebar.markdown("### 🤖 Ajan Ayarları")
    provider_choice = st.sidebar.selectbox("Yapay Zeka Sağlayıcısı (Provider)", ["OpenRouter", "Groq", "DeepSeek", "Google Gemini"], index=0)
    
    provider_config = {
        "OpenRouter": {
            "base_url": "https://openrouter.ai/api/v1",
            "key_file": ".openrouter_key",
            "state_key": "openrouter_api_key",
            "models": ["openrouter/auto", "openrouter/free", "google/gemini-3.5-flash", "google/gemini-3.1-pro", "openai/gpt-4o", "anthropic/claude-3.5-sonnet", "meta-llama/llama-4-scout", "Diğer (Özel Model ID Gir)"]
        },
        "Groq": {
            "base_url": "https://api.groq.com/openai/v1",
            "key_file": ".groq_key",
            "state_key": "groq_api_key",
            "models": ["llama-4-scout", "qwen3-32b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "Diğer (Özel Model ID Gir)"]
        },
        "DeepSeek": {
            "base_url": "https://api.deepseek.com/v1",
            "key_file": ".deepseek_key",
            "state_key": "deepseek_api_key",
            "models": ["deepseek-v4-flash", "deepseek-v4-pro", "deepseek-chat", "Diğer (Özel Model ID Gir)"]
        },
        "Google Gemini": {
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "key_file": ".gemini_key",
            "state_key": "gemini_api_key",
            "models": ["gemini-3.5-flash", "gemini-3.1-pro", "gemini-3.1-flash-lite", "gemini-2.5-flash", "Diğer (Özel Model ID Gir)"]
        }
    }
    
    conf = provider_config[provider_choice]
    KEY_FILE = conf["key_file"]
    state_key = conf["state_key"]
    
    # Check if key exists in file
    if state_key not in st.session_state:
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "r") as f:
                st.session_state[state_key] = f.read().strip()
        else:
            st.session_state[state_key] = ""
            
    # Login Screen if no key
    if not st.session_state[state_key]:
        with st.container():
            st.warning(f"Ajanı kullanabilmek için lütfen bir {provider_choice} API anahtarı girin.")
            api_key = st.text_input(f"{provider_choice} API Anahtarı", type="password")
            st.markdown(f"> 🔒 **Gizlilik:** Anahtarınız sadece bilgisayarınızda **{KEY_FILE}** dosyasında şifresiz olarak saklanır.")
            if st.button("Ajanı Başlat", use_container_width=True):
                if api_key:
                    st.session_state[state_key] = api_key
                    with open(KEY_FILE, "w") as f:
                        f.write(api_key)
                    st.rerun()
                else:
                    st.error("Lütfen geçerli bir anahtar girin.")
        return

    # 2. Setup AI Client
    client = OpenAI(
        base_url=conf["base_url"],
        api_key=st.session_state[state_key],
    )
    
    # Model Selection
    model_choice = st.sidebar.selectbox("Yapay Zeka Modeli Seçin", conf["models"], index=0)
    
    if model_choice == "Diğer (Özel Model ID Gir)":
        model = st.sidebar.text_input("Özel Model ID", help="Sağlayıcının desteklediği herhangi bir model ID'sini yazın.")
    else:
        model = model_choice

    # Logout button
    if st.sidebar.button(f"🔌 {provider_choice} Bağlantısını Kes", key="logout"):
        st.session_state[state_key] = ""
        if os.path.exists(KEY_FILE):
            os.remove(KEY_FILE)
        st.rerun()

    # 3. Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Display chat history
    for msg in st.session_state.messages:
        role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", "")
        if role != "system" and role != "tool": 
            # hide system and tool messages, and assistant tool calls
            if role == "assistant" and getattr(msg, "tool_calls", None):
                continue
            if isinstance(msg, dict):
                content = msg.get("content")
                if content:
                    with st.chat_message(role):
                        st.markdown(content)
            else:
                # msg is an object (like ChatCompletionMessage)
                if getattr(msg, "content", None):
                    with st.chat_message(role):
                        st.markdown(msg.content)

    # Chat Input
    if prompt := st.chat_input("Hisse, fon veya makro veriler hakkında soru sorun..."):
        # Add user message to chat UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Agent Loop
        with st.spinner("Süper Ajan piyasa verilerini analiz ediyor..."):
            from utils.ai_tools import AI_TOOLS_SCHEMA, AI_TOOLS_MAP
            
            # Build API messages for the current run
            api_messages = [{"role": "system", "content": "Sen profesyonel bir borsa ve finans analistisin. ŞU KURALLARA KESİNLİKLE UYACAKSIN: 1) Kullanıcı senden *spesifik bir hisse veya fon analizi* istediğinde, metin cevabı yazmadan ÖNCE MUTLAKA şu 6 aracı çağırıp verileri topla: get_live_price, get_financial_metrics, get_technical_analysis, get_latest_news, get_global_news, get_macro_events. 2) Kullanıcı sadece *genel piyasa durumu, dünya haberleri veya makro beklentiler* hakkında bilgi isterse `get_global_news` ve `get_macro_events` araçlarını kullan. Asla 'şu verilere siz bakın' deme. Sadece araçlardan gelen GERÇEK verilerle yorum yap, asla rakam veya haber uydurma. Eğer araç hata verirse 'Veri çekilemedi' de geç. Çıktılarını temiz Markdown ile, tablolar ve emojiler kullanarak sun."}]
            
            # Add conversation history
            for m in st.session_state.messages:
                api_messages.append(m)

            max_tool_calls = 10
            tool_call_count = 0
            
            while tool_call_count < max_tool_calls:
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=api_messages,
                        tools=AI_TOOLS_SCHEMA,
                        tool_choice="auto",
                        max_tokens=2500
                    )
                    
                    response_message = response.choices[0].message
                    
                    if response_message.tool_calls:
                        # Add assistant tool call request to messages
                        api_messages.append(response_message)
                        st.session_state.messages.append(response_message)
                        
                        for tool_call in response_message.tool_calls:
                            function_name = tool_call.function.name
                            function_to_call = AI_TOOLS_MAP.get(function_name)
                            
                            st.toast(f"Ajan çalıştırıyor: {function_name}()", icon="⚙️")
                            
                            if function_to_call:
                                function_args = json.loads(tool_call.function.arguments)
                                function_response = function_to_call(
                                    symbol=function_args.get("symbol")
                                )
                                
                                tool_msg = {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": function_name,
                                    "content": function_response,
                                }
                                api_messages.append(tool_msg)
                                st.session_state.messages.append(tool_msg)
                            else:
                                tool_msg = {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": function_name,
                                    "content": json.dumps({"error": "Function not found"}),
                                }
                                api_messages.append(tool_msg)
                                st.session_state.messages.append(tool_msg)
                        tool_call_count += 1
                    else:
                        ai_reply = response_message.content
                        with st.chat_message("assistant"):
                            st.markdown(ai_reply)
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                        break
                except Exception as e:
                    st.error(f"Süper Ajan API Hatası: {str(e)}")
                    break
