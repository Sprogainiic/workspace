# Chat -> Memory Flow

User Message
-> Chat Gateway
-> Intent Classification (preliminary)
-> Conversation Memory Adapter
-> Adapter Validation Gate

If FAIL:
-> do not allow memory proposal ingestion
-> request regeneration or defer write

If WARN:
-> send to Health Director with warnings
-> Health Director may approve only safe subset

If PASS:
-> send memory update proposals to Health Director

Health Director
-> approve / modify / reject proposals
-> write approved fields to canonical memory
-> keep uncertain fields as transient or deferred when appropriate

Then:
-> route validated state to relevant specialists if needed
-> produce final user-facing response through Chat Gateway
