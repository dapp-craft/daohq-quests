import random
from time import time
import sqlite3
from sqlite3 import IntegrityError

from fastapi import APIRouter, Depends, HTTPException

from tools import db_connection, validate_auth_chain, register_user, get_user_points, seconds_until_midnight


router = APIRouter()


@router.post('/pickup/coin/{coin_id}')
async def pickup_coin(
    coin_id,
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):

    coin_price = db.execute(
        '''
        SELECT price
        FROM Coins
        WHERE id = ?1
        ''', (coin_id,)
    ).fetchone()

    if not coin_price:
        raise HTTPException(status_code=400, detail="This coin does not exist")
    else:
        coin_price = coin_price[0]
    
    register_user(db, user_address)

    try:
        db.execute(
            '''
            UPDATE TodayCoins
            SET is_collected = 1
            WHERE user = ?1 AND coin = ?2
            ''', (user_address, coin_id)
        )

    except IntegrityError:
        raise HTTPException(status_code=400, detail="This coin has already been collected") 
    
    db.commit()


@router.get('/coins')
async def get_coins(
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):

    coins = db.execute(
        '''
        SELECT SUM(collected_coins)
        FROM ResetCoinsHistory
        WHERE user = ?1
        ''', (user_address,)
    ).fetchall()

    coins = [int(coin[0]) for coin in coins]

    return coins


@router.get('/points')
async def user_points(
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):
    user_address = user_address.lower()
    user_points = await get_user_points(user_address, db)
    return user_points


@router.put('/update/coins')
async def update_today_coins(
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):

    db.row_factory = sqlite3.Row

    last_reset_time = db.execute(
        '''
        SELECT timestamp
        FROM ResetCoinsHistory
        WHERE user = ?1
        ORDER BY timestamp DESC
        LIMIT 1
        ''', (user_address,)
    ).fetchone()
    
    if last_reset_time:
        last_reset_time = last_reset_time['timestamp']

    if last_reset_time and not seconds_until_midnight(last_reset_time) >= (24 * 60 * 60):
        return
    
    coins_data = db.execute(
        '''
        SELECT COUNT(tc.id) AS count, SUM(c.price) AS price
        FROM TodayCoins tc
        JOIN Coins c ON c.id = tc.coin  
        WHERE tc.user = ?1 AND tc.is_collected = 1
        ''', (user_address,)
    ).fetchone()

    collected_coins_count = coins_data['count']
    collected_coins_price = coins_data['price']

    db.execute(
        '''
        DELETE FROM TodayCoins
        WHERE user = ?1
        ''', (user_address,)
    )

    db.execute(
        '''
        INSERT INTO ResetCoinsHistory (timestamp, user, collected_coins, collected_coins_price)
        VALUES(?1, ?2, ?3, ?4)
        ''', (int(time()), user_address, collected_coins_count, collected_coins_price)
    )

    cursor = db.execute("SELECT id FROM Coins")
    coin_ids = cursor.fetchall()

    random_coin_ids = random.sample([coin[0] for coin in coin_ids], 60)

    values = [(user_address, coin_id) for coin_id in random_coin_ids]

    query = "INSERT INTO TodayCoins (user, coin) VALUES (?, ?)"
    cursor.executemany(query, values)

    db.commit()