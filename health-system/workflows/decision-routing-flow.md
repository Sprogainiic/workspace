# Decision Routing Flow

## Modes
- log_only
- state_update_only
- micro_response
- specialist_single
- director_merge
- weekly_analysis
- ambiguity_review

## Routing rules
- logging explicit event only -> log_only
- brief state report + simple acknowledgement -> state_update_only or micro_response
- single-domain question -> specialist_single
- cross-domain conflict or final plan question -> director_merge
- trend / plateau / progress review -> weekly_analysis
- contradiction or unclear extraction -> ambiguity_review
