
# Attendance App

This repository contains the codebase for the Attendance Application. Below are the steps to set it up on your local machine.

---

## **How to Set Up Locally**

### **1. Clone the Repository**
To get started, clone this repository using the following command:
```bash
git clone https://github.com/vaaditya320/attendance-ledger.git
```

---

### **2. Navigate to the Project Directory**
Change into the project directory:
```bash
cd attendance-ledger
```

---

### **3. Create a Virtual Environment**
Set up a Python virtual environment for the project:
```bash
python3 -m venv venv
```

Activate the virtual environment:
- On **Linux/Mac**:
  ```bash
  source venv/bin/activate
  ```
- On **Windows**:
  ```bash
  .\venv\Scripts\activate
  ```

---

### **4. Install Requirements**
Install the necessary Python dependencies:
```bash
pip install -r requirements.txt
```

---

### **5. Set Up Environment Variables**
Create a `.env` file in the root directory of the project and add the following environment variables:
```bash
MAILJET_API_KEY=your-mailjet-api-key
MAILJET_SECRET_KEY=your-mailjet-secret-key
```
Replace the placeholder values with your actual keys and secrets.

---

### **6. Apply Migrations**
Run the following command to apply database migrations:
```bash
python manage.py migrate
```

---

### **7. Run the Development Server**
Start the development server:
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

---

### **8. Access Admin Panel (Optional)**
To access the Django admin panel, create a superuser:
```bash
python manage.py createsuperuser
```

Follow the prompts to set up an admin account. Then navigate to `http://127.0.0.1:8000/admin` to log in.


# Step-by-Step Deployment Journey

---

## 1. Set Up EC2 Instance
1. Launch an EC2 instance (Ubuntu).
2. Connect via SSH:
   ```bash
   ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
   ```

---

## 2. Install Required Software
1. Update packages:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
2. Install Python and Nginx:
   ```bash
   sudo apt install python3-pip python3-venv nginx -y
   ```

---

## 3. Set Up Django Application
1. Clone your project:
   ```bash
   cd /home/ubuntu/projects
   git clone https://github.com/vaaditya320/attendance-ledger.git attendance
   cd attendance
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

4. Update `.env` file with Mailjet credentials.
   ```bash
   MAILJET_API_KEY = "your-mailjey-api-key"
   MAILJET_API_SECRET = "your-mailjey-api-secret"
   ```

6. Modify `settings.py`:
   - `DEBUG = False`
   - `ALLOWED_HOSTS = ["attendance.aadityavinayak.in.net"]`
   - `STATIC_ROOT = "/home/ubuntu/projects/attendance/staticfiles"`

---

## 4. Run Gunicorn
1. Start Gunicorn manually to serve your app:
   ```bash
   gunicorn --workers 3 --bind unix:/home/ubuntu/projects/attendance/attendance.sock attendance.wsgi:application
   ```

---

## 5. Configure Nginx
1. Create an Nginx configuration:
   ```bash
   sudo nano /etc/nginx/sites-available/attendance
   ```
   Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name attendance.aadityavinayak.in.net;

       location / {
           proxy_pass http://unix:/home/ubuntu/projects/attendance/attendance.sock;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /static/ {
           alias /home/ubuntu/projects/attendance/staticfiles/;
       }
   }
   ```

2. Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/attendance /etc/nginx/sites-enabled
   ```

3. Test and restart Nginx:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## 6. Set Permissions
1. Make sure the static files are accessible:
   ```bash
   sudo chmod -R 755 /home/ubuntu/projects/attendance/staticfiles
   ```

2. Ensure the Nginx user (`www-data`) has permission to read the static files and Gunicorn socket:
   ```bash
   sudo chown -R ubuntu:www-data /home/ubuntu/projects/attendance
   ```

---

## 7. DNS Configuration
1. Point your domain (`attendance.aadityavinayak.in.net`) to your EC2 instance's public IP.

---

## 8. Running the Application
Since you are running Gunicorn **manually**:
1. Open a new screen session:
   ```bash
   screen -S attendance
   ```
2. Run Gunicorn:
   ```bash
   gunicorn --workers 3 --bind unix:/home/ubuntu/projects/attendance/attendance.sock attendance.wsgi:application
   ```
3. Detach the screen (`Ctrl+A, then D`), so it continues running in the background.

---

# Summary of Key Paths
- **Static Files Directory**: `/home/ubuntu/projects/attendance/staticfiles`
- **Nginx Config File**: `/etc/nginx/sites-available/attendance`
- **Gunicorn Socket**: `/home/ubuntu/projects/attendance/attendance.sock`

- 
### Next Steps (Optional):

#### 1. Restrict Access to Static Files:
You can also add authentication to the static files directory by including the `auth_basic` configuration in the `/static/` location block in Nginx.

```nginx
location /static/ {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    alias /home/ubuntu/projects/attendance/staticfiles/;
}
```

#### 2. Add More Users:
To add more users to your `.htpasswd` file, run the following command (without the `-c` flag):

```bash
sudo htpasswd /etc/nginx/.htpasswd anotheruser
```

This will prompt you for the password for the new user.

#### 3. Remove Users:
To remove a user, you can simply delete the corresponding line from the `.htpasswd` file or use `htpasswd -D` to delete a user:

```bash
sudo htpasswd -D /etc/nginx/.htpasswd username
```


---

Now your application is live! You can always reconnect to your screen session to manage the running Gunicorn process.

