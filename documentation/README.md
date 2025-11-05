# 🎯 Would have I won? App

### This Streamlit-based application allows users to check how many times a given set of "lucky numbers" would have resulted in a winning match (based on a user-defined match count) in Hungarian lotteries since the game began. It connects to a PostgreSQL database to query public historical draw data.

### 🤝 Thanks for checking out my App!

## 📁 Project Structure

The project is structured into frontend, backend logic, configuration, and testing files:

```
.
├── .streamlit/
│   └── secrets.toml          # Database connection configuration
├── backend.py                # Core application logic and database querying
├── streamlit_app.py          # Streamlit frontend UI and session state management
├── requirements.txt          # Python dependencies
├── disclaimer_en.txt         # English disclaimer text
├── disclaimer_hu.txt         # Hungarian disclaimer text
├── test_backend.py           # Unit tests for the backend logic
└── test_app.py               # End-to-end (E2E) tests using Selenium
```

## 📋 File Descriptions

| File Name         | Purpose                                                                                                                                                                                                                                                                    |
|:------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| streamlit_app.py  | Frontend (UI & Routing). Contains the StreamlitFrontend class, which manages the application's multilingual text, dynamic number pickers, session state navigation (Welcome, Disclaimer, Selector, Picker, Results), and displays the final data fetched from the backend. |
| backend.py        | Backend (Logic & Data). Contains the WinningNumbers class. It handles all critical logic, including input validation (lottery ID, number count, number range), SQL query construction for the lotteries, and executing database operations via st.connection.              |
| requirements.txt  | Dependencies. Lists all necessary Python packages, including streamlit, psycopg2-binary (PostgreSQL adapter), and sqlalchemy.                                                                                                                                              |
| disclaimer_en.txt | Content. The English text for the user agreement/disclaimer.                                                                                                                                                                                                               |
| disclaimer_hu.txt | Content. The Hungarian text for the user agreement/disclaimer.                                                                                                                                                                                                             |
| test_backed.py    | Unit Tests. Uses unittest and unittest.mock to verify the validation methods (_check_validity_lottery, _check_validity_numbers, _check_validity_match_count) and data interaction logic (check_lottery_numbers and _run_db_queries).                                       |
| test_app.py       | E2E Tests. Uses pytest and selenium with Edge WebDriver to simulate a full user journey through the Streamlit app, checking that pages load and buttons correctly transition between states across both English and Hungarian languages.                                   |

## ⚙️ Local Setup of 🎯 Would I have won? App

### <span style="color: red;">IMPORTANT NOTICE: To comply with the strict gambling-related laws of Hungary a disclaimer was created. If you host the application yourself, then modify the documents in English and in Hungarian too. The developer (Mihály Katona) does not guarantee its completeness! See [LICENSE](../LICENSE)! <span>

- Change the [disclaimer_en.txt](../disclaimer_en.txt):
  - X
- Change the [disclaimer_hu.txt](../disclaimer_hu.txt)
  - Y

Follow these steps to get the 🎯 Would I have won? App running locally.

### 1. Prerequisites

Must have:

- Python 3.8+ installed.
- A self-hosted PostgreSQL database containing the public lottery draw data.
- Microsoft Edge WebDriver executable (msedgedriver.exe) installed locally, as test_app.py is configured to use it.
  - Download from https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH#downloads
  - Add to the root directory of the app.

### 2. Installation

- Clone the Repository (or download the files).
- Create a virtual environment and activate it (recommended).
- Install dependencies: ```pip install -r requirements.txt```

### 3. Database Configuration (.streamlit/secrets.toml)

Streamlit securely handles database credentials using the .streamlit/secrets.toml file. You must create this folder and file in your project root directory and populate it with your PostgreSQL connection details.

- Create the folder: ```mkdir .streamlit```
- Create the file:
    ```
    Set-Content -Path .streamlit/secrets.toml -Value '# Never upload to anywhere!
    # Required connection parameters for st.connection("postgresql", type="sql")
    # Replace the placeholders below with your PostgreSQL server details.
    [connections.postgresql]
    dialect = "postgresql"
    host = "localhost"
    port = "5432"
    database = "your_DB"
    username = "your_USERNAME"
    password = "your_password"
    '
    ```
- Add to .gitignore: ```/.streamlit/secrets.toml```


### 4. Running the Application

Execute the streamlit_app.py file from your terminal: ```streamlit run streamlit_app.py```

This will launch the app in your default web browser (usually at http://localhost:8501).

### 5. Running Tests

To run the full suite of unit and end-to-end tests:

- Ensure you have the required testing dependencies installed (included in requirements.txt).
- Ensure the Edge WebDriver is accessible to test_app.py.

Execute the tests:
- unit test: ```python -m unittest test_backend.py```
- end-to-end test: ```pytest test_app.py```

# ☁️ Host on Streamlit Community Cloud and Google Cloud SQL

- Fork the repository: https://github.com/KatonaMihaly/did-i-win-the-lottery.git

### <span style="color: red;">IMPORTANT NOTICE: To comply with the strict gambling-related laws of Hungary a disclaimer was created. If you host the application yourself, then modify the documents in English and in Hungarian too. The developer (Mihály Katona) does not guarantee its completeness! See [LICENSE](../LICENSE)! <span>

- Change the [disclaimer_en.txt](../disclaimer_en.txt):
  - X


- Change the [disclaimer_hu.txt](../disclaimer_hu.txt)
  - Y


- Go to Streamlit Community Cloud: https://share.streamlit.io/
- Choose "Deploy a public app from Github" and follow the process
- Click "Advanced settings" and paste the content of your secrets.toml to secrets.

If you host your database on Google Cloud SQL, then change your secrets to:
- dialect = "postgresql"
- host = **public IP of the Google Cloud SQL database**
- port = "5432"
- database = **name of the database on Google Cloud SQL**
- username = **username created in Google Cloud SQL for the database**
- password = **password for the created username in Google Cloud SQL**

Do not forget to add Streamlits public IPs to the allowed networks in your Google Cloud SQL database from https://docs.streamlit.io/deploy/streamlit-community-cloud/status

# ⬇️ Download public Hungarian lottery data
- Go to https://www.szerencsejatek.hu/
- Find the lottery Ötöslottó, Hatoslottó or Skandináv lottó
- Click "Korábbi sorsolások"
- Download in XLS

# 🔄 Update lottery data manually
- Change the downloaded XLS to match the following structure:

| date | lottery_id | n1 | n2 | ... | nm |
|:--------|:--------|:--------|:--------|:--------|:--------|

where the lottery_id is:
- hu5 for Ötöslottó
- hu6 for Hatoslottó
- hu7 for Skandináv lottó

where the m is the range for each lottery:
- 5 for hu5
- 6 for hu6
- 7 for hu7


- Save the restructured XLS to .csv named:
  -  [draw_numbers_hu5.csv](../data_refining/Hu5/draw_numbers_hu5.csv) for Ötöslottó
  - [draw_numbers_hu6.csv](../data_refining/Hu6/draw_numbers_hu6.csv) for Hatoslottó
  - [draw_numbers_hu7a.csv](../data_refining/Hu7/draw_numbers_hu7a.csv) for Skandináv lottó mechanical draw
  - [draw_numbers_hu7b.csv](../data_refining/Hu7/draw_numbers_hu7b.csv) for Skandináv lottó manual draw


- Paste it into the related folder in **data_refining** folder.
- Run the related *draw_numbers_hu*_refine.py* file. It creates an SQL compatible txt in **SQL_commands** folder.
- Update [lottery.sql](../data_refining/SQL_commands/lottery.sql) and paste it into your database hosts SQL query.

# 📜 License
MIT License

Copyright (c) 2025 Mihály Katona

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


