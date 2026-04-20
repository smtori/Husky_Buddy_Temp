import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(page_title='Moderation Log', layout='wide')

SideBarLinks()

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
        'status': (r.get('status') or 'flagged').lower(),
        'created_at': r.get('created_at', '')
    })

active_flags = sum(1 for r in reports if r['status'] == 'flagged')

st.metric('Active Flags', active_flags, border=True)


st.write('')

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
        st.session_state['moderation_filter'] = 'Flagged'

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
    symbol = STATUS_ICONS.get(status, '◉')
    status_label = status.title()

    with st.container(border=True):
        top_left, top_right = st.columns([5, 2])

        with top_left:
            st.subheader(f"⚠ {report['reason']}")
            st.write(f"**Reported:** {report['reported_name']} (ID: {report['reported_id']})")
            st.write(f"**By:** {report['reporter_name']} (ID: {report['reporter_id']})")
            st.caption(str(report['created_at']))

        with top_right:
            st.metric('Status', f'{symbol} {status_label}')

        st.info(f'“{report["reason"]}”')

        if st.session_state['active_investigation_report'] == report_id:
            st.subheader('Investigation Details')
            st.write(f"**Reported user:** {report['reported_name']} (ID: {report['reported_id']})")
            st.write(f"**Email:** {report['reported_email']}")
            if report['reported_year']:
                st.write(f"**Year:** {report['reported_year']}")
            st.write(f"**Original report:** {report['reason']}")

            message_key = f'message_{report_id}'
            moderator_message = st.text_area(
                'Message the reported user',
                key=message_key,
                placeholder='Write a message to the reported user asking for context or explaining next steps...'
            )

            mc1, mc2 = st.columns(2)
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
                st.session_state['active_investigation_report'] = report_id
                st.rerun()

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
