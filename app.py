# Incident Response Platform
# Main Streamlit app - combines classification (Phase-1) and playbook execution (Phase-2)
# Started with OpenAI but switched to Gemini for better results

import streamlit as st
import time
import os
from dotenv import load_dotenv

# Phase-1 imports
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

# Phase-2 import
from phase2_engine.core.runner_bridge import run_phase2_from_incident

# Execution and CVE imports
from src.execution_simulator import ExecutionSimulator
from src.cve_service import CVEService

# Load environment variables
load_dotenv()

# Configuration
THRESH_GO = 0.65  # Confidence threshold for Phase-2
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Page config
st.set_page_config(
    page_title="Incident Response Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "dialogue_ctx" not in st.session_state:
    st.session_state.dialogue_ctx = DialogueState()

if "phase1_output" not in st.session_state:
    st.session_state.phase1_output = None

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
    st.session_state.cve_service = CVEService()

if "enable_execution" not in st.session_state:
    st.session_state.enable_execution = False


# ============================================
# Sidebar
# ============================================
with st.sidebar:
    st.title("🛡️ Incident Response")
    st.markdown("---")
    
    # Simple status
    st.caption("**Model:** Gemini 2.5 Pro")
    
    if st.session_state.get("phase1_output"):
        st.success("✅ Incident analysed")
    else:
        st.info("💬 Describe an incident to begin")
    
    st.markdown("---")
    
    # Execution simulation toggle
    st.session_state.enable_execution = st.checkbox(
        "🚀 Enable Execution Simulation",
        value=st.session_state.enable_execution,
        help="Simulate execution of response actions (safe demo mode)"
    )
    
    st.markdown("---")
    
    # Reset button only
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.dialogue_ctx.reset()
        st.session_state.phase1_output = None
        st.session_state.execution_simulator.clear_log()
        st.rerun()
    
    st.markdown("---")
    st.caption("AI-powered incident classification and response automation")


# ============================================
# Main Content
# ============================================
st.title("🛡️ Incident Response ChatOps Assistant")
st.subheader("💬 Ask the Incident Assistant")
st.caption("Describe what happened in your own words. The assistant will classify it and suggest a response plan.")

st.markdown("---")

# ============================================
# Phase-1: Incident Description Input
# ============================================
st.subheader("📝 Describe the Incident")

incident_description = st.text_area(
    "Incident Description",
    height=150,
    placeholder="Example: We detected SQL injection attempts from IP 192.168.1.100 targeting our login endpoint. "
                "The attacker used union-based injection with payloads like ' UNION SELECT username, password FROM users--",
    help="Describe the security incident in as much detail as possible. Include IPs, URLs, attack patterns, etc.",
    key="incident_input",
)

classify_button = st.button(
    "🔍 Classify Incident",
    type="primary",
    disabled=not incident_description.strip(),
    use_container_width=True,
)

# Always use full classification (no fast mode toggle for users)
use_explicit = False


# ============================================
# Phase-1: Classification Logic
# ============================================
if classify_button and incident_description.strip():
    with st.spinner("Analyzing incident..."):
        t0 = time.perf_counter()
        
        description_text = incident_description.strip()
        
        # Extract IOCs first
        ents = st.session_state.extractor.extract(description_text)
        iocs = {
            "ip": ents.ips,
            "url": ents.urls,
            "domain": ents.domains,
            "hash": ents.hashes,
            "email": ents.emails,
        }
        
        # Classification
        if use_explicit:
            # Fast keyword-based detection
            fine_label, score = st.session_state.explicit_detector.detect(description_text)
            
            if fine_label:
                report_category = ClassificationRules.normalize_label(fine_label)[1]
                rationale = f"Detected based on keyword patterns for {fine_label}"
            else:
                report_category = "Unknown"
                fine_label = "unknown"
                score = 0.0
                rationale = "No clear pattern detected"
        else:
            # LLM-based classification
            kb_context = st.session_state.kb_retriever.get_context_for_label(description_text)
            
            classification = st.session_state.llm_adapter.classify_incident(
                description=description_text,
                context=kb_context,
            )
            
            fine_label = classification.get("fine_label", "unknown")
            score = classification.get("confidence", 0.0)
            report_category = classification.get("incident_type", "Unknown")
            rationale = classification.get("rationale", "")
        
        # Build Phase-1 output
        label = fine_label.lower().replace(" ", "_")
        
        st.session_state.phase1_output = {
            "incident_type": report_category,
            "fine_label": label,
            "confidence": score,
            "rationale": rationale,
            "entities": ents.__dict__(),
            "iocs": iocs,
            "related_CVEs": ents.cves,
            "kb_excerpt": kb_context[:600] if not use_explicit else "",
            "timestamp_ms": round((time.perf_counter() - t0) * 1000, 1),
        }
        
        # Update dialogue state
        st.session_state.dialogue_ctx.add_turn(
            user_input=description_text,
            classification=st.session_state.phase1_output,
        )
        
        st.success(f"✅ Classification complete in {st.session_state.phase1_output['timestamp_ms']}ms")


# ============================================
# Phase-1: Display Classification Results
# ============================================
if st.session_state.get("phase1_output"):
    p1 = st.session_state.phase1_output
    
    st.markdown("---")
    st.subheader("🧾 Current Case Overview")
    
    owasp_name = get_owasp_display_name(p1["fine_label"], show_specific=True)
    conf_pct = int(p1["confidence"] * 100)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"**Type:** {owasp_name}")
    with col2:
        badge = format_confidence_badge(p1["confidence"])
        if conf_pct >= 70:
            st.success(f"**Confidence:** {badge}")
        elif conf_pct >= 60:
            st.warning(f"**Confidence:** {badge}")
        else:
            st.error(f"**Confidence:** {badge}")
    
    # Rationale
    if p1.get("rationale"):
        with st.expander("📖 Classification Rationale"):
            st.write(p1["rationale"])
    
    # Indicators
    indicators = []
    if p1["iocs"].get("ip"):
        indicators.append(f"{len(p1['iocs']['ip'])} IP(s)")
    if p1["iocs"].get("url"):
        indicators.append(f"{len(p1['iocs']['url'])} URL(s)")
    if p1.get("related_CVEs"):
        indicators.append(f"{len(p1['related_CVEs'])} CVE(s)")
    
    if indicators:
        st.write("**Indicators:** " + ", ".join(indicators))
        
        # Show IOCs in expander
        with st.expander("🔍 Extracted Indicators"):
            if p1["iocs"]["ip"]:
                st.write("**IPs:**", ", ".join(p1["iocs"]["ip"]))
            if p1["iocs"]["url"]:
                st.write("**URLs:**", ", ".join(p1["iocs"]["url"]))
            if p1["related_CVEs"]:
                st.write("**CVEs:**", ", ".join(p1["related_CVEs"]))
    
    # OWASP details
    owasp_id = ClassificationRules.normalize_label(p1["fine_label"])[0]
    owasp_details = get_owasp_description(owasp_id)
    
    with st.expander("📚 OWASP Category Details"):
        st.write(f"**{owasp_details['name']}**")
        st.write(owasp_details["description"])
        if owasp_details.get("examples"):
            st.write("**Common Examples:**")
            for ex in owasp_details["examples"]:
                st.write(f"- {ex}")
    
    # CVE Lookup
    st.markdown("---")
    st.subheader("🔍 Related Vulnerabilities")
    
    with st.spinner("Searching CVE database..."):
        # Extract keywords for CVE search
        search_term = owasp_name.lower()
        if "injection" in search_term:
            search_term = "sql injection"
        elif "xss" in search_term or "cross" in search_term:
            search_term = "xss"
        elif "authentication" in search_term:
            search_term = "authentication bypass"
        
        cve_results = st.session_state.cve_service.search_vulnerabilities(search_term, max_results=3)
        
        if cve_results:
            for cve in cve_results:
                severity_color = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                    "LOW": "🟢"
                }.get(cve["severity"], "⚪")
                
                with st.expander(f"{severity_color} {cve['cve_id']} - {cve['severity']} (CVSS: {cve['cvss_score']})"):
                    st.write(cve["description"])
                    st.caption(f"Published: {cve['published']} | Modified: {cve['modified']}")
        else:
            st.info("No related CVEs found in database.")
    
    # ============================================
    # Phase-2: Automated Response Plan
    # ============================================
    ctx = st.session_state.dialogue_ctx
    
    if ctx.is_ready_for_phase2(thresh=THRESH_GO):
        st.markdown("---")
        st.subheader("⚙️ Automated Response")
        
        st.info("💡 Your incident has been classified with sufficient confidence. Generate an automated response plan below.")
        
        # Optional: Multi-incident merge (can be hidden for simpler demo)
        extra_incidents_text = st.text_area(
            "Additional incidents to merge (optional)",
            placeholder="Leave empty if there is only one incident.",
            help="If multiple related incidents occurred, describe them here to create a unified response plan.",
            key="extra_incidents",
            height=80,
        )
        
        # Always simulate in this demo (no toggle shown to users)
        dry_run = True
        
        phase2_button = st.button(
            "🚀 Generate Response Plan",
            type="primary",
            key="phase2_trigger",
            use_container_width=True,
        )
        
        # Phase-2 execution
        if phase2_button:
            with st.spinner("Generating response plan..."):
                
                # For now, just use current incident
                # (Multi-incident merge can be added later)
                phase2_result = run_phase2_from_incident(
                    incident=p1,
                    merged_with=None,
                    dry_run=dry_run,
                )
                
                status = phase2_result.get("status")
                
                if status != "success":
                    st.error("❌ No suitable playbook found for this incident.")
                    st.caption(phase2_result.get("description", ""))
                else:
                    st.success("✅ Response plan generated successfully!")
                    
                    playbooks = phase2_result.get("playbooks", [])
                    main_pb = phase2_result.get("playbook", "Unknown")
                    
                    st.info(f"**Playbook(s):** {', '.join(playbooks) or main_pb}")
                    st.caption(phase2_result.get("description", ""))
                    
                    # Explain simulation mode
                    st.caption("ℹ️ **Note:** This plan is generated in simulation mode. No real actions are executed on your systems.")
                    
                    # Execution Simulation
                    if st.session_state.enable_execution:
                        st.markdown("---")
                        st.subheader("🚀 Executing Response Actions")
                        
                        # Convert phase2 steps to executable format
                        executable_steps = []
                        for step in phase2_result["steps"]:
                            executable_steps.append({
                                "action": step.get("name", "Unknown Action"),
                                "description": step.get("ui_description", step.get("message", ""))
                            })
                        
                        # Progress tracking
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        def update_progress(current, total, action_name):
                            progress = current / total
                            progress_bar.progress(progress)
                            status_text.text(f"Executing step {current}/{total}: {action_name}")
                        
                        # Execute with simulation
                        execution_results = st.session_state.execution_simulator.execute_playbook(
                            executable_steps,
                            progress_callback=update_progress
                        )
                        
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                        
                        # Display execution results
                        st.success(f"✅ Executed {len(execution_results)} actions successfully!")
                        
                        with st.expander("📋 View Execution Log", expanded=True):
                            for idx, result in enumerate(execution_results, 1):
                                col1, col2 = st.columns([1, 11])
                                
                                with col1:
                                    if result["status"] == "success":
                                        st.markdown("✅")
                                    else:
                                        st.markdown("❌")
                                
                                with col2:
                                    st.markdown(f"**{result['step']}**")
                                    st.caption(result["message"])
                                    if result.get("details"):
                                        st.caption(f"Details: {result['details']}")
                                    st.caption(f"⏱️ {result['execution_time']:.2f}s")
                                
                                if idx < len(execution_results):
                                    st.markdown("---")
                    
                    # Group steps by phase
                    steps_by_phase = {}
                    for step in phase2_result["steps"]:
                        phase = step.get("phase", "unknown")
                        steps_by_phase.setdefault(phase, []).append(step)
                    
                    # Display steps organized by NIST IR phases
                    phase_order = [
                        ("preparation", "🛡️ Preparation"),
                        ("detection_analysis", "🔍 Detection & Analysis"),
                        ("containment", "⚠️ Containment"),
                        ("eradication", "🧹 Eradication"),
                        ("recovery", "♻️ Recovery"),
                        ("post_incident", "📋 Post-Incident Review"),
                        ("unknown", "❓ Other Steps"),
                    ]
                    
                    st.markdown("---")
                    st.subheader("📋 Response Plan Steps")
                    
                    for key, title in phase_order:
                        if key in steps_by_phase:
                            st.markdown(f"### {title}")
                            
                            for idx, s in enumerate(steps_by_phase[key], 1):
                                col1, col2 = st.columns([1, 11])
                                
                                with col1:
                                    st.markdown(f"**{idx}.**")
                                
                                with col2:
                                    st.markdown(f"**{s['name']}**")
                                    
                                    if s.get("ui_description"):
                                        st.caption(s["ui_description"])
                                    elif s.get("message"):
                                        st.caption(s["message"])
                    
                    st.markdown("---")
                    
                    # Automation summary
                    automation = phase2_result.get("automation", {})
                    if automation.get("executed"):
                        st.subheader("🤖 Automation Summary")
                        details = automation.get("details", {})
                        if details:
                            st.write(f"**Status:** {details.get('status', 'Unknown')}")
                            
                            summary = details.get("summary", {})
                            if summary:
                                col1, col2, col3, col4 = st.columns(4)
                                col1.metric("Total Steps", summary.get("total_steps", 0))
                                col2.metric("Succeeded", summary.get("succeeded", 0))
                                col3.metric("Failed", summary.get("failed", 0))
                                col4.metric("Blocked", summary.get("blocked", 0))
                    elif automation.get("dry_run"):
                        st.info("💡 **Dry Run Mode:** No actions were actually executed. Uncheck 'Dry Run' to run real automation (use with caution!).")
                    
                    st.success("✅ You can refine the incident description and regenerate the plan if needed.")

else:
    st.info("👆 Enter an incident description above and click 'Classify Incident' to begin.")


# ============================================
# Footer
# ============================================
st.markdown("---")
st.caption("🛡️ Incident Response Platform | Phase-1: LLM Classification | Phase-2: DAG Automation")
