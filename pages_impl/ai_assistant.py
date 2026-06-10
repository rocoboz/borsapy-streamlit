import streamlit as st
from openai import OpenAI
import json
import re

def render_ai_chart(symbol):
    from utils.data_loader import get_stock_history
    import plotly.graph_objects as go
    
    df = get_stock_history(symbol, period="3mo")
    if not df.empty and 'Close' in df.columns:
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'])])
        fig.update_layout(
            title=f"{symbol} Son 3 Aylık Fiyat Grafiği",
            xaxis_title="",
            yaxis_title="",
            template="plotly_dark",
            margin=dict(l=10, r=10, t=30, b=10),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"📊 {symbol} için grafik çizilemedi (Veri yok).")

def render_message_with_charts(content):
    # Split content by [CHART: SYMBOL]
    parts = re.split(r'\[CHART:\s*([A-Za-z0-9_-]+)\]', content)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                st.markdown(part)
        else:
            symbol = part.strip().upper()
            render_ai_chart(symbol)

def app():
    st.markdown("""
    <div class="animate-fade-in" style="margin-bottom: 20px;">
        <h1 style="color: #00d2ff; text-align: center;">🤖 Neo-Fintech Süper Ajan</h1>
        <p style="text-align: center; opacity: 0.8;">BorsaPY fonksiyonlarını kendi kendine kullanarak profesyonel analiz yapan Ajan.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. API Key Authentication
    if "openrouter_api_key" not in st.session_state:
        st.session_state.openrouter_api_key = ""
        
    if not st.session_state.openrouter_api_key:
        with st.container():
            st.warning("Ajanı kullanabilmek için lütfen bir OpenRouter API anahtarı girin.")
            api_key = st.text_input("OpenRouter API Anahtarı (sk-or-v1-...)", type="password")
            st.markdown("""
            > 🔒 **Gizlilik & Güvenlik:** API anahtarınız sunucularımızda veya veritabanlarımızda **asla depolanmaz**. Sadece kendi tarayıcınızın geçici hafızasında (local session) tutulur ve model işlemleri haricinde hiçbir yere gönderilmez. Sayfayı kapattığınızda otomatik olarak silinir.
            """)
            if st.button("Ajanı Başlat", use_container_width=True):
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
    model_choice = st.selectbox("Yapay Zeka Modeli Seçin", [
        "google/gemini-2.5-flash",
        "openai/gpt-4o",
        "anthropic/claude-3.5-sonnet",
        "meta-llama/llama-3.1-8b-instruct",
        "Diğer (Özel Model ID Gir)"
    ], index=0)
    
    if model_choice == "Diğer (Özel Model ID Gir)":
        model = st.text_input("OpenRouter Model ID", value="openrouter/auto", help="OpenRouter'da bulunan herhangi bir model ID'sini yazabilirsiniz (örn: deepseek/deepseek-chat, google/gemini-pro vb.)")
    else:
        model = model_choice

    # Logout button
    if st.sidebar.button("🔌 API Bağlantısını Kes", key="logout"):
        st.session_state.openrouter_api_key = ""
        st.rerun()

    # 3. Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] != "system" and msg["role"] != "tool": 
            # hide system and tool messages, and assistant tool calls
            if msg["role"] == "assistant" and getattr(msg, "tool_calls", None):
                continue
            if isinstance(msg, dict):
                content = msg.get("content")
                if content:
                    with st.chat_message(msg["role"]):
                        render_message_with_charts(content)
            else:
                # msg is an object (like ChatCompletionMessage)
                if msg.content:
                    with st.chat_message(msg.role):
                        render_message_with_charts(msg.content)

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
            api_messages = [{"role": "system", "content": "Sen profesyonel, analitik ve objektif bir finans, borsa ve kripto uzmanısın. Gerçek verilere dayalı yorum yaparsın. İhtiyacın olan veriyi çekmek için sana verilen fonksiyonları (tools) çağırmalısın. DİKKAT: Kesinlikle geçmiş eğitim verilerini kullanarak rakam uydurma (hallucinate). Araçların sana vermediği hiçbir oranı, haberi veya fiyatı analize ekleme. Eğer elinde o veri yoksa net bir şekilde 'Şu an bu veriye ulaşamıyorum' de. Çıktılarını kullanıcıya sunarken daima temiz, okunabilir Markdown formatı kullan. Önemli rakamları kalın (bold) yaz, liste veya tablolarla veriyi düzenli bir şekilde sun ve emoji kullanarak metni sıkıcılıktan kurtar. EĞER kullanıcı bir hisse, emtia, döviz veya fon için grafik çizmeni isterse veya analizi grafikle desteklemenin iyi olacağını düşünüyorsan, metnin tam o noktasına [CHART: SEMBOL] formatında bir komut ekle. Örn: [CHART: THYAO] veya [CHART: gram-altin] veya [CHART: USD]."}]
            
            # Add conversation history
            for m in st.session_state.messages:
                api_messages.append(m)

            max_tool_calls = 5
            tool_call_count = 0
            
            while tool_call_count < max_tool_calls:
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=api_messages,
                        tools=AI_TOOLS_SCHEMA,
                        tool_choice="auto"
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
                            render_message_with_charts(ai_reply)
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                        break
                except Exception as e:
                    st.error(f"Süper Ajan API Hatası: {str(e)}")
                    break
