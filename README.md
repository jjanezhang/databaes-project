# Databaes: Mini-Amazon Project

Team Members: Cynthia Wang, Roy Xiong, Samia Zaman, Jane Zhang

Project: Mini-Amazon

Team Name: Databaes

Link to Github Repository: https://github.com/jjanezhang/databaes-project

## How to run

1. Change directory to databaes-project
```
cd databaes-project
```

2. Switch environments, you should see a `(env)` prefix in the command prompt 
```
source env/bin/activate
```

3. Start Postgres
```
brew services start postgresql
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
