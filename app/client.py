import streamlit as st

from app.db import (
    add_client,
    create_assessment,
    delete_assessment,
    fetch_all_clients,
    fetch_answers_by_question,
    fetch_assessments,
    fetch_choices_by_assessment,
    fetch_questions_by_type,
    save_choice,
)


def client_view():
    """Client view for creating and completing assessments."""
    st.title("Client Assessment")
    
    # Step 1: Client Selection or Creation
    with st.container():
        st.header("Step 1: Select or Create Client")
        
        # Get all clients
        clients = fetch_all_clients()
        client_names = [client['name'] for client in clients]
        client_ids = [client['id'] for client in clients]
        
        # Radio button to select existing client or create new one
        client_option = st.radio(
            "Choose an option:",
            ["Select Existing Client", "Create New Client"],
            index=0 if clients else 1
        )
        
        client_id = None
        
        if client_option == "Select Existing Client" and clients:
            # Display a selectbox with client names
            selected_index = st.selectbox(
                "Select Client:", 
                range(len(client_names)),
                format_func=lambda i: client_names[i]
            )
            client_id = client_ids[selected_index]
            st.session_state['client_id'] = client_id
            st.session_state['client_name'] = client_names[selected_index]
            
        elif client_option == "Create New Client" or not clients:
            # Form to create a new client
            with st.form("new_client_form"):
                new_client_name = st.text_input("Client Name:")
                submit_button = st.form_submit_button("Create Client")
                
                if submit_button and new_client_name:
                    client_id = add_client(new_client_name)
                    st.session_state['client_id'] = client_id
                    st.session_state['client_name'] = new_client_name
                    st.success(f"Client '{new_client_name}' created successfully!")
                    st.rerun()  # Refresh the page to update client list
    
    # Only proceed if a client is selected or created
    if 'client_id' in st.session_state:
        client_id = st.session_state['client_id']
        client_name = st.session_state['client_name']
        
        # Step 2: Assessment Creation or Selection
        st.header(f"Step 2: Create Assessment for {client_name}")
        
        # Show existing assessments for this client
        existing_assessments = fetch_assessments(client_id)
        if existing_assessments:
            st.subheader("Existing Assessments")
            
            for assessment in existing_assessments:
                cols = st.columns([4, 1])
                
                # Make the assessment name clickable
                if cols[0].button(f"{assessment['name']} ({assessment['qtype']} type)", key=f"select_{assessment['id']}"):
                    st.session_state['assessment_id'] = assessment['id']
                    st.session_state['assessment_name'] = assessment['name']
                    st.session_state['assessment_type'] = assessment['qtype']
                    st.rerun()
                
                # Delete button
                if cols[1].button("Delete", key=f"delete_{assessment['id']}"):
                    if st.session_state.get('confirm_delete_assessment') == assessment['id']:
                        delete_assessment(assessment['id'])
                        st.success(f"Assessment '{assessment['name']}' deleted successfully!")
                        # Clear the confirmation state
                        if 'confirm_delete_assessment' in st.session_state:
                            del st.session_state['confirm_delete_assessment']
                        # Also clear assessment state if the deleted assessment was selected
                        if st.session_state.get('assessment_id') == assessment['id']:
                            for key in ['assessment_id', 'assessment_name', 'assessment_type', 'progress']:
                                if key in st.session_state:
                                    del st.session_state[key]
                        st.rerun()
                    else:
                        st.session_state['confirm_delete_assessment'] = assessment['id']
                        st.warning(f"Click 'Delete' again to confirm deletion of assessment '{assessment['name']}'.")
        
        # Form to create a new assessment
        with st.form("new_assessment_form"):
            assessment_name = st.text_input("Assessment Name:")
            assessment_type = st.selectbox(
                "Assessment Type:",
                ["org", "action"],
                format_func=lambda x: "Organization" if x == "org" else "Action"
            )
            
            submit_assessment = st.form_submit_button("Create Assessment")
            
            if submit_assessment and assessment_name:
                assessment_id = create_assessment(client_id, assessment_type, assessment_name)
                st.session_state['assessment_id'] = assessment_id
                st.session_state['assessment_name'] = assessment_name
                st.session_state['assessment_type'] = assessment_type
                st.success(f"Assessment '{assessment_name}' created successfully!")
                st.rerun()
        
        # Step 3: Answer Questions
        if 'assessment_id' in st.session_state:
            assessment_id = st.session_state['assessment_id']
            assessment_name = st.session_state['assessment_name']
            assessment_type = st.session_state['assessment_type']
            
            st.header(f"Step 3: Complete Assessment - {assessment_name}")
            
            # Fetch questions for this assessment type
            questions = fetch_questions_by_type(assessment_type)
            
            if not questions:
                st.warning(f"No questions found for {assessment_type} assessment type. Please add questions in the Admin Panel.")
            else:
                # Group questions by category
                categories = {}
                for q in questions:
                    cat = q['category']
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(q)
                
                # Initialize progress tracking if not already in session state
                if 'progress' not in st.session_state:
                    st.session_state['progress'] = {
                        'current_category_index': 0,
                        'completed_questions': set()
                    }
                
                # Get the current category
                category_names = list(categories.keys())
                current_cat_idx = st.session_state['progress']['current_category_index']
                
                # Navigation buttons for categories
                col1, col2 = st.columns([1, 1])
                if current_cat_idx > 0:
                    if col1.button("Previous Category"):
                        st.session_state['progress']['current_category_index'] -= 1
                        st.rerun()
                
                if current_cat_idx < len(category_names) - 1:
                    if col2.button("Next Category"):
                        st.session_state['progress']['current_category_index'] += 1
                        st.rerun()
                
                # Display current category
                current_category = category_names[current_cat_idx] if category_names else "Strategy & Leadership"
                st.subheader(f"Category: {current_category}")
                
                # Fetch existing choices if this is an existing assessment
                existing_choices = {}
                if 'assessment_id' in st.session_state:
                    choices = fetch_choices_by_assessment(st.session_state['assessment_id'])
                    for choice in choices:
                        question_id = choice['question_id']
                        existing_choices[question_id] = {
                            'actual': choice['answer_id_actual'],
                            'desired': choice['answer_id_desired']
                        }
                
                # Process questions for the current category
                with st.form(f"category_{current_cat_idx}_form"):
                    for i, question in enumerate(categories[current_category]):
                        question_id = question['id']
                        
                        # Add spacing between questions (except the first one)
                        if i > 0:
                            st.write("")  # Empty line for spacing
                        
                        # Display the question without qtype
                        st.write(f"**Q{question['qsequence']}**: {question['question']}")
                        
                        # Get answers for this question
                        answers = fetch_answers_by_question(question_id)
                        if not answers:
                            st.warning(f"No answers found for question ID {question_id}.")
                            continue
                        
                        answer_ids = [a['id'] for a in answers]
                        
                        # Get index of existing answers if they exist
                        actual_default_idx = 0
                        desired_default_idx = 0
                        
                        if question_id in existing_choices:
                            actual_id = existing_choices[question_id]['actual']
                            desired_id = existing_choices[question_id]['desired']
                            
                            if actual_id in answer_ids:
                                actual_default_idx = answer_ids.index(actual_id)
                            if desired_id in answer_ids:
                                desired_default_idx = answer_ids.index(desired_id)
                        
                        # Create container for answers with smaller vertical spacing
                        answer_container = st.container()
                        
                        with answer_container:
                            # Compact two-column layout: one radio group for 'actual', one for 'required', both horizontal
                            answer_labels = [f"{a['answer']} ({a['score']})" for a in answers]
                            cols = st.columns([1, 1])
                            with cols[0]:
                                actual_idx = st.radio(
                                    label="Actual",
                                    options=range(len(answers)),
                                    index=actual_default_idx,
                                    key=f"actual_radio_{question_id}",
                                    horizontal=True,
                                    format_func=lambda x: answer_labels[x]
                                )
                            with cols[1]:
                                required_idx = st.radio(
                                    label="Required",
                                    options=range(len(answers)),
                                    index=desired_default_idx,
                                    key=f"required_radio_{question_id}",
                                    horizontal=True,
                                    format_func=lambda x: answer_labels[x]
                                )
                            st.session_state[f"q_{question_id}_actual_idx"] = actual_idx
                            st.session_state[f"q_{question_id}_desired_idx"] = required_idx
                        
                        # Get the current actual_idx and desired_idx values from session state
                        actual_idx = st.session_state.get(f"q_{question_id}_actual_idx", actual_default_idx)
                        desired_idx = st.session_state.get(f"q_{question_id}_desired_idx", desired_default_idx)
                        
                        # Store the selected answer IDs
                        st.session_state[f"q_{question_id}_actual"] = answer_ids[actual_idx]
                        st.session_state[f"q_{question_id}_desired"] = answer_ids[desired_idx]
                    
                    # Submit button for this category
                    submit_category = st.form_submit_button("Save Answers")
                    
                    if submit_category:
                        # Save all answers for questions in this category
                        for question in categories[current_category]:
                            question_id = question['id']
                            actual_answer_id = st.session_state.get(f"q_{question_id}_actual")
                            desired_answer_id = st.session_state.get(f"q_{question_id}_desired")
                            
                            if actual_answer_id and desired_answer_id:
                                save_choice(assessment_id, question_id, desired_answer_id, actual_answer_id)
                                st.session_state['progress']['completed_questions'].add(question_id)
                        
                        st.success(f"Answers for {current_category} saved successfully!")
                        
                        # Auto-advance to next category if not the last one
                        if current_cat_idx < len(category_names) - 1:
                            st.session_state['progress']['current_category_index'] += 1
                            st.rerun()
                
                # Show progress
                total_questions = sum(len(qs) for qs in categories.values())
                completed = len(st.session_state['progress']['completed_questions'])
                st.progress(completed / total_questions)
                st.write(f"Progress: {completed}/{total_questions} questions completed")
                
                # Complete assessment button (only show if some progress has been made)
                if completed > 0:
                    if st.button("Complete Assessment"):
                        # Clear session state related to the assessment
                        for key in ['assessment_id', 'assessment_name', 'assessment_type', 'progress']:
                            if key in st.session_state:
                                del st.session_state[key]
                        
                        st.success("Assessment completed successfully! You can view the results in the Results Dashboard.")
                        st.rerun()
