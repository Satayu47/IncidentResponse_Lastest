# Incident Response Platform - Chat Interface
# Built this to make incident response easier for our team
# Started as a simple classifier, evolved into full chat interface

import streamlit as st
import time
import os
from dotenv import load_dotenv

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

# Phase-2 - playbook execution
from phase2_engine.core.runner_bridge import run_phase2_from_incident

# Other utilities
from src.execution_simulator import ExecutionSimulator
from src.cve_service import CVEService
from datetime import datetime
import test_cases

load_dotenv()

# Config - tweaked these values during testing
THRESH_GO = 0.65  # min confidence to proceed to phase 2
CLARIFY_THRESHOLD = 0.65  # ask questions below this
OWASP_VERSION = "2025"  # OWASP Top 10 version: "2021" or "2025"

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
    
    st.divider()
    
    st.header("🧪 Test Cases")
    test_case_id = st.selectbox(
        "Load Test Case",
        ["None"] + [tc["id"] for tc in test_cases.TEST_CASES],
        help="Select a test case to load"
    )
    
    if test_case_id != "None":
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
st.markdown(f"**Focus:** OWASP Top 10 **{OWASP_VERSION}** | Supports both 2021 & 2025")

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
                if ":2025" in incident_type or ":2021" in incident_type:
                    if ":2025" in incident_type:
                        version_info = " (OWASP 2025)"
                    elif ":2021" in incident_type:
                        version_info = " (OWASP 2021)"
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
    
    # Check if this is a command first (before classification)
    user_input_lower = user_input.strip().lower()
    is_generate_command = any(word in user_input_lower for word in ["yes", "generate", "create", "plan", "response", "proceed", "go ahead", "ok", "okay", "sure", "do it"])
    is_execute_command = any(word in user_input_lower for word in ["run", "execute", "start", "begin", "launch"])
    
    with st.chat_message("assistant"):
        if is_greeting:
            # Handle greetings and general messages
            welcome_message = """👋 **Hello! I'm your Incident Response ChatOps Bot.**

I help classify and respond to security incidents based on OWASP Top 10 2025 categories.

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
                    phase2_result = run_phase2_from_incident(
                        incident=st.session_state.phase1_output,
                        merged_with=None,
                        dry_run=True,
                    )
                    
                    if phase2_result.get("status") == "success":
                        st.session_state.phase2_result = phase2_result
                        
                        response = "✅ **Response plan created!**\n\n"
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
                
                # Only use fast path for VERY obvious cases (exact SQL patterns, etc.)
                # For everything else, trust Gemini's semantic understanding
                if explicit_label and explicit_conf >= 0.90:  # Only very high confidence
                    # Fast path - skip LLM for obvious cases like "' OR 1=1"
                    from src.classification_rules import canonicalize_label
                    canonical = canonicalize_label(explicit_label)
                    fine_label = canonical
                    score = explicit_conf
                    report_category = ClassificationRules.get_owasp_display_name(fine_label, show_specific=False)
                    rationale = f"Detected: {explicit_label}"
                else:
                    # Use LLM for semantic understanding - it handles vague descriptions better
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
                                except:
                                    pass
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
                        if explicit_label:
                            from src.classification_rules import canonicalize_label
                            fine_label = canonicalize_label(explicit_label)
                            score = explicit_conf
                            report_category = ClassificationRules.get_owasp_display_name(fine_label, show_specific=False)
                            rationale = f"Detected: {explicit_label}"
                        else:
                            fine_label = "other"
                            score = 0.3  # low confidence fallback
                            report_category = "Unknown Incident"
                            rationale = "Need more information"
                
                # Build classification result
                label = fine_label.lower().replace(" ", "_")
                
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
                    elif label == "security_misconfiguration":
                        search_keywords = ["misconfiguration", "default credentials"]
                    
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
                            except:
                                pass
                except:
                    pass
                
                # Extract OWASP version from classification if present
                detected_version = OWASP_VERSION  # Default
                if isinstance(classification, dict) and classification.get("owasp_version"):
                    detected_version = classification.get("owasp_version", OWASP_VERSION)
                elif ":2025" in report_category or ":2021" in report_category:
                    if ":2025" in report_category:
                        detected_version = "2025"
                    elif ":2021" in report_category:
                        detected_version = "2021"
                
                classification_result = {
                    "incident_type": report_category,
                    "fine_label": label,
                    "confidence": score,
                    "rationale": rationale,
                    "entities": ents.__dict__(),
                    "iocs": iocs,
                    "related_CVEs": related_cves[:5],  # Limit to 5 CVEs
                    "kb_excerpt": kb_context[:600] if kb_context else "",
                    "owasp_version": detected_version,  # Store version for display
                }
                
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
                    
                    version_badge = f"OWASP {OWASP_VERSION}"
                    response = f"✅ **I've analyzed your incident.**\n\n"
                    response += f"**Classification:** {user_friendly_name} ({version_badge})\n"
                    response += f"**Confidence:** {conf_pct}% "
                    
                    # Add confidence indicator
                    if conf_pct >= 80:
                        response += "🟢 (High)\n"
                    elif conf_pct >= 60:
                        response += "🟡 (Medium)\n"
                    else:
                        response += "🟠 (Low)\n"
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
                                    response += f"- {severity_emoji} **{cve_id}** {severity}{cvss_str}: {desc}...\n"
                                else:
                                    response += f"- **{cve_id}**\n"
                            except:
                                response += f"- **{cve_id}**\n"
                        response += "\n"
                    
                    # Check if ready for Phase-2
                    if st.session_state.dialogue_ctx.is_ready_for_phase2(thresh=THRESH_GO):
                        response += "🎯 **I have enough information!** Would you like me to generate a response plan?\n\n"
                        response += "Just say 'yes', 'generate plan', or 'create response plan' and I'll create step-by-step actions for you."
                    else:
                        response += "💡 I could use a bit more detail. Can you tell me more about what happened?"
                    
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
                    except:
                        # Fallback - make it more specific based on keywords
                        if any(word in description_text.lower() for word in ["syntax", "error", "weird", "strange"]):
                            clarifying_question = "This sounds like it might be a code injection issue. Can you tell me: What exact error messages or syntax did you see? Where did it appear (login page, search form, etc.)? Did you see any SQL errors or database messages?"
                        else:
                            clarifying_question = "I understand this is frustrating. Can you help me understand what happened? For example, what error messages did you see, or what suspicious activity did you notice?"
                    
                    # Use user-friendly language (already defined above)
                    version_badge = f"OWASP {OWASP_VERSION}"
                    response = f"🔍 I've analyzed your incident and I'm about {conf_pct}% confident this might be **{user_friendly_name}** ({version_badge}), but I'd like to gather more details to ensure accuracy.\n\n"
                    response += f"**{clarifying_question}**"
                    
                    st.write(response)
                    
                    # Store assistant message
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": response,
                        "classification": classification_result,
                        "timestamp": datetime.now()
                    })
                    
                    st.session_state.waiting_for_clarification = True
    
    st.rerun()

# Right Panel - Incident Details & Playbook (always visible)
with col2:
    st.header("📊 Incident Details")
    
    if st.session_state.get("current_classification") or st.session_state.get("phase1_output"):
        if st.session_state.get("phase1_output"):
            p1 = st.session_state.phase1_output
            category = p1.get("incident_type", "Unknown")
            owasp_id = ClassificationRules.get_owasp_display_name(p1["fine_label"], show_specific=False, version=OWASP_VERSION)
            
            # Extract OWASP ID and version for description lookup
            owasp_code = owasp_id.split(":")[0] if ":" in owasp_id else owasp_id.split()[0]
            owasp_desc = get_owasp_description(owasp_code)
            
            # Show version badge
            version_badge = f"🛡️ OWASP {OWASP_VERSION}"
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
                except:
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
st.caption("Powered by Gemini LLM | OWASP Top 10 2025 | NetworkX DAG Playbooks | OPA Policy Engine")

