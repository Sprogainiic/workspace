# Chat Gateway Flow

User Message
-> Chat Gateway
-> Intent Classification
-> Data Extraction
-> Conversation Memory Adapter
-> Adapter Validation Gate
-> Memory Update Proposal (via Health Director)

-> Determine needed specialists
-> Call specialist(s)
-> Validation Gate

-> Health Director:
 - approve / modify / reject memory proposals
 - resolve conflicts
 - produce final answer

-> Return response to user
