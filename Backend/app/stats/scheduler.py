from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config.config import Session
from users.models.user import User
from stats.statsService import StatsService

scheduler = AsyncIOScheduler()

# Global StatsService instance
stats_service = StatsService()

async def generate_daily_stats():
    """Generate conversation stats for every user once per day."""
    db = Session()
    try:
        user_ids = [row.id for row in db.query(User.id).all()]
    finally:
        db.close()

    for uid in user_ids:
        await stats_service.generate_stats(uid)

# Register the job: every day at midnight (00:00)
scheduler.add_job(generate_daily_stats, trigger="cron", hour=0, minute=0, id="daily_stats") 