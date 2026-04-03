"""Pre-built shortcut actions that bypass LLM for deterministic tasks.

Combines:
- Quick click patterns (Onyxdrift) for known UI elements
- Search shortcuts (Onyxdrift) with extended site coverage
- Enhanced form detection (all three agents) for login/registration/contact/logout
- Multi-step sequences for compound tasks
"""
from __future__ import annotations
import re
from bs4 import BeautifulSoup

from models import Candidate
from constraint_parser import extract_search_query
from config import SEARCH_INPUT_IDS


def _sel_attr(attribute: str, value: str) -> dict:
    return {"type": "attributeValueSelector", "attribute": attribute, "value": value, "case_sensitive": False}


def _click(attribute: str, value: str) -> list[dict]:
    return [{"type": "ClickAction", "selector": _sel_attr(attribute, value)}]


def _click_xpath(xpath: str) -> list[dict]:
    return [{"type": "ClickAction", "selector": {"type": "xpathSelector", "value": xpath}}]


# ---------------------------------------------------------------------------
# Quick click: regex → fixed element
# ---------------------------------------------------------------------------

def try_quick_click(prompt: str, url: str, seed: str | None, step: int) -> list[dict] | None:
    t = prompt.lower()
    from urllib.parse import urlsplit

    _port = urlsplit(url).port
    port = _port  # legacy name used below

    # Calendar
    if re.search(r"go\s+to\s+today|focus.*today|today.?s?\s+date\s+in\s+the\s+calendar", t):
        return _click("id", "focus-today")

    # AutoCalendar (8010): open "add NEW calendar" modal — NOT the same as "create new event".
    # The old pattern wrongly clicked new-event-cta; ADD_NEW_CALENDAR uses the sidebar + button.
    if _port == 8010 and re.search(
        r"add\s+calendar\s+button|modal\s+for\s+adding\s+a\s+new\s+calendar|open\s+the\s+modal.*new\s+calendar|"
        r"press\s+the\s+button\s+to\s+add\s+a\s+calendar",
        t,
    ) and not re.search(r"calendar\s+event|new\s+calendar\s+event|add\s+an?\s+event", t):
        return _click("aria-label", "Add new calendar")

    # Create new calendar *event* (different from ADD_NEW_CALENDAR)
    if re.search(r"add\s+a?\s*new\s+calendar\s+event|create\s+new\s+calendar\s+event", t):
        return _click("id", "new-event-cta")
    if re.search(r"click.*add\s+team|add\s+team\s+button", t):
        return _click("id", "add-team-btn")

    # Wishlist / favorites
    if re.search(r"(show\s+me\s+my\s+saved|my\s+wishlist|show.*wishlist|view.*wishlist|favorites?\s+page)", t):
        return _click("id", "favorite-action")

    # Navbar navigation
    if re.search(r"clicks?\s+on\s+the\s+jobs?\s+option\s+in\s+the\s+navbar", t):
        return _click("href", f"/jobs?seed={seed}") if seed else None
    if re.search(r"clicks?\s+on\s+.*profile\s+.*in\s+the\s+navbar", t):
        return _click("href", f"/profile/alexsmith?seed={seed}") if seed else None

    # Featured / spotlight items
    if re.search(r"(spotlight|featured)\s+.*(?:movie|film).*details|view\s+details\s+.*(?:spotlight|featured)\s+(?:movie|film)", t):
        return _click("id", "spotlight-view-details-btn")
    if re.search(r"(spotlight|featured)\s+.*book.*details|view\s+details\s+.*(?:featured|spotlight)\s+book", t):
        return _click("id", "featured-book-view-details-btn-1")
    if re.search(r"(spotlight|featured)\s+.*product.*details|view\s+details\s+.*(?:featured|spotlight)\s+product", t):
        return _click("id", "view-details")

    # Autoconnect home tab
    if port == 8008 and re.search(r"go\s+to\s+the\s+home\s+tab|home\s+tab\s+from\s+the\s+navbar", t):
        return _click_xpath("//header//nav/a[1]")

    # Clear selection
    if re.search(r"clear\s+(the\s+)?(current\s+)?selection", t):
        return _click_xpath("(//button[@role='checkbox'])[1]")

    # About page feature (multi-step)
    if re.search(r"about\s+page.*feature|feature.*about\s+page", t):
        if step == 0:
            return _click("id", "nav-about")
        elif step == 1:
            return [{"type": "ScrollAction", "down": True}]
        else:
            return _click_xpath("//h3[contains(text(),'Curated')]")

    # Like a post (autoconnect)
    m = re.search(r"like\s+(?:the\s+)?(?:post|first\s+post|latest\s+post)", t)
    if m and port == 8008:
        return _click("id", "post_like_button_p1")

    # --- Season 1 overfit additions ---

    # Calendar view switching (autocalendar 8010) — word boundaries avoid
    # false matches like "switch to monthly" or stray "week" in unrelated copy.
    if port == 8010:
        for view_name in ("day", "week", "month"):
            if re.search(rf"\bswitch to {view_name}\b", t, re.IGNORECASE) or re.search(
                rf"\b{view_name}\s+view\b", t, re.IGNORECASE
            ):
                label_map = {"day": "Select Day view", "week": "Select Week view", "month": "Select Month view"}
                if step == 0 and view_name == "day":
                    # Many builds allow direct click without opening the selector first.
                    return _click("aria-label", "Select Day view")
                if step == 0:
                    return _click("id", "view-selector")
                elif step == 1:
                    return _click("aria-label", label_map.get(view_name, f"Select {view_name.title()} view"))
                # step >= 2: fall through to LLM
                return None

    # Navbar hires (autowork 8009)
    if port == 8009:
        if re.search(r"hire\s+later.*navbar|navbar.*hire\s+later", t):
            return _click("href", f"/hire-later?seed={seed}") if seed else None
        if re.search(r"hires.*navbar|navbar.*hires", t):
            return _click("href", f"/hires?seed={seed}") if seed else None
        if "book a consultation" in t or "consultation" in t:
            return _click_xpath("//*[contains(@id, 'book-consultation-button')]")

    # About page (autodining 8003)
    if port == 8003 and re.search(r"about\s+page|navigate.*about.*information", t):
        return _click("id", "about-menu-item")

    # Contact page (autodining 8003) — CONTACT_PAGE_VIEW
    if port == 8003 and re.search(r"open\s+the\s+contact\s+page", t):
        if seed:
            return _click("href", f"/contact?seed={seed}")
        return _click("href", "/contact")

    # View cart (autozone 8002)
    if port == 8002:
        if re.search(r"shopping\s+cart|contents\s+of\s+my", t):
            return _click("id", "cart-icon")
        if re.search(r"wishlist", t):
            return _click("id", "wishlist-btn")

    # View cart (autobooks 8001)
    if port == 8001 and re.search(r"shopping\s+cart|view\s+the\s+shopping\s+cart|cart\s+contents", t):
        return _click_xpath("//*[contains(@id,'cart') or contains(@href,'/cart') or contains(.,'Cart')]")

    # Add book (autobooks 8001)
    if port == 8001 and re.search(r"(add|create)\s+a\s+book", t):
        return _click_xpath("//*[contains(@id,'add-book') or contains(@id,'new-book') or contains(.,'Add Book')]")

    # Help viewed (generic help nav)
    if re.search(r"\bhelp\s+page\b|open\s+the\s+help", t):
        return _click_xpath("//*[contains(@id,'help') or contains(@href,'help') or contains(.,'Help') or contains(.,'FAQ')]")

    # AutoList add-task click (8011)
    if port == 8011 and re.search(r"create\s+a\s+new\s+task|add\s+a\s+new\s+task", t):
        return _click_xpath("//*[contains(@id,'add-task') or contains(@id,'new-task') or contains(.,'Add Task')]")
    if port == 8011 and re.search(r"cancel\s+the\s+task\s+creation|cancel\s+creating\s+the\s+task", t):
        if step == 0:
            return _click_xpath("//*[contains(@id,'add-task') or contains(@id,'new-task') or contains(.,'Add Task')]")
        if step == 1:
            return _click_xpath("//*[contains(@id,'cancel') or contains(.,'Cancel') or contains(.,'Discard')]")
        return None

    # AutoLodge (8007): APPLY_FILTERS — rating + region dropdowns, then Apply (CheckEventTest APPLY_FILTERS).
    if port == 8007 and re.search(
        r"show\s+details\s+for\s+hotels|hotels\s+with.*rating|region\s+that\s+contains|apply\s+filters",
        t,
    ):
        if step == 0:
            return [
                {
                    "type": "SelectDropDownOptionAction",
                    "selector": _sel_attr("id", "rating-filter"),
                    "text": "Any",
                }
            ]
        if step == 1:
            region_label = "Ireland" if "ireland" in t else "All"
            return [
                {
                    "type": "SelectDropDownOptionAction",
                    "selector": _sel_attr("id", "region-filter"),
                    "text": region_label,
                }
            ]
        if step == 2:
            return _click_xpath("(//div[contains(@class,'filters-bar')]//button)[last()]")
        return None

    # View pending events (autocrm 8004)
    # Only handle steps 0 and 1; fall through to LLM for subsequent steps.
    if port == 8004 and "pending" in t and "event" in t:
        if step == 0:
            return _click("id", "appointments-nav")
        elif step == 1:
            return _click("id", "toggle-future-events")
        # step >= 2: fall through to LLM to complete the task
        return None

    # Enter location (autodrive 8012)
    if port == 8012:
        _loc_xpath = ("//input[contains(@placeholder, 'Pickup location') or "
                     "contains(@placeholder, 'Where from?') or "
                     "contains(@placeholder, 'Enter pickup') or "
                     "contains(@placeholder, 'Start location') or "
                     "contains(@placeholder, 'Where are you?')]")
        m_time = re.search(r"time\s+for\s+my\s+trip\s+to\s+be\s+at\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if m_time:
            time_val = m_time.group(1).strip()
            # Convert 22:00:00 -> 10:00 PM when needed.
            m24 = re.match(r"^(\d{1,2}):(\d{2})(?::\d{2})?$", time_val)
            if m24:
                hh = int(m24.group(1))
                mm = m24.group(2)
                ap = "AM" if hh < 12 else "PM"
                hh12 = hh % 12 or 12
                time_val = f"{hh12}:{mm} {ap}"
            if step == 0:
                return _click_xpath(
                    "//input[contains(@id,'time') or contains(@placeholder,'time') or contains(@aria-label,'time')]"
                )
            if step == 1:
                return _click_xpath(
                    f"//*[contains(@id,'time-option') and contains(., '{time_val}') or contains(., '{time_val}')]"
                )
            return None
        if "search location" in t:
            m2 = re.search(r"(?:for |details for )['\"]([^'\"]+)['\"]", prompt)
            if m2:
                if step == 0:
                    return _click_xpath(_loc_xpath)
                elif step == 1:
                    return [{"type": "TypeAction", "text": m2.group(1),
                             "selector": {"type": "xpathSelector", "value": _loc_xpath}}]
                # step >= 2: fall through to LLM
                return None
        if "enter" in t and "location" in t or "select a location" in t:
            if step == 0:
                return _click_xpath(_loc_xpath)
            # step >= 1: fall through to LLM to type and submit
            return None

    # Create label (automail 8005)
    if port == 8005 and "create" in t and "label" in t:
        if step == 0:
            return _click_xpath("//*[contains(@id, 'label-trigger') or contains(@id, 'tag-trigger')]")
        elif step == 1:
            m2 = re.search(r"(?:equal to |equals? |CONTAINS )['\"]([^'\"]+)['\"]", prompt)
            label_text = m2.group(1) if m2 else "label"
            return [{"type": "TypeAction", "text": label_text,
                     "selector": {"type": "xpathSelector",
                                  "value": "//input[contains(@id, 'label-trigger') or contains(@id, 'tag-trigger')]"}}]
        elif step == 2:
            return _click_xpath("//button[contains(@id, 'add-label-btn') or contains(@id, 'add-label-button')]")
        # step >= 3: fall through to LLM
        return None

    if port == 8005 and re.search(r"next\s+page\s+of\s+emails|move\s+forward.*emails", t):
        return _click_xpath(
            "//*[contains(@id,'next-page') or contains(@aria-label,'Next') or contains(., 'Next')]"
        )

    # ADD_TO_CART_MODAL_OPEN (autodelivery 8006): type restaurant name into food search first
    if port == 8006 and re.search(r"add-to-cart modal|add\s+to\s+cart\s+modal", t):
        m_rest = re.search(r"restaurant\s+equals\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if m_rest and step == 0:
            return [
                {
                    "type": "TypeAction",
                    "text": m_rest.group(1).strip(),
                    "selector": _sel_attr("id", "find-food"),
                }
            ]
        if step == 1:
            return _click_xpath("//*[contains(@id,'restaurant-card') or contains(@id,'restaurant-item')][1]")
        return None

    # Reserve hotel (autolodge 8007): type destination into main search first
    if port == 8007 and re.search(r"reserve\s+the\s+hotel", t):
        m_loc = re.search(r"location\s+equals\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if m_loc and step == 0:
            return [
                {
                    "type": "TypeAction",
                    "text": m_loc.group(1).strip(),
                    "selector": _sel_attr("id", "submit-query"),
                }
            ]
        if step == 1:
            return _click_xpath("//*[contains(@class,'property-card-link') or contains(@id,'property-card-link')][1]")
        return None

    # Search delivery restaurant (autodelivery 8006)
    if port == 8006 and "search" in t and "restaurant" in t:
        m2 = re.search(r"(?:exactly |query is |query equals? )['\"]([^'\"]+)['\"]", prompt)
        if m2 and step == 0:
            return [{"type": "TypeAction", "text": m2.group(1), "selector": _sel_attr("id", "find-food")}]
        # step >= 1 or no query match: fall through to LLM
        return None

    return None


# ---------------------------------------------------------------------------
# Search shortcut: direct type into known search input
# ---------------------------------------------------------------------------

def try_search_shortcut(prompt: str, website: str | None) -> list[dict] | None:
    if not website:
        return None
    input_id = SEARCH_INPUT_IDS.get(website)
    if input_id is None:
        return None
    query = extract_search_query(prompt)
    if not query:
        return None
    q = query.strip()
    if q.lower() in ("none", "null", "undefined", "n/a"):
        return None
    return [{"type": "TypeAction", "text": query, "selector": _sel_attr("id", input_id)}]


# ---------------------------------------------------------------------------
# Form-based shortcuts
# ---------------------------------------------------------------------------

def is_already_logged_in(soup: BeautifulSoup) -> bool:
    indicators = ["logout", "log out", "sign out", "my profile", "my account", "dashboard"]
    text = soup.get_text(separator=" ").lower()
    return any(ind in text for ind in indicators)


def detect_login_fields(candidates: list[Candidate]) -> list[dict] | None:
    username = password = submit = None

    for c in candidates:
        # Username field
        if username is None and c.tag == "input":
            if c.name in {"username", "user", "email", "login"}:
                username = c
            elif c.input_type in {"email", "text"} and c.placeholder and (
                "user" in c.placeholder.lower() or "email" in c.placeholder.lower()
            ):
                username = c

        # Password field
        if password is None and c.input_type == "password":
            password = c

        # Submit button
        if submit is None and c.tag in {"button", "input"}:
            if c.input_type == "submit":
                submit = c
            elif c.text and any(
                kw in c.text.lower()
                for kw in ("log in", "login", "sign in", "submit", "enter", "continue")
            ):
                submit = c

    if username and password and submit:
        return [
            {"type": "TypeAction", "text": "<username>", "selector": username.selector.model_dump()},
            {"type": "TypeAction", "text": "<password>", "selector": password.selector.model_dump()},
            {"type": "ClickAction", "selector": submit.selector.model_dump()},
        ]
    return None


def detect_logout_target(candidates: list[Candidate]) -> list[dict] | None:
    for c in candidates:
        if c.text and any(kw in c.text.lower() for kw in ("log out", "logout", "sign out")):
            return [{"type": "ClickAction", "selector": c.selector.model_dump()}]
    # Try href-based
    for c in candidates:
        if c.href and any(kw in c.href.lower() for kw in ("logout", "signout", "sign-out")):
            return [{"type": "ClickAction", "selector": c.selector.model_dump()}]
    return None


def get_registration_actions(candidates: list[Candidate]) -> list[dict] | None:
    username = email = password = confirm = submit = None
    password_seen = False

    for c in candidates:
        if username is None and c.tag == "input":
            if c.name in {"username", "user"} or (c.placeholder and "username" in c.placeholder.lower()):
                username = c

        if email is None and c.tag == "input":
            if c.input_type == "email" or c.name == "email" or (
                c.placeholder and "email" in c.placeholder.lower()
            ):
                email = c

        if c.input_type == "password" or (c.name and "password" in c.name.lower()):
            if not password_seen:
                password = c
                password_seen = True
            elif confirm is None:
                confirm = c

        if submit is None and c.tag in {"button", "input"}:
            if c.input_type == "submit":
                submit = c
            elif c.text and any(
                kw in c.text.lower()
                for kw in ("register", "sign up", "signup", "create", "submit")
            ):
                submit = c

    if not password or not submit:
        return None
    if not username and not email:
        return None

    actions: list[dict] = []
    if username:
        actions.append({"type": "TypeAction", "text": "<signup_username>", "selector": username.selector.model_dump()})
    if email:
        actions.append({"type": "TypeAction", "text": "<signup_email>", "selector": email.selector.model_dump()})
    actions.append({"type": "TypeAction", "text": "<signup_password>", "selector": password.selector.model_dump()})
    if confirm:
        actions.append({"type": "TypeAction", "text": "<signup_password>", "selector": confirm.selector.model_dump()})
    actions.append({"type": "ClickAction", "selector": submit.selector.model_dump()})
    return actions


def get_contact_actions(candidates: list[Candidate]) -> list[dict] | None:
    name_c = email_c = message_c = submit_c = None

    for c in candidates:
        if name_c is None and c.tag == "input":
            if c.name in {"name", "full_name", "fullname", "your_name"} or (
                c.placeholder and "name" in c.placeholder.lower()
            ):
                name_c = c

        if email_c is None and c.tag == "input":
            if c.name == "email" or c.input_type == "email" or (
                c.placeholder and "email" in c.placeholder.lower()
            ):
                email_c = c

        if message_c is None:
            if c.tag == "textarea":
                message_c = c
            elif c.name in {"message", "msg", "content", "body", "subject"}:
                message_c = c

        if submit_c is None and c.tag in {"button", "input"}:
            if c.input_type == "submit":
                submit_c = c
            elif c.text and any(kw in c.text.lower() for kw in ("send", "submit", "contact")):
                submit_c = c

    if not submit_c:
        return None
    # At minimum need message OR (name + email)
    if not message_c and (not name_c or not email_c):
        return None

    actions: list[dict] = []
    if name_c:
        actions.append({"type": "TypeAction", "text": "Test User", "selector": name_c.selector.model_dump()})
    if email_c:
        actions.append({"type": "TypeAction", "text": "<signup_email>", "selector": email_c.selector.model_dump()})
    if message_c:
        actions.append({"type": "TypeAction", "text": "Hello, this is a test message for support.", "selector": message_c.selector.model_dump()})
    actions.append({"type": "ClickAction", "selector": submit_c.selector.model_dump()})
    return actions


def try_shortcut(
    task_type: str | None,
    candidates: list[Candidate],
    soup: BeautifulSoup,
    step_index: int,
) -> list[dict] | None:
    """Attempt deterministic shortcut for the given task type."""
    if task_type is None:
        return None

    if task_type == "login":
        if is_already_logged_in(soup):
            return [{"type": "WaitAction", "time_seconds": 1}]
        return detect_login_fields(candidates)

    if task_type == "logout":
        result = detect_logout_target(candidates)
        if result:
            return result
        # May need to login first, then logout
        if not is_already_logged_in(soup):
            login = detect_login_fields(candidates)
            if login:
                return login
        return None

    if task_type == "registration":
        return get_registration_actions(candidates)

    if task_type == "contact":
        return get_contact_actions(candidates)

    return None
