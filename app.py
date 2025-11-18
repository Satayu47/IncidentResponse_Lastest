# Incident Response Platform - Chat Interface
# Built this to make incident response easier for our team
# Started as a simple classifier, evolved into full chat interface
# Had to refactor a few times to get the conversation flow right

import streamlit as st
import time
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Phase-1 stuff
from src import (
    LLMAdapter,
    SecurityExtractor,
    DialogueState,
    ExplicitDetector,
    ClassificationRules,
    KnowledgeBaseRetriever,
    get_owasp_display_name,
    get_owasp_description,
    format_confidence_badge,
)
from src.classification_validator import ClassificationValidator

# Phase-2 - playbook execution
from phase2_engine.core.runner_bridge import run_phase2_from_incident

# Other utilities
from src.execution_simulator import ExecutionSimulator
from src.cve_service import CVEService
from datetime import datetime
try:
    from tests import test_cases
except ImportError:
    # test_cases is optional - only needed for some test features
    test_cases = None

load_dotenv()

# Config - tweaked these values during testing
# Originally had 0.65 but changed to 0.70 for better safety after some misclassifications
THRESH_GO = 0.70  # min confidence to proceed to phase 2
CLARIFY_THRESHOLD = 0.70  # ask questions below this
OWASP_VERSION = "2025"  # OWASP Top 10 version: 2025 only

# OPA Configuration (optional)
OPA_URL = os.getenv("OPA_URL")  # e.g., "http://localhost:8181/v1/data/playbook/result"

# Page config
st.set_page_config(
    page_title="Incident Response ChatOps Bot",
    page_icon="🛡️",
    layout="wide",
)

# Initialize session state - lazy loading to avoid startup delays
if "dialogue_ctx" not in st.session_state:
    st.session_state.dialogue_ctx = DialogueState()

if "phase1_output" not in st.session_state:
    st.session_state.phase1_output = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []  # chat history

# Initialize services (only once per session)
if "llm_adapter" not in st.session_state:
    st.session_state.llm_adapter = LLMAdapter(model="gemini-2.5-pro")

if "extractor" not in st.session_state:
    st.session_state.extractor = SecurityExtractor()

if "explicit_detector" not in st.session_state:
    st.session_state.explicit_detector = ExplicitDetector()

# Initialize classification cache for performance optimization
if "classification_cache" not in st.session_state:
    from src.classification_cache import get_cache
    st.session_state.classification_cache = get_cache()

if "kb_retriever" not in st.session_state:
    st.session_state.kb_retriever = KnowledgeBaseRetriever()

if "execution_simulator" not in st.session_state:
    st.session_state.execution_simulator = ExecutionSimulator()

if "cve_service" not in st.session_state:
    nvd_api_key = os.getenv("NVD_API_KEY")  # optional, works without it
    st.session_state.cve_service = CVEService(api_key=nvd_api_key)

# UI state flags
if "enable_execution" not in st.session_state:
    st.session_state.enable_execution = False

if "playbook_approved" not in st.session_state:
    st.session_state.playbook_approved = False

if "waiting_for_clarification" not in st.session_state:
    st.session_state.waiting_for_clarification = False

if "show_details_panel" not in st.session_state:
    st.session_state.show_details_panel = False

if "executed_steps" not in st.session_state:
    st.session_state.executed_steps = {}

if "current_classification" not in st.session_state:
    st.session_state.current_classification = None


# ============================================
# Left Sidebar - Configuration & Test Cases
# ============================================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            # Reinitialize LLM adapter with new key
            st.session_state.llm_adapter = LLMAdapter(model="gemini-2.5-pro")
            st.success("API Key configured!")
            st.rerun()
    else:
        st.success("✅ Gemini API Key configured")
        # Show API key status hint
        if st.button("🔍 Test API Connection", help="Click to verify your API key is working"):
            try:
                # Quick test call
                test_result = st.session_state.llm_adapter.classify_incident(
                    description="test",
                    context="",
                    conversation_history=[]
                )
                st.success("✅ API connection successful!")
            except Exception as e:
                error_msg = str(e)
                if "API key" in error_msg or "authentication" in error_msg.lower():
                    st.error("❌ API key invalid or missing")
                    st.info("💡 Check your GEMINI_API_KEY in .env file or enter it above")
                elif "quota" in error_msg.lower() or "429" in error_msg:
                    st.warning("⚠️ API quota exceeded")
                    st.info("💡 Check your Gemini API usage limits")
                else:
                    st.error(f"❌ API Error: {type(e).__name__}")
                    st.caption(f"Details: {error_msg[:100]}")
    
    st.divider()
    
    st.header("🧪 Test Cases")
    test_case_id = st.selectbox(
        "Load Test Case",
        ["None"] + ([tc["id"] for tc in test_cases.TEST_CASES] if test_cases else []),
        help="Select a test case to load"
    )
    
    if test_case_id != "None" and test_cases:
        tc = test_cases.get_test_case(test_case_id)
        if tc and st.button("Load Test Case"):
            st.session_state.chat_messages.append({
                "role": "user",
                "content": tc["user_input"],
                "timestamp": datetime.now()
            })
            st.rerun()
    
    st.divider()
    
    if st.button("🔄 Reset Conversation"):
        st.session_state.dialogue_ctx.reset()
        st.session_state.phase1_output = None
        st.session_state.chat_messages = []
        st.session_state.playbook_approved = False
        st.session_state.enable_execution = False
        st.session_state.waiting_for_clarification = False
        st.session_state.show_details_panel = True  # Always show panel in new UI
        st.session_state.executed_steps = {}
        st.session_state.execution_simulator.clear_log()
        if "phase2_result" in st.session_state:
            del st.session_state.phase2_result
        st.rerun()


# ============================================
# Main Layout - Fixed 2-Column Layout
# ============================================
st.title("🛡️ Incident Response ChatOps Bot")
st.markdown("**Automated Dynamic Playbooks for Real-Time Threat Mitigation**")
st.markdown(f"**Focus:** OWASP Top 10 **{OWASP_VERSION}**")

# Fixed 2-column layout (always show right panel)
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Chat Interface")
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "classification" in message:
                cls = message["classification"]
                incident_type = cls.get('incident_type', 'Unknown')
                # Extract version if present
                version_info = ""
                if ":2025" in incident_type:
                    version_info = " (OWASP 2025)"
                # OWASP 2025 only - removed 2021 support
                st.caption(f"Classification: {incident_type}{version_info}")

# Chat input
if prompt := st.chat_input("Describe the security incident..."):
    user_input = prompt
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    with st.chat_message("user"):
        st.write(user_input)
    
    # Check if it's a greeting or general message
    prompt_lower = user_input.lower().strip()
    first_word = prompt_lower.split()[0] if prompt_lower.split() else ""
    is_greeting = (
        first_word in ["hi", "hello", "hey", "greetings"] or
        prompt_lower in ["hi", "hello", "hey", "help", "greetings"] or
        (len(prompt_lower.split()) <= 2 and "help" in prompt_lower)
    )
    
    # Check if this is a general question about the system (not an incident)
    is_general_question = (
        user_input.strip().endswith("?") and (
            any(word in prompt_lower for word in ["what is", "what does", "how does", "how do", "explain", "tell me about", "what are", "what can"]) or
            any(phrase in prompt_lower for phrase in ["what is owasp", "what is injection", "what is access control", "how does this work", "what can you do"])
        )
    ) or (
        any(phrase in prompt_lower for phrase in ["explain", "what does that mean", "can you explain", "tell me more", "what is this"])
    )
    
    # Check if user is asking about a previous classification
    is_explanation_request = (
        st.session_state.get("phase1_output") and (
            any(phrase in prompt_lower for phrase in ["what does that mean", "explain that", "what is", "tell me about", "can you explain"]) or
            any(word in prompt_lower for word in ["mean", "explain", "understand", "clarify"])
        )
    )
    
    # Check if this is a command first (before classification)
    user_input_lower = user_input.strip().lower()
    is_generate_command = any(word in user_input_lower for word in ["yes", "generate", "create", "plan", "response", "proceed", "go ahead", "ok", "okay", "sure", "do it"])
    is_execute_command = any(word in user_input_lower for word in ["run", "execute", "start", "begin", "launch"])
    
    with st.chat_message("assistant"):
        if is_greeting:
            # Handle greetings and general messages
            welcome_message = """👋 **Hello! I'm your Incident Response ChatOps Bot.**

I help classify and respond to security incidents based on OWASP Top 10:2025 categories.

**How to use:**

1. Describe a security incident (e.g., "I changed the number in the URL and saw another user's profile")

2. I'll classify it and generate an automated playbook

3. You'll see related CVEs and policy decisions

**Try these examples:**

- "I tried wrong passwords 30 times and it didn't block me"

- "Our API is showing stack trace to users"

- "The system allowed me to set my password to '12345'"

Or load a test case from the sidebar! 🧪"""
            
            st.markdown(welcome_message)
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": welcome_message,
                "timestamp": datetime.now()
            })
        elif is_general_question:
            # Handle general questions about the system, OWASP, security concepts, etc.
            try:
                # Use LLM to generate helpful answer
                # SAFETY: Add instruction to be accurate and avoid misinformation
                question_prompt = f"""You are a helpful security incident response assistant. The user asked: "{user_input}"

This seems like a general question about security concepts, OWASP, or how the system works - NOT an incident report.

CRITICAL SAFETY REQUIREMENTS:
- Only provide ACCURATE, VERIFIED information
- If you're not certain, say so
- Do NOT make up facts or provide incorrect information
- For OWASP: Use only official OWASP Top 10 2025 information
- For security concepts: Explain accurately, don't oversimplify to the point of being wrong
- If unsure, recommend consulting official documentation

Provide a helpful, conversational answer. If they're asking about:
- OWASP: Explain what OWASP Top 10 is and the 2025 categories (accurately)
- Security concepts: Explain in simple but accurate terms
- How the system works: Explain the classification and playbook process (accurately)
- General help: Be friendly and guide them

Keep it concise (2-3 sentences) and friendly. If it's not clear what they're asking, politely ask for clarification.

Answer:"""
                
                response_text = st.session_state.llm_adapter.model.generate_content(
                    question_prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.7,
                        top_p=0.9
                    )
                ).text.strip()
                
                st.markdown(response_text)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now()
                })
            except Exception as e:
                # Fallback to predefined answers
                if "owasp" in prompt_lower:
                    answer = """**OWASP Top 10** is a standard awareness document for web application security. 

The **2025 version** includes:
- A01: Broken Access Control
- A04: Cryptographic Failures  
- A05: Injection
- A07: Authentication Failures
- And 6 more categories

I classify security incidents into these categories and generate automated response playbooks. Would you like to report an incident?"""
                elif "injection" in prompt_lower:
                    answer = """**Injection attacks** occur when untrusted data is sent to an interpreter (like SQL, OS commands, or LDAP) as part of a command or query.

Common examples:
- SQL Injection: `' OR 1=1 --` in login forms
- Command Injection: Executing system commands via user input
- XSS: Injecting scripts into web pages

I can help classify and respond to injection incidents. Describe what you're seeing!"""
                elif "access control" in prompt_lower or "access" in prompt_lower:
                    answer = """**Broken Access Control** happens when users can access resources or perform actions they shouldn't be allowed to.

Examples:
- Changing URL parameters to see other users' data
- Accessing admin panels without permission
- Bypassing authentication checks

If you're experiencing this, describe what happened and I'll help classify it!"""
                else:
                    answer = """I'm here to help with security incident response! 

I can:
- Classify security incidents into OWASP 2025 categories
- Generate automated response playbooks
- Find related CVEs and vulnerabilities
- Guide you through incident response steps

Describe a security incident you're dealing with, or ask me about OWASP categories!"""
                
                st.markdown(answer)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": answer,
                    "timestamp": datetime.now()
                })
        elif is_explanation_request and st.session_state.get("phase1_output"):
            # User wants explanation of previous classification
            prev_classification = st.session_state.phase1_output
            incident_type = prev_classification.get("incident_type", "Unknown")
            fine_label = prev_classification.get("fine_label", "unknown")
            
            try:
                explanation_prompt = f"""The user previously reported an incident that I classified as: {incident_type} ({fine_label})

They're now asking: "{user_input}"

They want to understand what this classification means. Provide a clear, friendly explanation:
- What this type of incident is (ACCURATELY based on OWASP 2025)
- Why it's a security concern
- Common examples (real, accurate examples)
- What the response playbook will do

CRITICAL SAFETY REQUIREMENTS:
- Only provide ACCURATE information based on OWASP 2025 standards
- Do NOT make up examples or provide incorrect information
- If you're not certain about something, say so
- Base explanations on official OWASP definitions

Keep it conversational and helpful (2-3 sentences), but ACCURATE.

Explanation:"""
                
                explanation = st.session_state.llm_adapter.model.generate_content(
                    explanation_prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.7,
                        top_p=0.9
                    )
                ).text.strip()
                
                st.markdown(explanation)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": explanation,
                    "timestamp": datetime.now()
                })
            except Exception as e:
                # Fallback explanation
                owasp_desc = get_owasp_description(fine_label, version=OWASP_VERSION)
                explanation = f"**{incident_type}** means: {owasp_desc}\n\nWould you like me to generate a response plan for this incident?"
                st.markdown(explanation)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": explanation,
                    "timestamp": datetime.now()
                })
        elif not st.session_state.llm_adapter:
            error_msg = "⚠️ **Gemini API Key not configured!**\n\nPlease enter your Gemini API Key in the sidebar to use the classification feature."
            st.error(error_msg)
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": error_msg,
                "timestamp": datetime.now()
            })
        # Check if user wants to execute the plan
        elif is_execute_command and st.session_state.get("phase2_result"):
            with st.spinner("🚀 Executing response plan..."):
                try:
                    # Simulate execution
                    from src.execution_simulator import ExecutionSimulator
                    simulator = ExecutionSimulator()
                    steps = st.session_state.phase2_result.get("steps", [])
                    execution_results = simulator.execute_playbook(steps)
                    
                    response = "✅ **Response plan executed!**\n\n"
                    response += "**Execution Summary:**\n"
                    response += f"- Total steps: {len(execution_results)}\n"
                    response += f"- Completed: {sum(1 for r in execution_results if r.get('status') == 'success')}\n"
                    response += f"- Simulated: {sum(1 for r in execution_results if r.get('status') == 'simulated')}\n\n"
                    response += "**Note:** This is a simulation. In production, these actions would be executed against your systems.\n\n"
                    response += "Would you like to see detailed execution logs?"
                    
                    st.write(response)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now()
                    })
                except Exception as e:
                    st.write(f"❌ Error executing plan: {str(e)[:100]}")
        # If it's a command and we have a classified incident, generate plan
        elif is_generate_command and st.session_state.get("phase1_output") and st.session_state.dialogue_ctx.is_ready_for_phase2(thresh=THRESH_GO):
            with st.spinner("📋 Creating your response plan..."):
                try:
                    # Get OPA URL from environment if available
                    opa_url = OPA_URL if OPA_URL else None
                    
                    phase2_result = run_phase2_from_incident(
                        incident=st.session_state.phase1_output,
                        merged_with=None,
                        dry_run=True,
                        opa_url=opa_url,
                    )
                    
                    if phase2_result.get("status") == "success":
                        st.session_state.phase2_result = phase2_result
                        
                        # Check if multiple playbooks were merged
                        playbooks_used = phase2_result.get("playbooks", [])
                        is_merged = len(playbooks_used) > 1
                        
                        response = "✅ **Response plan created!**\n\n"
                        if is_merged:
                            playbook_names = [pb.replace("_", " ").title() for pb in playbooks_used]
                            response += f"🔄 **Merged Playbook:** {', '.join(playbook_names)}\n\n"
                            response += f"*This plan combines {len(playbooks_used)} playbooks to address multiple attack vectors.*\n\n"
                        response += "Here are the recommended steps:\n\n"
                        
                        # Group steps by phase
                        steps_by_phase = {}
                        for step in phase2_result.get("steps", []):
                            phase = step.get("phase", "unknown")
                            steps_by_phase.setdefault(phase, []).append(step)
                        
                        phase_display = {
                            "preparation": "🛡️ Preparation",
                            "detection_analysis": "🔍 Detection & Analysis",
                            "containment": "⚠️ Containment (Stop the threat)",
                            "eradication": "🧹 Eradication (Remove the threat)",
                            "recovery": "♻️ Recovery (Restore services)",
                            "post_incident": "📋 Post-Incident Review",
                        }
                        
                        phase_order = ["preparation", "detection_analysis", "containment", "eradication", "recovery", "post_incident"]
                        
                        for phase_key in phase_order:
                            if phase_key in steps_by_phase:
                                response += f"**{phase_display[phase_key]}**\n"
                                for idx, s in enumerate(steps_by_phase[phase_key], 1):
                                    response += f"{idx}. {s.get('name', 'Unknown')}\n"
                                response += "\n"
                        
                        response += "\n💡 **Would you like me to execute this plan?** (Say 'execute' or 'run' to proceed)"
                        
                        st.write(response)
                        
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": datetime.now()
                        })
                    else:
                        st.write("❌ I couldn't create a response plan for this incident type. Please provide more details or try a different description.")
                except Exception as e:
                    st.write(f"❌ Error creating plan: {str(e)[:100]}")
        else:
            # Process as incident description
            with st.spinner("🔍 Analyzing incident..."):
                # Classification logic
                description_text = user_input.strip()
                
                # Extract IOCs
                ents = st.session_state.extractor.extract(description_text)
                iocs = {
                    "ip": ents.ips,
                    "url": ents.urls,
                    "domain": ents.domains,
                    "hash": ents.hashes,
                    "email": ents.emails,
                }
                
                # Get knowledge base context
                kb_context = st.session_state.kb_retriever.get_context_for_label(description_text)
                
                # Try explicit detection first (only for very obvious cases)
                explicit_label, explicit_conf = st.session_state.explicit_detector.detect(description_text)
                
                # Initialize classification to avoid NameError
                classification = None
                
                # Use fast path for high-confidence explicit detection (optimization)
                # Lowered threshold from 0.90 to 0.85 to enable fast path more often
                if explicit_label and explicit_conf >= 0.85:  # High confidence - skip LLM
                    # Fast path - skip LLM for obvious cases like "' OR 1=1"
                    from src.classification_rules import canonicalize_label
                    canonical = canonicalize_label(explicit_label)
                    fine_label = canonical
                    score = explicit_conf
                    report_category = ClassificationRules.get_owasp_display_name(fine_label, show_specific=False)
                    rationale = f"Detected: {explicit_label}"
                else:
                    # Use LLM for semantic understanding - it handles vague descriptions better
                    # Check cache first to avoid redundant API calls (performance optimization)
                    cached_result = st.session_state.classification_cache.get(description_text)
                    
                    if cached_result:
                        # Cache hit - use cached result (much faster, ~5ms instead of ~103ms!)
                        fine_label = cached_result.get("fine_label", "unknown")
                        score = float(cached_result.get("confidence", 0.0))
                        report_category = cached_result.get("incident_type", "Unknown")
                        rationale = cached_result.get("rationale", "Cached classification")
                        llm_labels = cached_result.get("labels", [])  # Get labels from cache too
                        if not isinstance(llm_labels, list):
                            llm_labels = []
                    else:
                        # Cache miss - call LLM API
                        classification = None  # Initialize to avoid NameError
                        llm_labels = []  # Initialize LLM labels
                        try:
                            # Build rich context for LLM with FULL conversation history
                            # Get both structured context and natural conversation flow
                            conversation_summary = st.session_state.dialogue_ctx.get_conversation_context()
                            full_conversation = st.session_state.dialogue_ctx.get_full_conversation_history()
                            
                            # Add explicit detection hint if we found something (even if low confidence)
                            context_parts = [kb_context]
                            if explicit_label and explicit_conf >= 0.60:
                                context_parts.append(f"Keyword hint: '{explicit_label}' (confidence: {explicit_conf:.2f})")
                            
                            # Add NVD context if we have CVEs or can search for related vulnerabilities
                            if ents.cves:
                                cve_info = []
                                for cve_id in ents.cves[:3]:  # Limit to 3 CVEs
                                    try:
                                        cve_data = st.session_state.cve_service.get_cve_by_id(cve_id)
                                        if cve_data:
                                            cve_info.append(f"{cve_id}: {cve_data.get('description', '')[:200]}")
                                    except Exception:
                                        pass  # CVE lookup failed, continue without it
                                if cve_info:
                                    context_parts.append(f"Related CVEs:\n" + "\n".join(cve_info))
                            
                            full_context = "\n".join(context_parts)
                            
                            # Pass full conversation history so Gemini remembers everything
                            classification = st.session_state.llm_adapter.classify_incident(
                                description=description_text,
                                context=full_context,
                                conversation_history=full_conversation,  # Full natural conversation
                            )
                            
                            fine_label = classification.get("fine_label", "unknown")
                            score = float(classification.get("confidence", 0.0))
                            report_category = classification.get("incident_type", "Unknown")
                            rationale = classification.get("rationale", "AI-based classification")
                            
                            # Extract labels array from LLM if present (multi-label support)
                            llm_labels = classification.get("labels", [])
                            if not isinstance(llm_labels, list):
                                llm_labels = []
                            
                            # Cache the result for future use (performance optimization)
                            cache_entry = {
                                "fine_label": fine_label,
                                "confidence": score,
                                "incident_type": report_category,
                                "rationale": rationale
                            }
                            st.session_state.classification_cache.set(description_text, cache_entry)
                            
                            # If explicit detection found something and LLM agrees, boost confidence
                            if explicit_label and explicit_conf >= 0.70:
                                from src.classification_rules import canonicalize_label
                                explicit_canonical = canonicalize_label(explicit_label)
                                fine_label_canonical = canonicalize_label(fine_label)
                                if explicit_canonical == fine_label_canonical:
                                    score = max(score, 0.90)  # Both agree = high confidence
                                    rationale = f"Confirmed by both methods: {fine_label}"
                        except Exception as e:
                            # API call failed, use fallback
                            # Log error for debugging (but don't show to user)
                            import traceback
                            error_msg = str(e)
                            error_type = type(e).__name__
                            
                            # Check for common error types
                            if "API key" in error_msg or "authentication" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
                                error_hint = "API key may be missing or invalid. Check your GEMINI_API_KEY in .env file."
                            elif "quota" in error_msg.lower() or "429" in error_msg or "rate limit" in error_msg.lower():
                                error_hint = "API quota exceeded. Check your Gemini API usage limits."
                            elif "timeout" in error_msg.lower():
                                error_hint = "API request timed out. Please try again."
                            else:
                                error_hint = f"Error: {error_type}"
                            
                            print(f"LLM Classification Error: {error_msg}")
                            print(f"Error Type: {error_type}")
                            print(f"Traceback: {traceback.format_exc()}")
                            
                            if explicit_label:
                                from src.classification_rules import canonicalize_label
                                fine_label = canonicalize_label(explicit_label)
                                score = explicit_conf
                                report_category = ClassificationRules.get_owasp_display_name(fine_label, show_specific=False)
                                rationale = f"Detected: {explicit_label} (LLM unavailable: {error_hint})"
                            else:
                                fine_label = "other"
                                score = 0.3  # low confidence fallback
                                report_category = "Unknown Incident"
                                rationale = f"LLM classification failed: {error_hint}"
                
                # Build classification result
                label = fine_label.lower().replace(" ", "_")
                
                # Detect multiple labels from user input for playbook merging
                # Start with LLM labels if available, otherwise start with primary label
                detected_labels = llm_labels if llm_labels else [label]
                
                # Ensure primary label is included
                if label not in detected_labels:
                    detected_labels.insert(0, label)
                
                text_lower = description_text.lower()
                
                # Enhanced keyword detection for additional labels (backup if LLM missed something)
                # Check for multiple attack types mentioned with "and", "also", "plus", etc.
                has_multiple_indicators = any(word in text_lower for word in [" and ", " also ", " plus ", " combined with ", " as well as "])
                
                # Check for additional labels mentioned in the text
                if ("broken access control" in text_lower or "access control" in text_lower or 
                    "unauthorized access" in text_lower or "idor" in text_lower or
                    "can access" in text_lower and "admin" in text_lower):
                    if "broken_access_control" not in detected_labels:
                        detected_labels.append("broken_access_control")
                
                if ("injection" in text_lower or "sql injection" in text_lower or 
                    "xss" in text_lower or "command injection" in text_lower):
                    if "injection" not in detected_labels and "sql_injection" not in detected_labels:
                        detected_labels.append("injection")
                
                if ("authentication" in text_lower or "login" in text_lower or 
                    "session" in text_lower or "password" in text_lower and "weak" in text_lower):
                    if "broken_authentication" not in detected_labels:
                        detected_labels.append("broken_authentication")
                
                # Enhanced cryptographic detection
                if ("cryptographic" in text_lower or "encryption" in text_lower or 
                    "plaintext" in text_lower or "unencrypted" in text_lower or
                    "not encrypted" in text_lower or "without encryption" in text_lower or
                    "crypto" in text_lower and "attack" in text_lower):
                    if "cryptographic_failures" not in detected_labels:
                        detected_labels.append("cryptographic_failures")
                
                if "misconfiguration" in text_lower or "misconfig" in text_lower:
                    if "security_misconfiguration" not in detected_labels:
                        detected_labels.append("security_misconfiguration")
                
                # Remove duplicates while preserving order
                seen = set()
                unique_labels = []
                for lbl in detected_labels:
                    if lbl not in seen:
                        seen.add(lbl)
                        unique_labels.append(lbl)
                detected_labels = unique_labels
                
                # Calibrate confidence based on rationale quality
                # If rationale is detailed and specific, boost confidence slightly
                if rationale and len(rationale) > 50 and any(word in rationale.lower() for word in ["because", "indicates", "suggests", "typically", "likely", "could be", "might also"]):
                    # Detailed reasoning = more reliable
                    score = min(score * 1.05, 0.95)  # Small boost, cap at 0.95
                
                # Search for related CVEs based on incident type
                related_cves = list(ents.cves) if ents.cves else []
                try:
                    # Search NVD for CVEs related to this incident type
                    search_keywords = []
                    if label == "injection" or "sql_injection" in label:
                        search_keywords = ["SQL injection", "injection"]
                    elif label == "broken_access_control":
                        search_keywords = ["access control", "IDOR", "authorization"]
                    elif label == "broken_authentication":
                        search_keywords = ["authentication", "session"]
                    elif label == "cryptographic_failures":
                        search_keywords = ["cryptographic", "encryption", "TLS", "SSL"]
                    elif label == "security_misconfiguration":
                        search_keywords = ["misconfiguration", "default credentials"]
                    
                    # Also search for CVEs for all detected labels (multi-label support)
                    for detected_label in detected_labels:
                        if detected_label == "cryptographic_failures" and "cryptographic" not in [kw.lower() for kw in search_keywords]:
                            search_keywords.extend(["cryptographic", "encryption"])
                        elif detected_label == "injection" and "injection" not in [kw.lower() for kw in search_keywords]:
                            search_keywords.extend(["SQL injection", "injection"])
                        elif detected_label == "broken_access_control" and "access control" not in [kw.lower() for kw in search_keywords]:
                            search_keywords.extend(["access control", "IDOR"])
                    
                    if search_keywords:
                        for keyword in search_keywords[:2]:  # Limit to 2 searches
                            try:
                                cve_results = st.session_state.cve_service.search_vulnerabilities(keyword, max_results=3)
                                for cve in cve_results:
                                    cve_id = cve.get("cve_id") or cve.get("id")
                                    if cve_id and cve_id not in related_cves:
                                        related_cves.append(cve_id)
                                        if len(related_cves) >= 5:  # Limit to 5 CVEs total
                                            break
                                if len(related_cves) >= 5:
                                    break
                            except Exception:
                                pass  # CVE search failed, continue without it
                except Exception:
                    pass  # CVE enrichment failed, continue without it
                
                # Extract OWASP version from classification if present
                detected_version = OWASP_VERSION  # Default
                if classification and isinstance(classification, dict) and classification.get("owasp_version"):
                    detected_version = classification.get("owasp_version", OWASP_VERSION)
                elif ":2025" in report_category:
                    detected_version = "2025"
                # OWASP 2025 only - removed 2021 support
                
                classification_result = {
                    "incident_type": report_category,
                    "fine_label": label,
                    "labels": detected_labels,  # Multi-label support for playbook merging
                    "confidence": score,
                    "rationale": rationale,
                    "entities": ents.__dict__(),
                    "iocs": iocs,
                    "related_CVEs": related_cves[:5],  # Limit to 5 CVEs
                    "kb_excerpt": kb_context[:600] if kb_context else "",
                    "owasp_version": detected_version,  # Store version for display
                }
                
                # SAFETY: Validate classification before proceeding
                is_valid, validation_warnings = ClassificationValidator.validate_classification(classification_result)
                if not is_valid:
                    # Classification failed validation - show error
                    error_response = f"⚠️ **Classification Validation Failed**\n\n"
                    error_response += "I couldn't confidently classify this incident. This helps prevent misclassification.\n\n"
                    error_response += "**Issues:**\n"
                    for warning in validation_warnings:
                        error_response += f"- {warning}\n"
                    error_response += "\n**Please provide more details** about what happened so I can classify it accurately."
                    
                    st.write(error_response)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": error_response,
                        "timestamp": datetime.now()
                    })
                    st.stop()  # Stop processing - don't proceed with invalid classification
                
                # Add validation warnings to response if any
                if validation_warnings:
                    classification_result["validation_warnings"] = validation_warnings
                
                # Update dialogue state
                st.session_state.dialogue_ctx.add_turn(
                    user_input=description_text,
                    classification=classification_result,
                )
                
                st.session_state.phase1_output = classification_result
                
                # Generate response based on confidence
                conf_pct = int(score * 100)
                owasp_name = get_owasp_display_name(label, show_specific=True, version=OWASP_VERSION)
                
                # Helper function to make names user-friendly (remove technical codes)
                def make_user_friendly(name: str) -> str:
                    """Remove technical OWASP codes like 'A03' from display names."""
                    # Remove "A03 - " or "A04 - " prefixes
                    if " - " in name:
                        name = name.split(" - ", 1)[-1]
                    # Remove any remaining codes
                    for code in ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10"]:
                        name = name.replace(code, "").strip()
                    # Clean up any double spaces or leading dashes
                    name = name.replace("  ", " ").strip()
                    if name.startswith("-"):
                        name = name[1:].strip()
                    return name if name else "Security Incident"
                
                user_friendly_name = make_user_friendly(owasp_name)
                
                if score >= CLARIFY_THRESHOLD:
                    # High confidence - show classification
                    # SAFETY: Add validation and warnings
                    
                    version_badge = f"OWASP {detected_version}"  # Use detected version, not default
                    response = f"✅ **I've analyzed your incident.**\n\n"
                    response += f"**Classification:** {user_friendly_name} ({version_badge})\n"
                    response += f"**Confidence:** {conf_pct}% "
                    
                    # Add confidence indicator with safety warnings
                    if conf_pct >= 80:
                        response += "🟢 (High)\n"
                    elif conf_pct >= 60:
                        response += "🟡 (Medium)\n"
                        # SAFETY: Warn if medium confidence
                        response += "\n⚠️ **Note:** Medium confidence - please verify this classification is correct before taking action.\n"
                    else:
                        response += "🟠 (Low)\n"
                        # SAFETY: Strong warning for low confidence
                        response += "\n⚠️ **Warning:** Low confidence classification. Please provide more details or verify manually before proceeding.\n"
                    response += "\n"
                    
                    if rationale and rationale != "AI-based classification":
                        response += f"**Analysis:** {rationale}\n\n"
                    
                    # Show IOCs if found
                    has_iocs = False
                    ioc_list = []
                    if iocs.get("ip"):
                        has_iocs = True
                        ioc_list.append(f"📍 {len(iocs['ip'])} IP address(es)")
                    if iocs.get("url"):
                        has_iocs = True
                        ioc_list.append(f"🔗 {len(iocs['url'])} URL(s)")
                    if iocs.get("domain"):
                        has_iocs = True
                        ioc_list.append(f"🌐 {len(iocs['domain'])} domain(s)")
                    
                    if has_iocs:
                        response += f"**Indicators Found:** {' | '.join(ioc_list)}\n\n"
                    
                    # Show related CVEs
                    if classification_result.get("related_CVEs"):
                        cve_list = classification_result["related_CVEs"][:5]
                        response += f"**🔒 Related CVEs ({len(cve_list)}):**\n"
                        for cve_id in cve_list:
                            try:
                                cve_data = st.session_state.cve_service.get_cve_by_id(cve_id)
                                if cve_data:
                                    severity = cve_data.get("severity", "Unknown")
                                    cvss = cve_data.get("cvss_score")
                                    desc = cve_data.get("description", "")[:100]
                                    severity_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(severity, "⚪")
                                    cvss_str = f" (CVSS: {cvss})" if cvss else ""
                                    cve_link = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
                                    response += f"- {severity_emoji} **[{cve_id}]({cve_link})** {severity}{cvss_str}: {desc}...\n"
                                else:
                                    cve_link = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
                                    response += f"- **[{cve_id}]({cve_link})**\n"
                            except Exception:
                                cve_link = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
                                response += f"- **[{cve_id}]({cve_link})**\n"
                        response += "\n"
                    
                    # SAFETY: Add disclaimer about classification accuracy
                    if conf_pct < 90:
                        response += "⚠️ **Important:** This classification is based on AI analysis. Please verify it matches your situation before proceeding.\n\n"
                    
                    # Check if ready for Phase-2
                    if st.session_state.dialogue_ctx.is_ready_for_phase2(thresh=THRESH_GO):
                        response += "🎯 **I have enough information!** Would you like me to generate a response plan?\n\n"
                        response += "Just say 'yes', 'generate plan', or 'create response plan' and I'll create step-by-step actions for you.\n\n"
                        # SAFETY: Add disclaimer about playbooks
                        response += "⚠️ **Safety Note:** All playbook actions run in simulation mode by default. Review the plan carefully before any real execution."
                    else:
                        response += "💡 I could use a bit more detail. Can you tell me more about what happened?\n\n"
                        response += "⚠️ **Note:** I need more information to ensure accurate classification and avoid misclassification."
                    
                    st.write(response)
                    
                    # Store assistant message
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": response,
                        "classification": classification_result,
                        "timestamp": datetime.now(),
                        "playbook_actions": st.session_state.get("phase2_result", {}).get("steps", []),
                        "cves": classification_result.get("related_CVEs", [])
                    })
                    
                    st.session_state.waiting_for_clarification = False
                    st.session_state.current_classification = classification_result.get("incident_type")
                    
                else:
                    # Low confidence - ask clarifying question
                    conversation_history = st.session_state.dialogue_ctx.get_conversation_context()
                    
                    # Generate more specific question based on what we detected
                    try:
                        # Use full conversation history for better context
                        full_conversation = st.session_state.dialogue_ctx.get_full_conversation_history()
                        
                        # If we have a hint from explicit detection, use it
                        if explicit_label and explicit_conf >= 0.60:
                            # We detected something but not confident enough
                            if explicit_label == "injection":
                                clarifying_question = "This sounds like it might be an injection attack. Can you tell me more? For example: What exact error messages or syntax did you see? Was it on a login page, search form, or somewhere else?"
                            elif explicit_label == "broken_access_control":
                                clarifying_question = "This might be an access control issue. Can you clarify: What were they trying to access? Did they change a URL or parameter? What happened when they accessed it?"
                            else:
                                clarifying_question = st.session_state.llm_adapter.generate_clarifying_question(
                                    incident_description=description_text,
                                    current_classification=classification_result,
                                    conversation_history=full_conversation
                                )
                        else:
                            clarifying_question = st.session_state.llm_adapter.generate_clarifying_question(
                                incident_description=description_text,
                                current_classification=classification_result,
                                conversation_history=full_conversation
                            )
                    except Exception:
                        # Fallback - make it more specific based on keywords
                        if any(word in description_text.lower() for word in ["syntax", "error", "weird", "strange"]):
                            clarifying_question = "This sounds like it might be a code injection issue. Can you tell me: What exact error messages or syntax did you see? Where did it appear (login page, search form, etc.)? Did you see any SQL errors or database messages?"
                        else:
                            clarifying_question = "I understand this is frustrating. Can you help me understand what happened? For example, what error messages did you see, or what suspicious activity did you notice?"
                    
                    # Use user-friendly language (already defined above)
                    # Show actual classification even if confidence is low
                    actual_category = report_category if report_category != "Unknown Incident" else user_friendly_name
                    version_badge = f"OWASP {detected_version}"
                    
                    response = f"🔍 I've analyzed your incident and I'm about {conf_pct}% confident this might be **{user_friendly_name}** ({version_badge}), but I'd like to gather more details to ensure accuracy.\n\n"
                    response += f"**{clarifying_question}**\n\n"
                    response += f"**Current Classification:** {actual_category}"
                    
                    st.write(response)
                    
                    # Store assistant message
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": response,
                        "classification": classification_result,
                        "timestamp": datetime.now()
                    })
                    
                    st.session_state.waiting_for_clarification = True
                    # Store the actual classification, not "Unknown Incident"
                    st.session_state.current_classification = actual_category if actual_category != "Unknown Incident" else classification_result.get("incident_type")
    
    st.rerun()

# Right Panel - Incident Details & Playbook (always visible)
with col2:
    st.header("📊 Incident Details")
    
    if st.session_state.get("current_classification") or st.session_state.get("phase1_output"):
        if st.session_state.get("phase1_output"):
            p1 = st.session_state.phase1_output
            category = p1.get("incident_type", "Unknown")
            # Use detected version from classification result if available
            detected_ver = p1.get("owasp_version", OWASP_VERSION)
            owasp_id = ClassificationRules.get_owasp_display_name(p1["fine_label"], show_specific=False, version=detected_ver)
            
            # Extract OWASP ID and version for description lookup
            owasp_code = owasp_id.split(":")[0] if ":" in owasp_id else owasp_id.split()[0]
            owasp_desc = get_owasp_description(owasp_code)
            
            # Show version badge (use detected version)
            version_badge = f"🛡️ OWASP {detected_ver}"
            st.info(f"**{owasp_id}**\n\n{version_badge}\n\n{owasp_desc.get('description', 'No description available.')}")
        else:
            st.info("💡 Describe a security incident to see classification and playbook")
    else:
        st.info("💡 Describe a security incident to see classification and playbook")
    
    if st.session_state.get("phase2_result"):
        st.markdown("---")
        # Automated Playbook Section
        st.subheader("📋 Automated Playbook")
        
        phase2 = st.session_state.phase2_result
        steps = phase2.get("steps", [])
        
        if not steps:
            st.info("No playbook steps available.")
        else:
            st.caption(f"**Total Steps:** {len(steps)}")
            st.markdown("---")
            
            for idx, step in enumerate(steps, 1):
                step_id = step.get("id") or f"step_{idx}"
                step_name = step.get("name", "Unknown Step")
                step_desc = step.get("description") or step.get("ui_description") or step.get("message", "No description")
                step_status = st.session_state.executed_steps.get(step_id, "pending")
                
                # Make steps expandable
                with st.expander(f"Step {idx}: {step_name}", expanded=(idx <= 2)):  # First 2 expanded by default
                    st.write(f"**Status:** {step_status}")
                    st.write(f"**Description:** {step_desc}")
                    
                    # Execute button
                    button_key = f"exec_{step_id}_{idx}"
                    if st.button(f"Execute Step {idx}", key=button_key, disabled=(step_status == "executed")):
                        # Execute the step
                        try:
                            from src.execution_simulator import ExecutionSimulator
                            simulator = ExecutionSimulator()
                            result = simulator._execute_step({
                                "action": step_name,
                                "description": step_desc
                            })
                            
                            st.session_state.executed_steps[step_id] = "executed"
                            st.success(f"Step {idx} executed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error executing step: {str(e)[:50]}")
                    
                    # Show execution status
                    if step_status == "executed":
                        st.success(f"Step {idx} executed!")
    
    # Related CVEs Section
    if st.session_state.get("phase1_output"):
        st.markdown("---")
        st.subheader("🔍 Related CVEs")
        
        p1 = st.session_state.phase1_output
        related_cves = p1.get("related_CVEs", [])
        
        if not related_cves:
            st.info("No related CVEs found.")
        else:
            for cve_id in related_cves[:5]:  # Limit to 5 CVEs
                try:
                    cve_data = st.session_state.cve_service.get_cve_by_id(cve_id)
                    if cve_data:
                        severity = cve_data.get("severity", "Unknown")
                        cvss = cve_data.get("cvss_score")
                        desc = cve_data.get("description", "")[:200]
                        
                        # Make CVEs expandable
                        with st.expander(f"{cve_id} - CVSS: {cvss if cvss else 'N/A'}", expanded=False):
                            st.write(f"**Description:** {desc}")
                            st.write(f"**Severity:** {severity}")
                            st.write(f"**Link:** https://nvd.nist.gov/vuln/detail/{cve_id}")
                    else:
                        st.write(f"**{cve_id}**")
                except Exception:
                    st.write(f"**{cve_id}**")
    
    # OPA Policy Result (if available)
    for msg in reversed(st.session_state.chat_messages):
        if msg.get("role") == "assistant" and "opa_result" in msg:
            st.markdown("---")
            st.subheader("🤖 Automation Policy")
            opa_result = msg["opa_result"]
            if opa_result.get("can_automate"):
                st.success("✅ Automated response allowed")
            else:
                st.warning("⚠️ Requires human review")
            st.write(f"**Severity:** {opa_result.get('severity', 'N/A')}")
            st.write(f"**Reason:** {opa_result.get('reason', 'N/A')}")
            break

# Footer
st.divider()
st.caption("Powered by Gemini LLM | OWASP Top 10:2025 | NetworkX DAG Playbooks | OPA Policy Engine")

