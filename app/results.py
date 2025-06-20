import pandas as pd
import plotly.express as px
import streamlit as st

from app.db import fetch_all_clients, fetch_assessment_results, fetch_assessments


def results_view():
    """View for displaying assessment results and analysis."""
    st.title("Results Dashboard")
    
    # Step 1: Select Client
    clients = fetch_all_clients()
    if not clients:
        st.warning("No clients found. Please add clients first.")
        return
    
    client_names = [client['name'] for client in clients]
    client_ids = [client['id'] for client in clients]
    
    # Determine default index for client selectbox based on session state
    default_selected_client_index = 0
    if 'client_id' in st.session_state and st.session_state['client_id'] in client_ids:
        default_selected_client_index = client_ids.index(st.session_state['client_id'])
    
    selected_client_idx = st.selectbox(
        "Select Client:",
        range(len(client_names)),
        format_func=lambda i: client_names[i],
        index=default_selected_client_index, # Set default index
        key="results_client_selectbox" # Added key for persistence
    )
    
    client_id = client_ids[selected_client_idx]
    # Update session state if the selection changes
    if st.session_state.get('client_id') != client_id:
        st.session_state['client_id'] = client_id
        st.session_state['client_name'] = client_names[selected_client_idx]
        # Clear assessment details when client changes in results view as well
        # This might be optional depending on desired UX, but good for consistency
        for key_to_clear in ['assessment_id', 'assessment_name', 'assessment_type']:
            if key_to_clear in st.session_state:
                del st.session_state[key_to_clear]
        st.rerun()
    
    # Step 2: Select Assessment
    assessments = fetch_assessments(client_id)
    if not assessments:
        st.warning(f"No assessments found for {client_names[selected_client_idx]}. Please create assessments first.")
        return
    
    assessment_names = [a['name'] for a in assessments]
    assessment_ids = [a['id'] for a in assessments]
    
    selected_assessment_idx = st.selectbox(
        "Select Assessment:",
        range(len(assessment_names)),
        format_func=lambda i: f"{assessment_names[i]} ({assessments[i]['qtype']} type)"
    )
    
    assessment_id = assessment_ids[selected_assessment_idx]
    
    # Fetch assessment results
    results = fetch_assessment_results(assessment_id)
    if not results:
        st.warning("No results found for this assessment. Please complete the assessment first.")
        return
    
    # Convert results to DataFrame for analysis
    df = pd.DataFrame([dict(r) for r in results])
    
    # Display assessment summary
    st.header("Assessment Summary")
    st.subheader(f"Client: {client_names[selected_client_idx]}")
    st.subheader(f"Assessment: {assessment_names[selected_assessment_idx]}")
    
    # Calculate gap for each row (gap is 0 when actual >= desired)
    df['gap'] = df.apply(lambda row: max(0, row['desired_score'] - row['actual_score']), axis=1)
    
    # Calculate overall scores
    total_actual = df['actual_score'].sum()
    total_desired = df['desired_score'].sum()
    total_gap = df['gap'].sum()
    
    # Display overall scores
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Actual Score", total_actual)
    col2.metric("Total Required Score", total_desired)
    col3.metric("Overall Gap", total_gap)
    
    # Analysis by category
    st.header("Category Analysis")
    
    # Group by category and calculate metrics
    category_df = df.groupby('category').agg({
        'actual_score': 'sum',
        'desired_score': 'sum',
        'gap': 'sum'
    }).reset_index()
    
    # Calculate gap percentage correctly (sum of gaps / sum of desired)
    category_df['gap_percentage'] = (category_df['gap'] / category_df['desired_score'] * 100).round(1)
    
    # Sort by gap (largest first)
    category_df = category_df.sort_values('gap', ascending=False)
    
    # Display category metrics
    st.dataframe(category_df)
    
    # Bar chart of actual vs. desired by category
    st.subheader("Actual vs. Required Scores by Category")
    
    # Prepare data for bar chart
    chart_data = pd.melt(
        category_df,
        id_vars=['category'],
        value_vars=['actual_score', 'desired_score'],
        var_name='Score Type',
        value_name='Score'
    )
    
    # Rename the score types for better display
    chart_data['Score Type'] = chart_data['Score Type'].map({
        'actual_score': 'Actual',
        'desired_score': 'Required'
    })
    
    # Create a bar chart with Plotly
    fig = px.bar(
        chart_data,
        x='category',
        y='Score',
        color='Score Type',
        barmode='group',
        title='Actual vs. Required Scores by Category',
        labels={'category': 'Category', 'Score': 'Score'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gap analysis chart
    st.subheader("Score Gaps by Category")
    
    # Create a bar chart for gaps
    gap_fig = px.bar(
        category_df,
        x='category',
        y='gap',
        color='gap',
        title='Score Gaps by Category',
        labels={'category': 'Category', 'gap': 'Gap (Required - Actual)'},
        color_continuous_scale='RdYlGn_r'  # Red for large gaps, green for small gaps
    )
    
    st.plotly_chart(gap_fig, use_container_width=True)
    
    # Detailed question analysis
    st.header("Detailed Question Analysis")
    
    # Option to show only gaps (questions where desired > actual)
    show_only_gaps = st.checkbox("Show only gaps (questions where Required > Actual)", value=True)
    
    # Select a category to view detailed questions
    selected_category = st.selectbox(
        "Select Category for Detailed Analysis:",
        category_df['category'].tolist()
    )
    
    # Filter questions by selected category
    category_questions = df[df['category'] == selected_category]
    
    # Filter to show only gaps if checkbox is checked
    if show_only_gaps:
        category_questions = category_questions[category_questions['gap'] > 0]
    
    # Sort by gap (largest first)
    category_questions = category_questions.sort_values('gap', ascending=False)
    
    # Display questions and their scores
    for _, row in category_questions.iterrows():
        question = row['question']
        actual = row['actual_score']
        desired = row['desired_score']
        gap = row['gap']
        
        # Create an expander for each question
        with st.expander(f"{question} (Gap: {gap})"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Actual", actual)
            col2.metric("Required", desired)
            col3.metric("Gap", gap)
            
            st.write("**Actual Answer:**", row['actual_answer'])
            st.write("**Required Answer:**", row['desired_answer'])
    
    # Export results option
    st.header("Export Results")
    
    if st.button("Export to CSV"):
        # Convert the results DataFrame to CSV
        csv = df.to_csv(index=False).encode('utf-8')
        
        # Create a download button
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"assessment_{assessment_id}_results.csv",
            mime="text/csv"
        )
