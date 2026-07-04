import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.models import Song

logger = logging.getLogger("uvicorn.error")

# Seed song library containing 20 Marathi, 20 Hindi, and 20 English songs
SEED_SONGS = [
    # --- MARATHI DEVOTIONAL / MORNING (10 songs) ---
    {"title": "Pratham Tula Vandito", "artist": "Shankar Mahadevan", "genre": "marathi:devotional", "duration": 180, "youtube_id": "yt_m_dev1"},
    {"title": "Vitthal Te Vitthal Gajar", "artist": "Suresh Wadkar", "genre": "marathi:devotional", "duration": 180, "youtube_id": "yt_m_dev2"},
    {"title": "Gajanan Maharaj Aarti", "artist": "Anuradha Paudwal", "genre": "marathi:devotional", "duration": 150, "youtube_id": "yt_m_dev3"},
    {"title": "Majhe Pandharpur", "artist": "Pralhad Shinde", "genre": "marathi:devotional", "duration": 210, "youtube_id": "yt_m_dev4"},
    {"title": "Kanada Raja Pandharicha", "artist": "Sudhir Phadke", "genre": "marathi:devotional", "duration": 180, "youtube_id": "yt_m_dev5"},
    {"title": "Ooti Bhara Sadguru", "artist": "Asha Bhosle", "genre": "marathi:devotional", "duration": 180, "youtube_id": "yt_m_dev6"},
    {"title": "Dehachi Tijori", "artist": "Sudhir Phadke", "genre": "marathi:devotional", "duration": 190, "youtube_id": "yt_m_dev7"},
    {"title": "Utha Utha Sakal Jana", "artist": "Suresh Wadkar", "genre": "marathi:devotional", "duration": 180, "youtube_id": "yt_m_dev8"},
    {"title": "Pandharicha Vaas Chandrabhage", "artist": "Pralhad Shinde", "genre": "marathi:devotional", "duration": 200, "youtube_id": "yt_m_dev9"},
    {"title": "Datta Digambar Dynamic", "artist": "Ajay-Atul", "genre": "marathi:devotional", "duration": 180, "youtube_id": "yt_m_dev10"},

    # --- MARATHI POPULAR / GENERAL (10 songs) ---
    {"title": "Zingaat", "artist": "Ajay-Atul", "genre": "marathi:pop", "duration": 210, "youtube_id": "yt_m_pop1"},
    {"title": "Apsara Aali", "artist": "Ajay-Atul", "genre": "marathi:pop", "duration": 190, "youtube_id": "yt_m_pop2"},
    {"title": "Sairat Zaala Ji", "artist": "Ajay-Atul", "genre": "marathi:pop", "duration": 220, "youtube_id": "yt_m_pop3"},
    {"title": "Jeev Rangala", "artist": "Hariharan", "genre": "marathi:pop", "duration": 180, "youtube_id": "yt_m_pop4"},
    {"title": "Mee Raat Takli", "artist": "Lata Mangeshkar", "genre": "marathi:pop", "duration": 180, "youtube_id": "yt_m_pop5"},
    {"title": "Navrai Majhi", "artist": "Sunidhi Chauhan", "genre": "marathi:pop", "duration": 180, "youtube_id": "yt_m_pop6"},
    {"title": "Kombdi Palali", "artist": "Anand Shinde", "genre": "marathi:pop", "duration": 180, "youtube_id": "yt_m_pop7"},
    {"title": "Dolby Walya", "artist": "Nagesh Morwekar", "genre": "marathi:pop", "duration": 200, "youtube_id": "yt_m_pop8"},
    {"title": "Wajle Ki Bara", "artist": "Bela Shende", "genre": "marathi:pop", "duration": 190, "youtube_id": "yt_m_pop9"},
    {"title": "Yad Lagla", "artist": "Ajay Gogavale", "genre": "marathi:pop", "duration": 180, "youtube_id": "yt_m_pop10"},

    # --- HINDI DEVOTIONAL / MORNING (10 songs) ---
    {"title": "Hanuman Chalisa", "artist": "Hariharan", "genre": "hindi:devotional", "duration": 240, "youtube_id": "yt_h_dev1"},
    {"title": "Achyutam Keshavam", "artist": "Vikram Hazra", "genre": "hindi:devotional", "duration": 180, "youtube_id": "yt_h_dev2"},
    {"title": "Gayatri Mantra", "artist": "Anuradha Paudwal", "genre": "hindi:devotional", "duration": 180, "youtube_id": "yt_h_dev3"},
    {"title": "Kabir Amritwani", "artist": "Debashish Dasgupta", "genre": "hindi:devotional", "duration": 210, "youtube_id": "yt_h_dev4"},
    {"title": "Vakratunda Mahakaya", "artist": "Jagjit Singh", "genre": "hindi:devotional", "duration": 150, "youtube_id": "yt_h_dev5"},
    {"title": "Bhaje Sargam Har Har", "artist": "Pandit Jasraj", "genre": "hindi:devotional", "duration": 180, "youtube_id": "yt_h_dev6"},
    {"title": "Om Jai Jagdish Hare", "artist": "Anuradha Paudwal", "genre": "hindi:devotional", "duration": 180, "youtube_id": "yt_h_dev7"},
    {"title": "Raghupati Raghav Raja Ram", "artist": "Hariharan", "genre": "hindi:devotional", "duration": 200, "youtube_id": "yt_h_dev8"},
    {"title": "Shiv Tandav Stotram", "artist": "Uma Mohan", "genre": "hindi:devotional", "duration": 220, "youtube_id": "yt_h_dev9"},
    {"title": "Mere Ghar Ram Aaye Hain", "artist": "Jubin Nautiyal", "genre": "hindi:devotional", "duration": 180, "youtube_id": "yt_h_dev10"},

    # --- HINDI POPULAR / GENERAL (10 songs) ---
    {"title": "Kesariya", "artist": "Arijit Singh", "genre": "hindi:pop", "duration": 200, "youtube_id": "yt_h_pop1"},
    {"title": "Tum Hi Ho", "artist": "Arijit Singh", "genre": "hindi:pop", "duration": 180, "youtube_id": "yt_h_pop2"},
    {"title": "Kabira", "artist": "Tochi Raina", "genre": "hindi:pop", "duration": 190, "youtube_id": "yt_h_pop3"},
    {"title": "Chaiyya Chaiyya", "artist": "Sukhwinder Singh", "genre": "hindi:pop", "duration": 180, "youtube_id": "yt_h_pop4"},
    {"title": "Apna Bana Le", "artist": "Arijit Singh", "genre": "hindi:pop", "duration": 210, "youtube_id": "yt_h_pop5"},
    {"title": "Channa Mereya", "artist": "Arijit Singh", "genre": "hindi:pop", "duration": 200, "youtube_id": "yt_h_pop6"},
    {"title": "Zaalima", "artist": "Arijit Singh", "genre": "hindi:pop", "duration": 180, "youtube_id": "yt_h_pop7"},
    {"title": "Dil Diyan Gallan", "artist": "Atif Aslam", "genre": "hindi:pop", "duration": 210, "youtube_id": "yt_h_pop8"},
    {"title": "Pee Loon", "artist": "Mohit Chauhan", "genre": "hindi:pop", "duration": 180, "youtube_id": "yt_h_pop9"},
    {"title": "Namo Namo", "artist": "Amit Trivedi", "genre": "hindi:pop", "duration": 180, "youtube_id": "yt_h_pop10"},

    # --- ENGLISH INSPIRATIONAL / MORNING (10 songs) ---
    {"title": "Morning Has Broken", "artist": "Cat Stevens", "genre": "english:devotional", "duration": 180, "youtube_id": "yt_e_dev1"},
    {"title": "Beautiful Day", "artist": "U2", "genre": "english:devotional", "duration": 200, "youtube_id": "yt_e_dev2"},
    {"title": "Here Comes The Sun", "artist": "The Beatles", "genre": "english:devotional", "duration": 180, "youtube_id": "yt_e_dev3"},
    {"title": "A Sky Full Of Stars", "artist": "Coldplay", "genre": "english:devotional", "duration": 210, "youtube_id": "yt_e_dev4"},
    {"title": "Happy", "artist": "Pharrell Williams", "genre": "english:devotional", "duration": 180, "youtube_id": "yt_e_dev5"},
    {"title": "Morning Sun", "artist": "Robbie Williams", "genre": "english:devotional", "duration": 180, "youtube_id": "yt_e_dev6"},
    {"title": "Wake Me Up", "artist": "Avicii", "genre": "english:devotional", "duration": 200, "youtube_id": "yt_e_dev7"},
    {"title": "Best Day Of My Life", "artist": "American Authors", "genre": "english:devotional", "duration": 190, "youtube_id": "yt_e_dev8"},
    {"title": "Good Life", "artist": "OneRepublic", "genre": "english:devotional", "duration": 180, "youtube_id": "yt_e_dev9"},
    {"title": "Lovely Day", "artist": "Bill Withers", "genre": "english:devotional", "duration": 180, "youtube_id": "yt_e_dev10"},

    # --- ENGLISH POPULAR / GENERAL (10 songs) ---
    {"title": "Blinding Lights", "artist": "The Weeknd", "genre": "english:pop", "duration": 200, "youtube_id": "yt_e_pop1"},
    {"title": "As It Was", "artist": "Harry Styles", "genre": "english:pop", "duration": 167, "youtube_id": "yt_e_pop2"},
    {"title": "Shape of You", "artist": "Ed Sheeran", "genre": "english:pop", "duration": 233, "youtube_id": "yt_e_pop3"},
    {"title": "Flowers", "artist": "Miley Cyrus", "genre": "english:pop", "duration": 200, "youtube_id": "yt_e_pop4"},
    {"title": "Perfect", "artist": "Ed Sheeran", "genre": "english:pop", "duration": 210, "youtube_id": "yt_e_pop5"},
    {"title": "Cruel Summer", "artist": "Taylor Swift", "genre": "english:pop", "duration": 180, "youtube_id": "yt_e_pop6"},
    {"title": "Believer", "artist": "Imagine Dragons", "genre": "english:pop", "duration": 200, "youtube_id": "yt_e_pop7"},
    {"title": "STAY", "artist": "The Kid LAROI & Justin Bieber", "genre": "english:pop", "duration": 141, "youtube_id": "yt_e_pop8"},
    {"title": "Counting Stars", "artist": "OneRepublic", "genre": "english:pop", "duration": 220, "youtube_id": "yt_e_pop9"},
    {"title": "Levitating", "artist": "Dua Lipa", "genre": "english:pop", "duration": 203, "youtube_id": "yt_e_pop10"}
]

async def seed_default_songs(db: AsyncSession):
    """Seed the database with default songs if empty."""
    try:
        # Check if songs table is empty
        result = await db.execute(select(func.count(Song.id)))
        count = result.scalar()
        
        if count == 0:
            logger.info("Database is empty. Seeding default Hindi, Marathi, and English songs...")
            for song_data in SEED_SONGS:
                db_song = Song(
                    title=song_data["title"],
                    artist=song_data["artist"],
                    genre=song_data["genre"],
                    duration=song_data["duration"],
                    youtube_id=song_data["youtube_id"]
                )
                db.add(db_song)
            await db.commit()
            logger.info(f"Successfully seeded {len(SEED_SONGS)} default songs.")
        else:
            logger.info(f"Database already has {count} songs. Skipping seed.")
    except Exception as e:
        logger.error(f"Failed to seed default songs: {str(e)}")
        await db.rollback()
