import streamlit as st
import pandas as pd

st.title('VTuber Bets')

# File upload
file = st.file_uploader('Upload a CSV file with VTuber data', type='csv')

if file is not None:
    data = pd.read_csv(file)
    st.write(data)

# Display some metrics
if 'wins' in data.columns:
    total_wins = data['wins'].sum()
    st.write(f'Total Wins: {total_wins}')

if 'losses' in data.columns:
    total_losses = data['losses'].sum()
    st.write(f'Total Losses: {total_losses}')