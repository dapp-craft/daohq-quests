from sqlite3 import IntegrityError
from datetime import datetime, timezone

import httpx
import asyncio
from httpx import Timeout

from fastapi import APIRouter, Depends, HTTPException

from tools import db_connection, validate_auth_chain, register_user, get_user_points, check_assigned_date

from settings import DISPENSER_KEY

router = APIRouter()

lock = asyncio.Lock()

@router.post('/pickup/reward/{reward_id}')
async def pickup_reward(
    reward_id: int,
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):

    async with lock:
        reward_data = db.execute(
            '''
            SELECT price, blockchain_id, collection
            FROM Rewards
            WHERE id = ?1
            ''', (reward_id,)
        ).fetchone()

        if not reward_data:
            raise HTTPException(status_code=400, detail="This reward does not exist")
        else:
            reward_price = reward_data[0]

        is_reward_claimed = db.execute(
            '''
            SELECT id
            FROM CollectedRewards
            WHERE reward = ?1 AND user = ?2
            ''', (reward_id, user_address)
        ).fetchone()

        if is_reward_claimed:
            raise HTTPException(status_code=400, detail="This reward has already been collected") 
            
        register_user(db, user_address)

        previus_rewards_count = db.execute(
            '''
            SELECT COUNT(*)
            FROM CollectedRewards cr
            JOIN Rewards r ON r.id = cr.reward
            WHERE cr.user = ?1 AND r.price < ?2
            ''', (user_address, reward_price)
        ).fetchone()

        collected_rewards_count = db.execute(
            '''
            SELECT COUNT(*)
            FROM CollectedRewards
            WHERE user = ?1
            ''', (user_address,)
        ).fetchone()
        
        if previus_rewards_count != collected_rewards_count:
            raise HTTPException(status_code=403, detail='You can not get this reward')

        user_points = await get_user_points(user_address, db)

        if  user_points < reward_price:
            raise HTTPException(status_code=403, detail='Insufficient points for this reward')
        current_date = datetime.now(timezone.utc)

        async with httpx.AsyncClient(timeout=Timeout(None, connect=15.0)) as client:
            print(f"Trying to claim reward {reward_id} for {user_address}...")
            response = await client.post(
                'https://rewards.decentraland.org/api/rewards',
                json={
                    'campaign_key': DISPENSER_KEY,
                    'beneficiary': user_address,
                    'assign_target': reward_data[2],
                    'assign_value': str(reward_data[1])
                }
            )

            if response.status_code >= 300:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            data = response.json().get('data')
            print(response.json())

            if data:
                try:
                    actual_data = [el for el in data if check_assigned_date(el['assigned_at'], current_date)]
                    actual_data = [el for el in actual_data if el['status'] != 'rejected' and el['target'] == reward_data[2] and el['value'] == str(reward_data[1])]
                except Exception:
                    print("Malformed response from RewardAPI, assuming reward is minted")
                    actual_data = [{id: "<INVALID>"}]

                if len(actual_data) >= 2:
                    print('WE RECEIVED MORE THAN 1 REWARDS IN RESPONSE!!!')

                if actual_data:
                    response_reward_id = actual_data[0]['id']
                    try:
                        db.execute(
                            '''
                            INSERT INTO CollectedRewards (user, reward, reward_id)
                            VALUES (?1, ?2, ?3)
                            ''', (user_address, reward_id, response_reward_id)
                        )
                    except IntegrityError:
                        raise HTTPException(status_code=400, detail="This reward has already been collected")
                    
                else: raise HTTPException(status_code=503, detail="Reward API temporary unavailable")
            else: raise HTTPException(status_code=503, detail="Reward API temporary unavailable")


        return {"status": "Suit is on its way to your wallet"}


@router.get('/rewards')
async def user_rewards(
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):
    
    rewards = db.execute(
        '''
        SELECT reward
        FROM CollectedRewards
        WHERE user = ?1
        ''', (user_address,)
    ).fetchall()

    rewards = [int(reward[0]) for reward in rewards]

    return rewards