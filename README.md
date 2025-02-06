# deauther

## Requirements
* Linux
* A network adapter that supports monitor mode and packet injection
  
## Setup

### Step 1: Create and Activate a Virtual Environment
Before installing dependencies, create and activate a Virtual Environment:

```bash
python -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies
Install the required Python packages using:

```bash
pip install -r requirements.txt
```

### Step 3: Configure sudoers for Scripts
To allow monitor.sh and wifi.sh to run without prompting for a password, edit the sudoers file:

```bash
sudo visudo
```

Add the following lines at the end of the file, replacing username with your actual username:

```bash
username ALL=(ALL) NOPASSWD: /path/to/monitor.sh
username ALL=(ALL) NOPASSWD: /path/to/wifi.sh
```

### Step 4: Start the Server
Run the server with:

```bash
python server.py
```

Everything is now set up!

## Notes
If the phone is connected to the computer via USB when the server starts, and USB tethering is enabled on the phone while the computer is connected to the shared network, the terminal will display the IP address of the USB-Ethernet interface.
Knowing this interface address and the port the server is running on, you can access the website from your phone.
