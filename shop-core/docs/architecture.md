# shop-core architecture

## Target deployment model

Each customer site remains a completely separate Django deployment:

- separate database
- separate domain
- separate media
- separate `.env` / secrets
- separate client repository
- shared private `shop-core` package

There is no shared multi-tenant customer database.

## Core owns

- accounts/auth business rules
- catalog/product domain
- cart
- checkout/order rules
- inventory/stock rules
- wishlist/reviews
- customer support
- cancellation/returns
- analytics services
- reusable customizer engine
- reusable site configuration
- permissions and shared validators
- generic email/event hooks

## Client repository owns

- Django project settings and environment
- domain/database/deployment configuration
- branding
- client templates and template overrides
- client CSS/static assets
- client media
- copy/text/content
- client-only apps/features
- payment provider credentials/integration selection

## Template rule

Core templates must be namespaced and overridable.
Client template directories are searched before package templates.

## Feature flags

Client settings may define:

```python
SHOP_FEATURES = {
    "wishlist": True,
    "reviews": True,
    "support": True,
    "returns": True,
    "analytics": True,
    "warehouse": True,
    "customizer": True,
}
```

A disabled feature must disappear from navigation and reject direct
access, not merely hide its button.

## Migration compatibility

Current Arayeshi uses the Django app label `first` and the custom user
model `first.User`.

Therefore:

1. Do not rename `first` yet.
2. Do not rewrite existing migrations.
3. Extract pure utilities/services/selectors first.
4. Add compatibility tests for imports and migration state.
5. Move models only in a later phase while preserving app labels/table
   names and existing migration history.
6. Only after that may the old `first` Python package become a thin
   compatibility layer.

## Dependency direction

Preferred direction:

client project -> shop_core public API -> domain services -> models

Templates/views should not contain stock/order invariants.
Cross-domain writes go through service functions wrapped in
transactions where required.

## Initial extraction order

1. common utilities/validators/image helpers
2. permissions/decorators
3. catalog selectors/services
4. cart/order/inventory services
5. customer care
6. analytics
7. customizer/site configuration
8. models/migrations compatibility move
9. template/static override layer
