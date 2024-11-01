import sqlite3
import json

from time import time
from datetime import datetime, timedelta, timezone, UTC

from fastapi import Header, HTTPException, Request
from eth_utils import is_address
from eth_account.messages import encode_defunct
from web3 import Web3

from settings import SYSTEM_TOKEN, PREFIX


async def check_system_token(token = Header(alias='Authorize')):

    if token != SYSTEM_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


def validate_auth_chain(request: Request):

    # Assume that the chain contains 3 elements
    # 1. Signer
    # 2. ECDSA ephemeral
    # 3. ECDSA signed entity

    headers = {key: json.loads(value) for key, value in request.headers.items() if key.startswith('x-identity-auth-chain-')}
    
    if len(headers) == 0:
        raise HTTPException(status_code=401, detail="Auth chain is empty")
    
    header_data = headers['x-identity-auth-chain-2']['payload']
    method, path, timestamp = header_data.split(':')[:3]
    timestamp = int(timestamp)
    # print(method, path, timestamp)

    current_time = time() * 1000

    if method.lower() != request.method.lower() \
        or path != PREFIX + request.url.path \
        or (timestamp - current_time) > 10000 \
        or (current_time - timestamp) >= (5 * 60) * 1000:
            raise HTTPException(status_code=401, detail="Invalid chain")

    chain = [headers[key] for key in sorted(headers, key=lambda x: int(x.split('-')[-1]))]


    # Validate the first element
    if (chain[0]["type"] != "SIGNER"):
        raise HTTPException(status_code=401, detail="First element of auth chain must be a signer")

    # Checksum is not required
    if (not is_address(chain[0]["payload"])):
        raise HTTPException(status_code=401, detail="Invalid signer address")

    if (chain[0]["signature"] != ""):
        raise HTTPException(status_code=401, detail="First element of auth chain must not have a signature")

    # Validate the second element
    if (chain[1]["type"] != "ECDSA_EPHEMERAL"):
        raise HTTPException(status_code=401, detail="Second element of auth chain must be an ECDSA ephemeral")

    _, delegateAddress, expirationDate = parseEphemeralPayload(
        chain[1]["payload"])

    if (datetime.strptime(expirationDate, "%Y-%m-%dT%H:%M:%S.%fZ") < datetime.now()):
        raise HTTPException(status_code=401, detail="Expiration date is in the past")

    # Checksum is not required
    if (not is_address(delegateAddress)):
        raise HTTPException(status_code=401, detail="Invalid delegate address")

    validate_signature(chain[1]["payload"], chain[1]
                       ["signature"], chain[0]["payload"])

    # Validate the third element
    if (chain[2]["type"] != "ECDSA_SIGNED_ENTITY"):
        raise HTTPException(status_code=401, detail="Third element of auth chain must be an ECDSA signed entity")

    validate_signature(chain[2]["payload"], chain[2]
                       ["signature"], delegateAddress)
    
    return chain[0]['payload']
    

def parseEphemeralPayload(payload):
    """
    Verify the payload is in this form and extract the fields:
        <purpose>
        Ephemeral address: <delegate-address>
        Expiration: <date>
    """

    lines = payload.split("\n")

    if (len(lines) != 3):
        raise Exception("Invalid ECDSA ephemeral payload")

    if (lines[0] != "Decentraland Login"):
        raise Exception("Invalid ECDSA ephemeral payload")

    if (not lines[1].startswith("Ephemeral address: ")):
        raise Exception("Invalid ECDSA ephemeral payload")

    if (not lines[2].startswith("Expiration: ")):
        raise Exception("Invalid ECDSA ephemeral payload")

    purpose = lines[0]

    # Extract the delegate address
    delegateAddress = lines[1].split(": ")[1]

    # Extract the expiration date
    expirationDate = lines[2].split(": ")[1]

    # Check if the expiration date is a valid date
    try:
        datetime.strptime(expirationDate, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        raise Exception("Invalid expiration date")

    return (purpose, delegateAddress, expirationDate)


def validate_signature(message, signature, expected_address):

    try:
        # Prepare the message to match the format it had when signed
        message_encoded = encode_defunct(text=message)

        # Recover the address from the signature
        recovered_address = Web3().eth.account.recover_message(
            message_encoded, signature=signature)
    except Exception as e:
        raise Exception("Invalid signature fromat")

    # Compare the recovered address to the expected address
    if (recovered_address.lower() != expected_address.lower()):
        raise Exception("Invalid signature")



async def db_connection():

    with sqlite3.connect('database.sqlite') as db:
        yield db


def seconds_until_midnight(timestamp):
    
    timestamp = datetime.fromtimestamp(timestamp)

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    else:
        timestamp = timestamp.astimezone(UTC)

    next_midnight_utc = (datetime.now(UTC) + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    delta = next_midnight_utc - timestamp
    return delta.total_seconds()


# timestamp = datetime.now(UTC)
seconds_left = seconds_until_midnight(time())
print(f"Hours until midnight UTC: {(seconds_left / 60) / 60}")


def register_user(db, user_address):
    db.execute(
        '''
        INSERT OR IGNORE INTO Users
        (address) VALUES (?1)         
        ''', (user_address,)
    )

    db.commit()


async def get_user_points(user_address, db):
    
    today_reward_coins = db.execute(
        '''
        SELECT SUM(price)
        FROM TodayCoins cc
        JOIN Coins c ON cc.coin = c.id
        WHERE user = ?1 AND is_collected = 1
        ''', (user_address,)
    ).fetchone()
    today_reward_coins = today_reward_coins[0] or 0

    history_reward_coins = db.execute(
        '''
        SELECT SUM(collected_coins_price)
        FROM ResetCoinsHistory
        WHERE user = ?1
        ''', (user_address,)
    ).fetchone()
    history_reward_coins = history_reward_coins[0] or 0

    reward_coins = today_reward_coins + history_reward_coins
    
    reward_quests = db.execute(
        '''
        SELECT SUM(reward_count)
        FROM CompletedQuests cq
        JOIN Quests q ON cq.quest = q.id
        WHERE user = ?1
        ''', (user_address,)
    ).fetchone()

    reward_quests = reward_quests[0] or 0

    reward_daily = db.execute(
        '''
        SELECT COUNT(*)
        FROM CompletedDaily
        WHERE user = ?1
        ''', (user_address,)
    ).fetchone()

    if not reward_daily:
        reward_daily = 0
    else:
        reward_daily = reward_daily[0]

    # TODO
    if not reward_coins:
        reward_coins = 0
    if not reward_quests:
        reward_quests = 0
    if not reward_daily:
        reward_daily = 0

    daily_quest_price = db.execute(
        '''
        SELECT value
        FROM Settings
        WHERE id = "dailyQuestPrice"
        '''
    ).fetchone()[0]

    return reward_coins + reward_quests + (reward_daily * daily_quest_price)


def check_assigned_date(date_str, request_date):
    given_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    return given_date >= request_date