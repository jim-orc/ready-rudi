import sqlite3


def init_database():
    """Initialize the database with schema and sample data if it doesn't exist."""
    # Check if tables already exist
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    # Create tables if they don't exist
    if 'clients' not in tables:
        print("Creating clients table...")
        cursor.execute('''
        CREATE TABLE `clients` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, 
            `name` TEXT NOT NULL
        )
        ''')
    
    if 'questions' not in tables:
        print("Creating questions table...")
        cursor.execute('''
        CREATE TABLE "questions" (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, 
            `csequence` INTEGER NOT NULL DEFAULT 0, 
            `category` TEXT NOT NULL DEFAULT 'General', 
            `qtype` TEXT NOT NULL DEFAULT 'org', 
            `qsequence` INTEGER NOT NULL DEFAULT 0, 
            `question` TEXT NOT NULL
        )
        ''')
    
    if 'answers' not in tables:
        print("Creating answers table...")
        cursor.execute('''
        CREATE TABLE `answers` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT, 
            `question_id` INTEGER REFERENCES `questions`(`id`), 
            `score` INTEGER, 
            `answer` TEXT
        )
        ''')
    
    if 'assessments' not in tables:
        print("Creating assessments table...")
        cursor.execute('''
        CREATE TABLE `assessments` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT, 
            `client_id` INTEGER REFERENCES `clients`(`id`), 
            `qtype` TEXT DEFAULT 'org', 
            `name` TEXT NOT NULL
        )
        ''')
    
    if 'choices' not in tables:
        print("Creating choices table...")
        cursor.execute('''
        CREATE TABLE "choices" (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT, 
            `assessment_id` INTEGER REFERENCES `assessments`(`id`),
            `answer_id_desired` INTEGER REFERENCES `answers`(`id`), 
            `answer_id_actual` INTEGER REFERENCES `answers`(`id`)
        )
        ''')
    
    # Add sample data if the database is empty
    cursor.execute("SELECT COUNT(*) FROM clients")
    client_count = cursor.fetchone()[0]
    
    if client_count == 0:
        print("Adding sample data...")
        
        # Add sample clients
        cursor.execute("INSERT INTO clients (name) VALUES ('Sample Organization')")
        cursor.execute("INSERT INTO clients (name) VALUES ('Test Company')")
        
        # Add sample questions for org type
        org_questions = [
            (1, 'Leadership', 'org', 1, 'How would you rate the organization\'s leadership clarity?'),
            (1, 'Leadership', 'org', 2, 'How effective is the decision-making process?'),
            (2, 'Strategy', 'org', 1, 'Does the organization have a clear strategic direction?'),
            (2, 'Strategy', 'org', 2, 'How well is the strategy communicated throughout the organization?'),
            (3, 'Operations', 'org', 1, 'How efficient are the organization\'s operational processes?'),
            (3, 'Operations', 'org', 2, 'Are there documented procedures for key operations?')
        ]
        
        for q in org_questions:
            cursor.execute(
                "INSERT INTO questions (csequence, category, qtype, qsequence, question) VALUES (?, ?, ?, ?, ?)",
                q
            )
            question_id = cursor.lastrowid
            
            # Add sample answers for each question
            answers = [
                (question_id, 1, 'Poor - Significant improvement needed'),
                (question_id, 2, 'Fair - Some elements in place but gaps exist'),
                (question_id, 3, 'Good - Most elements in place, minor improvements needed'),
                (question_id, 4, 'Excellent - Fully developed and effective')
            ]
            
            for a in answers:
                cursor.execute(
                    "INSERT INTO answers (question_id, score, answer) VALUES (?, ?, ?)",
                    a
                )
        
        # Add sample questions for action type
        action_questions = [
            (1, 'Risk', 'action', 1, 'What is the level of risk associated with this action?'),
            (1, 'Risk', 'action', 2, 'Are there mitigation strategies in place?'),
            (2, 'Resources', 'action', 1, 'Are adequate resources available for this action?'),
            (2, 'Resources', 'action', 2, 'Is there a clear resource allocation plan?'),
            (3, 'Timeline', 'action', 1, 'Is the timeline realistic for implementation?'),
            (3, 'Timeline', 'action', 2, 'Are there clear milestones and checkpoints?')
        ]
        
        for q in action_questions:
            cursor.execute(
                "INSERT INTO questions (csequence, category, qtype, qsequence, question) VALUES (?, ?, ?, ?, ?)",
                q
            )
            question_id = cursor.lastrowid
            
            # Add sample answers for each question
            answers = [
                (question_id, 1, 'Not addressed - Major concerns'),
                (question_id, 2, 'Partially addressed - Some concerns remain'),
                (question_id, 3, 'Mostly addressed - Minor concerns'),
                (question_id, 4, 'Fully addressed - No concerns')
            ]
            
            for a in answers:
                cursor.execute(
                    "INSERT INTO answers (question_id, score, answer) VALUES (?, ?, ?)",
                    a
                )
    
    conn.commit()
    conn.close()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_database()
