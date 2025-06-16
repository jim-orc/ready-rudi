import pandas as pd
import streamlit as st

from app.db import (
    add_answer,
    add_question,
    delete_answer,
    delete_question,
    fetch_all_questions,
    fetch_answers_by_question,
    fetch_categories,
    update_answer,
    update_question,
)


def admin_view():
    """Admin panel for managing questions, answers, and scores."""
    st.title("Admin Panel")
    
    # Tabs for different admin functions
    tab1, tab2 = st.tabs(["Manage Questions", "Manage Answers"])
    
    with tab1:
        manage_questions()
    
    with tab2:
        manage_answers()

def manage_questions():
    """Interface for managing questions."""
    st.header("Manage Questions")
    
    # Create a new question
    with st.expander("Add New Question", expanded=False):
        with st.form("add_question_form"):
            # Get existing categories for dropdown
            categories = fetch_categories()
            
            # Form fields
            new_category = st.text_input("Category")
            category_select = st.selectbox(
                "Or select existing category:",
                [""] + categories,
                index=0
            )
            selected_category = new_category if new_category else category_select
            
            qtype = st.selectbox(
                "Question Type:",
                ["org", "action"],
                format_func=lambda x: "Organization" if x == "org" else "Action"
            )
            
            csequence = st.number_input("Category Sequence", min_value=0, value=0, step=1)
            qsequence = st.number_input("Question Sequence", min_value=0, value=0, step=1)
            question_text = st.text_area("Question")
            
            submit_button = st.form_submit_button("Add Question")
            
            if submit_button and selected_category and question_text:
                question_id = add_question(selected_category, qtype, qsequence, csequence, question_text)
                st.success(f"Question added successfully with ID: {question_id}")
                st.rerun()
    
    # List and edit existing questions
    st.subheader("Existing Questions")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_type = st.selectbox(
            "Filter by Type:",
            ["All", "org", "action"],
            format_func=lambda x: "All" if x == "All" else ("Organization" if x == "org" else "Action")
        )
    
    with col2:
        # Get categories for filter
        categories = fetch_categories()
        filter_category = st.selectbox("Filter by Category:", ["All"] + categories)
    
    # Get all questions
    questions = fetch_all_questions()
    
    # Apply filters
    filtered_questions = []
    for q in questions:
        if (filter_type == "All" or q['qtype'] == filter_type) and \
           (filter_category == "All" or q['category'] == filter_category):
            filtered_questions.append(q)
    
    # Convert to DataFrame for display
    if filtered_questions:
        df = pd.DataFrame([dict(q) for q in filtered_questions])
        df = df.rename(columns={
            'id': 'ID',
            'csequence': 'Cat Seq',
            'category': 'Category',
            'qtype': 'Type',
            'qsequence': 'Q Seq',
            'question': 'Question'
        })
        
        # Format the Type column
        df['Type'] = df['Type'].apply(lambda x: "Organization" if x == "org" else "Action")
        
        st.dataframe(df)
        
        # Question selection for editing/deleting
        question_ids = [q['id'] for q in filtered_questions]
        selected_q_idx = st.selectbox(
            "Select Question to Edit/Delete:",
            range(len(filtered_questions)),
            format_func=lambda i: f"ID {filtered_questions[i]['id']}: {filtered_questions[i]['question'][:50]}..."
        )
        
        selected_question = filtered_questions[selected_q_idx]
        
        # Edit or delete the selected question
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Edit Selected Question"):
                st.session_state['editing_question'] = selected_question
        
        with col2:
            if st.button("Delete Selected Question"):
                if st.session_state.get('confirm_delete') == selected_question['id']:
                    delete_question(selected_question['id'])
                    st.success(f"Question ID {selected_question['id']} deleted successfully!")
                    # Clear the session state
                    if 'confirm_delete' in st.session_state:
                        del st.session_state['confirm_delete']
                    st.rerun()
                else:
                    st.session_state['confirm_delete'] = selected_question['id']
                    st.warning(f"Click 'Delete Selected Question' again to confirm deletion of question ID {selected_question['id']}.")
        
        # Edit question form
        if st.session_state.get('editing_question'):
            q = st.session_state['editing_question']
            st.subheader(f"Edit Question ID: {q['id']}")
            
            with st.form("edit_question_form"):
                # Get existing categories for dropdown
                categories = fetch_categories()
                
                # Pre-fill form with existing values
                new_category = st.text_input("New Category")
                category_idx = categories.index(q['category']) if q['category'] in categories else 0
                category_select = st.selectbox(
                    "Or select existing category:",
                    [""] + categories,
                    index=category_idx + 1  # +1 because we added an empty option at index 0
                )
                selected_category = new_category if new_category else category_select
                
                qtype = st.selectbox(
                    "Question Type:",
                    ["org", "action"],
                    index=0 if q['qtype'] == "org" else 1,
                    format_func=lambda x: "Organization" if x == "org" else "Action"
                )
                
                csequence = st.number_input("Category Sequence", min_value=0, value=q['csequence'], step=1)
                qsequence = st.number_input("Question Sequence", min_value=0, value=q['qsequence'], step=1)
                question_text = st.text_area("Question", value=q['question'])
                
                update_button = st.form_submit_button("Update Question")
                
                if update_button and selected_category and question_text:
                    update_question(q['id'], selected_category, qtype, qsequence, csequence, question_text)
                    st.success(f"Question ID {q['id']} updated successfully!")
                    # Clear the editing state
                    if 'editing_question' in st.session_state:
                        del st.session_state['editing_question']
                    st.rerun()
    else:
        st.info("No questions found matching the selected filters.")

def manage_answers():
    """Interface for managing answers."""
    st.header("Manage Answers")
    
    # First, let the user select a question
    questions = fetch_all_questions()
    
    if not questions:
        st.warning("No questions found. Please add questions first.")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_type = st.selectbox(
            "Filter by Type:",
            ["All", "org", "action"],
            format_func=lambda x: "All" if x == "All" else ("Organization" if x == "org" else "Action"),
            key="answer_filter_type"
        )
    
    with col2:
        # Get categories for filter
        categories = fetch_categories()
        filter_category = st.selectbox("Filter by Category:", ["All"] + categories, key="answer_filter_category")
    
    # Apply filters to questions
    filtered_questions = []
    for q in questions:
        if (filter_type == "All" or q['qtype'] == filter_type) and \
           (filter_category == "All" or q['category'] == filter_category):
            filtered_questions.append(q)
    
    if not filtered_questions:
        st.info("No questions found matching the selected filters.")
        return
    
    # Question selection
    selected_q_idx = st.selectbox(
        "Select Question:",
        range(len(filtered_questions)),
        format_func=lambda i: f"{filtered_questions[i]['category']} - {filtered_questions[i]['question'][:50]}...",
        key="answer_question_selector"
    )
    
    selected_question = filtered_questions[selected_q_idx]
    question_id = selected_question['id']
    
    st.subheader(f"Answers for: {selected_question['question']}")
    
    # Add new answer
    with st.expander("Add New Answer", expanded=False):
        with st.form("add_answer_form"):
            answer_text = st.text_area("Answer")
            score = st.number_input("Score", value=0, step=1)
            
            submit_button = st.form_submit_button("Add Answer")
            
            if submit_button and answer_text:
                answer_id = add_answer(question_id, score, answer_text)
                st.success(f"Answer added successfully with ID: {answer_id}")
                st.rerun()
    
    # List existing answers
    answers = fetch_answers_by_question(question_id)
    
    if answers:
        # Convert to DataFrame for display
        df = pd.DataFrame([dict(a) for a in answers])
        df = df.rename(columns={
            'id': 'ID',
            'question_id': 'Question ID',
            'score': 'Score',
            'answer': 'Answer'
        })
        
        st.dataframe(df)
        
        # Answer selection for editing/deleting
        answer_ids = [a['id'] for a in answers]
        selected_a_idx = st.selectbox(
            "Select Answer to Edit/Delete:",
            range(len(answers)),
            format_func=lambda i: f"ID {answers[i]['id']}: {answers[i]['answer'][:50]}..."
        )
        
        selected_answer = answers[selected_a_idx]
        
        # Edit or delete the selected answer
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Edit Selected Answer"):
                st.session_state['editing_answer'] = selected_answer
        
        with col2:
            if st.button("Delete Selected Answer"):
                if st.session_state.get('confirm_delete_answer') == selected_answer['id']:
                    delete_answer(selected_answer['id'])
                    st.success(f"Answer ID {selected_answer['id']} deleted successfully!")
                    # Clear the session state
                    if 'confirm_delete_answer' in st.session_state:
                        del st.session_state['confirm_delete_answer']
                    st.rerun()
                else:
                    st.session_state['confirm_delete_answer'] = selected_answer['id']
                    st.warning(f"Click 'Delete Selected Answer' again to confirm deletion of answer ID {selected_answer['id']}.")
        
        # Edit answer form
        if st.session_state.get('editing_answer'):
            a = st.session_state['editing_answer']
            st.subheader(f"Edit Answer ID: {a['id']}")
            
            with st.form("edit_answer_form"):
                # Pre-fill form with existing values
                answer_text = st.text_area("Answer", value=a['answer'])
                score = st.number_input("Score", value=a['score'], step=1)
                
                update_button = st.form_submit_button("Update Answer")
                
                if update_button and answer_text:
                    update_answer(a['id'], score, answer_text)
                    st.success(f"Answer ID {a['id']} updated successfully!")
                    # Clear the editing state
                    if 'editing_answer' in st.session_state:
                        del st.session_state['editing_answer']
                    st.rerun()
    else:
        st.info(f"No answers found for this question. Please add answers.")
