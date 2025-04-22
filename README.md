# 🏥 Patient Triage Automation System

This project implements an intelligent, automated solution for managing patient triage and appointment scheduling in a healthcare setting. It combines conversational AI, rule-based triage logic, and robotic process automation (RPA) to streamline intake and booking workflows.

---

## About the Project
This project was developed as part of the Master of Science in Artificial Intelligence program at National College of Ireland. The goal is to create an intelligent, automated solution for managing patient triage and appointment scheduling in a healthcare setting.

---
## 📌 Key Features

- **Conversational Interface** using Google Agent Development Kit (ADK)
- **Clinical Decision Support System** built with Python & FastAPI
- **Backend Integration** with hospital systems using UiPath bots
- **Triage Automation** based on symptom urgency and rule logic
- **Patient Notifications** via email/SMS for confirmations

## 📁 Folder Structure

```
/backend     → Python FastAPI service for triage logic
/bots        → UiPath automation scripts for hospital system actions
```

---

## 🚀 Getting Started

### Requirements
- Python 3.10+
- FastAPI
- UiPath Studio
- Google Cloud Project (for ADK agent)

### Backend Setup

1. **Install Dependencies**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

2. . **Run the Application**
```bash
cd backend
uvicorn app.main:app --reload
```
Visit `http://127.0.0.1:8000/` to access the application. Login with the following credentials:
- Username: admin
- Password: admin

For Patient Side, visit `http://127.0.0.1:8000/booking` to access the application.

### UiPath Bots Setup

1. **Required Bots**
- `LogAppointment.xaml` - Handles appointment scheduling
- `NotifyPatient.xaml` - Manages patient notifications

2. **Bot Configuration**
- Ensure UiPath Studio is installed
- Open the project in UiPath Studio
- Configure the following settings:
  - Set the working directory to the project root
  - Configure email settings for notifications
  - Set up SMS gateway if needed

3. **Bot Usage**

**LogAppointment Bot**
- Input Parameters:
  - QueueItemId: ID of the queue item
  - DoctorId: Selected doctor's ID
  - Date: Appointment date
  - Time: Appointment time
- Actions:
  - Reads appointment data
  - Creates new appointment record
  - Updates queue status
  - Sends confirmation email
  - Prints appointment slip

**NotifyPatient Bot**
- Input Parameters:
  - AppointmentId: ID of the appointment
  - NotificationType: Type of notification (confirmation/reminder/reschedule/cancellation)
- Actions:
  - Sends email notification
  - Sends SMS notification
  - Updates notification log

4. **Running Bots**
- Open UiPath Studio
- Load the desired bot
- Set input parameters
- Run the bot

## 📄 License
MIT License

---

## 🙌 Acknowledgements
This project was developed as part of the Intelligent Agents and Process Automation coursework at National College of Ireland.
