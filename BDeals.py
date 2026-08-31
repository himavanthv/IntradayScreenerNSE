from nsepython import get_blockdeals
from nsepython import get_bulkdeals
from nsepython import nse_get_top_gainers
from nsepython import nse_largedeals_historical

# Fetch today's block deals data
block_data = get_blockdeals()
print("Today's Block Deals:")
#print(block_data)
from_date="01-11-2025"
to_date="19-12-2025"


# Fetch today's bulk deals data (often relevant to look at as well)
bulk_data = get_bulkdeals()
print("\nToday's Bulk Deals:")
#print(bulk_data)

block_data.to_csv('BlockData.csv')
bulk_data.to_csv('BulkData.csv')
#print(nse_get_top_gainers())
#largedeals = nse_largedeals_historical(from_date,to_date,'short_deals')
#largedeals.to_csv('ShortDeals.csv')