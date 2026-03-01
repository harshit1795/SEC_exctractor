import asyncio
import time
from app.api.health_scores import compute_finq_health_scores

async def test():
    t0 = time.time()
    await compute_finq_health_scores(category="Technology", limit=10)
    t1 = time.time()
    print(f"Time taken to compute FinQ health scores for Technology: {t1 - t0:.4f}s")
    
if __name__ == "__main__":
    asyncio.run(test())
