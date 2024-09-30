
import json 
import pandas as pd
import numpy as np
import argparse
import os
import aiofiles
import asyncio
import aiohttp

api_url = None 
path_to_data = None 
request_type = None

async def get_game_stats(game_id):
    url = api_url + game_id + "/" + request_type
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data

def build_id(year, type, game_number, round=None, match=None):
    if round is None and match is None:
        game = game_number
    else:
        game = game_number + 10 * match + 100 * (round - 1)
    if type == 3:
        expect_0 = game // 1000
        round_num =game % 1000 // 100
        match_up = game % 100 // 10
        game_num = game % 10
        if expect_0 != 0 or round_num > 4 or match_up > 2 or game_num > 7:
            return False
    return str(year) + str(type).zfill(2) + str(game).zfill(4)

async def save_game_stats(game_id):
    try:
        response = await get_game_stats(game_id)
        async with aiofiles.open(f"{path_to_data}/{request_type}/{game_id}.json", "w") as f:
            await f.write(json.dumps(response))
        async with aiofiles.open("download.log", "a") as f:
            await f.write(f"Downloaded {game_id}\n\n")
    except Exception as e:
        async with aiofiles.open("fail.log", "a") as fail_log:
            await fail_log.write(f"----------------------------------------\n")
            await fail_log.write(f"Error on {game_id}\n")
            await fail_log.write(f"{e}\n")
            await fail_log.write(f"----------------------------------------\n\n")

async def pull_stats(year_start, year_end):
    print("Starting")
    tasks = []
    with open("download.log", "a") as download_log, open("fail.log", 'a') as fail_log:
        download_log.write(f"--------------------------------------------------------------\nStarting download from {year_start} to {year_end}\n--------------------------------------------------------------\n\n")
        fail_log.write(f"--------------------------------------------------------------\nStarting download from {year_start} to {year_end}\n--------------------------------------------------------------\n\n")
    for season in range(year_start, year_end):
        for type in [1, 2]:
            for game in range(1, 2000):
                game_id = build_id(season, type, game)
                if os.path.exists(f"{path_to_data}/{request_type}/{game_id}.json"):
                    with open("fail.log", "a") as fail_log:
                        fail_log.write(f"Already downloaded {game_id}\n\n")
                    continue
                tasks.append(save_game_stats(game_id))
        for round in range(1, 5):
            for match in range(1, 3):
                for game in range(1, 8):
                    game_id = build_id(season, 3, game, round, match)
                    if os.path.exists(f"{path_to_data}/{request_type}/{game_id}.json"):
                        with open("fail.log", "a") as fail_log:
                            fail_log.write(f"Already downloaded {game_id}\n\n")
                        continue
                    tasks.append(save_game_stats(game_id))    
    await asyncio.gather(*tasks)

    async with open("download.log", "a") as download_log, open("fail.log", 'a') as fail_log:
        await download_log.write(f"--------------------------------------------------------------\nCompleted download from {year_start} to {year_end}\n--------------------------------------------------------------\n\n")
        await fail_log.write(f"--------------------------------------------------------------\nCompleted download from {year_start} to {year_end}\n--------------------------------------------------------------\n\n")
    print("Done")
    

async def main():
    global path_to_data
    global request_type
    global api_url
    
    parser = argparse.ArgumentParser(description='Download stats from NHL API')
    parser.add_argument('--inputs', '-i', type=str, help='Path to the store data + api url', default='ift6758/data')
    parser.add_argument('--start', '-s', type=int, help='Start year', default=2000)
    parser.add_argument('--end', '-e', type=int, help='End year', default=2021)
    parser.add_argument('--requested', '-r', type=str, help='The api request', default=path_to_data)
    args = parser.parse_args()
    inputs = json.load(open(args.inputs))
    path_to_data = inputs["path_to_data"]
    api_url = inputs["api_url"]
    
    if not os.path.exists(path_to_data + "/" + request_type):
        os.makedirs(path_to_data + "/" + request_type)
    request_type = args.requested
    await pull_stats(args.start, args.end)

if __name__ == "__main__":
    asyncio.run(main())
    

