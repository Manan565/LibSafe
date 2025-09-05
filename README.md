# 📚 Library Security System

A real-time webcam-based security system that monitors students' personal belongings in libraries and sends instant SMS notifications when items are moved or taken. Built with React, Flask, OpenCV, and Twilio.


##  Features

- **Real-time Object Detection**: Uses YOLOv3 to detect and track personal belongings
- **Movement Alerts**: Instant notifications when items are moved or taken
- **User Authentication**: Secure registration and login system
- **Webcam Integration**: Browser-based camera access for monitoring
- **SMS Notifications**: Twilio integration for instant alerts
- **PostgreSQL Database**: Robust data storage for users and monitoring sessions
- **Responsive Design**: Works on desktop and mobile devices


## 🛠️ Technology Stack

### Frontend
- **React 18** with Vite
- **Axios** for API calls
- **HTML5 Canvas** for webcam frame capture
- **CSS3** with custom styling

### Backend
- **Flask** Python web framework
- **PostgreSQL** database with SQLAlchemy ORM
- **OpenCV** for computer vision
- **YOLOv3** for object detection
- **Twilio API** for SMS notifications
- **JWT** for authentication
- **bcrypt** for password hashing

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- [Node.js](https://nodejs.org/) (v14 or higher)
- [Python](https://www.python.org/) (3.7 or higher)
- [PostgreSQL](https://www.postgresql.org/) (13 or higher)
- [Git](https://git-scm.com/)

You'll also need:
- A [Twilio account](https://www.twilio.com/) for SMS notifications
- YOLOv3 weights and configuration files
## Usage

### For Students:

1. **Register an Account**
   - Create an account with your name, email, and phone number
   - Phone number is required for SMS alerts

2. **Start Monitoring**
   - Click "Start Monitoring" to begin webcam surveillance
   - Allow camera access when prompted
   - The system will calibrate by detecting visible items

3. **Leave Your Desk**
   - Once calibration is complete, you can safely leave your belongings
   - The system will monitor for any movement or theft

4. **Receive Alerts**
   - Get instant SMS notifications if items are moved
   - Return to your desk to stop monitoring

### For Administrators:

- Monitor system usage through database queries
- View alert history and user activity
- Adjust detection sensitivity as needed


## 📈 Future Enhancements

- [ ] Mobile app development (React Native)
- [ ] Real-time dashboard for library staff
- [ ] Machine learning model fine-tuning for better accuracy
- [ ] Integration with library management systems
- [ ] Multi-language support
- [ ] Email notifications in addition to SMS
- [ ] Advanced analytics and reporting
- [ ] Face recognition for user verification

