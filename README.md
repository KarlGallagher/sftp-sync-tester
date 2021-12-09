## SFTP File Transfer Synchronisation Test Tool
This tool can be used to generally test SFTP file transfer synchronisation capabilities afforded by a specific server. It works by simulataneously uploading and downloading the same file in order to simulate concurrent access to an 'in flight' transfer

---

## Requirements
### Python Version
The minimum python version required is 3.7.x


### Windows Setup (Powershell)
From source directory run:

`. .\venv_setup.ps1`

### MacOS/Linux Setup (Shell (bash/zsh/sh))
From source directory run:

`source ./venv_setup.sh`

---

## Configuration
You can set the following properties via the *Configuration* class
- SLEEP_TIMEOUT_MS - Timeout between upload initiating and download commencing 
- SFTP_HOST - The hostname or IP address for the SFTP service
- SFTP_PORT - The port the SFTP service is bound to (22 is default)
- SFTP_USERNAME - The username used to authenticate access to the service
- SFTP_PASSWORD - The password used to authenticate access to the service

>Note: SSH Key based authentication is not currently supported

---

## SSH Known Hosts
Although passsword based authentication is used to authorise access, the underlying SFTP implmentation still requires a 'hosts' entry for the remote host running the SFTP server.

You can ensure a hosts entry is added by manually connecting to the host via a standard SSH client (native or [PuTTY](https://www.putty.org/)) for example:

`ssh <sftp_user>@<sftp_host>`

Or if you have bound the server to an non-standard port:

`ssh -p <sftp_port> <sftp_user>@<sftp_host>`

---

## Running The Tool
The tool is command line based and running with a *-h* parameter will provide a help output:

```
sync_test.py - INFO - SFTP File Transfer Sync Tester
usage: sync_test.py [-h] -i INPUT_FILE_PATH -u UPLOAD_FILE_PATH -o OUTPUT_FILE_PATH

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE_PATH, --input_file_path INPUT_FILE_PATH
                        Path to input file, including filename - (required)
  -u UPLOAD_FILE_PATH, --upload_file_path UPLOAD_FILE_PATH
                        remote path for upload, including filename - (required)
  -o OUTPUT_FILE_PATH, --output_file_path OUTPUT_FILE_PATH
                        local path for download, including filename - (required)
```

Example:

`python3 sync_test.py  -i  input.csv  -u 'uploads/input.csv'  -o './downloaded.csv'`