## team name ; coder (developer,ahmed ariba)



# name (HAFIZ MUHAMMAD AHMED RAZA , ARIBA SIDDIQUE) 
# Professional Student Attendance & Performance System

A modern, beautiful attendance management system built with Flask, SQLite, and a glassmorphic UI design.


## Project Description

EduTrack AI is a modern Student Attendance & Performance Management System designed for educational institutions.

The platform enables teachers to manage classes, students, and attendance records through an intuitive glassmorphic dashboard. Students can securely log in to view attendance records, enrolled classes, and overall attendance statistics.


## Features

### For Teachers (Admin)
- **User Registration & Authentication**: Secure teacher registration and login
- **Class Management**: Create, view, and delete classes with descriptions
- **Student Management**: Create student accounts with login credentials
- **Student Enrollment**: Assign students to classes
- **Attendance Marking**: Mark attendance (Present/Absent/Late) for any date
- **Reports**: View detailed attendance reports with statistics and progress bars

### For Students
- **Secure Login**: Students can log in with credentials provided by their teacher
- **Dashboard**: Overview of overall attendance statistics
- **Class View**: See all enrolled classes
- **Attendance History**: View detailed attendance records for each class

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Custom glassmorphic dark theme with modern UI

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Access the application**:
   Open your browser and go to `http://localhost:5000`

## Usage

### Getting Started

1. **Register as a Teacher**: Click "Register as Teacher" on the homepage
2. **Create Classes**: Go to Classes → Create Class
3. **Add Students**: Go to Students → Add Student (creates login credentials)
4. **Enroll Students**: Go to each class and add students from the dropdown
5. **Mark Attendance**: Go to Attendance → Select a class → Mark attendance

### Student Login

Students can log in using the credentials you created for them to:
- View their enrolled classes
- Check their attendance records
- See their overall attendance percentage

## Project Structure

```
attendance_system/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── instance/
│   └── attendance.db       # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css       # Main stylesheet
│   └── js/
│       └── main.js         # Frontend JavaScript
└── templates/
    ├── base.html           # Base template with navigation
    ├── index.html          # Landing page
    ├── login.html          # Login page
    ├── register.html       # Teacher registration
    ├── teacher/            # Teacher templates
    │   ├── dashboard.html
    │   ├── classes.html
    │   ├── create_class.html
    │   ├── view_class.html
    │   ├── students.html
    │   ├── create_student.html
    │   ├── attendance.html
    │   ├── mark_attendance.html
    │   ├── reports.html
    │   └── class_report.html
    └── student/            # Student templates
        ├── dashboard.html
        ├── classes.html
        └── attendance.html
```

## Database Models

- **Teacher**: Admin users who manage classes and students
- **Class**: Courses with name, subject, and description
- **Student**: Users with login credentials, created by teachers
- **Attendance**: Records linking students, classes, dates, and status

## Screenshots

The UI features:
- Dark glassmorphic design with gradient accents
- Responsive layout for all screen sizes
- Beautiful stat cards and progress indicators
- Color-coded attendance status (green/yellow/red)
- Smooth animations and hover effects

