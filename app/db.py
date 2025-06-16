import sqlite3
from pathlib import Path

# Path to the database file
DB_PATH = Path(__file__).parents[1] / "data.db"

def get_db_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_all_clients():
    """Fetch all clients from the database."""
    conn = get_db_connection()
    clients = conn.execute("SELECT id, name FROM clients").fetchall()
    conn.close()
    return clients

def fetch_client_by_id(client_id):
    """Fetch a client by ID."""
    conn = get_db_connection()
    client = conn.execute("SELECT id, name FROM clients WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    return client

def add_client(name):
    """Add a new client to the database."""
    conn = get_db_connection()
    cursor = conn.execute("INSERT INTO clients (name) VALUES (?)", (name,))
    client_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return client_id

def fetch_questions_by_type(qtype):
    """Fetch questions by type (org or action)."""
    conn = get_db_connection()
    questions = conn.execute("""
        SELECT id, csequence, category, qtype, qsequence, question
        FROM questions 
        WHERE qtype = ?
        ORDER BY csequence, qsequence
    """, (qtype,)).fetchall()
    conn.close()
    return questions

def fetch_answers_by_question(question_id):
    """Fetch answers for a specific question."""
    conn = get_db_connection()
    answers = conn.execute("""
        SELECT id, question_id, score, answer
        FROM answers
        WHERE question_id = ?
        ORDER BY score
    """, (question_id,)).fetchall()
    conn.close()
    return answers

def create_assessment(client_id, qtype, name):
    """Create a new assessment."""
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO assessments (client_id, qtype, name) VALUES (?, ?, ?)",
        (client_id, qtype, name)
    )
    assessment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return assessment_id

def save_choice(assessment_id, answer_id_desired, answer_id_actual):
    """Save a choice for an assessment."""
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO choices (assessment_id, answer_id_desired, answer_id_actual) VALUES (?, ?, ?)",
        (assessment_id, answer_id_desired, answer_id_actual)
    )
    conn.commit()
    conn.close()

def fetch_assessments(client_id=None):
    """Fetch assessments, optionally filtered by client_id."""
    conn = get_db_connection()
    if client_id:
        assessments = conn.execute("""
            SELECT a.id, a.qtype, a.name, c.name as client_name
            FROM assessments a
            JOIN clients c ON a.client_id = c.id
            WHERE a.client_id = ?
        """, (client_id,)).fetchall()
    else:
        assessments = conn.execute("""
            SELECT a.id, a.qtype, a.name, c.name as client_name
            FROM assessments a
            JOIN clients c ON a.client_id = c.id
        """).fetchall()
    conn.close()
    return assessments

def fetch_assessment_results(assessment_id):
    """Fetch results for a specific assessment."""
    conn = get_db_connection()
    results = conn.execute("""
        SELECT 
            q.category, q.question, 
            a_actual.answer as actual_answer, a_actual.score as actual_score,
            a_desired.answer as desired_answer, a_desired.score as desired_score
        FROM choices c
        JOIN answers a_actual ON c.answer_id_actual = a_actual.id
        JOIN answers a_desired ON c.answer_id_desired = a_desired.id
        JOIN questions q ON a_actual.question_id = q.id
        WHERE c.assessment_id = ?
        ORDER BY q.csequence, q.qsequence
    """, (assessment_id,)).fetchall()
    conn.close()
    return results

# Admin functions
def add_question(category, qtype, qsequence, csequence, question):
    """Add a new question."""
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO questions (category, qtype, qsequence, csequence, question) VALUES (?, ?, ?, ?, ?)",
        (category, qtype, qsequence, csequence, question)
    )
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return question_id

def update_question(question_id, category, qtype, qsequence, csequence, question):
    """Update an existing question."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE questions SET category=?, qtype=?, qsequence=?, csequence=?, question=? WHERE id=?",
        (category, qtype, qsequence, csequence, question, question_id)
    )
    conn.commit()
    conn.close()

def delete_question(question_id):
    """Delete a question and its associated answers."""
    conn = get_db_connection()
    # First delete associated answers
    conn.execute("DELETE FROM answers WHERE question_id=?", (question_id,))
    # Then delete the question
    conn.execute("DELETE FROM questions WHERE id=?", (question_id,))
    conn.commit()
    conn.close()

def add_answer(question_id, score, answer):
    """Add a new answer."""
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO answers (question_id, score, answer) VALUES (?, ?, ?)",
        (question_id, score, answer)
    )
    answer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return answer_id

def update_answer(answer_id, score, answer):
    """Update an existing answer."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE answers SET score=?, answer=? WHERE id=?",
        (score, answer, answer_id)
    )
    conn.commit()
    conn.close()

def delete_answer(answer_id):
    """Delete an answer."""
    conn = get_db_connection()
    conn.execute("DELETE FROM answers WHERE id=?", (answer_id,))
    conn.commit()
    conn.close()

def fetch_categories():
    """Fetch all unique categories."""
    conn = get_db_connection()
    categories = conn.execute("SELECT DISTINCT category FROM questions ORDER BY category").fetchall()
    conn.close()
    return [cat['category'] for cat in categories]

def fetch_all_questions():
    """Fetch all questions with their type and category."""
    conn = get_db_connection()
    questions = conn.execute("""
        SELECT id, csequence, category, qtype, qsequence, question
        FROM questions
        ORDER BY qtype, category, csequence, qsequence
    """).fetchall()
    conn.close()
    return questions

def delete_assessment(assessment_id):
    """Delete an assessment and its associated choices."""
    conn = get_db_connection()
    # First delete associated choices
    conn.execute("DELETE FROM choices WHERE assessment_id=?", (assessment_id,))
    # Then delete the assessment
    conn.execute("DELETE FROM assessments WHERE id=?", (assessment_id,))
    conn.commit()
    conn.close()

def fetch_assessment_by_id(assessment_id):
    """Fetch assessment details by ID."""
    conn = get_db_connection()
    assessment = conn.execute("""
        SELECT a.id, a.qtype, a.name, a.client_id, c.name as client_name
        FROM assessments a
        JOIN clients c ON a.client_id = c.id
        WHERE a.id = ?
    """, (assessment_id,)).fetchone()
    conn.close()
    return assessment

def fetch_choices_by_assessment(assessment_id):
    """Fetch choices for a specific assessment."""
    conn = get_db_connection()
    choices = conn.execute("""
        SELECT 
            c.id, c.assessment_id, c.answer_id_desired, c.answer_id_actual,
            a_actual.question_id,
            a_actual.score as actual_score, a_desired.score as desired_score
        FROM choices c
        JOIN answers a_actual ON c.answer_id_actual = a_actual.id
        JOIN answers a_desired ON c.answer_id_desired = a_desired.id
        WHERE c.assessment_id = ?
    """, (assessment_id,)).fetchall()
    conn.close()
    return choices
