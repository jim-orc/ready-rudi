# Ready Rudi Assessment Tool

A Streamlit application for conducting and analyzing assessments across various organizations and actions.

## Features

1. **Client Assessment Flow**
   - Create and manage clients
   - Create assessments with different types (organization or action)
   - Answer questions with both "actual" and "required" responses
   - Track progress through different question categories

2. **Admin Panel**
   - Manage questions (add, edit, delete)
   - Manage answers and their scores (add, edit, delete)
   - Filter and organize questions by type and category

3. **Results Dashboard**
   - View assessment results with gap analysis
   - Visualize scores by category
   - Export results to CSV

## Database Structure

The application uses a SQLite database with the following tables:
- `clients`: Stores client information
- `questions`: Stores assessment questions with categories and sequencing
- `answers`: Stores possible answers with their scores
- `assessments`: Tracks assessment instances
- `choices`: Records user selections for each assessment

## Installation

1. Ensure you have Python 3.12 or higher installed
2. Install dependencies:
   ```
   pip install -e .
   ```

## Running the Application

To start the Streamlit application, run:

```
streamlit run streamlit_app.py
```

## Usage Guide

### Client Assessment

1. Select or create a client
2. Create a new assessment (organization or action type)
3. Answer questions by selecting both actual and required answers
4. Navigate through categories and submit answers
5. Complete the assessment to view results

### Admin Panel

1. Add or edit questions, organized by category and type
2. Add or edit answers with associated scores
3. Filter and organize questions for easier management

### Results Dashboard

1. Select a client and assessment
2. View overall scores and gaps
3. Analyze results by category
4. Explore detailed question analysis
5. Export results for further analysis