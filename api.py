import uuid

from database import get_db
from decimal import Decimal
from settings import settings
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from fastapi import APIRouter, Depends, HTTPException, Query
from models import (
    Event, Schedule, ScheduleSeat, Seat, Section, Venue, User, Booking, 
    BookingSeat, Payment, EventSeat, EventType, SeatStatus, BookingStatus, 
    PaymentStatus, PaymentMethod
)


router = APIRouter()


# Testing Routes  -------------------------------------------------------------------------------------------
@router.get("/")
async def root():
    return {
        "status": "success",
        "message": f"Epicly Event Booking System - {settings.ENVIRONMENT.title()}",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }

@router.get("/test")
async def test_api():
    if settings.is_production:
        return {"error": "Configuration endpoint not available in production"}
    
    return {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database": {
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "name": settings.DB_NAME,
            "user": settings.DB_USER
        },
        "server": {
            "host": settings.SERVER_HOST,
            "port": settings.SERVER_PORT
        },
    }

# Health check -------------------------------------------------------------------------------------------
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Epicly Event Booking System",
        "version": "1.0.0"
    }

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# DB calls -------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Events -------------------------------------------------------------------------------------------

class EventResponse(BaseModel):
    event_id: int
    title: str
    event_type: str
    description: Optional[str]
    language: Optional[str]
    genre: Optional[str]
    duration: Optional[int]
    
    class Config:
        from_attributes = True

@router.get("/events", response_model=List[EventResponse])
async def get_events(
    type: Optional[str] = Query(None, description="Filter by event type"),
    language: Optional[str] = Query(None, description="Filter by language"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    city: Optional[str] = Query(None, description="Filter by city"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    query = db.query(Event)
    
    if type:
        query = query.filter(Event.event_type == type.upper())
    if language:
        query = query.filter(Event.language.ilike(f"%{language}%"))
    if genre:
        query = query.filter(Event.genre.ilike(f"%{genre}%"))
    
    if city or date:
        query = query.join(Schedule).join(Venue)
        if city:
            query = query.filter(Venue.city.ilike(f"%{city}%"))
        if date:
            try:
                filter_date = datetime.strptime(date, "%Y-%m-%d").date()
                query = query.filter(func.date(Schedule.start_time) == filter_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    events = query.distinct().all()
    return events

@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event_details(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


# Schedules  -------------------------------------------------------------------------------------------

class ScheduleResponse(BaseModel):
    schedule_id: int
    event_id: int
    venue_id: int
    section_id: int
    start_time: datetime
    end_time: datetime
    venue_name: str
    section_name: str
    city: str
    
    class Config:
        from_attributes = True

class SeatResponse(BaseModel):
    seat_id: int
    row_label: str
    seat_number: int
    seat_type: str
    base_price: Decimal
    status: str
    
    class Config:
        from_attributes = True


@router.get("/events/{event_id}/schedules", response_model=List[ScheduleResponse])
async def get_event_schedules(
    event_id: int,
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    venue: Optional[str] = Query(None, description="Filter by venue name"),
    city: Optional[str] = Query(None, description="Filter by city"),
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(Event.event_id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    query = db.query(Schedule).options(
        joinedload(Schedule.venue),
        joinedload(Schedule.section)
    ).filter(
        Schedule.event_id == event_id,
        Schedule.start_time > datetime.now()
    )
    
    if date:
        try:
            filter_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(func.date(Schedule.start_time) == filter_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if venue:
        query = query.join(Venue).filter(Venue.name.ilike(f"%{venue}%"))
    
    if city:
        if not venue:
            query = query.join(Venue)
        query = query.filter(Venue.city.ilike(f"%{city}%"))
    
    schedules = query.all()
    
    response = []
    for schedule in schedules:
        response.append({
            "schedule_id": schedule.schedule_id,
            "event_id": schedule.event_id,
            "venue_id": schedule.venue_id,
            "section_id": schedule.section_id,
            "start_time": schedule.start_time,
            "end_time": schedule.end_time,
            "venue_name": schedule.venue.name,
            "section_name": schedule.section.name,
            "city": schedule.venue.city
        })
    
    return response

@router.get("/schedules/{schedule_id}/seats", response_model=List[SeatResponse])
async def get_schedule_seats(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(Schedule).filter(Schedule.schedule_id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    seats_query = db.query(
        Seat.seat_id,
        Seat.row_label,
        Seat.seat_number,
        Seat.seat_type,
        Seat.base_price,
        ScheduleSeat.status
    ).join(
        ScheduleSeat, Seat.seat_id == ScheduleSeat.seat_id
    ).filter(
        ScheduleSeat.schedule_id == schedule_id
    ).order_by(Seat.row_label, Seat.seat_number)
    
    seats = seats_query.all()
    
    response = []
    for seat in seats:
        response.append({
            "seat_id": seat.seat_id,
            "row_label": seat.row_label,
            "seat_number": seat.seat_number,
            "seat_type": seat.seat_type,
            "base_price": seat.base_price,
            "status": seat.status
        })
    
    return response


# Seat Locking -------------------------------------------------------------------------------------------

class SeatLockRequest(BaseModel):
    schedule_id: int
    seat_ids: List[int]


@router.post("/seats/lock")
async def lock_seats(request: SeatLockRequest, db: Session = Depends(get_db)):
    try:
        schedule = db.query(Schedule).filter(Schedule.schedule_id == request.schedule_id).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        schedule_seats = db.query(ScheduleSeat).filter(
            ScheduleSeat.schedule_id == request.schedule_id,
            ScheduleSeat.seat_id.in_(request.seat_ids)
        ).all()
        
        if len(schedule_seats) != len(request.seat_ids):
            raise HTTPException(status_code=400, detail="Some seats not found for this schedule")
        
        unavailable_seats = [ss.seat_id for ss in schedule_seats if ss.status != SeatStatus.AVAILABLE]
        if unavailable_seats:
            raise HTTPException(
                status_code=400, 
                detail=f"Seats {unavailable_seats} are not available"
            )
        
        for schedule_seat in schedule_seats:
            schedule_seat.status = SeatStatus.BLOCKED
            schedule_seat.updated_at = datetime.now()
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Seats {request.seat_ids} locked for 5 minutes",
            "schedule_id": request.schedule_id,
            "locked_seats": request.seat_ids,
            "expires_at": datetime.now() + timedelta(minutes=5)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Bookings -------------------------------------------------------------------------------------------

class BookingRequest(BaseModel):
    user_id: int
    event_id: int
    schedule_id: int
    seat_ids: List[int]
    payment_method: str

class BookingResponse(BaseModel):
    booking_id: int
    user_id: int
    event_id: int
    schedule_id: Optional[int]
    amount: Decimal
    status: str
    total_amount: Decimal
    payment_link: Optional[str]
    
    class Config:
        from_attributes = True

@router.post("/bookings", response_model=BookingResponse)
async def create_booking(request: BookingRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.user_id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        event = db.query(Event).filter(Event.event_id == request.event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        schedule = db.query(Schedule).filter(Schedule.schedule_id == request.schedule_id).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        schedule_seats = db.query(ScheduleSeat).join(Seat).filter(
            ScheduleSeat.schedule_id == request.schedule_id,
            ScheduleSeat.seat_id.in_(request.seat_ids)
        ).all()
        
        if len(schedule_seats) != len(request.seat_ids):
            raise HTTPException(status_code=400, detail="Some seats not found")
        
        unavailable_seats = [
            ss.seat_id for ss in schedule_seats 
            if ss.status not in [SeatStatus.AVAILABLE, SeatStatus.BLOCKED]
        ]
        if unavailable_seats:
            raise HTTPException(
                status_code=400, 
                detail=f"Seats {unavailable_seats} are not available"
            )
        
        total_amount = sum(ss.seat.base_price for ss in schedule_seats)
        
        booking = Booking(
            user_id=request.user_id,
            event_id=request.event_id,
            schedule_id=request.schedule_id,
            amount=total_amount,
            status=BookingStatus.PENDING
        )
        db.add(booking)
        db.flush()
        
        for schedule_seat in schedule_seats:
            booking_seat = BookingSeat(
                booking_id=booking.booking_id,
                schedule_seat_id=schedule_seat.schedule_seat_id
            )
            db.add(booking_seat)
            
            schedule_seat.status = SeatStatus.BOOKED
            schedule_seat.updated_at = datetime.now()
        
        db.commit()
        
        payment_link = f"https://payment.epicly.com/pay/{booking.booking_id}"
        
        return {
            "booking_id": booking.booking_id,
            "user_id": booking.user_id,
            "event_id": booking.event_id,
            "schedule_id": booking.schedule_id,
            "amount": booking.amount,
            "status": booking.status,
            "total_amount": total_amount,
            "payment_link": payment_link
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bookings/{booking_id}", response_model=dict)
async def get_booking_details(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.event),
        joinedload(Booking.schedule),
        joinedload(Booking.booking_seats)
    ).filter(Booking.booking_id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    seats = []
    for booking_seat in booking.booking_seats:
        if booking_seat.schedule_seat_id:
            seat_info = db.query(Seat).join(ScheduleSeat).filter(
                ScheduleSeat.schedule_seat_id == booking_seat.schedule_seat_id
            ).first()
            if seat_info:
                seats.append({
                    "seat_id": seat_info.seat_id,
                    "row_label": seat_info.row_label,
                    "seat_number": seat_info.seat_number,
                    "seat_type": seat_info.seat_type,
                    "base_price": seat_info.base_price
                })
    
    return {
        "booking_id": booking.booking_id,
        "user": {
            "user_id": booking.user.user_id,
            "name": booking.user.name,
            "email": booking.user.email
        },
        "event": {
            "event_id": booking.event.event_id,
            "title": booking.event.title,
            "event_type": booking.event.event_type
        },
        "schedule": {
            "schedule_id": booking.schedule.schedule_id,
            "start_time": booking.schedule.start_time,
            "end_time": booking.schedule.end_time
        } if booking.schedule else None,
        "seats": seats,
        "amount": booking.amount,
        "status": booking.status,
        "created_at": booking.created_at
    }


# Payments -------------------------------------------------------------------------------------------

class PaymentRequest(BaseModel):
    booking_id: int
    amount: Decimal
    method: str

class PaymentResponse(BaseModel):
    payment_id: int
    booking_id: int
    amount: Decimal
    payment_method: str
    status: str
    transaction_id: Optional[str]
    
    class Config:
        from_attributes = True

@router.post("/payments", response_model=PaymentResponse)
async def create_payment(request: PaymentRequest, db: Session = Depends(get_db)):
    try:
        booking = db.query(Booking).filter(Booking.booking_id == request.booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking.status != BookingStatus.PENDING:
            raise HTTPException(status_code=400, detail="Booking is not in pending status")
        
        if request.method not in [pm.value for pm in PaymentMethod]:
            raise HTTPException(status_code=400, detail="Invalid payment method")
        
        payment = Payment(
            booking_id=request.booking_id,
            amount=request.amount,
            payment_method=request.method,
            status=PaymentStatus.PENDING,
            transaction_id=str(uuid.uuid4())
        )
        db.add(payment)
        db.flush()
        
        import random
        payment_success = random.choice([True, True, True, False]) # making payment random as we are not adding payment gateway
        
        if payment_success:
            payment.status = PaymentStatus.SUCCESS
            booking.status = BookingStatus.CONFIRMED
        else:
            payment.status = PaymentStatus.FAILED
            booking_seats = db.query(BookingSeat).filter(
                BookingSeat.booking_id == request.booking_id
            ).all() # Removing lock
            
            for booking_seat in booking_seats:
                if booking_seat.schedule_seat_id:
                    schedule_seat = db.query(ScheduleSeat).filter(
                        ScheduleSeat.schedule_seat_id == booking_seat.schedule_seat_id
                    ).first()
                    if schedule_seat:
                        schedule_seat.status = SeatStatus.AVAILABLE
        
        db.commit()
        
        return {
            "payment_id": payment.payment_id,
            "booking_id": payment.booking_id,
            "amount": payment.amount,
            "payment_method": payment.payment_method,
            "status": payment.status,
            "transaction_id": payment.transaction_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment_status(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return {
        "payment_id": payment.payment_id,
        "booking_id": payment.booking_id,
        "amount": payment.amount,
        "payment_method": payment.payment_method,
        "status": payment.status,
        "transaction_id": payment.transaction_id
    }


# Users -------------------------------------------------------------------------------------------

class UserRegisterRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str]

class UserLoginRequest(BaseModel):
    email: str


@router.post("/users/register")
async def register_user(request: UserRegisterRequest, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        user = User(
            name=request.name,
            email=request.email,
            phone=request.phone
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/login")
async def login_user(request: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "status": "success",
        "message": "Login successful",
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email
    }

@router.get("/users/{user_id}/bookings")
async def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    bookings = db.query(Booking).options(
        joinedload(Booking.event),
        joinedload(Booking.schedule)
    ).filter(Booking.user_id == user_id).order_by(Booking.created_at.desc()).all()
    
    response = []
    for booking in bookings:
        booking_data = {
            "booking_id": booking.booking_id,
            "event": {
                "event_id": booking.event.event_id,
                "title": booking.event.title,
                "event_type": booking.event.event_type
            },
            "schedule": {
                "schedule_id": booking.schedule.schedule_id,
                "start_time": booking.schedule.start_time,
                "end_time": booking.schedule.end_time
            } if booking.schedule else None,
            "amount": booking.amount,
            "status": booking.status,
            "created_at": booking.created_at,
            "is_upcoming": booking.schedule.start_time > datetime.now() if booking.schedule else False
        }
        response.append(booking_data)
    
    return {
        "user_id": user_id,
        "bookings": response
    }
