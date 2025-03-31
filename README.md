# expenSieve: Receipt Processing Web App
This is a Flask-based web application that allows users to upload multiple receipt images (or PDFs), extract structured expense data using OpenAI's GPT-4o Vision model, and save the parsed information to a CSV file. The application is designed to be mobile-friendly and supports multiple file uploads at once.

## Features
- **Multi-file Upload:** Upload multiple receipt images or PDFs at once.
- **Automatic Parsing:** Extracts Date, Expense Type, Vendor, City, Currency, Amount, Payment Mode, Time of Transaction, and Remarks.
- **Thumbnail Previews:** Displays thumbnails of uploaded receipts.
- **Editable Table:** Extracted data is shown in a table format, allowing users to edit fields before saving.
- **CSV Export:** Saves extracted data to a CSV file for record-keeping.
- **PDF Support:** Converts PDF receipts to images before processing.
- **Configurable API Calls:** Uses a `useOpenAI` flag to switch between cached responses and actual API calls for testing.

## Installation

### Prerequisites
- Python 3.8+
- Flask
- OpenAI API Key
- Required Python libraries (listed in `requirements.txt`)

### Steps
1. **Clone the repository**
   ```sh
   git clone <repo-url>
   cd <repo-folder>
   ```
2. **Create a virtual environment (optional but recommended)**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
   ```
3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set up environment variables**
   - Create a `.env` file and add your OpenAI API key:
     ```sh
     OPENAI_API_KEY=your_openai_api_key
     ```
5. **Run the application**
   ```sh
   flask run
   ```
6. **Access the web app**
   Open `http://127.0.0.1:5000/` in your browser.

## Usage
1. Click **Choose Files** and select receipt images or PDFs.
2. Click **Upload** to process the files.
3. Review and edit extracted details in the displayed table.
4. Click **Save to CSV** to store the data.

## File Structure
```
+-- static/
¦   +-- uploads/  # Uploaded files
¦   +-- processed/  # Resized and processed images
+-- templates/
¦   +-- index.html  # Frontend UI
+-- app.py  # Flask backend
+-- requirements.txt  # Dependencies
+-- .env  # Environment variables
+-- README.md  # Documentation
```

## Future Improvements
- Automatic integration with expense tracking platforms.
- Improved UI for better mobile experience.
- Email-based receipt auto-importing.

## License
MIT License

---

Happy tracking! ??

