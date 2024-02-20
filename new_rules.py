
import time

from poke import Game_env
from doudizhu.engine import Doudizhu
game = Game_env()
card_type = Doudizhu.CARD_TYPE
print(card_type[0]['name'])

cards = ['3', '4', '5', '6', '7', '8', '8', '9', 'J', 'J', 'Q', 'Q', 'Q', 'A', '2', '2', 'CJ']


def list_candidate(type_list,cards_str):  #候选牌列表
    cards_candidate = []
    for i in range(len(card_type)):
        for x in type_list:
            if card_type[i]['name'] == x:
                actions_list = card_type[i]['func']() #actions_list=[('BJ-CJ', 0)]
                for j in actions_list:    #j=('BJ-CJ', 0)
                    action = [a for a in j[0].split('-')]  #action=['BJ', 'CJ']
                    flag = True
                    for k in action:
                        if  cards_str.count(k) >= action.count(k):
                            pass
                        else:
                            flag = False
                            break
                    if flag == True:
                        cards_candidate.append(action)
    actions =cards_candidate
    cards_candidate = []
    return actions

def get_actions_candy(cards):
    def append_act():
        while player_cards!=[]:
            act = list_candidate(act_type_list,player_cards)
            mark = len(max(act, key=len, default=''))
            for y in act:
                if len(y)==mark:
                    candy_list.append(y)
                    for j in y:
                        player_cards.remove(j)
                    break
            act.clear()
    player_cards = cards.copy()
    acts = game.list_candidate(player_cards)
    act_type_list = []
    for i in acts:
        ok,act_type = Doudizhu.check_card_type(i)
        act_type_list.append(act_type[0][0])
    act_type_list = list(set(act_type_list))
    acts = [x for x in acts if len(x)>=5]
    candy_list = []
    if acts==[]:
        append_act()
        actions_candy = (len(candy_list),candy_list)
        return actions_candy
    else:
        len_mark = 17
        actions_candy = []
        for i in acts:
            candy_list.append(i)
            for z in i:
                player_cards.remove(z)
            append_act()
            act_count = len(candy_list)
            if act_count < len_mark:
                len_mark = act_count
                actions_candy.clear()
                actions_candy.append((len_mark,candy_list))
            candy_list = []        
            player_cards = cards.copy()
    return actions_candy
start_time = time.time()
a = get_actions_candy(cards)
print(a)
end_time = time.time()
print(end_time-start_time)














