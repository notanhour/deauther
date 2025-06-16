# deauther

## Requirements
* Linux
* A network adapter that supports monitor mode and packet injection
  
## Setup

### 1. Create and Activate a Virtual Environment
Before installing dependencies, create and activate a Virtual Environment:

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install the Required Packages
For it to work, install these:

```bash
sudo apt install iw aircrack-ng
```

### 2. Install Dependencies
Install the required Python packages using:

```bash
pip install -r requirements.txt
```

### 3. Configure sudoers for Scripts
To allow monitor.sh and wifi.sh to run without prompting for a password, edit the sudoers file:

```bash
sudo visudo
```

Add the following lines at the end of the file, replacing username with your actual username:

```bash
username ALL=(ALL) NOPASSWD: /path/to/monitor.sh
username ALL=(ALL) NOPASSWD: /path/to/wifi.sh
```

### 4. Start the Server
Run the server with:

```bash
python server.py
```

Everything is now set up!

## Notes
If the phone is connected to the computer via USB when the server starts, and USB tethering is enabled on the phone while the computer is connected to the shared network, the terminal will display the IP address of the USB-Ethernet interface. Knowing this interface address and the port the server is running on, you can access the website from your phone.

## Legal Notice & Responsible Use
This project, **deauther**, is intended for **educational**, **research**, and **authorized security testing** purposes. Use only on your own networks or networks that you have explicit permission to test.

Any unauthorized use of this tool against third-party networks is **illegal**. The developer assumes **no responsibility** for misuse or damages resulting from the use of this software.

By using this tool, you agree to:
- Use it **only in legal and ethical contexts**.
- Take **full responsibility** for your actions.
- Respect the privacy and property of others.

If you're unsure whether your use case is allowed — don't use it.

## License
This project is licensed under the MIT License:
```plaintext
Copyright (c) 2025 Nikolai Nazarov

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
