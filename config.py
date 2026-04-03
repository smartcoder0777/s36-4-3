"""Central configuration: site knowledge, playbooks, constants."""
from __future__ import annotations
from urllib.parse import urlsplit

# ---------------------------------------------------------------------------
# Port → project mapping (IWA sandbox)
# ---------------------------------------------------------------------------
PORT_TO_PROJECT: dict[int, str] = {
    8000: "autocinema",
    8001: "autobooks",
    8002: "autozone",
    8003: "autodining",
    8004: "autocrm",
    8005: "automail",
    8006: "autodelivery",
    8007: "autolodge",
    8008: "autoconnect",
    8009: "autowork",
    8010: "autocalendar",
    8011: "autolist",
    8012: "autodrive",
    8013: "autohealth",
    8014: "autostats",
    8015: "autodiscord",
}


def detect_website(url: str) -> str | None:
    port = urlsplit(url).port
    return PORT_TO_PROJECT.get(port) if port else None


# ---------------------------------------------------------------------------
# Selector priority (stable → fragile)
# ---------------------------------------------------------------------------
SELECTOR_PRIORITY: list[str] = [
    "id", "data-testid", "href", "aria-label", "name",
    "placeholder", "title", "text",
]

# ---------------------------------------------------------------------------
# LLM defaults
# ---------------------------------------------------------------------------
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 350
PAGE_IR_MAX_TOKENS = 1400
PAGE_IR_CHAR_LIMIT = PAGE_IR_MAX_TOKENS * 4

# ---------------------------------------------------------------------------
# Agent limits
# ---------------------------------------------------------------------------
AGENT_MAX_STEPS = 12
MAX_TASK_STATES = 8

# Event/use-case aliases seen in evals that should map to existing strategies.
EVENT_TASK_ALIASES: dict[str, str] = {
    "SEARCH_PRODUCT": "SEARCH_ITEM",
    "SEARCH": "SEARCH_RIDE",
    "ADD_TO_WISHLIST": "ADD_TO_WISHLIST_HOTEL",
    "UNHIDE_POST": "VIEW_HIDDEN_POSTS",
    "REMOVE_FROM_CART_BOOK": "REMOVE_FROM_CART",
    "BROWSE_FAVORITE_EXPERT": "NAVBAR_EXPERTS_CLICK",
    "VIEW_SUBNET": "FAVORITE_SUBNET",
}

# ---------------------------------------------------------------------------
# Per-website hints (detailed UI structure per site)
# ---------------------------------------------------------------------------
WEBSITE_HINTS: dict[str, str] = {
    "autocinema": (
        "SITE: Movie/film database. NAV: Films list, Login/Register, Admin panel (when logged in). "
        "Film cards show title, year, genre, director, duration. "
        "Click film -> detail page with Watch Trailer button, Add to Watchlist button, Share button, Comments section. "
        "Admin: Add Film, Edit Film, Delete Film (requires login with 'user '/'Passw0rd!'). "
        "Registration: username='newuser ', email='newuser @gmail.com', password='Passw0rd!'."
    ),
    "autobooks": (
        "SITE: Book store. NAV: Books, Cart icon, Login/Register. "
        "Books have title, author, genres, year, page_count, rating, price. "
        "Login/Register with placeholder credentials (' '/' '). "
        "Book detail: Add to Cart, Add to Wishlist, Open Preview buttons. "
        "READING LIST: On book detail, use Add to Reading List / bookmark—after login if required. "
        "Admin: Add Book, Edit Book, Delete Book. Cart icon top-right."
    ),
    "autozone": (
        "SITE: E-commerce store. NAV: Products grid, Category sidebar/filter, Cart icon, Wishlist. "
        "Products have name, brand, price, description, rating. "
        "Category filter on left sidebar (click to filter by category). "
        "Product card: Add to Cart, Add to Wishlist, Share buttons. "
        "Cart page: shows items, total, Proceed to Checkout button. "
        "Carousel sections: scroll left/right buttons on carousel cards."
    ),
    "autodining": (
        "SITE: Restaurant reservation/booking. NAV: Restaurants, About, Help/FAQ, Contact. "
        "Main page: search bar, country selector dropdown, date/time pickers, people/guest count. "
        "Guest dropdown: click on people/guest count to open dropdown and select number. "
        "Restaurant cards: click to view details. "
        "Help/FAQ page: expandable FAQ items. "
        "About page: feature cards (Trusted reviews, etc.). "
        "Contact form: name, email, message, subject fields."
    ),
    "autocrm": (
        "SITE: Legal case management + calendar. NAV: Dashboard, Matters, Clients, Calendar. "
        "MATTERS: Table rows show name, client, status, updated (e.g. '4d ago'). Click a row OR use row action "
        "(Revise Matter, Amend Project, aria-label edit) to open the matter editor. "
        "UPDATE MATTER: find the single row matching ALL constraints (name contains, client not_equals, updated, status), "
        "open it, change Status dropdown to the required value (e.g. Archived), click Save/Submit—UPDATE_MATTER must fire. "
        "Matters list: sortable columns. Add New Matter button. "
        "Clients list: rows show name, email, status, matters, last activity; click a row to open client detail. "
        "DELETE CLIENT: open Clients, find the row matching ALL TASK_CONSTRAINTS (not_contains/not_equals on name/email/etc.), "
        "open that client, then click Delete client (id often delete-client-button) and confirm—DELETE_CLIENT event must fire. "
        "Calendar: Add event button, date/time/label/event_type fields. "
        "Settings: Change user name option. "
        "Sort by column: click column header or sort button."
    ),
    "automail": (
        "SITE: Webmail client. NAV: Inbox, Drafts, Sent, Spam, Templates folder tabs. "
        "Email list: shows from_email, subject, date, is_starred, is_important flags. "
        "Actions per email: Star, Archive, Mark as Spam, Delete, Forward, Reply. "
        "Select email: checkbox. Select all: top checkbox. Clear selection: deselect all. "
        "Important: click flag/important icon. "
        "Templates tab: list of templates with template_name, subject, to fields. "
        "Template actions: Select (use it), Send, Save as Draft. "
        "Pagination: Next/Previous page arrows at bottom of email list."
    ),
    "autodelivery": (
        "SITE: Food delivery app. NAV: Restaurants list, Cart, Orders. "
        "Food search: type restaurant name, then open restaurant → menu. "
        "ADD-TO-CART MODAL: pick menu item meeting price/item constraints; click to open modal (not full checkout). "
        "Restaurant cards: name, cuisine, rating, description. Click to view restaurant detail. "
        "Restaurant detail: menu items with size, price, quantity selector. Add to cart. "
        "Cart page: shows items with preferences (dietary), size, quantity, price, restaurant name. "
        "Cart: Dropoff preference selector (Hand it to me / Leave at door / Text when arriving). "
        "Delivery priority: Normal/Priority/Scheduled option. "
        "Checkout: proceed to checkout button. "
        "Pagination: next/previous page for restaurant list. "
        "View all restaurants: click All Restaurants or similar nav link."
    ),
    "autolodge": (
        "SITE: Hotel/lodging booking (Airbnb-style). Shows listing cards. "
        "Listing card/detail: title, host_name, location, price/night, rating, reviews count, amenities list, guests. "
        "Guest selector: +/- buttons or dropdown to set number of guests. "
        "BOOKING FLOW: Search -> pick listing (avoid hotel_id/title excluded by constraints) -> "
        "click 'Book Now'/'Reserve' (id=book-button or similar) -> payment form opens -> "
        "select payment method radio (name=payment-method) -> click Confirm/Book/Submit. "
        "IMPORTANT: The booking event only fires after the final Submit/Confirm—not after radio select alone. "
        "WARNING: Do NOT click brand-link (id=brand-link) or nav_home_link—these navigate to homepage and lose your progress. "
        "Do NOT click travelers-count before booking. "
        "Payment methods: cash_on_arrival, credit_card, bank_transfer. "
        "Search bar id=submit-query. property-card-link opens listing detail. "
        "Filters bar below search: rating-filter and region-filter dropdowns, then Apply—this fires APPLY_FILTERS. "
        "Set region and rating per TASK, then click Apply (not only Search). "
        "Review form: rating stars + text area."
    ),
    "autoconnect": (
        "SITE: Professional network (LinkedIn-style). NAV: Feed, Jobs, People, Company Pages. "
        "Feed: posts with text, author, Like/Comment buttons. Comment: text field + submit. "
        "APPLY FOR JOB: Open **Jobs** tab, use search/filter so listing matches **job_title** AND **location** from constraints, "
        "click the job to open detail, then click **Apply**—required for APPLY_FOR_JOB event. "
        "Jobs section: job listings with title, company, location, Apply button. "
        "My Applications: list with status (Pending/Accepted/Rejected), Withdraw/Cancel button. "
        "Company Pages: Follow/Unfollow button on each page. "
        "People/Users: search bar for users. "
        "Profile: Edit profile (bio, skills, photo). "
        "Back to Jobs: breadcrumb or Back button from job detail."
    ),
    "autowork": (
        "SITE: Freelancer hiring platform. NAV: Jobs, Hires, Experts/Browse. "
        "WRITE JOB TITLE: Click **Post a Job** first; in the modal, type a **job title** whose text **contains** the "
        "required substring from constraints (e.g. 'gineers' inside 'Engineers')—WRITE_JOB_TITLE fires from that field. "
        "Expert/Consultant cards: name, role, country, rating, price. "
        "Expert actions: Hire Now button, Hire Later button, View Profile. "
        "Hire Later page: list of saved experts with Remove button. "
        "Job Posting: Post a Job / + button -> form with title, description, rate_from, rate_to, project size. "
        "Job posting form: title field, description, rate range, project size (Small/Medium/Large). "
        "Close job posting window: X/Cancel button on job posting modal. "
        "Search skills: search bar for skills. "
        "NAV: Jobs link, Hires link in navbar. "
        "Hiring Team: section showing team members."
    ),
    "autocalendar": (
        "SITE: Calendar app (Google Calendar-style). "
        "View buttons: Day, 5-day (work week), Week, Month -- click to switch view. "
        "Left sidebar: + button with aria-label 'Add new calendar' opens ADD_NEW_CALENDAR modal (not the same as Create new event). "
        "Add New Calendar modal: name + description fields. "
        "Events: click on time slot or + button to add event. "
        "Event form: title, date, time, visibility (Public/Private/Default), reminders (minutes), "
        "meeting_link, attendees (email), all_day toggle, recurrence, calendar, description, busy. "
        "Event actions: Edit, Delete. "
        "Attendees: add attendee email field in event edit form."
    ),
    "autolist": (
        "SITE: Task management (Trello/Monday-style). "
        "Tasks list: each task has name, description, date, priority (1=High/2=Medium/3=Low), status. "
        "Add Task button: + or 'Add Task' button to create new task. "
        "Task actions: Edit (pencil icon) -> modal, Delete (trash icon) -> confirm. "
        "Edit task modal: name, description, date, priority fields. "
        "Team tab/section: list of team members with name, role. "
        "Add member: search by name and add. "
        "Assign role: dropdown next to member name."
    ),
    "autodrive": (
        "SITE: Ride-sharing app (Uber-style). "
        "Main page: Location (pickup) input + Destination input fields. "
        "You must TYPE addresses into those fields and select a matching suggestion—clicking the field alone is not enough. "
        "Available rides: list with ride_name, price, estimated time, scheduled. "
        "Reserve button on each ride card. "
        "Date picker: select trip date (calendar widget). "
        "Time picker: select trip time; if constraints say time after/before a clock value, open the picker and choose a valid slot. "
        "Search location: type in the search/destination input box. "
        "Reservation history: list of upcoming/past rides with Cancel button. "
        "Cancel: click Cancel on a specific reservation. "
        "Next pickup: shows scheduled pickup details."
    ),
    "autohealth": (
        "SITE: Medical/healthcare platform. NAV: Doctors, Appointments, Medical Records/Analysis. "
        "Doctor cards: doctor_name, speciality, rating, consultation_fee, language. "
        "Doctor card actions: View Profile, Book Appointment, Contact Doctor. "
        "Doctor profile detail: full info, education section. "
        "Appointment form: doctor_name, speciality, date, time fields. "
        "Quick appointment form: speciality, patient_name, patient_email. "
        "Medical Records/Analysis: searchable list with record_title, doctor_name, record_type, date. "
        "Search: filter fields for doctor_name, speciality, record_title, etc. "
        "Contact doctor form: opens when Contact button clicked on doctor card."
    ),
    "autostats": (
        "Bittensor/marketing-style site: hero, charts, and many links to /subnets and ecosystem pages. "
        "Do not repeatedly click the same subnet nav link unless the TASK explicitly asks about subnets. "
        "Prefer: search bars, task-specific buttons, forms, and flows named in the TASK prompt. "
        "Charts, data tables, filter controls, export options, date range selectors."
    ),
    "autodiscord": (
        "Chat application. Server list, channels, messages, user search, "
        "server management. Channel messages in main panel."
    ),
}

# ---------------------------------------------------------------------------
# Task playbooks (130+ step-by-step guides per task type)
# ---------------------------------------------------------------------------
TASK_PLAYBOOKS: dict[str, str] = {
    "REGISTRATION": "PLAYBOOK: 1) Navigate to register/signup page. 2) Type signup_username into username field. 3) Type signup_email into email field. 4) Type signup_password into password field. 5) Click submit/register button. Use EXACT credential values.",
    "LOGIN": "PLAYBOOK: 1) Navigate to login page. 2) Type username into username/email field EXACTLY as given. 3) Type password into password field EXACTLY as given. 4) Click login/sign-in submit button.",
    "LOGIN_THEN_LOGOUT": "PLAYBOOK: 1) Navigate to login page. 2) Type username exactly. 3) Type password exactly. 4) Click login submit. 5) After login, find logout/sign-out button (often in nav/profile menu). 6) Click logout.",
    "LOGIN_THEN_LIST_ACTION": "PLAYBOOK: 1) **Login first**: open Login, type TASK_CREDENTIALS username/password exactly, submit. 2) **Books reading list**: browse or search for the book matching constraints (title/author/genre). 3) Open that book’s **detail** page. 4) Click **Add to reading list** / bookmark (not generic wishlist on another site).",
    "LOGIN_THEN_COMMENT": "PLAYBOOK: 1) Login (navigate to login, fill credentials, submit). 2) Find and navigate to the specific item. 3) Find the comment/review form on the detail page. 4) Type the comment text. 5) Submit.",
    "LOGIN_THEN_ADD_ITEM": "PLAYBOOK: 1) Login (navigate to login, fill credentials, submit). 2) Navigate to admin or add-item page (look for Admin/Add Film/Add Book in nav). 3) Fill ALL fields with EXACT values from task. 4) Submit.",
    "LOGIN_THEN_EDIT_ITEM": "PLAYBOOK: 1) Login. 2) Navigate to item list page (admin or main list). 3) Find the specific item matching the search/filter criteria. 4) Click Edit. 5) Update the specified fields EXACTLY. 6) Submit.",
    "LOGIN_THEN_DELETE_ITEM": "PLAYBOOK: 1) Login. 2) Navigate to item list. 3) Find the specific item. 4) Click Delete. 5) Confirm deletion if prompted.",
    "LOGIN_THEN_EDIT_PROFILE": "PLAYBOOK: 1) Login. 2) Navigate to profile/account/settings page. 3) Update the specified fields EXACTLY. 4) Save.",
    "LOGIN_THEN_PURCHASE": "PLAYBOOK: 1) Login. 2) Find the item and add to cart. 3) Navigate to cart/checkout. 4) Complete checkout form. 5) Submit order.",
    "SEARCH_ITEM": "PLAYBOOK: 1) Find the search bar on the page. 2) Type the search query EXACTLY as given in the task. 3) Submit search (press Enter or click search button). Do NOT modify the search query.",
    "FILTER_ITEM": "PLAYBOOK: 1) Find filter controls on the page. 2) Select/type the filter criteria EXACTLY as specified. 3) Apply the filter.",
    "NAVIGATE_DETAIL": "PLAYBOOK: 1) Browse or search for items. 2) Use list_cards or list_links tool to find item matching ALL criteria. 3) Click/navigate to that item's detail page. If you need to filter by criteria, use search or filter controls first.",
    "SHARE_ITEM": "PLAYBOOK: 1) Navigate to the specific item detail page. 2) Find the Share button/icon. 3) Click it.",
    "WATCH_TRAILER": "PLAYBOOK: 1) Navigate to the specific film/movie detail page. 2) Find the Watch Trailer or play button. 3) Click it.",
    "FILM_DETAIL": "PLAYBOOK: 1) On AutoCinema, browse the movie list. 2) Find a movie matching ALL TASK_CONSTRAINTS. 3) Click on that movie to open its detail page.",
    "SEARCH_FILM": "PLAYBOOK: 1) On AutoCinema, find the search bar. 2) Type a movie title that is NOT the excluded term. 3) Submit the search.",
    "OPEN_PREVIEW": "PLAYBOOK: 1) Navigate to the specific book detail page. 2) Find the Open Preview button. 3) Click it.",
    "ADD_BOOK": "PLAYBOOK: 1) On AutoBooks, login first if credentials provided. 2) Click Add Book button/link to open form. 3) Fill required fields including genres. 4) Submit Save/Create.",
    "ADD_COMMENT_BOOK": "PLAYBOOK: 1) On AutoBooks, find the book whose name CONTAINS the specified title. 2) Open that book's detail page. 3) Find the comments section. 4) Fill in commenter name and message. 5) Submit the comment.",
    "ADD_TO_CART": "PLAYBOOK: 1) Find and navigate to the specific book/item. 2) Click Add to Cart button.",
    "REMOVE_FROM_CART": "PLAYBOOK: 1) Navigate to the cart page. 2) Find the specific item in cart. 3) Click Remove/Delete.",
    "VIEW_CART": "PLAYBOOK: 1) Click the **Cart** / **shopping cart** icon in the top nav (or go to /cart). 2) Wait until the cart page loads.",
    "PURCHASE": "PLAYBOOK: 1) Add the item to cart. 2) Navigate to cart. 3) Click checkout/purchase button. 4) Fill out purchase form. 5) Submit.",
    "CONTACT": "PLAYBOOK: 1) Navigate to the Contact page. 2) Fill in name, email, message fields with EXACT values. 3) Submit the form.",
    "REGISTER": "PLAYBOOK: 1) Open Sign up/Register page. 2) Fill username/email/password from TASK_CONSTRAINTS or TASK_CREDENTIALS. 3) For source/not_equals rules, choose a valid option different from excluded values (and avoid 'None' unless explicitly required). 4) Submit registration.",
    "ADD_COMMENT": "PLAYBOOK: 1) Navigate to the specific item detail page. 2) Find the comment/review form. 3) Type the comment EXACTLY as specified. 4) Submit.",
    "LIST_ACTION": "PLAYBOOK: 1) Navigate to the item detail page. 2) Find the watchlist/reading-list button. 3) Click add or remove.",
    "SEARCH_LOCATION": "PLAYBOOK: 1) Find the search/destination input field. 2) Click to focus. 3) Type the destination EXACTLY as given (required for backend events). 4) Click the matching autocomplete result. 5) Submit/confirm if needed.",
    "RESERVE_RIDE": "PLAYBOOK: 1) Fill pickup and destination with typed addresses (and time/date if shown) so constraints hold. 2) Browse available rides (list_cards if needed). 3) Find the ride matching ALL TASK_CONSTRAINTS. 4) Click Reserve on the matching ride.",
    "CANCEL_RESERVATION": "PLAYBOOK: 1) Navigate to reservations/upcoming rides page. 2) Find the reservation matching ALL TASK_CONSTRAINTS. 3) Click Cancel. 4) Confirm if prompted.",
    "SELECT_DATE": "PLAYBOOK: 1) Find the date picker/calendar widget. 2) Click it to open. 3) Select a date satisfying TASK_CONSTRAINTS. 4) Confirm the selection.",
    "SELECT_TIME": "PLAYBOOK: 1) Find the time picker/dropdown. 2) Click to open. 3) Select a clock time that satisfies TASK_CONSTRAINTS (e.g. strictly after 17:00 for greater_than). 4) Confirm. Do not assume the default time is valid.",
    "NEXT_PICKUP": "PLAYBOOK: 1) Open **Trips**, **Upcoming**, or the **Next pickup** / scheduled ride card on the home or rides page. 2) Click that card or **View details** so the pickup detail opens. 3) If date/time pickers are shown, set **date** and **time** to EXACTLY match TASK_CONSTRAINTS (e.g. 2026-04-03 and 15:00:00). 4) Confirm/Save if a button is required so NEXT_PICKUP fires.",
    "STAR_AN_EMAIL": "PLAYBOOK: 1) Browse the inbox email list. 2) Find the email matching ALL constraints. 3) Click the Star icon on that email row.",
    "ARCHIVE_EMAIL": "PLAYBOOK: 1) Browse the inbox. 2) Find email matching constraints. 3) Click on that email. 4) Find Archive button. Click it.",
    "DELETE_EMAIL": "PLAYBOOK: 1) Find the email matching constraints. 2) Click the Delete/Trash icon on that email row.",
    "ADD_LABEL": "PLAYBOOK: 1) Find the email matching ALL TASK_CONSTRAINTS. 2) Open that email or select it. 3) Find the Label option. 4) Select a label that is NOT the excluded label_name.",
    "FORWARD_EMAIL": "PLAYBOOK: 1) Find the email matching constraints. 2) Click to open. 3) Click Forward button. 4) Fill in To field if needed. 5) Send.",
    "MARK_EMAIL_AS_IMPORTANT": "PLAYBOOK: 1) Find the email matching constraints. 2) Click the Important/Flag icon on that email.",
    "EDIT_DRAFT_EMAIL": "PLAYBOOK: 1) Navigate to Drafts folder. 2) Find draft matching constraints. 3) Click to open/edit the draft.",
    "EMAILS_NEXT_PAGE": "PLAYBOOK: 1) Look at the bottom of the email list for pagination. 2) Click the Next arrow/button.",
    "EMAILS_PREV_PAGE": "PLAYBOOK: 1) Look for Previous arrow at bottom of email list. 2) Click it.",
    "CLEAR_SELECTION": "PLAYBOOK: 1) Look for a Clear Selection button or uncheck Select All checkbox. 2) Click it.",
    "TEMPLATE_SENT": "PLAYBOOK: 1) Navigate to Templates section. 2) Find template matching constraints. 3) Click Send or Use Template.",
    "TEMPLATE_SAVED_DRAFT": "PLAYBOOK: 1) Navigate to Templates section. 2) Find template matching constraints. 3) Click Save as Draft.",
    "TEMPLATE_SELECTED": "PLAYBOOK: 1) Navigate to Templates section. 2) Find the template matching constraints. 3) Click Select or Use.",
    "SELECT_WEEK": "PLAYBOOK: 1) Find the view switcher buttons. 2) Click Week button.",
    "SELECT_MONTH": "PLAYBOOK: 1) Find view buttons. 2) Click Month button.",
    "SELECT_DAY": "PLAYBOOK: 1) Find view buttons. 2) Click Day button.",
    "SELECT_FIVE_DAYS": "PLAYBOOK: 1) Find view buttons. 2) Click 5-day or Work Week button.",
    "ADD_NEW_CALENDAR": "PLAYBOOK: 1) In the left sidebar, click the + button labeled 'Add new calendar' (opens modal—do NOT use 'Create new event' in the nav). 2) The ADD_NEW_CALENDAR event fires when the modal opens.",
    "CREATE_CALENDAR": "PLAYBOOK: 1) Click the + button next to Other calendars. 2) Fill in name and description satisfying constraints. 3) Click Create/Save.",
    "EVENT_ADD_ATTENDEE": "PLAYBOOK: 1) Find an event on the calendar. 2) Click on it to open. 3) Click Edit. 4) Find Add Attendee field. 5) Type email satisfying constraints. 6) Save.",
    "DELETE_ADDED_EVENT": "PLAYBOOK: 1) Browse calendar events. 2) Find the event matching ALL constraints. 3) Click on it. 4) Click Delete. 5) Confirm.",
    "CANCEL_ADD_EVENT": "PLAYBOOK: 1) Switch to Month/Week if needed. 2) Find the ONE event matching ALL constraints (title, description, attendees, visibility, date). 3) Open it → **Cancel** / **Delete event** / discard. 4) Confirm. Skip unrelated events.",
    "NEW_CALENDAR_EVENT_ADDED": "PLAYBOOK: 1) Click the + or Add Event button. 2) Fill in the event form satisfying ALL constraints. 3) Save the event.",
    "ADD_EVENT": "PLAYBOOK: 1) Click + or on a time slot. 2) Fill ALL fields from TASK_CONSTRAINTS. 3) Save.",
    "VIEW_PENDING_EVENTS": "PLAYBOOK: 1) Switch to a view showing upcoming events. 2) Find events matching constraint. 3) Navigate to or click on that event.",
    "AUTOLIST_TEAM_MEMBERS_ADDED": "PLAYBOOK: 1) Navigate to Team section. 2) Click Add Member. 3) Search for a member satisfying constraints. 4) Add them.",
    "AUTOLIST_TEAM_ROLE_ASSIGNED": "PLAYBOOK: 1) Go to Team section. 2) Find a member satisfying constraints. 3) Click their role dropdown. 4) Select the required role.",
    "AUTOLIST_EDIT_TASK_MODAL_OPENED": "PLAYBOOK: 1) Browse task list. 2) Find task matching ALL constraints. 3) Click the Edit/Pencil icon to open the edit modal.",
    "AUTOLIST_ADD_TASK_CLICKED": "PLAYBOOK: 1) Find the Add Task button. 2) Click it.",
    "AUTOLIST_TASK_ADDED": "PLAYBOOK: 1) Click the Add Task button to open form. 2) Fill fields satisfying ALL TASK_CONSTRAINTS. 3) Click Save/Submit.",
    "AUTOLIST_DELETE_TASK": "PLAYBOOK: 1) Navigate to Tasks section. 2) Find the task matching ALL TASK_CONSTRAINTS. 3) Click Delete button. 4) Confirm deletion.",
    "CONFIRM_AND_PAY": "PLAYBOOK: 1) Browse listings. Find matching ALL TASK_CONSTRAINTS. 2) Click Book Now. 3) Fill payment form with EXACT values. 4) Submit.",
    "VIEW_DOCTOR_PROFILE": "PLAYBOOK: 1) Browse doctor list. 2) Find doctor matching ALL constraints. 3) Click to view profile.",
    "SEARCH_DOCTORS": "PLAYBOOK: 1) Find search/filter fields for doctors. 2) Enter search criteria matching constraints. 3) Submit search.",
    "SEARCH_MEDICAL_ANALYSIS": "PLAYBOOK: 1) Navigate to Medical Records/Analysis. 2) Use search/filter fields. 3) Submit/search.",
    "VIEW_MEDICAL_ANALYSIS": "PLAYBOOK: 1) Navigate to Medical Records. 2) Find the record matching constraints. 3) Click to view details.",
    "OPEN_APPOINTMENT_FORM": "PLAYBOOK: 1) Browse doctor cards or search — avoid homepage carousel. 2) Find doctor/speciality matching ALL constraints (not_equals means pick a different option). 3) Click Book Appointment. 4) Fill date, time, patient fields per constraints. 5) Submit.",
    "OPEN_CONTACT_DOCTOR_FORM": "PLAYBOOK: 1) Find doctor matching ALL constraints. 2) Click Contact Doctor button.",
    "CONTACT_DOCTOR": "PLAYBOOK: 1) Find doctor matching constraints. 2) Click Contact. 3) Fill the contact form. 4) Submit.",
    "SEARCH_APPOINTMENT": "PLAYBOOK: 1) Go to Appointments section. 2) Search/filter for matching appointments. 3) View results.",
    "REQUEST_QUICK_APPOINTMENT": "PLAYBOOK: 1) Find Quick Appointment (or Book Appointment) — not carousel arrows. 2) Fill patient name, email, speciality/doctor fields so not_equals/not_contains constraints hold (e.g. pick speciality != excluded value). 3) Submit/confirm so the appointment event fires.",
    "VIEW_DOCTOR_EDUCATION": "PLAYBOOK: 1) Browse doctors list. 2) Find doctor matching ALL constraints. 3) Click on doctor's card. 4) Find Education tab/section. 5) Click it.",
    "COMMENT_ON_POST": "PLAYBOOK: 1) Find a post in the feed. 2) Click the Comment button. 3) Type the EXACT comment text. 4) Submit.",
    "FOLLOW_PAGE": "PLAYBOOK: 1) Go to **Companies** or search. 2) Open the company page whose recommendation/snippet **contains** the required substring (TASK_CONSTRAINTS). 3) Click **Follow** on that page.",
    "UNFOLLOW_PAGE": "PLAYBOOK: 1) Find the company page. 2) Click Unfollow.",
    "CANCEL_APPLICATION": "PLAYBOOK: 1) Navigate to My Applications or Jobs. 2) Find the application matching constraints. 3) Click Withdraw/Cancel.",
    "SEARCH_USERS": "PLAYBOOK: 1) Find the user search bar. 2) Type the query. 3) Submit.",
    "VIEW_USER_PROFILE": "PLAYBOOK: 1) Search/browse users. 2) Find user matching constraints. 3) Click user name/card/avatar to open profile details.",
    "BACK_TO_ALL_JOBS": "PLAYBOOK: 1) Navigate to Jobs section. 2) Find a job satisfying constraints. 3) Click on it. 4) Find and click Back to all jobs link.",
    "EDIT_PROFILE_BIO": "PLAYBOOK: 1) Navigate to Profile/Settings. 2) Find Bio field. 3) Set bio to EXACT value. 4) Save.",
    "HIRE_BTN_CLICKED": "PLAYBOOK: 1) Browse expert/consultant list. 2) Find expert matching ALL constraints. 3) Click Hire Now.",
    "HIRE_LATER": "PLAYBOOK: 1) Browse expert list. 2) Find expert matching constraints. 3) Click Hire Later.",
    "HIRE_LATER_REMOVED": "PLAYBOOK: 1) Navigate to Hire Later page. 2) Find expert matching constraints. 3) Click Remove.",
    "SELECT_HIRING_TEAM": "PLAYBOOK: 1) Find the Hiring Team section. 2) Find member matching constraints. 3) Click to view.",
    "CHOOSE_PROJECT_SIZE": "PLAYBOOK: 1) Find the project size selector. 2) Choose a size NOT the excluded one.",
    "CLOSE_POST_A_JOB_WINDOW": "PLAYBOOK: 1) Open the job posting form. 2) Fill in rate_from/rate_to. 3) Close the window (X/Cancel).",
    "NAVBAR_JOBS_CLICK": "PLAYBOOK: 1) Find Jobs link in the navbar. 2) Click it.",
    "NAVBAR_HIRES_CLICK": "PLAYBOOK: 1) Find Hires link in the navbar. 2) Click it.",
    "NAVBAR_HIRE_LATER_CLICK": "PLAYBOOK: 1) Find **Hire later** (or Hire Later list) in the navbar or account menu. 2) Click it to open the saved experts page.",
    "SEARCH_SKILL": "PLAYBOOK: 1) Find the skill search bar. 2) Type the query. 3) Submit.",
    "EDIT_PROFILE_LOCATION": "PLAYBOOK: 1) Navigate to Profile/Settings. 2) Find Location field. 3) Enter value satisfying constraints. 4) Save.",
    "EDIT_PROFILE_EMAIL": "PLAYBOOK: 1) Navigate to Profile/Settings/Account. 2) Find Email field. 3) Enter value satisfying constraints. 4) Save.",
    "BOOKING_CONFIRM": "PLAYBOOK: 1) Browse listings. Find matching ALL TASK_CONSTRAINTS. 2) Set guests count. 3) Click Book Now/Reserve. 4) Fill payment form. 5) Submit/Confirm.",
    "RESERVE_HOTEL": "PLAYBOOK: 1) In the main search bar, type **location** from TASK_CREDENTIALS (e.g. city/country). 2) Submit or pick a suggestion so listings load. 3) Find ONE property matching ALL constraints (location, guests, hotel_id/title not_equals/not_contains). 4) Open the **property card** (property-card-link). 5) Set **guests** to the required count if shown. 6) Click **Book Now** / **Reserve**. 7) On the booking form, choose **payment method** per constraints. 8) Click **Confirm/Submit** to finish—step 8 is required for the event.",
    "SEARCH_HOTEL": "PLAYBOOK: 1) Find the hotel search bar. 2) Type a query that helps satisfy constraints. 3) Submit. 4) Pick the matching hotel row/card, not favorite.",
    "PAYMENT_METHOD_SELECTED": "PLAYBOOK: 1) Search for hotels. 2) Select a hotel satisfying ALL constraints (hotel_id, title). 3) Click Book/Reserve on the hotel detail page. 4) On the booking form, select the payment method radio that satisfies constraints (e.g. 'cash_on_arrival'). 5) Click the Confirm/Book/Submit button to finalize—selecting the radio alone does NOT complete the booking.",
    "EDIT_NUMBER_OF_GUESTS": "PLAYBOOK: 1) Find hotel/listing matching constraints. 2) Find the guest count selector. 3) Set it to the required number.",
    "SUBMIT_REVIEW": "PLAYBOOK: 1) Find listing matching constraints. 2) Click Write Review. 3) Set rating. 4) Type review text. 5) Submit.",
    "ADD_TO_WISHLIST_HOTEL": "PLAYBOOK: 1) Find hotel matching constraints. 2) Click Add to Wishlist/heart icon.",
    "APPLY_FILTERS": "PLAYBOOK: 1) Find filter controls (hotels: rating + region dropdowns). 2) Set values to satisfy TASK_CONSTRAINTS (rating, region contains/equals). 3) Click Apply (not Search) to emit APPLY_FILTERS.",
    "PEOPLE_DROPDOWN_OPENED": "PLAYBOOK: 1) Find the people/guest selector. 2) Click to open the dropdown. 3) Select the number satisfying the constraint.",
    "COUNTRY_SELECTED": "PLAYBOOK: 1) Find the country/destination dropdown. 2) Set other filters per constraints. 3) Open dropdown. 4) Select the specified country.",
    "RESTAURANT_NEXT_PAGE": "PLAYBOOK: 1) Look for pagination at bottom. 2) Click the Next button.",
    "RESTAURANT_PREV_PAGE": "PLAYBOOK: 1) Look for pagination. 2) Click Previous button.",
    "SEARCH_DELIVERY_RESTAURANT": "PLAYBOOK: 1) Find the restaurant search bar. 2) Type query satisfying constraints. 3) Submit.",
    "DROPOFF_PREFERENCE": "PLAYBOOK: 1) Find order matching constraints. 2) Find the dropoff preference selector. 3) Select an option satisfying constraints.",
    "DELIVERY_PRIORITY_SELECTED": "PLAYBOOK: 1) Find order matching constraints. 2) Find delivery priority selector. 3) Select a priority satisfying constraints.",
    "VIEW_DELIVERY_RESTAURANT": "PLAYBOOK: 1) Browse restaurant list. 2) Find restaurant matching constraints. 3) Click on it.",
    "VIEW_ALL_RESTAURANTS": "PLAYBOOK: 1) Click All Restaurants or equivalent link/tab.",
    "OPEN_CHECKOUT_PAGE": "PLAYBOOK: 1) Find order matching constraints. 2) Navigate to checkout.",
    "SEARCH_RESTAURANT": "PLAYBOOK: 1) Find the restaurant search bar. 2) Type EXACT query. 3) Submit search.",
    "VIEW_RESTAURANT": "PLAYBOOK: 1) Browse restaurant listing cards. 2) Find restaurant matching ALL constraints. 3) Click on it to open detail page.",
    "TAG_FILTER_SELECTED": "PLAYBOOK: 1) In restaurant list/search page, set search text and tag filter according to constraints. 2) Ensure selected tag/search satisfy contains/not_contains rules. 3) Apply/select filter.",
    "HELP_FAQ_TOGGLED": "PLAYBOOK: 1) Navigate to Help/FAQ page. 2) Find FAQ item NOT containing excluded text. 3) Click to expand.",
    "HELP_VIEWED": "PLAYBOOK: 1) Find Help or FAQ link in navigation. 2) Click it.",
    "OCCASION_SELECTED": "PLAYBOOK: 1) In booking form, open occasion/special-occasion selector. 2) Choose an option that satisfies constraints. 3) Keep booking fields valid (people/date/time) if required.",
    "ABOUT_FEATURE_CLICK": "PLAYBOOK: 1) Navigate to About page. 2) Find the feature card matching text. 3) Click on it.",
    "CONTACT_FORM_SUBMIT": "PLAYBOOK: 1) Navigate to Contact page. 2) Fill form satisfying constraints. 3) Submit.",
    "CATEGORY_FILTER": "PLAYBOOK: 1) Find the category filter. 2) Click the category matching the specified value.",
    "VIEW_WISHLIST": "PLAYBOOK: 1) Find the Wishlist link/icon. 2) Click to view saved items.",
    "PROCEED_TO_CHECKOUT": "PLAYBOOK: 1) Go to cart. 2) Click Proceed to Checkout.",
    "ORDER_COMPLETED": "PLAYBOOK: 1) Find item matching constraints. 2) Navigate to it. 3) Complete purchase/order.",
    "CAROUSEL_SCROLL": "PLAYBOOK: 1) Find carousel section NOT the excluded one. 2) Click the scroll button.",
    "SHARE_PRODUCT": "PLAYBOOK: 1) Find product matching constraints. 2) Click Share button.",
    "ADD_CLIENT": "PLAYBOOK: 1) Navigate to Clients section. 2) Click Add New Client. 3) Fill form satisfying constraints. 4) Save.",
    "DELETE_CLIENT": "PLAYBOOK: 1) Go to Clients. 2) Identify the row matching ALL constraints (name/email/status/matters/last). 3) Open that client (click row). 4) Click Delete client. 5) Confirm if prompted so DELETE_CLIENT fires.",
    "ADD_NEW_MATTER": "PLAYBOOK: 1) Navigate to Matters section. 2) Click Add New Matter. 3) Fill form. 4) Save.",
    "SORT_MATTER_BY_CREATED_AT": "PLAYBOOK: 1) Navigate to Matters list. 2) Find the created_at column header. 3) Click it to sort.",
    "CHANGE_USER_NAME": "PLAYBOOK: 1) Navigate to Settings or Profile. 2) Find the user name field. 3) Set it to the specified value. 4) Save.",
    "WRITE_JOB_TITLE": "PLAYBOOK: 1) Click **Post a Job** (navbar, dashboard, or floating CTA) to open the posting form/modal. "
    "2) Find the job title / position title input. 3) Type a title that CONTAINS the required substring from CONSTRAINTS "
    "(e.g. contains 'gineers' → type 'Senior Engineers' or 'Engineers'—the substring must appear in the field). "
    "4) Do not close the form before typing. 5) Do not submit unless the task asks to publish.",
    "ENTER_DESTINATION": "PLAYBOOK: 1) Find the destination input field. 2) Click to focus. 3) Clear if pre-filled. 4) Type a valid destination DIFFERENT from the NOT constraint (typing is mandatory). 5) Confirm.",
    "ENTER_LOCATION": "PLAYBOOK: 1) Find the location/pickup input field. 2) Click to focus. 3) Type the EXACT location from TASK_CONSTRAINTS in the same step or immediately after—never stop at focus-only. 4) Click matching autocomplete suggestion. 5) Confirm.",
    "SEARCH_RIDE": "PLAYBOOK: 1) On AutoRide, find the ride search/filter interface. 2) Apply filters or scroll to find ride matching ALL constraints. 3) Click on matching ride.",
    "MARK_AS_SPAM": "PLAYBOOK: 1) Browse the inbox. 2) Find email matching ALL constraints. 3) Click on it or select it. 4) Find Mark as Spam button. 5) Click it.",
    "MARK_AS_UNREAD": "PLAYBOOK: 1) Browse the inbox email list. 2) Find email matching ALL constraints. 3) Click or use menu. 4) Click Mark as Unread.",
    "VIEW_EMAIL": "PLAYBOOK: 1) Browse the email list. 2) Find the email matching constraint. 3) Click to open and view.",
    "THEME_CHANGED": "PLAYBOOK: 1) Find Settings/Preferences. 2) Look for Theme/Appearance settings. 3) Select Dark theme. 4) Save/Apply.",
    "COLLAPSE_MENU": "PLAYBOOK: 1) Browse restaurants. 2) Find matching restaurant. 3) Click to expand. 4) Find collapse button. 5) Click it.",
    "CONTACT_CARD_CLICK": "PLAYBOOK: 1) Find contact cards. 2) Find the card NOT containing excluded value. 3) Click on it.",
    "SCROLL_VIEW": "PLAYBOOK: 1) Find scrollable section NOT containing excluded name. 2) Scroll in specified direction.",
    "HELP_CATEGORY_SELECTED": "PLAYBOOK: 1) Navigate to Help page. 2) Find category matching constraint. 3) Click on it.",
    "HELP_PAGE_VIEW": "PLAYBOOK: 1) Find Help/FAQ link in navigation/footer. 2) Click it.",
    "QUANTITY_CHANGED": "PLAYBOOK: 1) Navigate to cart. 2) Find item matching constraints. 3) Set quantity to satisfy constraint. 4) Confirm.",
    "ITEM_INCREMENTED": "PLAYBOOK: 1) Navigate to cart. 2) Find item quantity control. 3) Increment to target value. 4) Confirm.",
    "VIEW_DETAIL": "PLAYBOOK: 1) Browse product listing. 2) Find product matching ALL constraints. 3) Click to open detail page.",
    "SAVE_POST": "PLAYBOOK: 1) Browse feed/posts. 2) Find post matching constraints. 3) Click Save/Bookmark.",
    "HOME_NAVBAR": "PLAYBOOK: 1) Find navigation bar. 2) Click Home tab/link.",
    "VIEW_HIDDEN_POSTS": "PLAYBOOK: 1) Go to profile or settings. 2) Find Hidden Posts section. 3) Navigate to it.",
    "SEARCH_JOBS": "PLAYBOOK: 1) Find Jobs section. 2) Find search input. 3) Type query satisfying constraints. 4) Submit.",
    "APPLY_FOR_JOB": "PLAYBOOK: 1) Open **Jobs** from navbar or /jobs if needed. 2) Use search/filter so **job title** AND "
    "**location** (city/state) from CONSTRAINTS match one listing. 3) Click that job card/row to open detail. "
    "4) Click **Apply** (or Easy Apply)—the APPLY_FOR_JOB event requires this click after the right job is open.",
    "SEARCH_SUBMIT": "PLAYBOOK: 1) Find search input. 2) Type query from TASK_CONSTRAINTS. 3) Submit.",
    "EVENT_WIZARD_OPEN": "PLAYBOOK: 1) Find Add Event button. 2) Click it to open wizard. 3) If title field appears, type title satisfying constraints.",
    "CELL_CLICKED": "PLAYBOOK: 1) Switch to 5 days view. 2) Find a cell matching date/time constraints. 3) Click on that cell.",
    "EVENT_REMOVE_ATTENDEE": "PLAYBOOK: 1) Find an event. 2) Click to open. 3) Find attendees list. 4) Find attendee NOT matching excluded email. 5) Click Remove.",
    "SELECT_TODAY": "PLAYBOOK: 1) Find the focus-today button. 2) Click it.",
    "AUTOLIST_SELECT_TASK_PRIORITY": "PLAYBOOK: 1) Find task with priority NOT the excluded value. 2) Click priority selector. 3) Select High or target value. 4) Save.",
    "AUTOLIST_CANCEL_TASK_CREATION": "PLAYBOOK: 1) Click Add Task. 2) Fill fields as specified. 3) Click Cancel/Discard instead of Submit.",
    "AUTOLIST_TEAM_CREATED": "PLAYBOOK: 1) Open **Teams** (sidebar or tab). 2) Click **Create team** / **+ Team**. 3) Fill **name** and **description** so **not_contains** / **contains** rules on name, description, and **member** fields are all satisfied (pick values that avoid excluded substrings). 4) Add member if the form requires it. 5) **Save** / **Create** so the team-created event fires.",
    "AUTOLIST_COMPLETE_TASK": "PLAYBOOK: 1) Find task matching ALL constraints. 2) Click Complete/checkmark button. 3) Confirm.",
    "AUTOLIST_SELECT_DATE_FOR_TASK": "PLAYBOOK: 1) Find task. 2) Click Edit or date field. 3) Select date satisfying constraint. 4) Confirm.",
    "DELETE_BOOK": "PLAYBOOK: 1) Login with credentials. 2) Navigate to your books. 3) Find matching book. 4) Click Delete. 5) Confirm.",
    "EDIT_BOOK": "PLAYBOOK: 1) Login. 2) Find book matching constraints. 3) Click Edit. 4) Modify fields. 5) Save.",
    "ADD_TO_READING_LIST": "PLAYBOOK: 1) If not logged in, login with TASK_CREDENTIALS. 2) **Search** or browse books for the title/author in constraints. 3) Open the **book detail** page. 4) Click **Add to reading list** / **Save** / bookmark for reading list.",
    "REMOVE_FROM_READING_LIST": "PLAYBOOK: 1) Login. 2) Navigate to Reading List. 3) Find book satisfying constraints. 4) Click Remove.",
    "CONTACT_BOOK": "PLAYBOOK: 1) Navigate to Contact page. 2) Fill form satisfying constraints. 3) Submit.",
    "REGISTRATION_BOOK": "PLAYBOOK: 1) Navigate to Register page. 2) Fill in username, email, password. 3) Submit.",
    "BOOK_DETAIL": "PLAYBOOK: 1) Browse books list. 2) Find book matching ALL constraints. 3) Click to open detail page.",
    "FILTER_BOOK": "PLAYBOOK: 1) Find filter/genre panel. 2) Select genre matching constraint. 3) Apply filter.",
    "SEARCH_BOOK": "PLAYBOOK: 1) Find search bar. 2) Type exact query. 3) Submit.",
    "VIEW_CART_BOOK": "PLAYBOOK: 1) Login first when credentials are provided. 2) Click cart icon in navbar (or /cart). 3) Wait for cart page to render.",
    "LOGIN_BOOK": "PLAYBOOK: 1) Click Login. 2) Type username and password. 3) Click Login button.",
    "LOGOUT_BOOK": "PLAYBOOK: 1) Login first. 2) Find logout option. 3) Click Logout.",
    "ADD_TO_WATCHLIST": "PLAYBOOK: 1) Login if required. 2) Browse films. 3) Find film matching constraints. 4) Click to open detail. 5) Click Add to Watchlist.",
    "REMOVE_FROM_WATCHLIST": "PLAYBOOK: 1) Login. 2) Navigate to watchlist. 3) Find item. 4) Click Remove.",
    "SHARE_MOVIE": "PLAYBOOK: 1) Browse films. 2) Find film matching constraints. 3) Click to open detail. 4) Click Share.",
    "CHECKOUT_STARTED": "PLAYBOOK: 1) Find a product whose **line total** or checkout amount matches the **total** in constraints. 2) Click **Buy now** on that product/card. 3) Do not stop on the catalog—open checkout.",
    "ABOUT_PAGE_VIEW": "PLAYBOOK: 1) Find About link. 2) Click it.",
    "DATE_DROPDOWN_OPENED": "PLAYBOOK: 1) Find date selector. 2) Click to open. 3) Select date satisfying constraint. 4) Confirm.",
    "TIME_DROPDOWN_OPENED": "PLAYBOOK: 1) Find time selection dropdown. 2) Click to open. 3) Select time matching constraint. 4) Confirm.",
    "BILLING_SEARCH": "PLAYBOOK: 1) Navigate to Billing section. 2) Find search/filter inputs. 3) Enter query. 4) Select date_filter satisfying constraints. 5) Apply.",
    "LOG_EDITED": "PLAYBOOK: 1) Navigate to Logs/Time entries. 2) Find log entry matching constraints. 3) Click Edit. 4) Make change. 5) Save.",
    "ARCHIVE_MATTER": "PLAYBOOK: 1) Navigate to Matters. 2) Find matter satisfying constraints. 3) Click Archive. 4) Confirm.",
    "UPDATE_MATTER": "PLAYBOOK: 1) Go to **Matters** (/matters). 2) Scan rows for the ONE matter matching ALL CONSTRAINTS "
    "(name contains substring, client not_equals, updated column, current status if listed). 3) Click the row or "
    "**Revise Matter** / edit action to open the editor. 4) Set **Status** to the required value (e.g. Archived) in the dropdown. "
    "5) Click **Save** or **Submit** so UPDATE_MATTER fires. Do not stop after opening the list.",
    "VIEW_CLIENT_DETAILS": "PLAYBOOK: 1) Navigate to Clients. 2) Find client matching constraints. 3) Click to open details.",
    "VIEW_MATTER_DETAILS": "PLAYBOOK: 1) Navigate to Matters. 2) Find matter matching constraints. 3) Click to open details.",
    "SEND_EMAIL": "PLAYBOOK: 1) Click Compose/New Email. 2) Fill To, Subject, Body satisfying constraints. 3) Click Send.",
    "SEARCH_EMAIL": "PLAYBOOK: 1) Find Search bar. 2) Type query. 3) Submit.",
    "DELETE_REVIEW": "PLAYBOOK: 1) Find restaurant matching constraints. 2) Open it. 3) Find review matching constraints. 4) Click Delete. 5) Confirm.",
    "RESTAURANT_FILTER": "PLAYBOOK: 1) Find cuisine filter. 2) Apply filter satisfying constraints.",
    "ADD_TO_CART_MENU_ITEM": "PLAYBOOK: 1) Browse restaurants. 2) Find restaurant. 3) Find menu item matching constraints. 4) Add to cart.",
    "ADD_TO_CART_MODAL_OPEN": "PLAYBOOK: 1) Search **restaurant** name from TASK_CREDENTIALS in the food search bar. 2) Open that **restaurant** (card/link). 3) On the menu, find an item whose **price** satisfies greater_than / less_than and **item contains** text if given. 4) Click that item or **+** / **Add** to open the **add-to-cart modal** (do not checkout—modal open is the goal).",
    "QUICK_ORDER_STARTED": "PLAYBOOK: 1) Find Quick Order button on any restaurant card. 2) Click it.",
    "FAQ_OPENED": "PLAYBOOK: 1) Navigate to FAQ page. 2) Find FAQ item matching constraint. 3) Click to expand.",
    "MESSAGE_HOST": "PLAYBOOK: 1) Find hotel matching ALL constraints. 2) Click to open. 3) Find Message Host button. 4) Type message. 5) Send.",
    "BOOK_A_CONSULTATION": "PLAYBOOK: 1) Go to Experts/Browse. 2) Find expert matching constraints (name/rating/jobs/rate). 3) Open the expert card/profile. 4) Click Book a consultation.",
    "EDIT_CHECK_IN_OUT_DATES": "PLAYBOOK: 1) Find listing matching constraints. 2) Open booking form. 3) Modify dates. 4) Save.",
    "WISHLIST_OPENED": "PLAYBOOK: 1) Find Wishlist/Saved Hotels icon. 2) Click to open.",
    "REMOVE_FROM_WISHLIST": "PLAYBOOK: 1) Open wishlist. 2) Find listing matching constraints. 3) Click Remove.",
    "JOBS_NAVBAR": "PLAYBOOK: 1) Find Jobs tab in navbar. 2) Click it.",
    "EDIT_PROFILE": "PLAYBOOK: 1) Find user matching constraints. 2) Navigate to Profile. 3) Click Edit Profile. 4) Update fields. 5) Save.",
    "POST_STATUS": "PLAYBOOK: 1) Find status input on feed. 2) Click in text box. 3) Type content satisfying constraints. 4) Click Post.",
    "REMOVE_POST": "PLAYBOOK: 1) Find post satisfying constraints. 2) Click 3-dot menu. 3) Click Remove/Delete. 4) Confirm.",
    "EDIT_PROFILE_TITLE": "PLAYBOOK: 1) Navigate to profile settings. 2) Find title field. 3) Click Edit, clear, type new value. 4) Save.",
    "POST_A_JOB": "PLAYBOOK: 1) Find Post a Job button. 2) Click it.",
    "NAVBAR_EXPERTS_CLICK": "PLAYBOOK: 1) Find Experts link in navbar. 2) Click it.",
    "ADD_SKILL": "PLAYBOOK: 1) Navigate to Skills section. 2) Find Add Skill button. 3) Type skill name satisfying constraints. 4) Save.",
    "FAVORITE_EXPERT_SELECTED": "PLAYBOOK: 1) Go to Experts list. 2) Find expert matching name/role/country constraints. 3) Click favorite/star/bookmark toggle on that expert.",
    "SUBMIT_JOB": "PLAYBOOK: 1) Navigate to Post a Job. 2) Fill title, rate_from, rate_to satisfying constraints. 3) Submit.",
    "HIRE_LATER_START": "PLAYBOOK: 1) Navigate to Hire Later page. 2) Find expert matching constraints. 3) Click Start Hiring.",
    "EDIT_ABOUT": "PLAYBOOK: 1) Navigate to profile. 2) Find About/Bio section. 3) Click Edit. 4) Update text satisfying constraints. 5) Save.",
    "SELECT_CALENDAR": "PLAYBOOK: 1) Find calendar list/sidebar. 2) Find calendar matching constraints. 3) Click to select it.",
    "UNSELECT_CALENDAR": "PLAYBOOK: 1) Find calendar list. 2) Find calendar matching constraints. 3) Click to unselect it.",
    "DOCTOR_CONTACTED_SUCCESSFULLY": "PLAYBOOK: 1) Find doctor matching ALL constraints. 2) Open Contact Doctor form. 3) Fill form satisfying constraints. 4) Submit.",
    "VIEW_DOCTOR_AVAILABILITY": "PLAYBOOK: 1) Browse doctors list. 2) Find doctor matching constraints. 3) Click profile. 4) Navigate to Availability tab.",
    "SEARCH_MATTER": "PLAYBOOK: 1) Find Matters search bar. 2) Type query satisfying constraints. 3) Submit.",
    "FILTER_CLIENTS": "PLAYBOOK: 1) On Clients page, find filter/search. 2) Apply filters satisfying constraints. 3) Show filtered list.",
    "FILTER_MATTER_STATUS": "PLAYBOOK: 1) On Matters page, find status filter. 2) Filter by status matching constraint. 3) Apply.",
    "DOCUMENT_DELETED": "PLAYBOOK: 1) Navigate to Documents. 2) Find document matching ALL constraints. 3) Click to view or delete as task requires.",
    "REVIEW_SUBMITTED": "PLAYBOOK: 1) Find restaurant matching constraints. 2) Open it. 3) Find Write Review button. 4) Fill rating and review text. 5) Submit.",
    "BACK_TO_ALL_RESTAURANTS": "PLAYBOOK: 1) Navigate to restaurant matching constraints. 2) Open detail page. 3) Find Back button. 4) Click it.",
    "ADDRESS_ADDED": "PLAYBOOK: 1) Find delivery address section. 2) Click Add Address. 3) Type exact address. 4) Fill additional fields. 5) Save.",
    "SHARE_HOTEL": "PLAYBOOK: 1) Find hotel matching ALL constraints. 2) Click to open. 3) Find Share button. 4) Enter recipient email. 5) Send.",
    "POPULAR_HOTELS_VIEWED": "PLAYBOOK: 1) Find Popular Hotels section. 2) Apply rating filter if available. 3) Click to view.",
    "TRIP_DETAILS": "PLAYBOOK: 1) View trips list. 2) Find trip matching ALL constraints. 3) Click to view details.",
    "SELECT_CAR": "PLAYBOOK: 1) Find ride matching constraints. 2) Click to open. 3) Select car option.",
    "SEARCH_DESTINATION": "PLAYBOOK: 1) Find destination search bar. 2) Type a destination NOT the excluded value. 3) Submit.",
    "REFILL_PRESCRIPTION": "PLAYBOOK: 1) Navigate to Prescriptions. 2) Find prescription matching constraints. 3) Click Refill. 4) Confirm.",
    "VIEW_PRESCRIPTION": "PLAYBOOK: 1) Navigate to Prescriptions. 2) Find prescription matching constraints. 3) Click to view details.",
    "FILTER_DOCTOR_REVIEWS": "PLAYBOOK: 1) Navigate to Reviews/Doctors. 2) Find filter. 3) Set filter matching constraints. 4) Apply.",
    "QUICK_REORDER": "PLAYBOOK: 1) Find Recent Orders section. 2) Find order satisfying constraints. 3) Click Reorder.",
    "EDIT_CART_ITEM": "PLAYBOOK: 1) Navigate to Cart. 2) Find item matching constraints. 3) Click Edit.",
    "DELETE_MATTER": "PLAYBOOK: 1) Navigate to Matters. 2) Find matter matching constraints. 3) Click Delete. 4) Confirm.",
    "CREATE_LABEL": "PLAYBOOK: 1) Find Labels section. 2) Click + or Create Label. 3) Type name satisfying constraints. 4) Save.",
    "REMOVE_FROM_CART_BOOK": "PLAYBOOK: 1) Login first using TASK_CREDENTIALS. 2) Open shopping cart. 3) Find the book matching constraints (name/year/price). 4) Click Remove/Delete from cart.",
    "DOCUMENT_RENAMED": "PLAYBOOK: 1) Open Documents section. 2) Select a document row. 3) Click Rename/Edit name action. 4) Type the exact new_name value from constraints. 5) Save/confirm rename.",
    "FAVORITE_SUBNET": "PLAYBOOK: 1) Go to Subnets list. 2) Find subnet matching provided subnet_id or subnet name. 3) Click favorite/star/heart toggle for that subnet.",
    "DELETE_TASK": "PLAYBOOK: 1) Navigate to task list. 2) Find task matching ALL constraints. 3) Click Delete. 4) Confirm.",
    "CREATE_TASK": "PLAYBOOK: 1) Find New Task/Add Task button. 2) Fill fields with EXACT values. 3) Save/Submit.",
    "EDIT_TASK": "PLAYBOOK: 1) Find task matching constraints. 2) Click Edit. 3) Update fields. 4) Save.",
    "COMPLETE_TASK": "PLAYBOOK: 1) Find task matching constraints. 2) Click Complete/Done/Checkmark.",
    "JOB_POSTING": "PLAYBOOK: 1) Find Post a Job button. 2) Click it. 3) Type EXACT job title. 4) Submit.",
    "HIDE_POST": "PLAYBOOK: 1) On the feed, find the post whose text **contains** the long snippet in CONSTRAINTS (scroll if needed). 2) Open the post **⋯** / **More** menu. 3) Click **Hide** / **Hide post** / **Not interested** as offered.",
    "TEMPLATE_CANCELED": "PLAYBOOK: 1) Go to **Templates** (or Mail settings). 2) Find the template matching **body contains**, **subject equals**, **to** constraints. 3) Open menu → **Cancel** / **Delete** / **Discard** so TEMPLATE_CANCELED fires.",
    "CONTACT_PAGE_VIEW": "PLAYBOOK: 1) Click **Contact** in the nav/footer (or /contact). 2) Stop when the Contact page is visible.",
    "FILTER_FILM": "PLAYBOOK: 1) Open **Films** / browse. 2) Use **genre** and/or **year** filters so values satisfy CONSTRAINTS (e.g. year ≤ value, genre equals). 3) Click **Apply** / **Filter**. 4) Open the matching film card if required.",
    "SEARCH_PRESCRIPTION": "PLAYBOOK: 1) Go to **Prescriptions** / Medical records. 2) Use search or filters for **medicine_name**, **doctor_name**, etc. 3) Narrow until one row matches ALL **not_equals** / **contains** rules. 4) Open details if required.",
    "VOICE_MUTE_TOGGLE": "PLAYBOOK: 1) Join or select the **voice channel** matching **channel_name** and **server_name**. 2) Click the **mute** / microphone control to toggle mute.",
    "LEAVE_VOICE_CHANNEL": "PLAYBOOK: 1) Open server and voice channel matching constraints. 2) Join/select that voice channel. 3) Click Disconnect/Leave call button.",
    "ADD_REACTION": "PLAYBOOK: 1) Open the **channel** (not_equals constraints). 2) Find the **message** not matching excluded **message_id**. 3) Hover message → **Add reaction** → pick emoji.",
    "EDIT_USER_BOOK": "PLAYBOOK: 1) **Login** with TASK_CREDENTIALS. 2) Go to profile / **My books**. 3) Find the book field to edit per task. 4) Save.",
    "SETTINGS_APPEARANCE": "PLAYBOOK: 1) Open Settings. 2) Navigate to Appearance/Theme. 3) Choose the required theme (e.g. dark). 4) Save/apply if present.",
    "DISCONNECT_WALLET": "PLAYBOOK: 1) Open wallet/account settings. 2) Locate wallet entry matching constraints. 3) Click Disconnect/Unlink. 4) Confirm if prompted.",
    "SEARCH_PRODUCT": "PLAYBOOK: 1) Find product search bar. 2) Type query from TASK_CONSTRAINTS exactly. 3) Submit search (Enter or search button). 4) Wait for filtered product results.",
    "SEARCH": "PLAYBOOK: 1) Use search input relevant to the app (rides/location/products depending on page). 2) Type query from constraints. 3) Submit and verify results update.",
    "NEW_LOG_ADDED": "PLAYBOOK: 1) Navigate to Logs/Time entries. 2) Click Add New Log. 3) Fill description/duration/matter constraints. 4) Save/Submit so NEW_LOG_ADDED fires.",
    "DELETE_SERVER": "PLAYBOOK: 1) Open server/channel list and find server matching constraints. 2) Open server settings/context menu. 3) Click Delete Server. 4) Confirm deletion.",
    "UNHIDE_POST": "PLAYBOOK: 1) Open Hidden posts section. 2) Find post matching constraints. 3) Click Unhide/Restore from menu.",
    "RESERVATION_COMPLETE": "PLAYBOOK: 1) On restaurant booking flow, choose restaurant matching constraints. 2) Set people/date/time/occasion as required. 3) Click Reserve/Complete booking to fire RESERVATION_COMPLETE.",
    "ADD_TO_WISHLIST": "PLAYBOOK: 1) Find item/hotel matching constraints. 2) Click Add to Wishlist/heart icon. 3) Ensure wishlist toggle turns on.",
    "FAVORITE_EXPERT_SELECTED": "PLAYBOOK: 1) Go to Experts list. 2) Find expert matching constraints. 3) Click favorite/star toggle.",
    "BROWSE_FAVORITE_EXPERT": "PLAYBOOK: 1) Open Experts/Browse experts section. 2) Open favorites/saved experts tab if present. 3) Click any favorite expert card to browse details.",
    "VIEW_SUBNET": "PLAYBOOK: 1) Open Subnets list. 2) Find subnet by name/id constraints. 3) Click subnet card/title to open details.",
    "GENERAL": "PLAYBOOK: Success requires triggering the correct backend event (submit/book/order). Find forms or primary CTAs (Book, Reserve, Submit, Search) matching the TASK. Avoid hero carousels (next/prev slide) unless the task asks to browse slides. Avoid cycling the same marketing/nav href. Use TASK_CONSTRAINTS for field values.",
}

# ---------------------------------------------------------------------------
# Search input IDs per website (for search shortcuts)
# ---------------------------------------------------------------------------
SEARCH_INPUT_IDS: dict[str, str] = {
    "automail": "mail-search",
    "autocinema": "input",
    "autodining": "search-field",
    "autodelivery": "food-search",
    "autobooks": "input",
    "autozone": "input",
    "autoconnect": "input",
    "autohealth": "input",
}

# ---------------------------------------------------------------------------
# Known element IDs for quick-click shortcuts
# ---------------------------------------------------------------------------
QUICK_CLICK_IDS: dict[str, str] = {
    "focus_today": "focus-today",
    "new_event": "new-event-cta",
    "add_team": "add-team-btn",
    "wishlist": "favorite-action",
    "spotlight_movie": "spotlight-view-details-btn",
    "featured_book": "featured-book-view-details-btn-1",
    "featured_product": "view-details",
    "nav_about": "nav-about",
}
