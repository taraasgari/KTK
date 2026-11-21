Integration order:

1. Add Store reference to Product
2. Add Store reference to Category
3. Add Store reference to Order
4. Add Store reference to Customer

Migration strategy:
- Add nullable fields first
- Create default store
- Backfill existing records
- Verify data ownership
- Make fields required

Dashboard:
- Every query must use current store context
- Owner access is checked per store
