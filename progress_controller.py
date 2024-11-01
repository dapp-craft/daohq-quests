from fastapi import APIRouter, Depends

from tools import db_connection, validate_auth_chain


router = APIRouter()


@router.delete('/progress')
async def delete_progress(
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):

    db.execute(
        '''
        DELETE FROM CompletedQuests
        WHERE user = ?1
        ''', (user_address,)
    )

    db.commit()


@router.delete('/progress/daily')
async def delete_daily_progress(
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):

    db.execute(
        '''
        DELETE FROM CompletedDaily
        WHERE user = ?1
        ''', (user_address,)
    )

    db.commit()


@router.delete('/rewards')
async def delete_rewards(
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):

    db.execute(
        '''
        DELETE FROM CollectedRewards
        WHERE user = ?1
        ''', (user_address,)
    )

    db.commit()


@router.delete('/progress/coins')
async def delete_coints_progress(
    db=Depends(db_connection),
    user_address=Depends(validate_auth_chain)
):
    
    db.execute(
        '''
        UPDATE TodayCoins
        SET is_collected = 0
        WHERE user = ?1
        ''', (user_address,)
    )
    
    db.commit()
