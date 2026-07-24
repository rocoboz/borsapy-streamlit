import streamlit as st
from openai import OpenAI
import json
import re

def _to_api_message(message):
    if isinstance(message, dict):
        return message
    if hasattr(message, "model_dump"):
        return message.model_dump(exclude_none=True)
    return {
        "role": getattr(message, "role", "assistant"),
        "content": getattr(message, "content", None),
    }

def app():
    # --- Modern Dark UI Styling ---
    from streamlit_lottie import st_lottie
    from utils.ui import load_lottieurl

    st.markdown("""
    <style>
    /* Main Chat Area Polish */
    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
        border: 1px solid var(--border-dark);
        margin-bottom: 10px;
        background: #18181b;
    }
    .stChatMessage[data-testid="chatAvatarIcon-user"] {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .stChatMessage[data-testid="chatAvatarIcon-assistant"] {
        background: rgba(16, 185, 129, 0.05);
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    colA, colB = st.columns([1, 4])
    with colA:
        lottie_ai_url = "https://lottie.host/801a610f-6246-4e58-94df-74f0c43ca3f0/E8w9tJp33y.json"
        lottie_ai_json = load_lottieurl(lottie_ai_url)
        if lottie_ai_json:
            st_lottie(lottie_ai_json, height=100, key="ai_lottie")
            
    with colB:
        st.markdown("""
        <div class="animate-fade-in" style="margin-bottom: 5px;">
            <h3 style="color: #f4f4f5; margin-bottom: 0;">🧠 BorsaPY Süper Ajan</h3>
            <p style="opacity: 0.8; font-size: 0.9em; margin-top: 5px; color: #a1a1aa;">BorsaPY fonksiyonlarını kullanarak profesyonel analiz yapan Ajan.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 1. AI Provider Selection Config (Expanded with NVIDIA NIM, OpenAI, SambaNova, Ollama)
    provider_config = {
        "OpenRouter (Ücretsiz & Ücretli)": {
            "base_url": "https://openrouter.ai/api/v1",
            "state_key": "openrouter_api_key",
            "models": ["openrouter/auto", "openrouter/free", "deepseek/deepseek-r1:free", "google/gemini-3.5-flash", "google/gemini-3.1-pro", "openai/gpt-4o", "anthropic/claude-3.5-sonnet", "meta-llama/llama-4-scout", "Diğer (Özel Model ID Gir)"]
        },
        "OpenAI (Resmi ChatGPT / GPT-4o)": {
            "base_url": "https://api.openai.com/v1",
            "state_key": "openai_api_key",
            "models": ["gpt-4o", "gpt-4o-mini", "o3-mini", "o1", "Diğer (Özel Model ID Gir)"]
        },
        "NVIDIA NIM (Ücretsiz Kredili)": {
            "base_url": "https://integrate.api.nvidia.com/v1",
            "state_key": "nvidia_api_key",
            "models": ["deepseek-ai/deepseek-r1", "meta/llama-3.3-70b-instruct", "nvidia/llama-3.1-nemotron-70b-instruct", "qwen/qwen2.5-72b-instruct", "Diğer (Özel Model ID Gir)"]
        },
        "SambaNova (Ücretsiz & Ultra Hızlı)": {
            "base_url": "https://api.sambanova.ai/v1",
            "state_key": "sambanova_api_key",
            "models": ["Meta-Llama-3.3-70B-Instruct", "DeepSeek-R1-Distill-Llama-70B", "Qwen2.5-Coder-32B-Instruct", "Diğer (Özel Model ID Gir)"]
        },
        "Groq (Ücretsiz Tier)": {
            "base_url": "https://api.groq.com/openai/v1",
            "state_key": "groq_api_key",
            "models": ["llama-4-scout", "qwen3-32b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "Diğer (Özel Model ID Gir)"]
        },
        "DeepSeek": {
            "base_url": "https://api.deepseek.com/v1",
            "state_key": "deepseek_api_key",
            "models": ["deepseek-v4-flash", "deepseek-v4-pro", "deepseek-chat", "Diğer (Özel Model ID Gir)"]
        },
        "Google Gemini": {
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "state_key": "gemini_api_key",
            "models": ["gemini-3.5-flash", "gemini-3.1-pro-preview", "gemini-2.0-flash-001", "gemini-2.0-pro-exp-02-05", "Diğer (Özel Model ID Gir)"]
        },
        "Ollama / Yerel LLM (Ngrok / Localhost)": {
            "base_url": "http://localhost:11434/v1",
            "state_key": "ollama_api_key",
            "models": ["llama3.3", "qwen2.5", "deepseek-r1", "mistral", "gemma2", "Diğer (Özel Model ID Gir)"]
        }
    }

    # Main Screen Top Controls & Settings Panel
    with st.expander("⚙️ Yapay Zeka Ajan Ayarları & Model Seçimi", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            provider_choice = st.selectbox("Yapay Zeka Sağlayıcısı (Provider)", list(provider_config.keys()), index=0)
            conf = provider_config[provider_choice]
            state_key = conf["state_key"]
            
            # Custom Base URL logic for Ollama / Remote LLMs
            target_base_url = conf["base_url"]
            if "Ollama" in provider_choice:
                custom_url = st.text_input(
                    "API Base URL (Ngrok veya Localhost)", 
                    value=st.session_state.get("custom_base_url", conf["base_url"]),
                    help="Yerel bilgisayarınızdaki Ollama'yı public web sitesine bağlamak için Ngrok URL'inizi yazın (örn: https://xxxx.ngrok-free.app/v1)."
                )
                if custom_url:
                    target_base_url = custom_url.strip()
                    st.session_state["custom_base_url"] = target_base_url
                    
        with c2:
            model_choice = st.selectbox("Yapay Zeka Modeli", conf["models"], index=0)
            if model_choice == "Diğer (Özel Model ID Gir)":
                model = st.text_input("Özel Model ID", help="Sağlayıcının desteklediği model ID'si.")
                if not model:
                    st.warning("⚠️ Lütfen bir Model ID girin.")
                    st.stop()
            else:
                model = model_choice
        with c3:
            reasoning_choice = st.selectbox("Düşünme Seviyesi (Reasoning)", ["Yok (Standart)", "low", "medium", "high"], index=0, help="Sadece Gemini 3.5 Flash ve o1 gibi destekleyen modellerde çalışır.")

        if "Ollama" in provider_choice:
            st.info("🌐 **Yerel LLM'inizi Public Sitede Kullanma Rehberi:**\n1. Bilgisayarınızda terminal açın ve Ollama'yı başlatın: `ollama serve`\n2. Ücretsiz Ngrok ile port açın: `ngrok http 11434`\n3. Verilen `https://xxxx.ngrok-free.app` adresinin sonuna `/v1` ekleyerek yukarıdaki Base URL alanına yapıştırın.")

        st.markdown("---")
        
        # Action Buttons row inside expander
        bcol1, bcol2, bcol3 = st.columns(3)
        with bcol1:
            if st.button(f"🔌 {provider_choice} Bağlantısını Kes", key="logout", use_container_width=True):
                st.session_state[state_key] = ""
                st.rerun()
        with bcol2:
            if st.button("🧹 Sohbet Geçmişini Temizle", key="clear_chat", help="Tüm sohbet geçmişini ve ajan bağlamını sıfırlar.", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with bcol3:
            if "messages" in st.session_state and len(st.session_state.messages) > 0:
                chat_export_text = "# BorsaPY AI Asistan Analiz Raporu\n\n"
                for m in st.session_state.messages:
                    role_name = "👤 Kullanıcı" if m.get("role") == "user" else "🤖 BorsaPY Ajanı"
                    content = m.get("content")
                    if content and isinstance(content, str):
                        chat_export_text += f"### {role_name}\n{content}\n\n---\n\n"
                st.download_button(
                    label="💾 Sohbet Raporunu İndir",
                    data=chat_export_text,
                    file_name="borsapy_ai_analiz.md",
                    mime="text/markdown",
                    key="download_chat_md",
                    use_container_width=True
                )

    # Auto-set dummy key for Ollama / Yerel LLM
    if "Ollama" in provider_choice and not st.session_state.get(state_key):
        st.session_state[state_key] = "ollama"

    # Keep user API keys in session, check st.secrets fallback for public deployment
    if state_key not in st.session_state or not st.session_state[state_key]:
        try:
            sec_val = st.secrets.get(state_key.upper(), "") or st.secrets.get(state_key, "")
            if sec_val:
                st.session_state[state_key] = sec_val
            else:
                st.session_state[state_key] = ""
        except Exception:
            st.session_state[state_key] = ""
            
    # Login Screen if no key
    if not st.session_state[state_key]:
        with st.container():
            st.warning(f"Ajanı kullanabilmek için lütfen bir {provider_choice} API anahtarı girin.")
            api_key = st.text_input(f"{provider_choice} API Anahtarı", type="password", key=f"input_{state_key}")
            st.markdown("> 🔒 **Public Kullanım Güvenliği:** API anahtarınız bu Streamlit oturumunda bellekte isolasyon altında tutulur; diske, sunucuya veya ortak veritabanına kaydedilmez. Oturum kapandığında silinir.")
            if st.button("Ajanı Başlat", use_container_width=True):
                if api_key:
                    st.session_state[state_key] = api_key
                    st.rerun()
                else:
                    st.error("Lütfen geçerli bir anahtar girin.")
        return

    # 2. Setup AI Client (Supports custom Base URL for Ngrok / Remote Ollama)
    client = OpenAI(
        base_url=target_base_url,
        api_key=st.session_state[state_key],
    )

    # 4. Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Mesaj geçmişini son 100 girdi ile sınırla (token context genişletildi)
    MAX_HISTORY = 100
    if len(st.session_state.messages) > MAX_HISTORY:
        st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]
        
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

    # 3.5. Quick Suggestions (Hazır Promptlar)
    st.markdown("##### 💡 Örnek Sorgular (Hızlı Başlat)")
    
    # Kategori bazlı hazır örnekler
    suggestions = [
        {"icon": "🏢", "label": "Hisse Önerisi", "prompt": "BIST 100 endeksinde F/K oranı 15'ten küçük ve kârlılığı yüksek alınabilir hisseleri bul"},
        {"icon": "📈", "label": "THYAO Analiz", "prompt": "THYAO hissesinin teknik göstergeleri (RSI, MACD, SMA) ve en son KAP haberleri ne durumda?"},
        {"icon": "🪙", "label": "Kripto Durumu", "prompt": "Bitcoin on-chain durumunu ve piyasa korku/açgözlülük endeksini analiz et"},
        {"icon": "📊", "label": "En İyi Fonlar", "prompt": "Son 1 yılda en yüksek getiri sağlayan TEFAS yatırım fonlarını listele"},
        {"icon": "🌍", "label": "Makro Görünüm", "prompt": "Küresel piyasalarda (S&P 500, VIX, DXY), tahvillerde ve petrol fiyatlarında son durum nedir?"},
        {"icon": "🎰", "label": "ASIAA Varantı", "prompt": "ASIAA varantının dayanak varlığı (ASELS) için teknik trende göre Call/Put varant senaryolarını anlat"}
    ]
    
    # 3'lü gridler halinde butonları çizdir
    cols_s = st.columns(3)
    clicked_prompt = None
    for idx, sug in enumerate(suggestions):
        col = cols_s[idx % 3]
        if col.button(f"{sug['icon']} {sug['label']}", key=f"sug_{idx}", use_container_width=True):
            clicked_prompt = sug["prompt"]
            
    # Eğer hazır butona tıklandıysa prompt'u ata veya chat input'u oku
    prompt = None
    if clicked_prompt:
        prompt = clicked_prompt
    
    # Chat Input
    chat_prompt = st.chat_input("Hisse, fon veya makro veriler hakkında soru sorun...")
    if chat_prompt:
        prompt = chat_prompt

    if prompt:
        # Add user message to chat UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Agent Loop
        with st.status("Swarm Orkestratörü piyasayı analiz ediyor...", expanded=True) as status_container:
            from agents.prompts import ROUTER_PROMPT, STOCK_EXPERT_PROMPT, CRYPTO_EXPERT_PROMPT, FUND_EXPERT_PROMPT, MACRO_EXPERT_PROMPT, WARRANT_EXPERT_PROMPT
            from agents.schemas import ROUTER_SCHEMA, STOCK_SCHEMA, CRYPTO_SCHEMA, FUND_SCHEMA, MACRO_SCHEMA, WARRANT_SCHEMA
            from agents.tools import (
                get_stock_financials, get_multiple_stock_financials, get_stock_technicals, screen_bist_stocks,
                get_crypto_technicals, get_crypto_momentum,
                get_fund_performance, get_fund_allocation, get_fund_risk_metrics, screen_top_funds,
                get_tcmb_rates, get_macro_overview, get_fear_greed_index, get_brent_oil_price, get_turkish_bond_yields,
                transfer_to_stock_expert, transfer_to_crypto_expert, transfer_to_fund_expert, transfer_to_macro_expert, transfer_to_warrant_expert
            )
            from utils.ai_tools import get_latest_news, get_global_news, get_macro_events, get_currency_and_gold_price
            
            ALL_TOOLS_MAP = {
                "get_stock_financials": get_stock_financials,
                "get_multiple_stock_financials": get_multiple_stock_financials,
                "get_stock_technicals": get_stock_technicals,
                "screen_bist_stocks": screen_bist_stocks,
                "get_latest_news": get_latest_news,
                "get_global_news": get_global_news,
                "get_macro_events": get_macro_events,
                "get_crypto_technicals": get_crypto_technicals,
                "get_crypto_momentum": get_crypto_momentum,
                "get_fund_performance": get_fund_performance,
                "get_fund_allocation": get_fund_allocation,
                "get_fund_risk_metrics": get_fund_risk_metrics,
                "screen_top_funds": screen_top_funds,
                "get_currency_and_gold_price": get_currency_and_gold_price,
                "get_tcmb_rates": get_tcmb_rates,
                "get_macro_overview": get_macro_overview,
                "get_fear_greed_index": get_fear_greed_index,
                "get_brent_oil_price": get_brent_oil_price,
                "get_turkish_bond_yields": get_turkish_bond_yields,
                "transfer_to_stock_expert": transfer_to_stock_expert,
                "transfer_to_crypto_expert": transfer_to_crypto_expert,
                "transfer_to_fund_expert": transfer_to_fund_expert,
                "transfer_to_macro_expert": transfer_to_macro_expert,
                "transfer_to_warrant_expert": transfer_to_warrant_expert
            }

            if "current_agent" not in st.session_state:
                st.session_state.current_agent = "router"
            
            # Reset to router for each new message to ensure proper routing
            st.session_state.current_agent = "router"

            api_messages = [{"role": "system", "content": ""}] # Placeholder for system prompt
            
            # --- SMART CONTEXT PRUNER PIPELINE ---
            # Find the index of the latest user message
            last_user_idx = -1
            for i, m in enumerate(st.session_state.messages):
                r = m.get("role") if isinstance(m, dict) else getattr(m, "role", "")
                if r == "user":
                    last_user_idx = i
                    
            for i, m in enumerate(st.session_state.messages):
                is_dict = isinstance(m, dict)
                role = m.get("role") if is_dict else getattr(m, "role", "")
                content = m.get("content") if is_dict else getattr(m, "content", None)
                tool_calls = m.get("tool_calls") if is_dict else getattr(m, "tool_calls", None)
                
                if i >= last_user_idx:
                    # Current turn: Keep everything exactly as is for the active tool loop
                    api_messages.append(m)
                else:
                    # Past turns (History pruning)
                    if role == "tool":
                        continue # Drop raw JSON tool responses to save tokens
                    
                    if role == "assistant":
                        if tool_calls and not content:
                            continue # Drop purely functional 'I am calling a tool' messages
                        
                        if is_dict:
                            # Strip tool_calls to prevent API validation errors
                            clean_m = {k: v for k, v in m.items() if k != "tool_calls"}
                            api_messages.append(clean_m)
                        else:
                            api_messages.append({"role": "assistant", "content": content})
                    else:
                        api_messages.append(m)
            # ------------------------------------

            max_tool_calls = 15
            tool_call_count = 0
            
            while tool_call_count < max_tool_calls:
                try:
                    # Dynamically set agent prompt and tools
                    agent_config = {
                        "router": {"prompt": ROUTER_PROMPT, "schema": ROUTER_SCHEMA},
                        "stock": {"prompt": STOCK_EXPERT_PROMPT, "schema": STOCK_SCHEMA},
                        "crypto": {"prompt": CRYPTO_EXPERT_PROMPT, "schema": CRYPTO_SCHEMA},
                        "fund": {"prompt": FUND_EXPERT_PROMPT, "schema": FUND_SCHEMA},
                        "macro": {"prompt": MACRO_EXPERT_PROMPT, "schema": MACRO_SCHEMA},
                        "warrant": {"prompt": WARRANT_EXPERT_PROMPT, "schema": WARRANT_SCHEMA}
                    }
                    curr_cfg = agent_config[st.session_state.current_agent]
                    
                    system_prompt = curr_cfg["prompt"]
                    api_messages[0] = {"role": "system", "content": system_prompt}
                    
                    kwargs = {
                        "model": model,
                        "messages": api_messages,
                        "tools": curr_cfg["schema"],
                        "tool_choice": "auto",
                        "max_tokens": 16384
                    }
                    if reasoning_choice != "Yok (Standart)":
                        kwargs["reasoning_effort"] = reasoning_choice
                        
                    response = client.chat.completions.create(**kwargs)
                    
                    response_message = response.choices[0].message
                    
                    if response_message.tool_calls:
                        # Store provider responses as plain dicts for OpenAI-compatible API stability.
                        assistant_msg = _to_api_message(response_message)
                        api_messages.append(assistant_msg)
                        st.session_state.messages.append(assistant_msg)
                        
                        for tool_call in response_message.tool_calls:
                            function_name = tool_call.function.name
                            function_to_call = ALL_TOOLS_MAP.get(function_name)
                            
                            st.toast(f"{st.session_state.current_agent.upper()} Ajanı çalışıyor: {function_name}()", icon="⚙️")
                            status_container.write(f"⚙️ **{st.session_state.current_agent.upper()}** veri çekiyor: `{function_name}()`")
                            
                            # Handle dynamic agent transfers
                            if function_name == "transfer_to_stock_expert":
                                st.session_state.current_agent = "stock"
                                st.toast("Ajan Değiştirildi: Hisse Uzmanı devrede!", icon="🏢")
                                status_container.write("🔀 **Yönlendirme:** 🏢 Hisse Senedi Uzmanına aktarıldı!")
                            elif function_name == "transfer_to_crypto_expert":
                                st.session_state.current_agent = "crypto"
                                st.toast("Ajan Değiştirildi: Kripto Uzmanı devrede!", icon="🪙")
                                status_container.write("🔀 **Yönlendirme:** 🪙 Kripto Uzmanına aktarıldı!")
                            elif function_name == "transfer_to_fund_expert":
                                st.session_state.current_agent = "fund"
                                st.toast("Ajan Değiştirildi: Fon Uzmanı devrede!", icon="📊")
                                status_container.write("🔀 **Yönlendirme:** 📊 Fon Uzmanına aktarıldı!")
                            elif function_name == "transfer_to_macro_expert":
                                st.session_state.current_agent = "macro"
                                st.toast("Ajan Değiştirildi: Makro & Emtia Uzmanı devrede!", icon="🌍")
                                status_container.write("🔀 **Yönlendirme:** 🌍 Makro & Emtia Uzmanına aktarıldı!")
                            elif function_name == "transfer_to_warrant_expert":
                                st.session_state.current_agent = "warrant"
                                st.toast("Ajan Değiştirildi: Varant & Türev Uzmanı devrede!", icon="🎰")
                                status_container.write("🔀 **Yönlendirme:** 🎰 Varant & Türev Uzmanına aktarıldı!")
                            if function_to_call:
                                try:
                                    function_args = json.loads(tool_call.function.arguments)
                                    function_response = function_to_call(**function_args)
                                except json.JSONDecodeError:
                                    function_response = json.dumps({"error": "Invalid JSON arguments generated by AI."})
                                except Exception as e:
                                    function_response = json.dumps({"error": f"Tool execution error: {str(e)}"})
                                
                                tool_msg = {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": function_name,
                                    "content": function_response,
                                }
                                # Sadece transfer fonksiyonu DEĞİLSE api_messages'a ekle (DeepSeek/Llama uyumluluğu için)
                                if not function_name.startswith("transfer_to_"):
                                    api_messages.append(tool_msg)
                                st.session_state.messages.append(tool_msg)
                            else:
                                tool_msg = {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": function_name,
                                    "content": json.dumps({"error": "Function not found"}),
                                }
                                if not function_name.startswith("transfer_to_"):
                                    api_messages.append(tool_msg)
                                st.session_state.messages.append(tool_msg)
                        
                        # Eğer transfer gerçekleştiyse, son eklenen asistan transfer istek mesajını (tool_calls barındıran)
                        # api_messages listesinden kaldırıyoruz ki bir sonraki turda yeni ajanın şemasıyla çelişmesin.
                        is_transfer = any(tc.function.name.startswith("transfer_to_") for tc in response_message.tool_calls)
                        if is_transfer and api_messages and api_messages[-1] == assistant_msg:
                            api_messages.pop()
                            
                        tool_call_count += 1
                    else:
                        ai_reply = response_message.content
                        status_container.update(label="Analiz Tamamlandı!", state="complete", expanded=False)
                        with st.chat_message("assistant"):
                            st.markdown(ai_reply)
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                        break
                except Exception as e:
                    status_container.update(label="API Bağlantı Hatası!", state="error", expanded=True)
                    err_str = str(e)
                    if "401" in err_str or "Unauthorized" in err_str or "api_key" in err_str.lower():
                        st.error("🔒 **Geçersiz API Anahtarı (401):** Girdiğiniz anahtar hatalı veya süresi dolmuş. Lütfen anahtarı kontrol edip 'Bağlantıyı Kes' ile tekrar giriş yapın.")
                    elif "429" in err_str or "rate limit" in err_str.lower() or "quota" in err_str.lower():
                        st.error("⏳ **İstek Limiti Aşıldı (429):** Bu model için istek limitiniz doldu. Birkaç dakika bekleyin veya farklı bir model deneyin.")
                    elif "503" in err_str or "overloaded" in err_str.lower() or "unavailable" in err_str.lower():
                        st.error("🔄 **Model Geçici Olarak Meşgul (503):** Seçilen model şu an yoğun veya kullanılamıyor. Farklı bir model deneyin.")
                    else:
                        st.error(f"🚨 **Süper Ajan API Hatası:** {err_str}")
                    break
            else:
                fallback_reply = (
                    "Analiz döngüsü beklenenden fazla veri aracı çağırdı ve güvenlik limiti nedeniyle durduruldu. "
                    "Lütfen soruyu biraz daraltarak tekrar deneyin."
                )
                status_container.update(label="Analiz güvenlik limitiyle durduruldu.", state="error", expanded=True)
                st.warning(fallback_reply)
                st.session_state.messages.append({"role": "assistant", "content": fallback_reply})
