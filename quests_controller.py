from sqlite3 import IntegrityError
from time import time

from fastapi import APIRouter, Depends, HTTPException

from tools import db_connection, validate_auth_chain, seconds_until_midnight, register_user


router = APIRouter()

@router.post('/complete/daily')
async def complete_daily_quest(
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):

    cursor = db.cursor()

    register_user(db, user_address)

    last_quest_timestamp = cursor.execute(
        '''
        SELECT timestamp
        FROM CompletedDaily
        WHERE user = ?1
        ORDER BY timestamp DESC
        LIMIT 1
        ''', (user_address,)
    ).fetchone()

    completed_quests_today = cursor.execute(
        '''
        SELECT COUNT(*)
        FROM CompletedDaily
        WHERE user = ?1 AND ?2 - timestamp <= (24 * 60 * 60)
        ''', (user_address, time() + seconds_until_midnight(time()))
    ).fetchone()
    
    if last_quest_timestamp:
        last_quest_timestamp = last_quest_timestamp = last_quest_timestamp[0]
        completed_quests_today = completed_quests_today[0]

        daily_quest_per_day = db.execute(
            '''
            SELECT value
            FROM Settings
            WHERE id = "dailyQuestPerDay"
            '''
        ).fetchone()[0]


        if seconds_until_midnight(last_quest_timestamp) <= (24 * 60 * 60) and completed_quests_today >= daily_quest_per_day:
            raise HTTPException(status_code=400, detail="Too many daily quests for today")
        # elif seconds_until_midnight(last_quest_timestamp) >= (24 * 60 * 60):
        #     cursor.execute(
        #         '''
        #         DELETE FROM CollectedCoins
        #         WHERE user = ?1   
        #         ''', (user_address,)
        #     )
    
    last_quest = db.execute(
        '''
        SELECT cq.timestamp
        FROM CompletedQuests cq
        JOIN Quests q ON cq.quest = q.id
        WHERE cq.user = ?1
        ORDER BY q.day DESC, q.quest_order DESC
        LIMIT 1
        ''', (user_address,)
    ).fetchone()
        
    if not last_quest or seconds_until_midnight(last_quest[0]) <= (24 * 60 * 60):
        raise HTTPException(status_code=400, detail="Daily quests haven't started")
    
    cursor.execute(
        '''
        INSERT INTO CompletedDaily (user, timestamp)
        VALUES (?1, ?2)
        ''', (user_address, int(time()))
    )

    db.commit()

    if not cursor.rowcount:
        raise HTTPException(status_code=500) 


@router.post('/complete')
async def complete_quest(
    quest_id,
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):
    cursor = db.cursor()

    register_user(db, user_address)

    try:
        quest_order, day, reward_count, minimum_order = cursor.execute(
            '''
            SELECT quest_order, day, reward_count, (
                SELECT MIN(quest_order)
                FROM Quests
                WHERE day = day
            ) AS minimum_order
            FROM Quests
            WHERE id = ?1
            ''', (quest_id,)
        ).fetchone()[0:4]
    except TypeError:
        raise HTTPException(status_code=400, detail="This quest does not exist")

    if quest_order > minimum_order:
        previus_completed_quest = cursor.execute(
            '''
            SELECT cq.id
            FROM CompletedQuests cq
            JOIN Quests q ON q.id = cq.quest
            WHERE q.day = ?1 AND q.quest_order = ?2 AND cq.user = ?3
            ''', (day, quest_order-1, user_address)
        ).fetchone()
        if not previus_completed_quest:
            raise HTTPException(status_code=400, detail="You did not complete previus day")
        else:
            pass
    elif day == 1:
        pass
    else:
        last_completed_quest = cursor.execute(
            '''
            SELECT cq.timestamp
            FROM CompletedQuests cq
            JOIN Quests q ON q.id = cq.quest
            WHERE q.day = ?1 AND cq.user = ?2 AND q.quest_order = (
                SELECT MAX(quest_order)
                FROM Quests
                WHERE day = ?1
            )
            ''', (day-1, user_address)
        ).fetchone()
        if not last_completed_quest:
            raise HTTPException(status_code=400, detail="You did not complete previus day")
        else:
            last_quest_timestamp = last_completed_quest[0]
            if seconds_until_midnight(last_quest_timestamp) <= (24 * 60 * 60):
                raise HTTPException(status_code=400, detail="Too many quests for today")
            else:
                pass
    try:
        cursor.execute(
            '''
            INSERT INTO CompletedQuests (user, quest, timestamp)
            VALUES (?1, ?2, ?3)
            ''', (user_address, quest_id, int(time()))
        )
    except IntegrityError:
        raise HTTPException(status_code=400, detail="This quest has already been completed") 
    
    db.commit()

    return quest_id

