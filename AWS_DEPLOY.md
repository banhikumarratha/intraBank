# ☁️ Deploying SaveLoan to AWS (Free Tier)

For your application, the best AWS service is **Amazon EC2 (Elastic Compute Cloud)**.

## ❓ Why EC2?
Your application stores data in **local JSON files** (`users.json`, `loans.json`, etc.).
- **Serverless (Lambda/App Runner):** NOT suitable. These services wipe local files every time they restart. You would lose all your user data.
- **EC2:** It's like a remote computer. It permits **persistent storage**, meaning your JSON files stay saved on the disk even if you restart the app.
- **Cost:** The `t2.micro` or `t3.micro` instance types are **Free Tier eligible** (750 hours/month for the first 12 months), making it effectively free for testing.

---

## 🚀 Step-by-Step Deployment Guide

### Phase 1: Launch an EC2 Instance (Virtual Server)

1. **Login to AWS Console** and search for **EC2**.
2. Click **Launch Instance**.
3. **Name:** `SaveLoan-Server`.
4. **OS Image:** Choose **Ubuntu** (Ubuntu Server 22.04 LTS is a good choice).
5. **Instance Type:** Select `t2.micro` or `t3.micro` (Look for the "Free tier eligible" tag).
6. **Key Pair:** 
   - Click "Create new key pair".
   - Name it `saveloan-key`.
   - Download the `.pem` file to your computer.
7. **Network Settings (Security Group):**
   - Check "Allow SSH traffic from".
   - Check "Allow HTTP traffic from the internet".
   - **Important:** Click "Edit" -> Add Security Group Rule:
     - **Type:** Custom TCP
     - **Port range:** `5000`
     - **Source:** Anywhere (`0.0.0.0/0`)
8. Click **Launch Instance**.

### Phase 2: Connect to Your Server

1. Open your terminal (Mac/Linux) or PowerShell (Windows).
2. Move your key to a safe folder and restrict permissions:
   ```bash
   chmod 400 path/to/saveloan-key.pem
   ```
3. Connect via SSH (replace `1.2.3.4` with your EC2 instance's Public IP address):
   ```bash
   ssh -i path/to/saveloan-key.pem ubuntu@1.2.3.4
   ```

### Phase 3: Setup the Server Environment

Once connected to the server, run these commands to prepare it:

1. **Update system:**
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv git
   ```

2. **Clone your project:**
   *Note: Since your code is local, the easiest way to transfer it is using `scp` or creating a zip.*
   
   **Option A (If you have a git repo):**
   ```bash
   git clone https://github.com/yourusername/your-repo.git project
   cd project
   ```

   **Option B (Copy from your local machine):**
   Open a *new* terminal window on your computer (not the SSH one) and run:
   ```bash
   # Upload project folder to EC2
   scp -i path/to/saveloan-key.pem -r /Users/banhi/Desktop/project ubuntu@1.2.3.4:~/project
   ```

3. **Install Dependencies:**
   Back in your SSH session:
   ```bash
   cd ~/project
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn  # Production server (better than python app.py)
   ```

### Phase 4: Run the Application

#### Option A: Quick Test (Stops when you close terminal)
```bash
python3 app.py
```
*Your app is now accessible at `http://YOUR_EC2_IP:5000`*

#### Option B: Keep Running (Recommended)
Use `gunicorn` to run it in the background:

```bash
# Run with gunicorn on port 5000, as a daemon (-D)
gunicorn -w 4 -b 0.0.0.0:5000 app:app --daemon
```

### Phase 5: Verify
1. Open your browser.
2. Go to `http://YOUR_EC2_PUBLIC_IP:5000`.
3. You should see your application running!

---

## ⚠️ Important Notes

1. **Persistence:** Since you are using EC2, your `data/*.json` files will be saved on the server's disk. 
2. **Backups:** If you terminate (delete) the EC2 instance, you lose the data. "Stop" preserves data, "Terminate" deletes it.
3. **Cost:** Remember to **Stop** or **Terminate** the instance when you are done testing to ensure you stay within Free Tier limits.
