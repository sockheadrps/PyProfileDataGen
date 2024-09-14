import configparser
import os

# Load the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the environment variable for the GitHub username
github_user_name = os.getenv('GITHUB_USER_NAME')

# Update the github_user_name in the config file
config.set('Settings', 'github_user_name', github_user_name)

# Write the changes back to the config.ini file
with open('config.ini', 'w') as configfile:
    config.write(configfile)