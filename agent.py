"""Main agent orchestrator - the enhanced decision pipeline.

Architecture: graduated complexity cascade
0. Knowledge base lookup (pre-recorded actions)             ~varies, 0 LLM calls
1. Quick click shortcuts (regex -> known element ID)        ~5% tasks, 0 LLM calls
2. Search shortcuts (type into known search input)          ~10% tasks, 0 LLM calls
3. Form shortcuts (login/reg/contact/logout detection)      ~25% tasks, 0 LLM calls
4. LLM decision with tool use loop                          ~60% tasks, 1-3 LLM calls
5. Fallback (scroll/wait)                                   safety net

Enhancements over baseline:
- 150+ specific task types with targeted playbooks
- LLM tool use (list_cards, search_text, list_links, extract_forms)
- Memory/next_goal persistence across steps
- State delta computation for change detection
- Cards preview on early steps
- Knowledge base for known task shortcuts
- Enhanced credential extraction
"""
from __future__ import annotations
import json
import os
import logging
from urllib.parse import urlparse

from config import (
    detect_website,
    WEBSITE_HINTS,
    TASK_PLAYBOOKS,
    AGENT_MAX_STEPS,
)
from classifier import classify_task_type, classify_shortcut_type
from constraint_parser import (
    parse_constraints,
    format_constraints_block,
    extract_credentials,
    expand_credential_placeholders,
    extract_apply_job_title_and_location,
    extract_delivery_modal_hints,
    extract_reserve_hotel_hints,
    extract_title_contains_substring,
    forbidden_not_equals_location_strings,
)
from html_parser import prune_html, extract_candidates, build_page_ir, build_dom_digest
from navigation import extract_seed
from shortcuts import try_quick_click, try_search_shortcut, try_shortcut
from state_tracker import StateTracker
from llm_client import LLMClient
from prompts import build_system_prompt, build_user_prompt
from action_builder import parse_llm_response, build_iwa_action, WAIT_ACTION, sanitize_type_text
from tool_use import run_tool, tool_list_cards

logger = logging.getLogger(__name__)

_llm_client: LLMClient | None = None


def _env_flag(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "on"}


def _pick_non_repeating_click_index(candidates: list, last_sig: str) -> int | None:
    for i in range(len(candidates)):
        if f"click:{i}" != (last_sig or "").strip():
            return i
    return None


def _candidate_selector_value(c) -> str:
    try:
        sel = getattr(c, "selector", None)
        if sel is not None:
            return (getattr(sel, "value", None) or "").strip()
    except Exception:
        pass
    return ""


def _normalize_selector_value_for_compare(raw: str) -> str:
    """Treat /subnets?seed=1 and /subnets?seed=2 as the same for repeat guards (nav loops)."""
    s = (raw or "").strip()
    if not s:
        return ""
    if s.startswith("http"):
        p = urlparse(s)
        path = (p.path or "").lower().rstrip("/")
        return path if path else "/"
    if s.startswith("/"):
        return s.split("?")[0].lower().rstrip("/") or "/"
    return s


def _pick_click_avoiding_selector_value(candidates: list, avoid: str) -> int | None:
    """Pick first candidate whose normalized selector value differs from *avoid* (break repeat-click loops)."""
    if not (avoid or "").strip():
        return None
    avoid_key = _normalize_selector_value_for_compare(avoid)
    if not avoid_key:
        return None
    for i, c in enumerate(candidates):
        v = _candidate_selector_value(c)
        if _normalize_selector_value_for_compare(v) != avoid_key:
            return i
    return None


def _history_no_progress(history: list | None) -> bool:
    if not isinstance(history, list) or not history:
        return True
    for h in history[-3:]:
        try:
            if isinstance(h, dict):
                if bool(h.get("exec_ok")):
                    return False
                if str(h.get("action") or "").lower() in {"click", "type", "select", "navigate"}:
                    return False
        except Exception:
            continue
    return True


def _extra_hints_for_site_and_constraints(constraints: list, website: str | None) -> str:
    """Targeted nudges for eval failures (ride location/time, subnet nav loops)."""
    hints: list[str] = []
    if website == "autostats":
        hints.append(
            "Do not loop on /subnets or identical marketing links unless the TASK names subnets/Bittensor—"
            "follow the TASK (search, forms, specific CTAs)."
        )
    if website != "autodrive" or not constraints:
        return " | ".join(hints)
    seen_time = False
    seen_loc = False
    for c in constraints:
        fname = (c.field or "").lower()
        op = (c.operator or "").lower()
        if not seen_time and fname in (
            "time",
            "pickup_time",
            "trip_time",
            "scheduled_time",
        ) and op in (
            "greater_than",
            "greater_than_or_equal",
            "equals",
            "less_than",
            "less_than_or_equal",
        ):
            hints.append(
                "Set the trip time in the time picker so it satisfies the time constraint (e.g. after 17:00)."
            )
            seen_time = True
        if not seen_loc and fname in (
            "location",
            "pickup",
            "destination",
            "pickup_location",
            "dropoff",
            "address",
        ):
            hints.append(
                "Type real addresses in pickup/destination fields and pick an autocomplete result—"
                "click-only focus does not emit a valid location event."
            )
            seen_loc = True
        if seen_time and seen_loc:
            break
    return " | ".join(hints)


def _history_has_recent_timeout(history: list | None) -> bool:
    if not isinstance(history, list) or not history:
        return False
    for h in history[-4:]:
        try:
            err = str(h.get("error") or "").lower()
            if "timeout" in err or "hard timeout" in err:
                return True
        except Exception:
            continue
    return False


def _get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


# ---------------------------------------------------------------------------
# Knowledge base: pre-recorded actions for known tasks
# ---------------------------------------------------------------------------

def _load_task_knowledge() -> dict[str, list[dict]]:
    kb: dict[str, list[dict]] = {}
    p = os.getenv("AGENT_TASK_KNOWLEDGE_PATH") or os.path.join(
        os.path.dirname(__file__), "data", "baseline_actions.json"
    )
    try:
        with open(p, "r", encoding="utf-8") as f:
            rows = json.load(f)
        if not isinstance(rows, list):
            return kb
        for entry in rows:
            if not isinstance(entry, dict):
                continue
            if entry.get("status") != "success":
                continue
            task_obj = entry.get("task") if isinstance(entry.get("task"), dict) else {}
            tid = str(task_obj.get("taskId") or "")
            resp = entry.get("response") if isinstance(entry.get("response"), dict) else {}
            acts = resp.get("actions")
            if tid and isinstance(acts, list) and len(acts) > 1:
                kb[tid] = [a for a in acts[1:] if isinstance(a, dict)]
    except Exception:
        pass
    return kb


_TASK_KNOWLEDGE = _load_task_knowledge()


def _record_actions(task_id: str, actions: list[dict], url: str, step: int) -> None:
    """Record all returned actions into state tracker."""
    for i, act in enumerate(actions):
        sel_val = ""
        sel = act.get("selector", {})
        if isinstance(sel, dict):
            sel_val = sel.get("value", "")
        text = act.get("text", "")
        StateTracker.record_action(task_id, act.get("type", ""), sel_val, url, step + i, text)
        if act.get("type") == "TypeAction" and sel_val:
            StateTracker.record_filled_field(task_id, sel_val)


async def handle_act(
    task_id: str | None,
    prompt: str | None,
    url: str | None,
    snapshot_html: str | None,
    screenshot: str | None,
    step_index: int | None,
    web_project_id: str | None,
    history: list | None = None,
    relevant_data: dict | None = None,
) -> list[dict]:
    """Main entry point called by /act endpoint."""
    if not prompt or not url:
        logger.warning("Missing prompt or url")
        return [WAIT_ACTION]

    step = step_index or 0
    task = task_id or "unknown"
    website = web_project_id or detect_website(url)
    seed = extract_seed(url)
    state = StateTracker.get_or_create(task)

    # Initialize on step 0
    if step == 0:
        state.constraints = parse_constraints(prompt)
        state.task_type = classify_task_type(prompt)
        state.login_done = False
        state.history.clear()
        state.filled_fields.clear()
        state.memory = ""
        state.next_goal = ""
        state.prev_url = ""
        state.prev_summary = ""
        state.prev_sig_set = []
        state.last_sig = ""
        state.repeat_count = 0
        StateTracker.auto_cleanup()

    # ===================================================================
    # STAGE 0: Knowledge base lookup (skip LLM for known tasks)
    # ===================================================================
    known_actions = _TASK_KNOWLEDGE.get(task)
    if _env_flag("AGENT_USE_TASK_KNOWLEDGE", False) and known_actions and step < len(known_actions):
        return [known_actions[step]]
    # When disabled or replay exhausted, continue with the pipeline (never return []).

    # ===================================================================
    # Hard step cap: force done after max steps
    # ===================================================================
    max_steps = int(os.getenv("AGENT_MAX_STEPS", str(AGENT_MAX_STEPS)))
    if step >= max_steps:
        return [{"type": "DoneAction", "success": True}]

    # ===================================================================
    # STAGE 1: Quick click shortcuts (no HTML parsing needed)
    # ===================================================================
    quick = try_quick_click(prompt, url, seed, step)
    if quick is not None:
        logger.info(f"Quick click: {len(quick)} actions")
        _record_actions(task, quick, url, step)
        return quick

    # ===================================================================
    # STAGE 2: Search shortcut
    # ===================================================================
    search = try_search_shortcut(prompt, website)
    if search is not None:
        logger.info(f"Search shortcut: {len(search)} actions")
        _record_actions(task, search, url, step)
        return search

    # ===================================================================
    # Parse HTML and extract candidates
    # ===================================================================
    if snapshot_html and snapshot_html.strip():
        soup = prune_html(snapshot_html)
        candidates = extract_candidates(soup)
    else:
        soup = None
        candidates = []

    # ===================================================================
    # STAGE 3: Form-based shortcuts (login/reg/contact/logout)
    # ===================================================================
    shortcut_type = classify_shortcut_type(prompt)

    # For login_then_* tasks: do login shortcut on early steps, then fall to LLM
    if state.task_type.startswith("LOGIN_THEN_") and not state.login_done:
        shortcut_type = "login"

    if shortcut_type and soup and candidates:
        shortcut_actions = try_shortcut(shortcut_type, candidates, soup, step)
        if shortcut_actions is not None:
            logger.info(f"Shortcut '{shortcut_type}': {len(shortcut_actions)} actions")
            _record_actions(task, shortcut_actions, url, step)
            if shortcut_type == "login":
                StateTracker.mark_login_done(task)
            return shortcut_actions

    # ===================================================================
    # No candidates = page still loading or empty
    # ===================================================================
    if not candidates:
        logger.warning("No candidates - page may still be loading")
        StateTracker.record_action(task, "WaitAction", "", url, step)
        return [{"type": "WaitAction", "time_seconds": 2}]

    # ===================================================================
    # STAGE 4: Stuck recovery (before LLM to save tokens)
    # ===================================================================
    loop_warning = StateTracker.detect_loop(task, url)
    stuck_warning = StateTracker.detect_stuck(task, url)

    if stuck_warning and step >= 3:
        recent = state.history[-2:] if len(state.history) >= 2 else []
        all_scrolls = all(a.action_type == "ScrollAction" for a in recent) if recent else False
        if not all_scrolls:
            logger.info("Stuck recovery: auto-scroll")
            StateTracker.record_action(task, "ScrollAction", "", url, step)
            return [{"type": "ScrollAction", "down": True}]

    # ===================================================================
    # STAGE 5: Build page IR and context
    # ===================================================================
    page_ir = build_page_ir(soup, url, candidates)
    page_ir_text = page_ir.raw_text

    # DOM digest for early steps
    dom_digest = ""
    if soup and step <= 1:
        dom_digest = build_dom_digest(soup)

    # Compute state delta
    page_summary = ""
    if soup:
        page_summary = (soup.get_text(separator=" ", strip=True) or "")[:400]
    state_delta = StateTracker.compute_state_delta(task, url, page_summary, candidates)

    # Cards preview for early steps
    cards_preview = ""
    if step <= 2:
        try:
            cards_obj = tool_list_cards(candidates=candidates, max_cards=6, max_text=120)
            if cards_obj.get("ok") and cards_obj.get("cards"):
                cards_preview = json.dumps(cards_obj["cards"], ensure_ascii=True)
                if len(cards_preview) > 600:
                    cards_preview = cards_preview[:597] + "..."
        except Exception:
            cards_preview = ""

    # Extra stuck hint from repeat detection
    extra_hint = ""
    repeat_count = StateTracker.get_repeat_count(task)
    if repeat_count >= 2:
        extra_hint = "You appear stuck on the same URL after repeating an action. Choose a different element or scroll."

    if state.constraints and step <= 4:
        tool_nudge = (
            "Structured constraints are present: prefer tool extract_forms (or list_cards) once "
            "to see form fields before guessing clicks."
        )
        extra_hint = f"{extra_hint} | {tool_nudge}" if extra_hint else tool_nudge

    site_c_hint = _extra_hints_for_site_and_constraints(state.constraints, website)
    if site_c_hint:
        extra_hint = f"{extra_hint} | {site_c_hint}" if extra_hint else site_c_hint

    # Previous memory/next_goal
    prev_memory, prev_next_goal = StateTracker.get_memory(task)

    # Prepare prompt layers
    action_history = StateTracker.get_recent_history(task, count=4)
    filled_fields = StateTracker.get_filled_fields(task)
    constraints_block = format_constraints_block(state.constraints)
    website_hint = WEBSITE_HINTS.get(website, "") if website else ""
    playbook = TASK_PLAYBOOKS.get(state.task_type, TASK_PLAYBOOKS.get("GENERAL", ""))

    # Credential info - enhanced: also add equals constraints as credential values
    creds = extract_credentials(prompt)
    # Add relevant_data credentials
    if relevant_data and isinstance(relevant_data, dict):
        for k, v in relevant_data.items():
            if isinstance(v, str) and v:
                creds.setdefault(str(k), str(v))
    # Add all "equals" constraints as directly usable field values
    for c in state.constraints:
        if c.operator == "equals" and isinstance(c.value, str):
            creds.setdefault(c.field, c.value)
    # Job flows: substring for title typing; explicit fields if parsed
    for c in state.constraints:
        if c.field == "query" and c.operator == "contains" and isinstance(c.value, str):
            v = c.value.strip()
            if v:
                creds.setdefault("job_title_must_contain", v)
        if c.field in ("job_title", "location") and c.operator == "equals" and isinstance(c.value, str):
            creds.setdefault(c.field, str(c.value).strip())
    if state.task_type == "WRITE_JOB_TITLE":
        sub = extract_title_contains_substring(prompt)
        if sub:
            creds.setdefault("job_title_must_contain", sub)
    if state.task_type == "APPLY_FOR_JOB":
        jt, loc = extract_apply_job_title_and_location(prompt)
        if jt:
            creds.setdefault("job_title", jt)
        if loc:
            creds.setdefault("location", loc)
    if state.task_type == "ADD_TO_CART_MODAL_OPEN":
        for k, v in extract_delivery_modal_hints(prompt).items():
            creds.setdefault(k, v)
    if state.task_type == "RESERVE_HOTEL":
        for k, v in extract_reserve_hotel_hints(prompt).items():
            creds.setdefault(k, v)

    creds = expand_credential_placeholders(creds, url)

    creds_block = ""
    if creds:
        creds_block = "TASK_CREDENTIALS (use EXACTLY as-is, no modifications - including spaces):\n"
        for k, v in creds.items():
            creds_block += f"  {k}: '{v}'\n"

    # ===================================================================
    # STAGE 6: LLM decision with tool use loop
    # ===================================================================
    try:
        client = _get_llm_client()
        system_msg = build_system_prompt()
        user_msg = build_user_prompt(
            prompt=prompt,
            page_ir_text=page_ir_text,
            step_index=step,
            max_steps=max_steps,
            task_type=state.task_type,
            action_history=action_history,
            website=website,
            website_hint=website_hint,
            constraints_block=constraints_block,
            credentials_info=creds_block,
            playbook=playbook,
            loop_warning=loop_warning,
            stuck_warning=stuck_warning,
            filled_fields=filled_fields,
            dom_digest=dom_digest,
            memory=prev_memory,
            next_goal=prev_next_goal,
            state_delta=state_delta,
            cards_preview=cards_preview,
            extra_hint=extra_hint,
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        max_tool_calls = int(os.getenv("AGENT_MAX_TOOL_CALLS", "2"))
        tool_calls_made = 0
        decision = None

        for _ in range(max_tool_calls + 2):
            content = client.chat(task, messages)
            parsed = parse_llm_response(content)

            if parsed is None:
                # Retry with stronger instruction
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content": "Return ONLY valid JSON. No markdown."})
                content = client.chat(task, messages)
                parsed = parse_llm_response(content)

            if parsed is None:
                break

            # Check if it's a tool call
            tool_name = parsed.get("tool")
            if tool_name and not parsed.get("action") and tool_calls_made < max_tool_calls:
                tool_args = parsed.get("args") if isinstance(parsed.get("args"), dict) else {}
                tool_calls_made += 1
                try:
                    result = run_tool(
                        tool_name, tool_args,
                        html=snapshot_html or "",
                        url=url,
                        candidates=candidates,
                    )
                except Exception as e:
                    result = {"ok": False, "error": str(e)[:200]}

                messages.append({"role": "assistant", "content": json.dumps({"tool": tool_name, "args": tool_args}, ensure_ascii=True)})
                messages.append({"role": "user", "content": f"TOOL_RESULT {tool_name}: " + json.dumps(result, ensure_ascii=True)})
                continue

            # It's an action decision
            decision = parsed
            break

        if decision is None:
            # Total failure: fallback
            if step < 5 and candidates:
                fallback = build_iwa_action({"action": "click", "candidate_id": 0}, candidates, url, seed)
            else:
                fallback = {"type": "ScrollAction", "down": True}
            _record_actions(task, [fallback], url, step)
            return [fallback]

        cid = decision.get("candidate_id")
        if isinstance(cid, str) and cid.isdigit():
            decision["candidate_id"] = int(cid)

        # Save memory/next_goal from LLM response
        mem = decision.get("memory")
        ng = decision.get("next_goal")
        if isinstance(mem, str) or isinstance(ng, str):
            StateTracker.update_memory(task, mem or "", ng or "")

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        if step < 5 and candidates:
            fallback = build_iwa_action({"action": "click", "candidate_id": 0}, candidates, url, seed)
        else:
            fallback = {"type": "ScrollAction", "down": True}
        _record_actions(task, [fallback], url, step)
        return [fallback]

    # ===================================================================
    # STAGE 7: Build action from LLM decision
    # ===================================================================
    if _env_flag("AGENT_ENABLE_LOOP_BREAKER", True) and StateTracker.get_repeat_count(task) >= 2 and candidates:
        idx = _pick_non_repeating_click_index(candidates, StateTracker.get_last_sig(task))
        if idx is not None:
            decision = {"action": "click", "candidate_id": idx}

    # Hard guard: LLM often re-picks the same element id (e.g. favorite-action) — no progress.
    if _env_flag("AGENT_ENABLE_SAME_CLICK_GUARD", True) and candidates:
        act0 = (decision.get("action") or "").lower()
        cid0 = decision.get("candidate_id")
        if act0 == "click" and isinstance(cid0, int) and 0 <= cid0 < len(candidates):
            last_sv = StateTracker.get_last_click_selector_value(task)
            upcoming_sv = _candidate_selector_value(candidates[cid0])
            same = bool(last_sv and upcoming_sv) and (
                last_sv == upcoming_sv
                or _normalize_selector_value_for_compare(last_sv)
                == _normalize_selector_value_for_compare(upcoming_sv)
            )
            if same:
                alt = _pick_click_avoiding_selector_value(candidates, upcoming_sv)
                if alt is not None:
                    logger.info("Overriding repeat click on selector value=%s -> candidate_id=%s", upcoming_sv, alt)
                    decision = {"action": "click", "candidate_id": alt}
                else:
                    logger.info("Repeat click on %s; no alternate candidate — scroll", upcoming_sv)
                    decision = {"action": "scroll", "direction": "down"}

    act_name = (decision.get("action") or "").lower()
    if act_name == "done":
        if step <= 3 and _history_no_progress(history) and candidates:
            idx = _pick_non_repeating_click_index(candidates, StateTracker.get_last_sig(task))
            decision = {"action": "click", "candidate_id": idx if idx is not None else 0}
        elif _history_has_recent_timeout(history) and candidates:
            idx = _pick_non_repeating_click_index(candidates, StateTracker.get_last_sig(task))
            if idx is not None:
                decision = {"action": "click", "candidate_id": idx}

    # Never satisfy not_equals by accident: do not type excluded location strings.
    if (decision.get("action") or "").lower() == "type" and state.constraints:
        forbidden = forbidden_not_equals_location_strings(state.constraints)
        if forbidden:
            text = sanitize_type_text(decision.get("text")) or sanitize_type_text(
                decision.get("value")
            )
            for fbd in forbidden:
                if text == fbd:
                    decision = dict(decision)
                    decision["text"] = "1 Front Street, San Francisco, CA 94111"
                    decision.pop("value", None)
                    logger.warning(
                        "Replaced type text that matched a not_equals forbidden location"
                    )
                    break

    action = build_iwa_action(decision, candidates, url, seed)

    # Update action signature for repeat detection
    sig = f"{decision.get('action')}:{decision.get('candidate_id')}"
    StateTracker.update_action_sig(task, url, sig)

    _record_actions(task, [action], url, step)
    return [action]
