import streamlit as st
import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Page config
st.set_page_config(
    page_title="VTuber Bets",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.2em;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    with open('bets.json', 'r', encoding='utf-8') as f:
        bets = json.load(f)
    with open('user.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    return bets, users

# Initialize session state
if 'bets' not in st.session_state:
    bets, users = load_data()
    st.session_state.bets = bets
    st.session_state.users = users

def page_leaderboard():
    st.markdown("## 🏆 Leaderboard")
    
    users_list = list(st.session_state.users.values())
    users_sorted = sorted(users_list, key=lambda x: x['coins'], reverse=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Rank", "")
    with col2:
        st.metric("User", "")
    with col3:
        st.metric("Coins", "")
    with col4:
        st.metric("Correct Bets", "")
    with col5:
        st.metric("Win Rate", "")
    
    st.divider()
    
    for idx, user in enumerate(users_sorted, 1):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write(f"**#{idx}**")
        with col2:
            st.write(f"**{user['username']}**")
        with col3:
            st.write(f"💰 {user['coins']}")
        with col4:
            st.write(f"✅ {user['bets_correct']}/{user['bets_placed']}")
        with col5:
            if user['bets_placed'] > 0:
                win_rate = (user['bets_correct'] / user['bets_placed']) * 100
                st.write(f"{win_rate:.1f}%")
            else:
                st.write("N/A")

def page_bets():
    st.markdown("## 🎲 Active Bets")
    
    # Filter bets by status
    status_filter = st.selectbox("Filter by Status", ["All", "open", "voting", "closed"])
    
    filtered_bets = st.session_state.bets
    if status_filter != "All":
        filtered_bets = [b for b in filtered_bets if b['status'] == status_filter]
    
    for bet in filtered_bets:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {bet['vtuber']}")
                st.markdown(f"**{bet['title']}**")
                st.markdown(f"_{bet['description']}_")
                st.markdown(f"Category: `{{bet['category']}}`")
                
                if bet['status'] == 'closed' and bet['result']:
                    st.success(f"✅ Result: {{bet['result']}}")
                elif bet['status'] == 'open':
                    st.info("🔵 Betting Open")
                elif bet['status'] == 'voting':
                    st.warning("🟡 Voting in Progress")
            
            with col2:
                st.metric("Status", bet['status'].upper())
            
            # Display options
            st.markdown("**Options:**")
            col1, col2 = st.columns(2)
            
            with col1:
                for option in bet['options'][:1]:
                    bets_count = sum(1 for b in bet['bets'].values() if b['option'] == option)
                    st.write(f"• {{option}} ({{bets_count}} bets)")
            
            with col2:
                for option in bet['options'][1:]:
                    bets_count = sum(1 for b in bet['bets'].values() if b['option'] == option)
                    st.write(f"• {{option}} ({{bets_count}} bets)")
            
            # Show bet details if any
            if bet['bets']:
                with st.expander("View Bets"):
                    for username, bet_info in bet['bets'].items():
                        st.write(f"{{username}}: {{bet_info['amount']}} coins → {{bet_info['option']}}")
            
            st.divider()

def page_create():
    st.markdown("## ✨ Create New Bet")
    
    with st.form("create_bet_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            vtuber_name = st.text_input("VTuber Name", placeholder="e.g., Filian 🦆")
        
        with col2:
            category = st.selectbox("Category", ["Boss Fight", "Yap Session", "Tech Scuff", "Death Count", "Chaos Moment", "Game Completion", "Other"])
        
        title = st.text_input("Bet Title", placeholder="e.g., Will they beat the boss?")
        description = st.text_area("Description", placeholder="Add more context about this bet...")
        
        st.markdown("### Options")
        col1, col2 = st.columns(2)
        
        with col1:
            option1 = st.text_input("Option 1", placeholder="YES / True / Outcome A")
        
        with col2:
            option2 = st.text_input("Option 2", placeholder="NO / False / Outcome B")
        
        col1, col2 = st.columns(2)
        
        with col1:
            close_time = st.time_input("When does betting close?")
        
        with col2:
            st.write("(Note: Creating bets will save to the file)")
        
        submit = st.form_submit_button("Create Bet", use_container_width=True)
        
        if submit:
            if not all([vtuber_name, title, description, option1, option2]):
                st.error("Please fill in all fields!")
            else:
                st.success(f"Bet created! 🎉")
                st.info(f"Created: {{vtuber_name}} - {{title}}")

# Main app
st.title("🎲 VTuber Bets")
st.markdown("*Predict VTuber moments and earn coins!*")

tab1, tab2, tab3 = st.tabs(["🎲 Bets", "🏆 Leaderboard", "✨ Create Bet"])

with tab1:
    page_bets()

with tab2:
    page_leaderboard()

with tab3:
    page_create()
