# Schema for BookMyShow(LLD)

Table Users {
  user_id BIGINT [pk, increment]
  name VARCHAR(100)
  email VARCHAR(100) [unique]
}

Table Venues {
  venue_id BIGINT [pk, increment]
  name VARCHAR(200)
  location VARCHAR(200)
  capacity INT
}

Table Sections {
  section_id BIGINT [pk, increment]
  venue_id BIGINT [ref: > Venues.venue_id]
  name VARCHAR(100) -- e.g. Screen 1, VIP Zone, Stand A
  capacity INT
}

Table Seats {
  seat_id BIGINT [pk, increment]
  section_id BIGINT [ref: > Sections.section_id]
  row_label VARCHAR(5)
  seat_number INT
  seat_type VARCHAR(20) -- REGULAR, PREMIUM, VIP, GENERAL
  base_price DECIMAL(10,2)
}

Table Events {
  event_id BIGINT [pk, increment]
  title VARCHAR(200)
  event_type VARCHAR(20) -- MOVIE, COMEDY_SHOW, SPORTS, CONCERT
  description TEXT
  language VARCHAR(50)
  genre VARCHAR(50)
  duration INT -- minutes (movies/comedy)
  created_at TIMESTAMP
}

Table EventSeats {
  event_seat_id BIGINT [pk, increment]
  event_id BIGINT [ref: > Events.event_id]
  venue_id BIGINT [ref: > Venues.venue_id]
  seat_id BIGINT [ref: > Seats.seat_id]
  start_time DATETIME
  end_time DATETIME
  status VARCHAR(20) -- AVAILABLE, BOOKED, BLOCKED
}

Table Schedules {
  schedule_id BIGINT [pk, increment]
  event_id BIGINT [ref: > Events.event_id]
  venue_id BIGINT [ref: > Venues.venue_id]
  section_id BIGINT [ref: > Sections.section_id]
  start_time DATETIME
  end_time DATETIME
}

Table ScheduleSeats {
  schedule_seat_id BIGINT [pk, increment]
  schedule_id BIGINT [ref: > Schedules.schedule_id]
  seat_id BIGINT [ref: > Seats.seat_id]
  status VARCHAR(20) -- AVAILABLE, BOOKED, BLOCKED
}

Table Bookings {
  booking_id BIGINT [pk, increment]
  user_id BIGINT [ref: > Users.user_id]
  event_id BIGINT [ref: > Events.event_id]
  schedule_id BIGINT [ref: > Schedules.schedule_id]
  event_seat_id BIGINT [ref: > EventSeats.event_seat_id]
  amount DECIMAL(10,2)
  status VARCHAR(20) -- PENDING, CONFIRMED, CANCELLED
  created_at TIMESTAMP
}

Table Payments {
  payment_id BIGINT [pk, increment]
  booking_id BIGINT [ref: > Bookings.booking_id]
  amount DECIMAL(10,2)
  payment_method VARCHAR(20) -- UPI, CARD, NETBANKING, WALLET
  status VARCHAR(20) -- SUCCESS, FAILED
  created_at TIMESTAMP
}
