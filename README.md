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

2. Switch environments, you should see a `(env)` prefix in the command prompt 
```
source env/bin/activate
```

3. Start Postgres

MacOS:
```
brew services start postgresql
```
Linux:
```
sudo service postgresql start
```

4. Open`.flaskenv`and change the variables `DB_USER` and `DB_PASSWORD` to your own Postgres credentials. Then run the following command:

```
db/setup.sh
```
Follow the instructions and enter your password when prompted.

5. Run flask
```
flask run
```

6. Go to http://localhost:5000/ and start using Mini Amazon!

7. To stop the website, press <kbd>Ctrl</kbd><kbd>C</kbd> in the shell where flask is running.


## Generating the Test Dataset

1. Run db/generated/gen.py. This should generate a couple of csv files.
2. Copy these csv files over to db/data.
3. Run db/setup.sh, and the test dataset should be loaded into Postgres!
