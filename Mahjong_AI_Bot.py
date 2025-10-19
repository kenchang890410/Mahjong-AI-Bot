import pyautogui
from mahjong_utils.models.tile import parse_tiles
from mahjong_utils.shanten import shanten
import mss
import cv2, os
import numpy as np
import time
import copy

#init
my_turn = False
count = 0
threshold = 0.93
count_sum = 0
images = ['1m.png', '2m.png', '3m.png', '4m.png', '5m.png', '6m.png', '7m.png', '8m.png', '9m.png', '1p.png', '2p.png', '3p.png', '4p.png', '5p.png', '6p.png', '7p.png', '8p.png', '9p.png', '1s.png', '2s.png', '3s.png', '4s.png', '5s.png', '6s.png', '7s.png', '8s.png', '9s.png', '1z.png', '2z.png', '3z.png', '4z.png', '5z.png', '6z.png', '7z.png']
hand = []
played_card = []
yaojio = ['1m', '9m', '1s', '9s', '1p', '9p', '1z', '2z', '3z', '4z', '5z', '6z', '7z']
most_right_card = ""
zong = '7z'
paiee = '5z'
zongcount = 0 
paieecount = 0
guoshi_mode = False
dontrichi = False

print("start")

with mss.mss() as sct:
    
    while 1:
        
        #init
        hand = []
        count = 0
        zongcount = 0 
        paieecount = 0
        guoshi_mode = False
        my_turn = False

        monitor_number = 2
        mon = sct.monitors[monitor_number]

        monitor = {
        "top": 904,       # 從螢幕最上方開始 903 for monitor 2
        "left": 250,    # 從螢幕最左邊的265像素處開始
        "width": 1315,  # 要截取的區域的寬度
        "height": 130,   # 要截取的區域的高度
        "mon": monitor_number,
        }
        output = "sct-mon{mon}_{top}x{left}_{width}x{height}.png".format(**monitor)
        
        sct_img = sct.grab(monitor)
        img = np.array(sct.grab(monitor))
        cv2.imwrite("hand.png", img)
        most_right_card_range = img[:,1181:1314]
        gray_image2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        most_right_card_range = cv2.cvtColor(most_right_card_range, cv2.COLOR_BGR2GRAY)

        # read hand
        for i in range(0, len(images)):

            image1 = cv2.imread("./card/" + images[i])
            
            gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)

            result = cv2.matchTemplate(gray_image2, gray_image1, cv2.TM_CCOEFF_NORMED)
            most_right_card_result = cv2.matchTemplate(most_right_card_range, gray_image1, cv2.TM_CCOEFF_NORMED)

            loc = np.where(result >= threshold)

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(most_right_card_result)

            if max_val > threshold:
                most_right_card = images[i].split(".")[0]

            previous_loc = None

            while loc[0].size != 0:

                pt = (loc[1][0], loc[0][0])
                if previous_loc is not None:
                    distance = np.sqrt((pt[0] - previous_loc[0])**2 + (pt[1] - previous_loc[1])**2)
                    if distance < 20:
                        loc = (np.delete(loc[0], 0), np.delete(loc[1], 0))
                        continue
                
                count += 1
                hand.append(images[i].split(".")[0])
                previous_loc = pt
                loc = (np.delete(loc[0], 0), np.delete(loc[1], 0))
            
        if(count == 0):
            count_sum = count_sum + 1
        else:
            count_sum = 0

        if(count_sum > 600):
            print("break")
            break

        if(count == 14):
            my_turn = True
        else:
            my_turn = False

        #場上情況 按和、立直
        monitorhe = {
            "top": 0,       # 從螢幕最上方開始
            "left": 0,    # 從螢幕最左邊的265像素處開始
            "width": 1920,  # 要截取的區域的寬度
            "height": 1080,   # 要截取的區域的高度
            "mon": monitor_number,
            }
        
        outputhe = "sct-mon{mon}_{top}x{left}_{width}x{height}.png".format(**monitorhe)
        sct_imghe = sct.grab(monitorhe)
        imghe = np.array(sct.grab(monitorhe))
        if(imghe[256, 1490][0] == 71):
            time.sleep(10)
            #click after place counting
            pyautogui.click(x=1742, y=971)
            time.sleep(20)
            print("place counting")
            
            #click after score counting
            pyautogui.click(x=1742, y=971)
            time.sleep(20)
            print("score counting")

            #click after gift counting
            pyautogui.click(x=1742, y=971)
            time.sleep(20)
            print("gift counting")

            #click after gift counting 100%
            outputhe = "sct-mon{mon}_{top}x{left}_{width}x{height}.png".format(**monitorhe)
            sct_imghe = sct.grab(monitorhe)
            imghe = np.array(sct.grab(monitorhe))
            cv2.imwrite("testgift.png", imghe)
            print("snapshot gift")
            if(imghe[406, 1362][0] != 101):
                pyautogui.click(x=1742, y=971)
                print("gift full")
                time.sleep(10)

            #click game mode
            pyautogui.click(x=1332, y=328)
            time.sleep(10)
            print("game mode")

            #click rank mode
            pyautogui.click(x=1364, y=720)#copper 404 sliver 562
            time.sleep(10)
            print("rank mode")

            #click tong or nan mode
            pyautogui.click(x=1370, y=711)
            print("tong mode")

            continue
        
        # 國士無雙判斷 
        yaojio_set = set(yaojio)
        hand_set = set(hand)
        yaojio_intersection = yaojio_set.intersection(hand_set)

        yaojio_intersection_counts = {element: max(yaojio.count(element), hand.count(element)) for element in yaojio_intersection}
        
        if yaojio_intersection_counts:
            yaojio_max_count = max(yaojio_intersection_counts.values())

        if(len(yaojio_intersection) > 9) and (yaojio_max_count > 1):
            guoshi_mode = True

        #paie
        if(imghe[798, 1006][0] == 53) and (guoshi_mode == False):
            pyautogui.click(x=1006, y=798)
            continue

        #richi
        if(imghe[798, 1006][0] < 30) and dontrichi == False:
            pyautogui.click(x=1006, y=798)

        #skip pon kong chi
        if(imghe[825, 1290][0] == 80):
            pyautogui.click(x=1290, y=825)

        if my_turn :

            print("my turn")
            if(imghe[555, 28][0] > 100):
                pyautogui.click(x=38, y=560)
                dontrichi = False
                played_card = []
            
            
            hand_original = []
            hand_original = copy.deepcopy(hand)

            if most_right_card in hand_original:
                hand_original.remove(most_right_card)
                hand_original.append(most_right_card)
            
            #調整手牌順序符合 mahjong_utils
            handcom = ""
            remode = 0
            for i in range(len(hand)-1,-1,-1):
                
                if("z" in hand[i]) and remode == 1:
                    hand[i] = hand[i].split("z")[0]
                if("z" in hand[i]) and remode == 0:
                    remode = 1

                if("s" in hand[i]) and remode == 2:
                    hand[i] = hand[i].split("s")[0]
                if("s" in hand[i]) and remode == 1:
                    remode = 2

                if("p" in hand[i]) and remode == 3:
                    hand[i] = hand[i].split("p")[0]
                if("p" in hand[i]) and remode == 2:
                    remode = 3

                if("m" in hand[i]) and remode == 4:
                    hand[i] = hand[i].split("m")[0]
                if("m" in hand[i]) and remode == 3:
                    remode = 4

            for i in range(len(hand)):
                handcom = handcom + hand[i] 

            result = shanten(parse_tiles(handcom))
            print("shanten count : ", result.shanten)

            if(int(result.shanten) == -1):
                continue
            
            #尋找最佳捨牌
            current_shanten = int(result.shanten)
            bestcard = "10z"
            zhenting_bestcard = "11z"
            for i in range(2):

                goodlist = []
                goodkey = []
                goodadvance = []
                for key in result.discard_to_advance:
                    value = result.discard_to_advance.get(key, 'Key not found')
                    if(int(str(value).split("shanten=")[1].split(" ")[0]) == current_shanten):
                        goodadvance.append(str(value).replace(" ", "").split("}")[0].split("{")[1].split(","))
                        goodlist.append(int(str(value).split("advance_num=")[1].split(" ")[0]))
                        goodkey.append(str(key))
                    
                advance_num_best = 0
                if current_shanten == 0:
                    zhenting_advance_num_best = 0
                
                for i in range(len(goodlist)):

                    if(goodlist[i] > advance_num_best):

                        zhenting_advance_num_best = goodlist[i]
                        zhenting_bestcard = goodkey[i]

                    played_card_set = set(played_card)
                    goodadvance_set = set(goodadvance[i])
                    zhenting_intersection = played_card_set.intersection(goodadvance_set)

                    zhenting_intersection_counts = {element: max(played_card.count(element), goodadvance[i].count(element)) for element in zhenting_intersection}
                    
                    if zhenting_intersection_counts:
                        zhenting_max_count = max(zhenting_intersection_counts.values())
                        if zhenting_max_count > 0 and current_shanten == 0:
                            print("zhenting")
                            continue
                    if(goodlist[i] > advance_num_best):

                        advance_num_best = goodlist[i]
                        bestcard = goodkey[i]
                
                if bestcard == "10z":
                    current_shanten -= 1
                else:
                    break
            
            if bestcard != "10z":
                dontrichi = False

            if bestcard == "10z" and zhenting_advance_num_best > 6:
                bestcard = zhenting_bestcard
            elif bestcard == "10z" and (dontrichi == False):
                dontrichi = True
                pyautogui.click(x=1422 ,y=815)
                continue
            elif bestcard == "10z" and dontrichi == True:
                bestcard = most_right_card
            
            print("bestcard : ", bestcard)
            print("most_right_card : ", most_right_card)
            print("hand : ", hand_original)

            #change 5z 7z position

            if most_right_card in hand_original:
                hand_original.pop(-1)

            for i in range(4):

                if paiee in hand_original:
                    
                    hand_original.remove(paiee)
                    paieecount += 1

                if zong in hand_original:
                    hand_original.remove(zong)
                    zongcount += 1

            for i in range(paieecount):
                hand_original.append(paiee)

            for i in range(zongcount):
                if '6z' in hand_original:
                    hand_original.insert(hand_original.index('6z'), zong)
                elif(paiee in hand_original):
                    hand_original.insert(hand_original.index(paiee), zong)
                else:
                    hand_original.append(zong)

            hand_original.append(most_right_card)
            print("change 5z 7z hand : ", hand_original)
            
            #drop card
            if(bestcard == most_right_card):
                pyautogui.click(x=1499 ,y=960)
                pyautogui.click(x=1499 ,y=960)
                pyautogui.click(x=948 ,y=665)
                played_card.append(bestcard)
            else:
                drop_card_position_x = 308 + (hand_original.index(bestcard) * 90)
                pyautogui.click(x=drop_card_position_x ,y=970)
                pyautogui.click(x=drop_card_position_x ,y=970)
                pyautogui.click(x=948 ,y=665)
                played_card.append(bestcard)

            print("played_card", played_card)

        time.sleep(1)