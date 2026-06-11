import streamlit as st
from openai import OpenAI
import json
import os
import re

PROFILE_FILE = "user_profile.json"

def load_profile():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_profile(data):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def app():
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
            "state_key": "openrouter_api_key",
            "models": ["openrouter/auto", "openrouter/free", "google/gemini-3.5-flash", "google/gemini-3.1-pro", "openai/gpt-4o", "anthropic/claude-3.5-sonnet", "meta-llama/llama-4-scout", "Diğer (Özel Model ID Gir)"]
        },
        "Groq": {
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
            "models": ["gemini-3.5-flash", "gemini-3.1-pro", "gemini-3.1-flash-lite", "gemini-2.5-flash", "Diğer (Özel Model ID Gir)"]
        }
    }
    
    conf = provider_config[provider_choice]
    state_key = conf["state_key"]
    
    # Check if key exists in session state
    if state_key not in st.session_state:
        st.session_state[state_key] = ""
            
    # Login Screen if no key
    if not st.session_state[state_key]:
        with st.container():
            st.warning(f"Ajanı kullanabilmek için lütfen bir {provider_choice} API anahtarı girin.")
            api_key = st.text_input(f"{provider_choice} API Anahtarı", type="password")
            st.markdown("> 🔒 **Gizlilik:** Anahtarınız sunucuya veya herhangi bir dosyaya kaydedilmez. Sadece bu oturum (session) boyunca tarayıcı belleğinde geçici olarak saklanır.")
            if st.button("Ajanı Başlat", use_container_width=True):
                if api_key:
                    st.session_state[state_key] = api_key
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
        st.rerun()

    st.sidebar.divider()

    # 3. User Profile System
    st.sidebar.markdown("### 👤 Yatırımcı Profilim")
    st.sidebar.markdown("<small>Ajanlar analizlerini bu profile göre kişiselleştirir. Boş bırakılabilir.</small>", unsafe_allow_html=True)
    
    profile = load_profile()
    
    with st.sidebar.expander("Profili Düzenle", expanded=False):
        p_age = st.number_input("Yaşınız", min_value=18, max_value=100, value=profile.get("age", 30))
        p_risk = st.selectbox("Risk İştahınız", ["Düşük (Garantici)", "Orta (Dengeli)", "Yüksek (Agresif)"], 
                              index=["Düşük (Garantici)", "Orta (Dengeli)", "Yüksek (Agresif)"].index(profile.get("risk", "Orta (Dengeli)")))
        p_goal = st.selectbox("Yatırım Amacınız", ["Emeklilik Birikimi", "Orta Vade Büyüme", "Kısa Vade Vurgun / Al-Sat", "Temettü / Pasif Gelir"], 
                              index=["Emeklilik Birikimi", "Orta Vade Büyüme", "Kısa Vade Vurgun / Al-Sat", "Temettü / Pasif Gelir"].index(profile.get("goal", "Orta Vade Büyüme")))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Kaydet", use_container_width=True):
                save_profile({"age": p_age, "risk": p_risk, "goal": p_goal})
                st.toast("Profil başarıyla kaydedildi!", icon="✅")
                st.rerun()
        with col2:
            if st.button("Sil", use_container_width=True):
                if os.path.exists(PROFILE_FILE):
                    os.remove(PROFILE_FILE)
                st.toast("Profil silindi!", icon="🗑️")
                st.rerun()

    # 4. Chat Interface
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
        with st.spinner("Swarm Orkestratörü piyasayı analiz ediyor..."):
            from agents.prompts import ROUTER_PROMPT, STOCK_EXPERT_PROMPT, CRYPTO_EXPERT_PROMPT, FUND_EXPERT_PROMPT, MACRO_EXPERT_PROMPT
            from agents.schemas import ROUTER_SCHEMA, STOCK_SCHEMA, CRYPTO_SCHEMA, FUND_SCHEMA, MACRO_SCHEMA
            from agents.tools import (
                get_stock_financials, get_multiple_stock_financials, get_stock_technicals, 
                get_crypto_technicals, get_crypto_momentum,
                get_fund_performance, get_fund_allocation, get_fund_risk_metrics,
                transfer_to_stock_expert, transfer_to_crypto_expert, transfer_to_fund_expert, transfer_to_macro_expert
            )
            from utils.ai_tools import get_latest_news, get_global_news, get_macro_events, get_currency_and_gold_price
            
            ALL_TOOLS_MAP = {
                "get_stock_financials": get_stock_financials,
                "get_multiple_stock_financials": get_multiple_stock_financials,
                "get_stock_technicals": get_stock_technicals,
                "get_latest_news": get_latest_news,
                "get_global_news": get_global_news,
                "get_macro_events": get_macro_events,
                "get_crypto_technicals": get_crypto_technicals,
                "get_crypto_momentum": get_crypto_momentum,
                "get_fund_performance": get_fund_performance,
                "get_fund_allocation": get_fund_allocation,
                "get_fund_risk_metrics": get_fund_risk_metrics,
                "get_currency_and_gold_price": get_currency_and_gold_price,
                "transfer_to_stock_expert": transfer_to_stock_expert,
                "transfer_to_crypto_expert": transfer_to_crypto_expert,
                "transfer_to_fund_expert": transfer_to_fund_expert,
                "transfer_to_macro_expert": transfer_to_macro_expert
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

            max_tool_calls = 10
            tool_call_count = 0
            
            while tool_call_count < max_tool_calls:
                try:
                    # Dynamically set agent prompt and tools
                    agent_config = {
                        "router": {"prompt": ROUTER_PROMPT, "schema": ROUTER_SCHEMA},
                        "stock": {"prompt": STOCK_EXPERT_PROMPT, "schema": STOCK_SCHEMA},
                        "crypto": {"prompt": CRYPTO_EXPERT_PROMPT, "schema": CRYPTO_SCHEMA},
                        "fund": {"prompt": FUND_EXPERT_PROMPT, "schema": FUND_SCHEMA},
                        "macro": {"prompt": MACRO_EXPERT_PROMPT, "schema": MACRO_SCHEMA}
                    }
                    curr_cfg = agent_config[st.session_state.current_agent]
                    
                    # Inject User Profile into Prompt
                    system_prompt = curr_cfg["prompt"]
                    profile_data = load_profile()
                    if profile_data:
                        profile_str = f"\n\n🚨 DİKKAT! KULLANICI PROFİLİ 🚨\n- Yaş: {profile_data.get('age')}\n- Risk İştahı: {profile_data.get('risk')}\n- Yatırım Amacı: {profile_data.get('goal')}\nLÜTFEN TÜM ANALİZLERİNİ VE GÜVEN SKORUNU BU KULLANICI PROFİLİNE (RİSK İŞTAHINA VE AMACINA) GÖRE KİŞİSELLEŞTİR!"
                        system_prompt += profile_str
                        
                    api_messages[0] = {"role": "system", "content": system_prompt}
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=api_messages,
                        tools=curr_cfg["schema"],
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
                            function_to_call = ALL_TOOLS_MAP.get(function_name)
                            
                            st.toast(f"{st.session_state.current_agent.upper()} Ajanı çalışıyor: {function_name}()", icon="⚙️")
                            
                            # Handle dynamic agent transfers
                            if function_name == "transfer_to_stock_expert":
                                st.session_state.current_agent = "stock"
                                st.toast("Ajan Değiştirildi: Hisse Uzmanı devrede!", icon="🏢")
                            elif function_name == "transfer_to_crypto_expert":
                                st.session_state.current_agent = "crypto"
                                st.toast("Ajan Değiştirildi: Kripto Uzmanı devrede!", icon="🪙")
                            elif function_name == "transfer_to_fund_expert":
                                st.session_state.current_agent = "fund"
                                st.toast("Ajan Değiştirildi: Fon Uzmanı devrede!", icon="📊")
                            elif function_name == "transfer_to_macro_expert":
                                st.session_state.current_agent = "macro"
                                st.toast("Ajan Değiştirildi: Makro & Emtia Uzmanı devrede!", icon="🌍")
                                
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
