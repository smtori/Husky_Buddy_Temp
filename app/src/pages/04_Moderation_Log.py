import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(page_title='Moderation Log', layout='wide')

SideBarLinks()



st.header('Moderation Log')
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if st.button('← Back to Admin Home', type='secondary', use_container_width=False):
        st.switch_page('pages/00_Admin_Home.py')

st.markdown(
    """
<style>
.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

.definition-card {
    border: 2px solid #222;
    border-radius: 18px;
    padding: 18px 24px;
    background: #f7f7f7;
    margin-bottom: 14px;
}

.definition-title {
    font-size: 1.3rem;
    font-weight: 800;
    margin-bottom: 0.35rem;
}

.definition-text {
    color: #444;
    font-size: 0.98rem;
    line-height: 1.5;
}

.metric-box {
    border: 2px solid #222;
    border-radius: 18px;
    padding: 18px 24px;
    background: #f7f7f7;
    margin-bottom: 14px;
    font-size: 1.25rem;
    font-weight: 700;
}

.metric-number {
    float: right;
    font-weight: 800;
    font-size: 1.5rem;
}

.report-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 0.35rem;
}

.report-meta {
    color: #6f6f6f;
    font-size: 0.96rem;
    margin-bottom: 0.28rem;
}

.report-reason {
    background: white;
    border-radius: 999px;
    padding: 10px 16px;
    font-weight: 600;
    margin-top: 12px;
    margin-bottom: 16px;
}

.status-pill {
    border: 2px solid #222;
    border-radius: 999px;
    padding: 8px 18px;
    font-weight: 600;
    background: white;
    display: inline-block;
}

.status-pending {
    color: #222;
    border-color: #222;
}

.status-flagged {
    color: #b45309;
    border-color: #b45309;
}

.status-resolved {
    color: #166534;
    border-color: #166534;
}

.status-dismissed {
    color: #6b7280;
    border-color: #6b7280;
}

.investigation-box {
    border: 2px solid #222;
    border-radius: 16px;
    padding: 16px 18px;
    background: #fafafa;
    margin-top: 10px;
    margin-bottom: 8px;
}

.investigation-title {
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

div.stButton > button {
    border-radius: 14px;
    height: 46px;
    font-weight: 600;
    border: 1.5px solid #222;
    background: white;
}

div.stButton > button:hover {
    background: #f0f0f0;

}
</style>
""",
    unsafe_allow_html=True,
)

API_BASE = 'http://api:4000'


def fetch_json(url: str):
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()


try:
    reports_raw = fetch_json(f'{API_BASE}/reports')
except Exception as e:
    st.error(f'Could not load reports: {e}')
    reports_raw = []

try:
    users_raw = fetch_json(f'{API_BASE}/users')
except Exception as e:
    st.error(f'Could not load users for name lookup: {e}')
    users_raw = []

user_lookup = {}
for user in users_raw:
    user_lookup[user['student_id']] = {
        'name': user['name'],
        'email': user['email'],
        'year': user.get('year', '')
    }

reports = []
for r in reports_raw:
    reporter_id = r.get('reporter_id')
    reported_id = r.get('reported_id')
    reporter_info = user_lookup.get(reporter_id, {})
    reported_info = user_lookup.get(reported_id, {})

    reports.append({
        'report_id': r.get('report_id'),
        'reporter_id': reporter_id,
        'reported_id': reported_id,
        'reporter_name': reporter_info.get('name', f'User {reporter_id}'),
        'reported_name': reported_info.get('name', f'User {reported_id}'),
        'reported_email': reported_info.get('email', 'No email available'),
        'reported_year': reported_info.get('year', ''),
        'reason': r.get('reason', 'No reason provided'),
        'status': (r.get('status') or 'pending').lower(),
        'created_at': r.get('created_at', '')
    })

pending_count = sum(1 for r in reports if r['status'] == 'pending')
active_flags = sum(1 for r in reports if r['status'] == 'flagged')


st.markdown(
    f"<div class='metric-box'>Pending Reports: <span class='metric-number'>{pending_count}</span></div>",
    unsafe_allow_html=True,
)

st.markdown(
    f"<div class='metric-box'>Active Flags: <span class='metric-number'>{active_flags}</span></div>",
    unsafe_allow_html=True,
)

if 'moderation_filter' not in st.session_state:
    st.session_state['moderation_filter'] = 'All'

if 'active_investigation_report' not in st.session_state:
    st.session_state['active_investigation_report'] = None

c1, c2, c3 = st.columns(3)

with c1:
    if st.button('All', key='mod_filter_all', use_container_width=True):
        st.session_state['moderation_filter'] = 'All'

with c2:
    if st.button('Pending', key='mod_filter_pending', use_container_width=True):
        st.session_state['moderation_filter'] = 'Pending'

with c3:
    if st.button('Resolved', key='mod_filter_resolved', use_container_width=True):
        st.session_state['moderation_filter'] = 'Resolved'

selected_filter = st.session_state['moderation_filter']
filtered_reports = reports
if selected_filter != 'All':
    filtered_reports = [
        r for r in reports
        if r['status'] == selected_filter.lower()
    ]

STATUS_ICONS = {
    'pending': '◉',
    'flagged': '⚑',
    'resolved': '✓',
    'dismissed': '–'
}

for report in filtered_reports:
    status = report['status']
    report_id = report['report_id']

    if status == 'resolved':
        status_class = 'status-resolved'
    elif status == 'dismissed':
        status_class = 'status-dismissed'
    elif status == 'flagged':
        status_class = 'status-flagged'
    else:
        status_class = 'status-pending'

    with st.container(border=True):
        top_left, top_right = st.columns([5, 2])

        with top_left:
            st.markdown(
                f"<div class='report-title'>⚠ {report['reason']}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='report-meta'><b>Reported:</b> {report['reported_name']} (ID: {report['reported_id']})</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='report-meta'><b>By:</b> {report['reporter_name']} (ID: {report['reporter_id']})</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='report-meta'>{report['created_at']}</div>",
                unsafe_allow_html=True,
            )

        with top_right:
            st.markdown(
                f"""
                <div style="display:flex; justify-content:flex-end; margin-top:8px;">
                    <div class="status-pill {status_class}">
                        {STATUS_ICONS.get(status, '◉')} {status.title()}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"<div class='report-reason'>“{report['reason']}”</div>",
            unsafe_allow_html=True,
        )

        if st.session_state['active_investigation_report'] == report_id:
            st.markdown(
                "<div class='investigation-box'><div class='investigation-title'>Investigation Details</div></div>",
                unsafe_allow_html=True,
            )
            st.write(f"**Reported user:** {report['reported_name']} (ID: {report['reported_id']})")
            st.write(f"**Email:** {report['reported_email']}")
            if report['reported_year']:
                st.write(f"**Year:** {report['reported_year']}")
            st.write(f"**Original report:** {report['reason']}")

            message_key = f"message_{report_id}"
            moderator_message = st.text_area(
                'Message the reported user',
                key=message_key,
                placeholder='Write a message to the reported user asking for context or explaining next steps...'
            )

            mc1, mc2 = st.columns([1, 1])
            with mc1:
                if st.button('Send Message', key=f'send_message_{report_id}', use_container_width=True):
                    if moderator_message.strip():
                        st.success(f"Message prepared for {report['reported_name']} at {report['reported_email']}")
                    else:
                        st.warning('Write a message before sending.')
            with mc2:
                if st.button('Close Investigation Panel', key=f'close_investigation_{report_id}', use_container_width=True):
                    st.session_state['active_investigation_report'] = None
                    st.rerun()

        b1, b2, b3 = st.columns(3)

        with b1:
            if st.button('Dismiss', key=f'dismiss_{report_id}', use_container_width=True):
                try:
                    r = requests.put(
                        f'{API_BASE}/reports/{report_id}',
                        json={'status': 'dismissed'},
                        timeout=5,
                    )
                    r.raise_for_status()
                    if st.session_state['active_investigation_report'] == report_id:
                        st.session_state['active_investigation_report'] = None
                    st.rerun()
                except Exception as e:
                    st.error(f'Could not dismiss report {report_id}: {e}')

        with b2:
            if st.button('Investigate', key=f'investigate_{report_id}', use_container_width=True):
                try:
                    if report['status'] != 'flagged':
                        r = requests.put(
                            f'{API_BASE}/reports/{report_id}',
                            json={'status': 'flagged'},
                            timeout=5,
                        )
                        r.raise_for_status()
                    st.session_state['active_investigation_report'] = report_id
                    st.rerun()
                except Exception as e:
                    st.error(f'Could not open investigation for report {report_id}: {e}')

        with b3:
            if st.button('Resolved', key=f'resolved_{report_id}', use_container_width=True):
                try:
                    r = requests.put(
                        f'{API_BASE}/reports/{report_id}',
                        json={'status': 'resolved'},
                        timeout=5,
                    )
                    r.raise_for_status()
                    if st.session_state['active_investigation_report'] == report_id:
                        st.session_state['active_investigation_report'] = None
                    st.rerun()
                except Exception as e:
                    st.error(f'Could not resolve report {report_id}: {e}')

    st.write('')