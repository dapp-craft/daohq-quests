import sqlite3
import json
from time import time

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile

from tools import db_connection, check_system_token, seconds_until_midnight, validate_auth_chain


router = APIRouter()


@router.post('/sync/quests')
async def quests_sync(
    sync_file: UploadFile = File(...), 
    db=Depends(db_connection), 
    _=Depends(check_system_token)
):
    
    json_data = await sync_file.read()
    quests = json.loads(json_data)['quests']
    coins = json.loads(json_data)['coins']
    rewards = json.loads(json_data)['rewards']
    daily_quest_per_day = json.loads(json_data)['dailyQuestPerDay']
    daily_quest_price = json.loads(json_data)['dailyQuestPrice']
    coins_per_day = json.loads(json_data)['coinsPerDay']

    db.execute('DELETE FROM Quests')

    for quest_id, quest_data in quests.items():

        db.execute(
            '''
            INSERT INTO Quests (id, quest_order, day, reward_count)
            VALUES (?1, ?2, ?3, ?4)
            ''', (quest_id, quest_data['order'], quest_data['day'], quest_data['reward_count'])
        )

    db.execute('DELETE FROM Coins')

    for coin_id, coin_price in coins.items():

        db.execute(
            '''
            INSERT INTO Coins (id, price)
            VALUES (?1, ?2)
            ''', (coin_id, coin_price)
        )
    
    db.execute('DELETE FROM Rewards')

    for reward_id, reward_data in rewards.items():

        db.execute(
            '''
            INSERT INTO Rewards (id, price, blockchain_id, collection)
            VALUES (?1, ?2, ?3, ?4)
            ''', (reward_id, reward_data['price'], reward_data['blockchain_id'], reward_data['collection'])
        )

    db.execute(
        '''
        INSERT OR REPLACE INTO Settings (id, value)
        VALUES (?1, ?2)
        ''', ('dailyQuestPerDay', daily_quest_per_day)
    )

    db.execute(
        '''
        INSERT OR REPLACE INTO Settings (id, value)
        VALUES (?1, ?2)
        ''', ('dailyQuestPrice', daily_quest_price)
    )

    db.execute(
        '''
        INSERT OR REPLACE INTO Settings (id, value)
        VALUES (?1, ?2)
        ''', ('coinsPerDay', coins_per_day)
    )

    db.commit()


@router.get('/until-midnight')
async def until_midnight():
    return seconds_until_midnight(time())


@router.get('/user/status')
async def user_status(
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):

    user_address = user_address.lower()
    db.row_factory = sqlite3.Row

    result = {
        'last_quest': None,
        'day': None,
        'today_daily_quests': None,
        'today_coins': None,
    }

    today_coins = db.execute(
        '''
        SELECT coin
        FROM TodayCoins
        WHERE user = ?1 AND is_collected = 0
        ''', (user_address,)
    ).fetchall()
    if not today_coins:
        today_coins = []
    today_coins = [today_coin['coin'] for today_coin in today_coins]
    result['today_coins'] = today_coins

    last_quest = db.execute(
        '''
        SELECT cq.quest, q.quest_order, q.day, cq.timestamp
        FROM CompletedQuests cq
        JOIN Quests q ON cq.quest = q.id
        WHERE cq.user = ?1
        ORDER BY q.day DESC, q.quest_order DESC
        LIMIT 1
        ''', (user_address,)
    ).fetchone()

    if not last_quest:
        return result
    else: 
        last_quest = dict(last_quest)
        result['last_quest'] = {'quest': last_quest['quest'], 'order': last_quest['quest_order']}

    last_day_quest = db.execute(
            '''
            SELECT q.id
            FROM Quests q
            WHERE q.day = ?1 AND q.quest_order = (
                SELECT MAX(quest_order)
                FROM Quests
                WHERE day = ?1
            )
            ''', (last_quest['day'],)
        ).fetchone()
    
    last_day_quest_id = last_day_quest['id']

    if last_quest['quest'] == last_day_quest_id:

        day = last_quest['day']
        last_day = db.execute(
            '''
            SELECT MAX(day)
            FROM Quests
            '''
        ).fetchone()[0]

        if day == last_day and seconds_until_midnight(last_quest['timestamp']) >= (24 * 60 * 60):
            day = 0
        elif seconds_until_midnight(last_quest['timestamp']) >= (24 * 60 * 60):
            day = last_quest['day'] + 1
    else:
        day = last_quest['day']
    result['day'] = day


    today_daily_quests = db.execute(
        '''
        SELECT COUNT(*) AS count
        FROM CompletedDaily
        WHERE user = ?1 AND ?2 - timestamp <= (24 * 60 * 60)
        ''', (user_address, time() + seconds_until_midnight(time()))
    ).fetchone()
    
    if not today_daily_quests:
        today_daily_quests = 0
    else: today_daily_quests = today_daily_quests['count']
    result['today_daily_quests'] = today_daily_quests

    return result
