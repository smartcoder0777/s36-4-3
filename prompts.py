"""Enhanced multi-layer prompt construction with memory, state delta, and tool use support."""
from __future__ import annotations


def build_system_prompt() -> str:
    return (
        "You are a web automation agent. Return JSON only (no markdown). "
        "Keys: action, candidate_id, text, url, evaluation_previous_goal, memory, next_goal.\n"
        "action: click|type|select_option|navigate|scroll|done. "
        "click/type/select_option: candidate_id=integer from the Interactive elements list. "
        "navigate: url=full URL (keep ?seed=X param). "
        "done: only when task is fully completed.\n"
        "SUCCESS: Tasks are graded on backend events (form submit, booking, order). You must complete "
        "the flow that fires that event—filling fields per CONSTRAINTS and clicking Submit/Book/Confirm. "
        "Browsing carousels or clicking Next/Previous on hero sliders does NOT complete most tasks.\n"
        "CAROUSEL/TRAP: Do NOT click carousel next/prev/home/logo unless the TASK explicitly asks to "
        "browse slides. Prefer: forms, Book/Reserve/Submit, search bars, doctor/restaurant cards, "
        "and in-app navigation that matches the TASK.\n"
        "LISTINGS (hotels, restaurants, doctors): If constraints use greater_than / not_equals / "
        "not_contains on ids or titles, you must find and open or book the item that satisfies ALL "
        "constraints—do NOT spam favorite/heart/star or generic nav links; use search, filters, "
        "list rows, or Book/View details.\n"
        "Do NOT click nav_home_link, brand-link, or home/logo unless the task is explicitly to return home.\n"
        "BOOKING FORMS: After selecting a payment radio or filling a booking field, you MUST click the "
        "Confirm/Book/Submit button—selecting alone never fires a backend event.\n"
        "MARKETING/NAV: On landing pages with many identical links (e.g. /subnets), do not cycle the same "
        "href or hero carousel—use the TASK wording to pick search, signup, or the one CTA that matches.\n"
        "RIDE/TRIP (pickup, destination, time): After focusing a location field, you MUST type a real address "
        "on the next step and choose a suggestion if offered. For time constraints (e.g. after 17:00), open "
        "the time control and pick a slot that satisfies greater_than/less_than—default time is usually wrong.\n"
        "HOTEL FILTERS: When the task mentions rating/region filters, use the filter bar controls and click "
        "**Apply** so APPLY_FILTERS fires—search alone is not enough.\n"
        "CALENDAR: 'Add new calendar' (sidebar +) opens a new calendar modal—do not confuse with 'create new event'.\n"
        "CRM DELETE: Go to Clients, find the row matching ALL constraints, open the client, then Delete client and confirm.\n"
        "RULES: Copy values EXACTLY from CREDENTIALS/CONSTRAINTS (include trailing spaces). "
        "equals->type exact value. not_equals->use any OTHER value. contains->find item with that substring. "
        "not_contains/not_in->find item WITHOUT that value. greater/less->numeric comparison.\n"
        "CREDENTIALS: username/email may have trailing spaces - type them exactly as shown in quotes.\n"
        "MULTI-STEP: complete login first, then the secondary action. Track progress in memory.\n"
        "TOOLS: Return {\"tool\":\"<name>\",\"args\":{...}} to inspect page. Max 1 tool per step. "
        "Tools: list_cards({max_cards?,max_text?}); search_text({query}); list_links({}); extract_forms({}). "
        "Use extract_forms early if the task needs booking or multi-field forms.\n"
        "JSON ONLY. No explanation."
    )


def build_user_prompt(
    *,
    prompt: str,
    page_ir_text: str,
    step_index: int,
    max_steps: int,
    task_type: str,
    action_history: list[str],
    website: str | None,
    website_hint: str = "",
    constraints_block: str = "",
    credentials_info: str = "",
    playbook: str = "",
    loop_warning: str | None = None,
    stuck_warning: str | None = None,
    filled_fields: set[str] | None = None,
    dom_digest: str = "",
    # New features
    memory: str = "",
    next_goal: str = "",
    state_delta: str = "",
    cards_preview: str = "",
    extra_hint: str = "",
) -> str:
    parts: list[str] = []

    # --- Core task context ---
    parts.append(f"TASK: {prompt}")

    cap = max(1, int(max_steps))
    site_line = f"TYPE:{task_type} SITE:{website or 'unknown'} STEP:{step_index} of {cap}"
    parts.append(site_line)

    # --- Urgency signal ---
    remaining = max(1, cap - step_index)
    if remaining <= 3:
        parts.append(f"WARNING: ONLY {remaining} STEPS LEFT - take the most direct action NOW.")

    # --- Website hints ---
    if website_hint:
        hint_capped = website_hint[:150] + "..." if len(website_hint) > 150 else website_hint
        parts.append(f"\nSITE_HINTS: {hint_capped}")

    # --- Credentials ---
    if credentials_info:
        parts.append(f"\n{credentials_info}")

    # --- Constraints ---
    if constraints_block:
        parts.append(f"\n{constraints_block}")
        parts.append(
            "\nEVAL_HINT: Satisfy every constraint via the real UI flow (select fields, type text, then "
            "Submit/Book/Confirm). action=done only after that flow is complete—not while still on a carousel or landing hero."
        )

    # --- Playbook ---
    if playbook:
        playbook_capped = playbook[:350] + "..." if len(playbook) > 350 else playbook
        parts.append(f"\n{playbook_capped}")

    # --- Page summary (DOM digest, early steps only) ---
    if dom_digest and step_index <= 1:
        dom_capped = dom_digest[:200]
        parts.append(f"\nDOM:\n{dom_capped}")

    # --- Cards preview (early steps only) ---
    if cards_preview and step_index <= 2:
        parts.append(f"\nCARDS:\n{cards_preview}")

    # --- Warnings ---
    if loop_warning:
        parts.append(f"\nWARNING: {loop_warning}")
    if stuck_warning:
        parts.append(f"\nWARNING: {stuck_warning}")
    if extra_hint:
        parts.append(f"\nHINT: {extra_hint}")

    # --- Action history ---
    if action_history:
        history_text = "\n".join(f"  {h}" for h in action_history)
    else:
        history_text = "  None yet"
    parts.append(f"\nHISTORY:\n{history_text}")

    # --- Memory from previous step ---
    if memory or next_goal:
        mem_parts = []
        if memory:
            mem_parts.append(f"PREVIOUS MEMORY: {memory}")
        if next_goal:
            mem_parts.append(f"PREVIOUS NEXT_GOAL: {next_goal}")
        parts.append("\n" + "\n".join(mem_parts))

    # --- State delta ---
    if state_delta:
        parts.append(f"\nDELTA: {state_delta[:200]}")

    # --- Filled fields ---
    if filled_fields:
        parts.append(f"\nALREADY FILLED: {', '.join(sorted(filled_fields))}")

    # --- Page IR (always) ---
    parts.append(f"\nBROWSER_STATE:\n{page_ir_text}")

    # --- Final instruction ---
    parts.append("\nONE JSON action only.")

    return "\n".join(parts)
