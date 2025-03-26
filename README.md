**TITLE**: Drone Delivery Service
**DESCRIPTION**: A service where customers orders from our store, and the drone will deliver it to them.

**PRE-REQUISITES**
1. Have docker running on your desktop (DockerHub)
2. Have SQL software on your local machine (WAMP/MAMP)

**BEFORE RUNNING SERVICE(S)**
Please go to the docker compose files for your respective OS: "docker-compose_windows" for Windows users and "docker-compose_mac" for Mac users, and ensure that the following are correct
- Under 'db', ensure that MYSQL_ALLOW_EMPTY_PASSWORD and MYSQL_ROOT_PASSWORD have the correct values
- Under each services, ensure that dbURL has the correct link (especially password and port number)

**RUNNING THE SERVICE(S)**
1. Go to ESD/SQL/SuperScript.sql and run the SQL script
2. Ensure that you are at the correct directory --> ESD
3. Open command prompt (on VSCode)
4. Type in "docker-compose_<...> up -d" to start running the service based on your respective docker-compose file
5. Open up index.html to begin using the services!

**USE CASE 1 STEPS**

**USE CASE 2 STEPS**

**USE CASE 3 STEPS**