# HeehawBot

Discord bot for a personal discord server.
Implements things like audio playback and some commands for game information. Under development, used everyday and loved by many...

## Installation

### Basic
```
# Clone repo
git clone git@github.com:jschaare/HeehawBot.git
cd HeehawBot

# Create virtual environment if you want
python3 -m venv venv
# Linux
source venv/bin/activate
# Windows
source venv/Scripts/activate

# Install packages 
pip install -r requirements.txt

# Add configs
cp config.json.example config.json
# ADD KEYS AND ENVIRONMENT INFO INTO config.json

# Run bot
python3 -m heehawbot
```

### Docker
```
#Build and run
docker build -t hhbot . && docker run hhbot
```

## License
HeehawBot uses an [MIT License](LICENSE)