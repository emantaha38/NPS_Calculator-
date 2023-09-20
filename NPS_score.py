import streamlit as st
import pandas as pd
import numpy as np
import io
import base64
import tempfile

# Initialize a placeholder for uploaded data
uploaded_data = None

# Define the NPS function
def nps(x):
    if x > 8:
        return "Promoters"
    elif x < 3:
        return "HD"
    elif x < 7:
        return "Detractors"
    else:
        return "Neutral"

# Define the Streamlit app
def main():
    st.image('https://www.clootrack.com/hubfs/Clootrack_Feb2022/images/NPSscore3-980x612.png')
    st.title("Net Promoter Score (NPS) Calculator")
    
    # Upload new data
    uploaded_file = st.file_uploader("Upload new data (Excel file)", type=["xlsx"])
    
    global uploaded_data
    
    if uploaded_file is not None:
        uploaded_data = pd.read_excel(uploaded_file)
    
    if uploaded_data is not None:
        st.write("Uploaded Data:")
        st.write(uploaded_data)  # Keep 'Agent Name' column in display
        
        # Calculate NPS for uploaded data
        uploaded_data['NPS score'] = uploaded_data['Q1'].apply(nps)
        
        uploaded_data_nps = uploaded_data.groupby(['Agent Name', 'NPS score'])['Msisdn'].count().unstack().fillna(0)
        
        uploaded_data_nps['Total_score'] = uploaded_data_nps[['Detractors', 'HD', 'Neutral', 'Promoters']].sum(axis=1)
        uploaded_data_nps['HD_percent'] = np.where(uploaded_data_nps['Total_score'] == 0, 0, (uploaded_data_nps['HD'] / uploaded_data_nps['Total_score'] * 100).round().astype(int))
        uploaded_data_nps['HD_percent'] = uploaded_data_nps['HD_percent'].apply(lambda x: f"{x}%")
        uploaded_data_nps['Promoters_Num'] = uploaded_data_nps['Promoters'] - (uploaded_data_nps['Detractors'] + uploaded_data_nps['HD'])
        uploaded_data_nps['Promoters_Percent'] = np.where(uploaded_data_nps['Total_score'] == 0, 0, (uploaded_data_nps['Promoters_Num'] / uploaded_data_nps['Total_score'] * 100).round().astype(int))
        uploaded_data_nps['Promoters_Percent'] = uploaded_data_nps['Promoters_Percent'].apply(lambda x: f"{x}%")
        
        # Download processed data as Excel
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            with pd.ExcelWriter(temp_file.name, engine='xlsxwriter') as writer:
                uploaded_data_nps.to_excel(writer, sheet_name='Processed Data', index=True)  # Keep index to include 'Agent Name'
        
        with open(temp_file.name, "rb") as file:
            bytes_data = file.read()
        
        b64_data = base64.b64encode(bytes_data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64_data}" download="processed_data.xlsx">Download Processed Data</a>'
        
        st.write("Processed Data (with 'Agent Name' column):")
        st.write(uploaded_data_nps)
        st.markdown(href, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
