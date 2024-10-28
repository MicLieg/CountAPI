# Counter API

This is a simple API that allows you to increment a counter on each request and simultaneously get the current state of the counter as well as the first and last access timestamps. IP addresses and user agents are also stored to prevent abuse.

## Endpoints

### GET `/v1/count?counter=COUNTER_ID`

#### Parameters

- `counter`: The ID of the counter to increment.

#### Response

- `created_at`: The timestamp of when the counter was created.
- `count`: The current count of the counter.
- `last_access`: The timestamp of the last access to the counter.

## Setup

To store the counter data, a running and accessible MongoDB instance is required. There is a free tier available on [MongoDB Atlas](https://www.mongodb.com/pricing) that can be used for this purpose.

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create `.env` file

Copy the `.env.sample` file to `.env` and set the correct environment variables.

### Run

```bash
python main.py
```

## Test

First request:

````bash
curl http://localhost:5000/v1/count?counter=test

```json
{
  "created_at": "Mon, 28 Oct 2024 10:00:00 GMT",
  "count": 1,
  "last_access": null
}
````

Second request:

````bash
curl http://localhost:5000/v1/count?counter=test

```json
{
  "created_at": "Mon, 28 Oct 2024 10:00:00 GMT",
  "count": 2,
  "last_access": "Mon, 28 Oct 2024 10:00:00 GMT"
}
````

Third request:

````bash
curl http://localhost:5000/v1/count?counter=test

```json
{
  "created_at": "Mon, 28 Oct 2024 10:00:00 GMT",
  "count": 2,
  "last_access": "Mon, 28 Oct 2024 10:00:10 GMT"
}
````
