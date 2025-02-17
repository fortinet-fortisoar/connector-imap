#### Following enhancements have been made to the IMAP connector in version 3.5.8:
- Removed a vulnerability identified in the notification listener.
- Updated the connector code to use NotifierThread's new is_alive method instead of the deprecated isAlive method.