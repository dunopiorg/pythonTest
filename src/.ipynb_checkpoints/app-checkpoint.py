from subprocess import run
import config

if __name__ == "__main__":
    for game in config.GAME_LIST:
        run("nohup python3 main.py --gamekey %s &" % game, shell=True)
        