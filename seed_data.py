"""
Sample data seeding script for Epicly Event Booking System - Cline generated not by me(Rakshit Sharma)
"""
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from database import SessionLocal, create_tables
from models import (
    User, Venue, Section, Seat, Event, Schedule, ScheduleSeat,
    EventType, SeatType, SeatStatus
)

def seed_database():
    """Seed the database with sample data"""
    db = SessionLocal()
    
    try:
        # Create tables first
        create_tables()
        
        # Clear existing data (for development)
        db.query(ScheduleSeat).delete()
        db.query(Schedule).delete()
        db.query(Seat).delete()
        db.query(Section).delete()
        db.query(Event).delete()
        db.query(Venue).delete()
        db.query(User).delete()
        db.commit()
        
        # Create sample users
        users = [
            User(name="John Doe", email="john@example.com", phone="9876543210"),
            User(name="Jane Smith", email="jane@example.com", phone="9876543211"),
            User(name="Bob Johnson", email="bob@example.com", phone="9876543212"),
        ]
        db.add_all(users)
        db.commit()
        
        # Create sample venues
        venues = [
            Venue(
                name="PVR Cinemas Phoenix Mall",
                location="Phoenix Mall, Whitefield",
                capacity=200,
                address="Phoenix Marketcity, Whitefield Road, Bangalore",
                city="Bangalore",
                state="Karnataka"
            ),
            Venue(
                name="Inox Forum Mall",
                location="Forum Mall, Koramangala",
                capacity=150,
                address="Forum Mall, Koramangala, Bangalore",
                city="Bangalore",
                state="Karnataka"
            ),
            Venue(
                name="Kanteerava Stadium",
                location="Kanteerava Stadium",
                capacity=25000,
                address="Kanteerava Stadium, Bangalore",
                city="Bangalore",
                state="Karnataka"
            ),
            Venue(
                name="Palace Grounds",
                location="Palace Grounds",
                capacity=50000,
                address="Palace Grounds, Bangalore",
                city="Bangalore",
                state="Karnataka"
            ),
        ]
        db.add_all(venues)
        db.commit()
        
        # Create sections for venues
        sections = []
        
        # Cinema sections
        for venue in venues[:2]:  # First 2 venues are cinemas
            sections.extend([
                Section(venue_id=venue.venue_id, name="Screen 1", capacity=100),
                Section(venue_id=venue.venue_id, name="Screen 2", capacity=100),
            ])
        
        # Stadium sections
        sections.extend([
            Section(venue_id=venues[2].venue_id, name="East Stand", capacity=8000),
            Section(venue_id=venues[2].venue_id, name="West Stand", capacity=8000),
            Section(venue_id=venues[2].venue_id, name="North Stand", capacity=4500),
            Section(venue_id=venues[2].venue_id, name="South Stand", capacity=4500),
        ])
        
        # Concert venue sections
        sections.extend([
            Section(venue_id=venues[3].venue_id, name="VIP Section", capacity=5000),
            Section(venue_id=venues[3].venue_id, name="General Section", capacity=45000),
        ])
        
        db.add_all(sections)
        db.commit()
        
        # Create seats for sections
        seats = []
        
        # Cinema seats (first 4 sections)
        for section in sections[:4]:
            for row in ['A', 'B', 'C', 'D', 'E']:
                for seat_num in range(1, 21):  # 20 seats per row
                    seat_type = SeatType.PREMIUM if row in ['A', 'B'] else SeatType.REGULAR
                    base_price = Decimal('300.00') if seat_type == SeatType.PREMIUM else Decimal('200.00')
                    
                    seats.append(Seat(
                        section_id=section.section_id,
                        row_label=row,
                        seat_number=seat_num,
                        seat_type=seat_type.value,
                        base_price=base_price
                    ))
        
        # Stadium seats (next 4 sections)
        for section in sections[4:8]:
            for row in range(1, 21):  # 20 rows
                for seat_num in range(1, 21):  # 20 seats per row
                    seats.append(Seat(
                        section_id=section.section_id,
                        row_label=str(row),
                        seat_number=seat_num,
                        seat_type=SeatType.GENERAL.value,
                        base_price=Decimal('500.00')
                    ))
        
        # Concert venue seats (last 2 sections)
        for section in sections[8:]:
            seat_type = SeatType.VIP if 'VIP' in section.name else SeatType.GENERAL
            base_price = Decimal('2000.00') if seat_type == SeatType.VIP else Decimal('1000.00')
            
            for row in range(1, 11):  # 10 rows
                for seat_num in range(1, 51):  # 50 seats per row
                    seats.append(Seat(
                        section_id=section.section_id,
                        row_label=str(row),
                        seat_number=seat_num,
                        seat_type=seat_type.value,
                        base_price=base_price
                    ))
        
        # Add seats in batches to avoid memory issues
        batch_size = 1000
        for i in range(0, len(seats), batch_size):
            batch = seats[i:i + batch_size]
            db.add_all(batch)
            db.commit()
        
        # Create sample events
        events = [
            # Movies
            Event(
                title="Avengers: Endgame",
                event_type=EventType.MOVIE.value,
                description="The epic conclusion to the Infinity Saga",
                language="English",
                genre="Action/Adventure",
                duration=181
            ),
            Event(
                title="RRR",
                event_type=EventType.MOVIE.value,
                description="A fictional story about two legendary revolutionaries",
                language="Telugu",
                genre="Action/Drama",
                duration=187
            ),
            Event(
                title="Spider-Man: No Way Home",
                event_type=EventType.MOVIE.value,
                description="Spider-Man's identity is revealed",
                language="English",
                genre="Action/Adventure",
                duration=148
            ),
            
            # Comedy Shows
            Event(
                title="Zakir Khan Live",
                event_type=EventType.COMEDY_SHOW.value,
                description="Stand-up comedy by Zakir Khan",
                language="Hindi",
                genre="Comedy",
                duration=90
            ),
            
            # Sports
            Event(
                title="Bangalore FC vs Mumbai City FC",
                event_type=EventType.SPORTS.value,
                description="ISL Football Match",
                language="English",
                genre="Football",
                duration=120
            ),
            
            # Concerts
            Event(
                title="AR Rahman Live Concert",
                event_type=EventType.CONCERT.value,
                description="Live concert by the Mozart of Madras",
                language="Multi-language",
                genre="Music",
                duration=180
            ),
        ]
        db.add_all(events)
        db.commit()
        
        # Create schedules for events
        schedules = []
        base_time = datetime.now() + timedelta(days=1)
        
        # Movie schedules (multiple shows per day)
        for i, event in enumerate(events[:3]):  # First 3 are movies
            for day_offset in range(7):  # 7 days
                for show_time in [10, 14, 18, 21]:  # 4 shows per day
                    start_time = base_time + timedelta(days=day_offset, hours=show_time)
                    end_time = start_time + timedelta(minutes=event.duration + 30)  # +30 for ads/break
                    
                    # Alternate between venues and sections
                    venue_idx = i % 2
                    section_idx = (i * 2) + (day_offset % 2)
                    
                    schedules.append(Schedule(
                        event_id=event.event_id,
                        venue_id=venues[venue_idx].venue_id,
                        section_id=sections[section_idx].section_id,
                        start_time=start_time,
                        end_time=end_time
                    ))
        
        # Comedy show schedules
        comedy_event = events[3]
        for day_offset in [5, 12, 19]:  # 3 shows
            start_time = base_time + timedelta(days=day_offset, hours=20)
            end_time = start_time + timedelta(minutes=comedy_event.duration)
            
            schedules.append(Schedule(
                event_id=comedy_event.event_id,
                venue_id=venues[0].venue_id,
                section_id=sections[0].section_id,
                start_time=start_time,
                end_time=end_time
            ))
        
        # Sports event schedule
        sports_event = events[4]
        start_time = base_time + timedelta(days=10, hours=19)
        end_time = start_time + timedelta(minutes=sports_event.duration)
        
        schedules.append(Schedule(
            event_id=sports_event.event_id,
            venue_id=venues[2].venue_id,
            section_id=sections[4].section_id,  # East Stand
            start_time=start_time,
            end_time=end_time
        ))
        
        # Concert schedule
        concert_event = events[5]
        start_time = base_time + timedelta(days=15, hours=19)
        end_time = start_time + timedelta(minutes=concert_event.duration)
        
        schedules.append(Schedule(
            event_id=concert_event.event_id,
            venue_id=venues[3].venue_id,
            section_id=sections[8].section_id,  # VIP Section
            start_time=start_time,
            end_time=end_time
        ))
        
        db.add_all(schedules)
        db.commit()
        
        # Create schedule seats (link seats to schedules with availability)
        schedule_seats = []
        
        for schedule in schedules:
            # Get all seats for this schedule's section
            section_seats = db.query(Seat).filter(Seat.section_id == schedule.section_id).all()
            
            for seat in section_seats:
                schedule_seats.append(ScheduleSeat(
                    schedule_id=schedule.schedule_id,
                    seat_id=seat.seat_id,
                    status=SeatStatus.AVAILABLE.value
                ))
        
        # Add schedule seats in batches
        batch_size = 1000
        for i in range(0, len(schedule_seats), batch_size):
            batch = schedule_seats[i:i + batch_size]
            db.add_all(batch)
            db.commit()
        
        print("✅ Database seeded successfully!")
        print(f"Created:")
        print(f"  - {len(users)} users")
        print(f"  - {len(venues)} venues")
        print(f"  - {len(sections)} sections")
        print(f"  - {len(seats)} seats")
        print(f"  - {len(events)} events")
        print(f"  - {len(schedules)} schedules")
        print(f"  - {len(schedule_seats)} schedule seats")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
