import asyncio
from app.services.data_source_manager import DataSourceManager

async def test():
    manager = DataSourceManager()
    df = await manager.get_fundamentals_data('VZ')
    q4 = df[df['FiscalPeriod'] == '2025Q4']
    print('Q4 Metrics:', sorted(q4['Metric'].tolist()))

asyncio.run(test())
