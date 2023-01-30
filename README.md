example config.yml
```
openai:
  api_key: <your openai api key>
  organization: <your openai organization identifier>
  model: "text-davinci-003"
  max_tokens_per_request: 500

telegram:
  bot_key: <your bot key>
  chat_id: <your chat id>
  polling_interval_in_seconds: 3

environment_files:
    data: "src/data.json"
    log: "logs/wg_bot_log.json"

```

example data/data.json
```
{
 "persons": [
  {
   "id": 0,
   "name": "Name1",
   "is_present": true,
   "karma": 100,
   "consumable_ids": [
    0,
    1,
    2,
    4
   ],
   "current_task_ids": [
    2
   ],
   "weekly_task_history_ids": [
    2,
    5,
    5
   ]
  },
  {
   "id": 1,
   "name": "Name2",
   "is_present": false,
   "karma": 100,
   "consumable_ids": [
    3,
    8,
    6
   ],
   "current_task_ids": [],
   "weekly_task_history_ids": []
  },
  {
   "id": 2,
   "name": "Name3",
   "is_present": true,
   "karma": 100,
   "consumable_ids": [
    5,
    7
   ],
   "current_task_ids": [
    3,
    4
   ],
   "weekly_task_history_ids": [
    3
   ]
  }
 ],
 "consumables": [
  {
   "id": 0,
   "name": "toilet paper",
   "is_available": true
  },
  {
   "id": 1,
   "name": "dish soap",
   "is_available": true
  },
  {
   "id": 2,
   "name": "sponges",
   "is_available": true
  },
  {
   "id": 3,
   "name": "trash bags",
   "is_available": true
  },
  {
   "id": 4,
   "name": "cleaning cloth",
   "is_available": true
  },
  {
   "id": 5,
   "name": "detergent",
   "is_available": true
  },
  {
   "id": 6,
   "name": "scrubbing milk",
   "is_available": true
  },
  {
   "id": 7,
   "name": "soap",
   "is_available": true
  },
  {
   "id": 8,
   "name": "zewa",
   "is_available": true
  }
 ],
 "tasks": [
  {
   "id": 0,
   "is_weekly": true,
   "name": "bathroom",
   "is_done": false
  },
  {
   "id": 1,
   "is_weekly": true,
   "name": "kitchen",
   "is_done": false
  },
  {
   "id": 2,
   "is_weekly": true,
   "name": "floor",
   "is_done": false
  },
  {
   "id": 3,
   "is_weekly": false,
   "name": "peter",
   "is_done": false
  },
  {
   "id": 4,
   "is_weekly": false,
   "name": "trash",
   "is_done": false
  },
  {
   "id": 5,
   "is_weekly": false,
   "name": "airing",
   "is_done": false
  }
 ]
}

```