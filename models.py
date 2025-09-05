from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum

Base = declarative_base()

class SeatType(str, Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    VIP = "VIP"
    GENERAL = "GENERAL"

class EventType(str, Enum):
    MOVIE = "MOVIE"
    COMEDY_SHOW = "COMEDY_SHOW"
    SPORTS = "SPORTS"
    CONCERT = "CONCERT"

class SeatStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    BLOCKED = "BLOCKED"

class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class PaymentMethod(str, Enum):
    UPI = "UPI"
    CARD = "CARD"
    NETBANKING = "NETBANKING"
    WALLET = "WALLET"

class PaymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    bookings = relationship("Booking", back_populates="user")

class Venue(Base):
    __tablename__ = "venues"
    
    venue_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    capacity = Column(Integer, nullable=False)
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    sections = relationship("Section", back_populates="venue")
    event_seats = relationship("EventSeat", back_populates="venue")
    schedules = relationship("Schedule", back_populates="venue")

class Section(Base):
    __tablename__ = "sections"
    
    section_id = Column(BigInteger, primary_key=True, autoincrement=True)
    venue_id = Column(BigInteger, ForeignKey("venues.venue_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    venue = relationship("Venue", back_populates="sections")
    seats = relationship("Seat", back_populates="section")
    schedules = relationship("Schedule", back_populates="section")

class Seat(Base):
    __tablename__ = "seats"
    
    seat_id = Column(BigInteger, primary_key=True, autoincrement=True)
    section_id = Column(BigInteger, ForeignKey("sections.section_id", ondelete="CASCADE"), nullable=False)
    row_label = Column(String(5), nullable=False)
    seat_number = Column(Integer, nullable=False)
    seat_type = Column(String(20), nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        CheckConstraint("seat_type IN ('REGULAR', 'PREMIUM', 'VIP', 'GENERAL')", name="check_seat_type"),
        UniqueConstraint("section_id", "row_label", "seat_number", name="unique_seat_position"),
    )
    
    section = relationship("Section", back_populates="seats")
    event_seats = relationship("EventSeat", back_populates="seat")
    schedule_seats = relationship("ScheduleSeat", back_populates="seat")

class Event(Base):
    __tablename__ = "events"
    
    event_id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    event_type = Column(String(20), nullable=False)
    description = Column(Text)
    language = Column(String(50))
    genre = Column(String(50))
    duration = Column(Integer)  # in minutes
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        CheckConstraint("event_type IN ('MOVIE', 'COMEDY_SHOW', 'SPORTS', 'CONCERT')", name="check_event_type"),
    )
    
    event_seats = relationship("EventSeat", back_populates="event")
    schedules = relationship("Schedule", back_populates="event")
    bookings = relationship("Booking", back_populates="event")

class EventSeat(Base):
    __tablename__ = "event_seats"
    
    event_seat_id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id = Column(BigInteger, ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False)
    venue_id = Column(BigInteger, ForeignKey("venues.venue_id", ondelete="CASCADE"), nullable=False)
    seat_id = Column(BigInteger, ForeignKey("seats.seat_id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="AVAILABLE")
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        CheckConstraint("status IN ('AVAILABLE', 'BOOKED', 'BLOCKED')", name="check_event_seat_status"),
    )
    
    event = relationship("Event", back_populates="event_seats")
    venue = relationship("Venue", back_populates="event_seats")
    seat = relationship("Seat", back_populates="event_seats")
    booking_seats = relationship("BookingSeat", back_populates="event_seat")

class Schedule(Base):
    __tablename__ = "schedules"
    
    schedule_id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id = Column(BigInteger, ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False)
    venue_id = Column(BigInteger, ForeignKey("venues.venue_id", ondelete="CASCADE"), nullable=False)
    section_id = Column(BigInteger, ForeignKey("sections.section_id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    event = relationship("Event", back_populates="schedules")
    venue = relationship("Venue", back_populates="schedules")
    section = relationship("Section", back_populates="schedules")
    schedule_seats = relationship("ScheduleSeat", back_populates="schedule")
    bookings = relationship("Booking", back_populates="schedule")

class ScheduleSeat(Base):
    __tablename__ = "schedule_seats"
    
    schedule_seat_id = Column(BigInteger, primary_key=True, autoincrement=True)
    schedule_id = Column(BigInteger, ForeignKey("schedules.schedule_id", ondelete="CASCADE"), nullable=False)
    seat_id = Column(BigInteger, ForeignKey("seats.seat_id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default="AVAILABLE")
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        CheckConstraint("status IN ('AVAILABLE', 'BOOKED', 'BLOCKED')", name="check_schedule_seat_status"),
        UniqueConstraint("schedule_id", "seat_id", name="unique_schedule_seat"),
    )
    
    schedule = relationship("Schedule", back_populates="schedule_seats")
    seat = relationship("Seat", back_populates="schedule_seats")
    booking_seats = relationship("BookingSeat", back_populates="schedule_seat")

class Booking(Base):
    __tablename__ = "bookings"
    
    booking_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    event_id = Column(BigInteger, ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False)
    schedule_id = Column(BigInteger, ForeignKey("schedules.schedule_id", ondelete="CASCADE"))  # NULL if one-time event
    event_seat_id = Column(BigInteger, ForeignKey("event_seats.event_seat_id", ondelete="CASCADE"))  # NULL if recurring
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        CheckConstraint("status IN ('PENDING', 'CONFIRMED', 'CANCELLED')", name="check_booking_status"),
    )
    
    user = relationship("User", back_populates="bookings")
    event = relationship("Event", back_populates="bookings")
    schedule = relationship("Schedule", back_populates="bookings")
    booking_seats = relationship("BookingSeat", back_populates="booking")
    payments = relationship("Payment", back_populates="booking")

class BookingSeat(Base):
    __tablename__ = "booking_seats"
    
    booking_seat_id = Column(BigInteger, primary_key=True, autoincrement=True)
    booking_id = Column(BigInteger, ForeignKey("bookings.booking_id", ondelete="CASCADE"), nullable=False)
    event_seat_id = Column(BigInteger, ForeignKey("event_seats.event_seat_id", ondelete="CASCADE"))  # for one-time event
    schedule_seat_id = Column(BigInteger, ForeignKey("schedule_seats.schedule_seat_id", ondelete="CASCADE"))  # for recurring
    created_at = Column(DateTime, default=func.current_timestamp())
    
    __table_args__ = (
        CheckConstraint(
            "(event_seat_id IS NOT NULL AND schedule_seat_id IS NULL) OR (event_seat_id IS NULL AND schedule_seat_id IS NOT NULL)",
            name="check_seat_reference"
        ),
    )
    
    booking = relationship("Booking", back_populates="booking_seats")
    event_seat = relationship("EventSeat", back_populates="booking_seats")
    schedule_seat = relationship("ScheduleSeat", back_populates="booking_seats")

class Payment(Base):
    __tablename__ = "payments"
    
    payment_id = Column(BigInteger, primary_key=True, autoincrement=True)
    booking_id = Column(BigInteger, ForeignKey("bookings.booking_id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    transaction_id = Column(String(100))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        CheckConstraint("payment_method IN ('UPI', 'CARD', 'NETBANKING', 'WALLET')", name="check_payment_method"),
        CheckConstraint("status IN ('SUCCESS', 'FAILED', 'PENDING')", name="check_payment_status"),
    )
    
    booking = relationship("Booking", back_populates="payments")
