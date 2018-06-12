import time
import threading
import config
import argparse
from lib import game_app

# Program Start
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gamekey", help="game key")
    args = parser.parse_args()
    if args.gamekey:
        game_id = args.gamekey
    else:
        game_id = '20170909SSHT0'  # 20170609SSHH0  20170912OBNC0 20170914SKOB0 20170926HHLT0
    sleep_second = config.SLEEP_TIME
    gm_app = game_app.GameApp(game_id)

    msg_thread = threading.Thread(target=gm_app.message_printer_thread, name='Message Thread')
    msg_thread.start()
    
    caster_thread = threading.Thread(target=gm_app.message_maker_thread, name='Score Table Thread')
    caster_thread.start()
    # Test Start ------------------------------------
    game_live_list = gm_app.test_live_data(game_id)
    for game_live_dict in game_live_list:
        result = gm_app.get_what_info(game_live_dict)

        if result:
            gm_app.make_sentence(result)
        time.sleep(sleep_second)
    
    gm_app.game_thread = 0
    # Test End -------------------------------------
