import os

from readerware_browser.app import APP

if __name__ == "__main__":
    os.environ["DB_USERNAME"] = "test"
    os.environ["DB_PASSWORD"] = "test"
    APP.run(host="127.0.0.1", port=8080, debug=True)
