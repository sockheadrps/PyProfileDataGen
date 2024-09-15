import configparser
import os

# Load the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the environment variable for the GitHub username

github_user_name = 'codingwithstrangers'
gif_frame_duration = '10000'


# Update the github_user_name in the config file
config.set('Settings', 'github_user_name', github_user_name)
config.set('Settings', 'gif_frame_duration', gif_frame_duration)


# Write the changes back to the config.ini file
with open('config.ini', 'w') as configfile:
    config.write(configfile)