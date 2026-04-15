import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Edit Profile")
st.markdown("Keep your HuskyBuddy profile up to date so we can find you the best matches!")

# ── Session state ──────────────────────────────────────────────────────────────
if "show_success_modal" not in st.session_state:
    st.session_state.show_success_modal = False
if "form_key_counter" not in st.session_state:
    st.session_state.form_key_counter = 0

# ── Success dialog ─────────────────────────────────────────────────────────────
@st.dialog("Profile Updated!")
def show_success_dialog():
    st.markdown("### Your profile has been successfully updated!")
    st.markdown("We'll use your latest info to find your next HuskyBuddy match.")
    if st.button("Back to Home", use_container_width=True, key="dialog_home"):
        st.session_state.show_success_modal = False
        st.switch_page("pages/Home.py")

# ── API base ───────────────────────────────────────────────────────────────────
BASE_URL = "http://web-api:4000"

# ── Static options drawn directly from the DB schema / seed data ───────────────

# husky_user.year ENUM
YEAR_OPTIONS = ["1st", "2nd", "3rd", "4th", "5th", "Grad"]

# All majors from the INSERT INTO majors seed block
MAJOR_OPTIONS = sorted([
    "Africana Studies", "American Sign Language-English Interpreting",
    "Advanced Manufacturing Systems", "Analytics", "Applied Physics",
    "Architectural Studies", "Architecture", "Art", "Behavioral Neuroscience",
    "Biochemistry", "Bioengineering", "Biology", "Biomedical Physics",
    "Biotechnology", "Business Administration", "Cell and Molecular Biology",
    "Chemical Engineering", "Chemistry", "Civil Engineering",
    "Communication and Media Studies", "Communication Studies",
    "Computer Engineering", "Computer Science", "Cultural Anthropology",
    "Cybersecurity", "Data Science", "Design", "Digital Communication and Media",
    "Ecology and Evolutionary Biology", "Economics",
    "Electrical and Computer Engineering", "Electrical Engineering", "English",
    "Environmental and Sustainability Sciences", "Environmental Engineering",
    "Environmental Studies", "Finance and Accounting Management",
    "Game Art and Animation", "Game Design", "Global Asian Studies",
    "Health Science", "Healthcare Administration", "History",
    "History Culture and Law", "Human Services", "Industrial Engineering",
    "Information Technology", "Interdisciplinary Studies",
    "International Affairs", "International Business", "Journalism",
    "Landscape Architecture", "Linguistics", "Management", "Marine Biology",
    "Mathematics", "Mechanical Engineering", "Mechatronics",
    "Media and Screen Studies", "Media Arts", "Music", "Nursing",
    "Performance and Extended Realities", "Pharmaceutical Sciences",
    "Pharmacy Studies", "Philosophy", "Physics", "Political Science",
    "Politics Philosophy and Economics", "Project Management", "Psychology",
    "Public Health", "Public Relations", "Religious Studies", "Sociology",
    "Spanish", "Speech-Language Pathology and Audiology", "Studio Art",
    "Theatre", "Undeclared",
])

# interest_tag.tag_type values from seed data
INTEREST_OPTIONS = [
    "Sports and Fitness",
    "Arts and Creativity",
    "Tech",
    "Gaming",
    "Food and Social",
    "Careers and Academic",
    "Entertainment and Culture",
    "Wellness and Lifestyle",
]

# campus_spot.spot_name values from seed data
CAMPUS_SPOT_OPTIONS = [
    "Marino Recreation Center",
    "Snell Library",
    "Tatte Bakery",
    "Prudential Center",
    "Kigo Kitchen",
]

# student_availability.day_of_week ENUM
DAY_OPTIONS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ── Form ───────────────────────────────────────────────────────────────────────
if not st.session_state.show_success_modal:
    with st.form(f"edit_profile_form_{st.session_state.form_key_counter}"):

        # ── Basic info ────────────────────────────────────
        st.subheader("Basic Info")
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *")
            last_name  = st.text_input("Last Name *")
        with col2:
            email = st.text_input("Northeastern Email *", placeholder="abc@northeastern.edu")
            year  = st.selectbox("Year *", options=[""] + YEAR_OPTIONS)

        # ── Major ────────────────────────────────
        st.subheader("Major(s)")
        majors = st.multiselect(
            "Select your major(s) *",
            options=MAJOR_OPTIONS,
            help="You can select more than one if you are double-majoring."
        )

        # ── Interests ────────────────────────
        st.subheader("Interests")
        interests = st.multiselect(
            "Select your interest categories *",
            options=INTEREST_OPTIONS,
            help="These are used to find your best HuskyBuddy match."
        )

        # ── Favorite campus spots ────────────────
        st.subheader("Favorite Spots Around Campus")
        spots = st.multiselect(
            "Select your favorite spots *",
            options=CAMPUS_SPOT_OPTIONS,
        )

        # ── Availability ───────────────────────────
        st.subheader("Availability")
        st.markdown("Add up to **3** availability windows.")

        avail_slots = []
        for i in range(1, 4):
            with st.expander(f"Time Slot {i}", expanded=(i == 1)):
                col_day, col_start, col_end = st.columns(3)
                with col_day:
                    day = st.selectbox(
                        "Day", options=["(none)"] + DAY_OPTIONS,
                        key=f"day_{i}"
                    )
                with col_start:
                    start = st.time_input("Start Time", key=f"start_{i}")
                with col_end:
                    end = st.time_input("End Time", key=f"end_{i}")

                if day != "(none)":
                    avail_slots.append({
                        "day_of_week": day,
                        "start_time": str(start),
                        "end_time": str(end),
                    })

        submitted = st.form_submit_button("Save Profile", use_container_width=True)

        if submitted:
            missing = []
            if not first_name:
                missing.append("First Name")
            if not last_name:
                missing.append("Last Name")
            if not email:
                missing.append("Northeastern Email")
            if not year:
                missing.append("Year")
            if not majors:
                missing.append("Major(s)")
            if not interests:
                missing.append("Interests")
            if not spots:
                missing.append("Favorite Spots")
            if not avail_slots:
                missing.append("At least one Availability window")

            if missing:
                st.error(f"Please fill in: {', '.join(missing)}")
            elif not email.endswith("@northeastern.edu"):
                st.error("Email must be a valid @northeastern.edu address.")
            else:
                bad_slots = [
                    s["day_of_week"] for s in avail_slots
                    if s["end_time"] <= s["start_time"]
                ]
                if bad_slots:
                    st.error(f"End time must be after start time for: {', '.join(bad_slots)}")
                else:
                    profile_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "year": year,
                        "majors": majors,           # list of major_name strings
                        "interests": interests,     # list of tag_type strings
                        "campus_spots": spots,      # list of spot_name strings
                        "availability": avail_slots,  # list of {day_of_week, start_time, end_time}
                    }

                    try:
                        response = requests.put(f"{BASE_URL}/students/profile", json=profile_data)

                        if response.status_code == 200:
                            st.session_state.show_success_modal = True
                            st.rerun()
                        else:
                            st.error(
                                f"Failed to update profile: "
                                f"{response.json().get('error', 'Unknown error')}"
                            )

                    except requests.exceptions.RequestException as e:
                        st.error(f"Error connecting to the API: {str(e)}")
                        st.info("Please ensure the API server is running.")

    if st.button("Cancel", key="page_cancel"):
        st.switch_page("pages/Home.py")

if st.session_state.show_success_modal:
    show_success_dialog()