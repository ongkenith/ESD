**TITLE**: Drone Delivery Service
**DESCRIPTION**: A service where customers orders from our store, and the drone will deliver it to them.

**PRE-REQUISITES**
1. Have docker running on your desktop (DockerHub)
2. Have SQL software on your local machine

**RUNNING THE SERVICE(S)**
1. Go to ESD/SQL/SuperScript.sql and run the SQL script
2. Ensure that you are at the correct directory --> ESD
3. Go to the docker compose file and change the dbURL to the correct URL (depending on how you access your SQL on your machine)
    - If you are a Mac User, remove "MYSQL_ALLOW_EMPTY_PASSWORD" environment variable and add "MYSQL_PASSWORD" with your respective password
4. Open command prompt (on VSCode)
5. Type in "docker-compose up -d" to start running the service
6. Open up index.html to begin using the services!