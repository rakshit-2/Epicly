### Events -----------------------------------------

## GET /events/{event_id}/schedules

### Curl
```
curl -X 'GET' \
  'http://localhost:8000/events/2/schedules?date=2025-09-12&venue=Inox%20Forum%20Mall&city=Bangalore' \
  -H 'accept: application/json'
```
### Response
```
[
  {
    "schedule_id": 48,
    "event_id": 2,
    "venue_id": 2,
    "section_id": 3,
    "start_time": "2025-09-12T02:35:28.102260",
    "end_time": "2025-09-12T06:12:28.102260",
    "venue_name": "Inox Forum Mall",
    "section_name": "Screen 1",
    "city": "Bangalore"
  },
  {
    "schedule_id": 49,
    "event_id": 2,
    "venue_id": 2,
    "section_id": 4,
    "start_time": "2025-09-12T15:35:28.102260",
    "end_time": "2025-09-12T19:12:28.102260",
    "venue_name": "Inox Forum Mall",
    "section_name": "Screen 2",
    "city": "Bangalore"
  },
  {
    "schedule_id": 50,
    "event_id": 2,
    "venue_id": 2,
    "section_id": 4,
    "start_time": "2025-09-12T19:35:28.102260",
    "end_time": "2025-09-12T23:12:28.102260",
    "venue_name": "Inox Forum Mall",
    "section_name": "Screen 2",
    "city": "Bangalore"
  },
  {
    "schedule_id": 51,
    "event_id": 2,
    "venue_id": 2,
    "section_id": 4,
    "start_time": "2025-09-12T23:35:28.102260",
    "end_time": "2025-09-13T03:12:28.102260",
    "venue_name": "Inox Forum Mall",
    "section_name": "Screen 2",
    "city": "Bangalore"
  }
]
```


### Schedules -----------------------------------------


## GET /schedules/{schedule_id}/seats

### Curl
```
curl -X 'GET' \
  'http://localhost:8000/schedules/49/seats' \
  -H 'accept: application/json'
```
### Response
```
[
  {
    "seat_id": 301,
    "row_label": "A",
    "seat_number": 1,
    "seat_type": "PREMIUM",
    "base_price": "300.00",
    "status": "AVAILABLE"
  },
  {
    "seat_id": 302,
    "row_label": "A",
    "seat_number": 2,
    "seat_type": "PREMIUM",
    "base_price": "300.00",
    "status": "AVAILABLE"
  },
  ...
]
```

### Seats Lockking -----------------------------------------

## POST /seats/lock

### Curl
```
curl -X 'POST' \
  'http://localhost:8000/seats/lock' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "schedule_id": 49,
  "seat_ids": [
    301, 302, 303
  ]
}'
```
### Response
```
{
  "status": "success",
  "message": "Seats [301, 302, 303] locked for 5 minutes",
  "schedule_id": 49,
  "locked_seats": [
    301,
    302,
    303
  ],
  "expires_at": "2025-09-06T06:39:20.279123"
}
```

### bookings -----------------------------------------


## POST /bookings

### Curl
```
curl -X 'POST' \
  'http://localhost:8000/bookings' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 1,
  "event_id": 2,
  "schedule_id": 49,
  "seat_ids": [
    301, 302, 303
  ],
  "payment_method": "UPI"
}'
```
### Response
```
{
  "booking_id": 1,
  "user_id": 1,
  "event_id": 2,
  "schedule_id": 49,
  "amount": "900.00",
  "status": "PENDING",
  "total_amount": "900.00",
  "payment_link": "https://payment.epicly.com/pay/1"
}
```

## GET /bookings/{booking_id}

### Curl
```
curl -X 'GET' \
  'http://localhost:8000/bookings/1' \
  -H 'accept: application/json'
```
### Response
```
{
  "booking_id": 1,
  "user": {
    "user_id": 1,
    "name": "Rakshit Sharma",
    "email": "rakshit@email.com"
  },
  "event": {
    "event_id": 2,
    "title": "RRR",
    "event_type": "MOVIE"
  },
  "schedule": {
    "schedule_id": 49,
    "start_time": "2025-09-12T15:35:28.102260",
    "end_time": "2025-09-12T19:12:28.102260"
  },
  "seats": [
    {
      "seat_id": 301,
      "row_label": "A",
      "seat_number": 1,
      "seat_type": "PREMIUM",
      "base_price": "300.00"
    },
    {
      "seat_id": 302,
      "row_label": "A",
      "seat_number": 2,
      "seat_type": "PREMIUM",
      "base_price": "300.00"
    },
    {
      "seat_id": 303,
      "row_label": "A",
      "seat_number": 3,
      "seat_type": "PREMIUM",
      "base_price": "300.00"
    }
  ],
  "amount": "900.00",
  "status": "CONFIRMED",
  "created_at": "2025-09-06T06:34:46.032583"
}
```

### Payments -----------------------------------------


## POST /payments

### Curl
```
curl -X 'POST' \
  'http://localhost:8000/payments' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "booking_id": 1,
  "amount": 900,
  "method": "UPI"
}'
```
### Response
```
{
  "payment_id": 1,
  "booking_id": 1,
  "amount": "900.00",
  "payment_method": "UPI",
  "status": "SUCCESS",
  "transaction_id": "652a1ba8-292c-4b8a-b1af-cd98a3d7b76c"
}
```

## GET /payments/{payment_id}

### Curl
```
curl -X 'GET' \
  'http://localhost:8000/payments/1' \
  -H 'accept: application/json'
```
### Response
```
{
  "payment_id": 1,
  "booking_id": 1,
  "amount": "900.00",
  "payment_method": "UPI",
  "status": "SUCCESS",
  "transaction_id": "652a1ba8-292c-4b8a-b1af-cd98a3d7b76c"
}
```

### Users -----------------------------------------

## POST /users/register

### Curl
```
curl -X 'POST' \
  'http://localhost:8000/users/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Ashutosh",
  "email": "ashutosh@email.com",
  "phone": "12345678910"
}'
```
### response
```
{
  "status": "success",
  "message": "User registered successfully",
  "user_id": 4,
  "name": "Ashutosh",
  "email": "ashutosh@email.com"
}
```


## POST /users/login

### Curl
```
curl -X 'POST' \
  'http://localhost:8000/users/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "rakshit@email.com"
}'
```
### response
```
{
  "status": "success",
  "message": "Login successful",
  "user_id": 1,
  "name": "Rakshit Sharma",
  "email": "rakshit@email.com"
}
```

## GET /users/{user_id}/bookings

### Curl
```
curl -X 'GET' \
  'http://localhost:8000/users/1/bookings' \
  -H 'accept: application/json'
```
### response
```
{
  "user_id": 1,
  "bookings": [
    {
      "booking_id": 1,
      "event": {
        "event_id": 2,
        "title": "RRR",
        "event_type": "MOVIE"
      },
      "schedule": {
        "schedule_id": 49,
        "start_time": "2025-09-12T15:35:28.102260",
        "end_time": "2025-09-12T19:12:28.102260"
      },
      "amount": 900,
      "status": "CONFIRMED",
      "created_at": "2025-09-06T06:34:46.032583",
      "is_upcoming": true
    }
  ]
}
```
