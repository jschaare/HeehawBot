# HeehawBot

## Running
1. Copy config.json.example to config.json, and then add your tokens
2. Install required packages with `pip install -r requirements.txt`
3. Run the bot with `python -m bot`

## Docker
Docker is a great way to run the bot in a contained environment.
```
#Build and run
docker-compose up -d --build

#Check if running
docker-compose ps

#Shut down container
docker-compose down

#Check container logs
docker-compose logs
```

## To Do
* Add new cogs
    * Planetside 2
    * Music player
    * etc...
* Hook into persistant DB for some cogs
* Do more things