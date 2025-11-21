📝 Automated Article Download & Processing System
Built with Python, Selenium, and Pandas | Internship Project at eVC-Tech
🚀 Project Overview

This project automates the complete workflow of downloading unedited article files from a publishing platform (SAGE), processing them, merging associated resources, and generating a clean structured report for editorial teams.

The automation reads Article IDs (AID) and Journal IDs (JID) from a CSV file and processes each entry one at a time, ensuring accurate background operation without manual effort.

⚙️ Key Features

🔐 Automated Login to the publishing portal using Selenium.
📥 Automated file download of unedited .docx articles via dynamic postback JavaScript buttons.
📄 Reads AID & JID from CSV and processes sequentially.
🔁 Skips already processed articles to avoid duplication.
🧠 Headless background execution for uninterrupted automation.
🧾 Merges processed results into a final structured HTML report.
📤 Email automation for sending processed reports to copy-editors.
♻️ Automatic cleanup of temporary article folders after merge completion.

🧠 How Python Is Used
Python acts as the backbone of the entire automation pipeline.
Using Selenium WebDriver, the system dynamically interacts with the publishing website—locating elements based on JavaScript postback controls, triggering downloads, and managing timing using explicit waits to avoid UI rendering issues.
The CSV data (containing AID and JID) is handled using Pandas, allowing row-by-row execution. The script checks the downloads directory using OS module operations to detect if a merged report already exists and skips redundant processing.
The entire merge and formatting logic is written in Python, converting multiple input articles and metadata into a single final structured output, demonstrating Python’s strength in automation, file handling, and robust workflow control.

🧰 Tech Stack
Category	Tools
Language	Python
Automation	Selenium WebDriver (Chrome/Edge)
Data Handling	Pandas
File Processing	OS, Docx libraries, HTML generation
Execution Mode	Headless Browser Mode


📂 Folder Structure
|-- automation-script
|   |-- downloads/
|   |-- processed/
|   |-- merged_reports/
|   |-- articles.csv
|   |-- main.py
|   |-- merge.py
|   |-- email_sender.py

▶️ How to Run
pip install -r requirements.txt
python main.py

🙌 Acknowledgements:
This project was developed during a 14-week internship at eVC-Tech, focusing on workflow automation and content processing systems.
