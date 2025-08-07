# Databaes: Mini-Amazon Project

Team Members: Cynthia Wang, Roy Xiong, Samia Zaman, Jane Zhang

Project: Mini-Amazon

Team Name: Databaes

Link to Github Repository: https://github.com/jjanezhang/databaes-project

## How to Run Mini Amazon
0. Clone this repo
```
git clone git@github.com:jjanezhang/databaes-project.git
```

1. Change directory to databaes-project
```
cd databaes-project
```

2. Create and activate a virtual environment
```
python3 -m venv env
source env/bin/activate
```

3. Download and Install the latest PostgreSQL server

MacOS:
```
brew install postgresql@17
echo 'export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
psql --version # verify
brew services start postgresql
```

Linux:
```
sudo service postgresql start
```

4. Create a new db called 'amazon' and open psql command line using that db

```commandline
createdb amazon
psql amazon
```

5. Set the following env vars (not necessarily the same value)
```
export DB_NAME=amazon     
export DB_USER=amazon_user
export DB_PASS=amazon_pass
export FLASK_APP=amazon.py
export FLASK_ENV=development
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5001 

SECRET_KEY=default_secret
```

5. Run the app!
```
flask run
```
Follow the prompt to view the running website!
6. Explore:
i) Sign up as a customer and explore products
![Screenshot 2025-08-06 at 8.50.09 PM.png](../../../../../var/folders/z1/s419t3bj1ws4917vrtpdcflm0000gn/T/TemporaryItems/NSIRD_screencaptureui_fpb4u5/Screenshot%202025-08-06%20at%208.50.09%E2%80%AFPM.png)
ii) Log in and create a new product (i.e. become a seller)
![Screenshot 2025-08-06 at 8.49.39 PM.png](../../../../../var/folders/z1/s419t3bj1ws4917vrtpdcflm0000gn/T/TemporaryItems/NSIRD_screencaptureui_wDlD1g/Screenshot%202025-08-06%20at%208.49.39%E2%80%AFPM.png)

6. To stop the website, press <kbd>Ctrl</kbd><kbd>C</kbd> in the shell where flask is running.


## Generating the Test Dataset

1. Run db/generated/gen.py. This should generate a couple of csv files.
2. Copy these csv files over to db/data.
3. Run db/setup.sh, and the test dataset should be loaded into Postgres!
