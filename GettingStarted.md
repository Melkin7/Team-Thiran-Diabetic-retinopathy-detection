## Installation :     

### Prerequisites
Ensure you have the following installed:
* Python 3.8 or higher
* MySQL Server 8.0+
* pip (Python package manager)

### Required Python Packages
Install the required packages using:
```bash
pip install -r requirements.txt
```

The main dependencies include:
* PyTorch - Deep learning framework
* torchvision - Image transformations and models
* Tkinter - GUI toolkit (usually comes with Python)
* MySQL Connector - Database connectivity
* Pillow - Image processing
* matplotlib, numpy, pandas - Data processing and visualization    
## Setup Instructions :

### Step 1: Clone/Download the Project
Ensure all project files are in the same directory.

### Step 2: Database Setup
1. **Start MySQL Server**:
   ```bash
   sudo systemctl start mysql
   ```

2. **Run the database setup script**:
   ```bash
   sudo mysql < setup_database.sql
   ```
   
   This will create:
   - Database: `diabetic_retinopathy_db`
   - Table: `THEGREAT` (for user authentication and predictions)
   - User: `dr_user` with password `dr_password_2024`
   - Test accounts: `admin/admin123` and `testuser/test123`

### Step 3: Model Weights
The pre-trained model weights (`classifier.pt`) should be placed in the project root directory. This file contains the trained ResNet152 model parameters.

### Step 4: Configure Database Connection (Optional)
The application uses environment variables for database credentials with the following defaults:
- Host: `localhost`
- User: `dr_user`
- Password: `dr_password_2024`
- Database: `diabetic_retinopathy_db`

To customize, set these environment variables:
```bash
export DR_DB_HOST="localhost"
export DR_DB_USER="your_username"
export DR_DB_PASSWORD="your_password"
export DR_DB_NAME="your_database"
```

### Step 5: Run the Application
Activate the virtual environment (if using one) and run:
```bash
python blindness.py
```

The GUI will launch. You can:
1. **Sign Up**: Create a new user account
2. **Login**: Use existing credentials (e.g., `admin/admin123`)
3. **Upload Image**: Select a retinal image for DR detection
4. **View Prediction**: Get AI-powered severity classification

### Step 6: Test with Sample Images
Use the images in the `sampleimages/` folder to test the system:
```bash
sampleimages/eye10.jpg  # Should predict "Moderate"
sampleimages/eye1.png   # Should predict "No DR"
```

---

## Optional: SMS Notifications (Twilio Integration)

If you want to enable SMS notifications for predictions:

1. **Create a Twilio Account**:
   - Sign up at [Twilio](http://twilio.com/)
   - Verify your phone number
   - Get your Account SID and Auth Token from the dashboard

2. **Configure SMS Integration**:
   - Edit `send_sms.py` and add your Twilio credentials
   - In `blindness.py`, uncomment:
     ```python
     #from send_sms import *
     #send(value, classes)
     ```

3. **Test**: After enabling, predictions will trigger SMS notifications with the diagnostic results.

---
## Troubleshooting

**Database Connection Issues:**
- Ensure MySQL server is running: `sudo systemctl status mysql`
- Verify database credentials in environment variables
- Check if `diabetic_retinopathy_db` database exists

**Model Loading Errors:**
- Confirm `classifier.pt` file is in the project root directory
- Check file size (should be ~677 MB)
- Ensure PyTorch is properly installed

**Import Errors:**
- Activate virtual environment if using one
- Reinstall requirements: `pip install -r requirements.txt`

---

**Sample Images**: You can use the retinal images in the `sampleimages/` folder (from the original APTOS test dataset) for validation and testing.

---

**Developed by Team Thiran**
