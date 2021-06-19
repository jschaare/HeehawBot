# HeehawBot

## Running
1. Copy config.json.example to config.json, and then add your tokens
2. Create virtual environment and activate
3. Install required packages with `pip install -r requirements.txt`
4. Run the bot with `python -m heehawbot`

## Docker
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