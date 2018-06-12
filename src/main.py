import time
import threading
import config
import argparse
from lib import record
from lib import game_app

# Program Start
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gamekey", help="game key")
    parser.add_argument("--clear", help="game key")
    args = parser.parse_args()

    if args.clear:
        record.Record().set_clear_message_log()
        exit()

    if args.gamekey:
        game_id = args.gamekey
    else:
        game_id = '20170909SSHT0'  # 20170609SSHH0  20170912OBNC0 20170914SKOB0 20170926HHLT0 20170909NCHH0 20170923SSHH0
    sleep_second = config.SLEEP_TIME
    gm_app = game_app.GameApp(game_id)

    msg_thread = threading.Thread(target=gm_app.message_printer_thread, name='Message Thread')
    msg_thread.start()
    
    caster_thread = threading.Thread(target=gm_app.message_maker_thread, name='Score Table Thread')
    caster_thread.start()
    # Test Start ------------------------------------
    game_live_list = gm_app.test_live_data(game_id)
    for game_live_dict in game_live_list:
        try:
            result = gm_app.get_what_info(game_live_dict)
            if result:
                    gm_app.make_sentence(result)
        except Exception as ex:
            print(ex)
        time.sleep(sleep_second)
    
    gm_app.game_thread = 0
    # Test End -------------------------------------
