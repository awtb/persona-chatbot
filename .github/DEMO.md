# Demo

This file is intended for evidence materials that demonstrate the bot in action.

## What to Show

- A short end-to-end flow of selecting an avatar and starting a conversation
- Evidence that a user fact is stored and visible in the facts view
- A dedicated moment where the bot recalls the fact after `/reset`

## Scenario: Long-Term Memory After Chat Reset

Recommended sequence:

1. Open the bot and show the avatar selection menu.
2. Open the Pavel Durov avatar card and select it.
3. Send a message with a fact that should be stored in long-term memory.
   Example: `My name is Ilyas.`
4. Show the bot reply in the active conversation.
5. Open the facts view and show that the name was saved.
6. Run `/reset`.
7. Ask a follow-up question that checks whether the bot still remembers the fact.
   Example: `You don't know my name?`
8. Show that the bot recalls the stored fact after the reset.

## Screenshots

### 1. Welcome and Avatar Selection

The bot starts with the main menu and the avatar list.

<a href="assets/demo/welcome-and-avatar-selection.png">
  <img
    src="assets/demo/welcome-and-avatar-selection.png"
    alt="Welcome and avatar selection"
    width="360"
  />
</a>

### 2. Avatar Details for Pavel Durov

The Pavel Durov profile is opened before starting the chat.

<a href="assets/demo/pavel-durov-avatar-details.png">
  <img
    src="assets/demo/pavel-durov-avatar-details.png"
    alt="Pavel Durov avatar details"
    width="900"
  />
</a>

### 3. Chat After Sharing a Name

The user shares their name and the selected avatar replies in character.

<a href="assets/demo/chat-after-sharing-name.png">
  <img
    src="assets/demo/chat-after-sharing-name.png"
    alt="Chat after sharing a name"
    width="900"
  />
</a>

### 4. Facts Menu With the Saved Name

The facts view shows that the name was persisted as long-term memory.

<a href="assets/demo/facts-menu-with-saved-name.png">
  <img
    src="assets/demo/facts-menu-with-saved-name.png"
    alt="Facts menu with the saved name"
    width="760"
  />
</a>

### 5. Memory Recall After Reset

After `/reset`, the bot still recalls the stored name in a fresh chat context.

<a href="assets/demo/reset-and-memory-recall.png">
  <img
    src="assets/demo/reset-and-memory-recall.png"
    alt="Memory recall after reset"
    width="760"
  />
</a>

## Memory Extraction Log

The worker logs also show that the fact was extracted and saved from the chat turn:

```text
worker-1  | {"chat_id": "UUID('2487ca2e-e2b3-4120-9b6e-44ba1d0bfc97')", "user_id": "UUID('9b9041de-31da-44ab-a244-52078c01e82d')", "avatar_id": "UUID('0b2c46e9-8466-42e5-ac47-8ff71c5f91ab')", "user_message_id": "UUID('ac907a89-d45a-4c58-90c8-bc4f1688b800')", "assistant_message_id": "UUID('8325631f-d0ea-402b-960a-fbb18176f6a6')", "user_message_chars": 34, "assistant_message_chars": 329, "existing_facts_count": 0, "saved_facts_count": 1, "extracted_facts": {"facts": [{"kind": "profile", "content": "name is Ilyas"}]}, "event": "Analyzed recent turn for memory extraction", "logger": "persona_chatbot.services.memory", "level": "info", "timestamp": "2026-03-17T10:21:14.557017Z", "service": "persona-chatbot-worker", "logging_mode": "structured", "message": "Analyzed recent turn for memory extraction"}
worker-1  | {"event": "Processed", "logger": "faststream.access.redis", "level": "info", "timestamp": "2026-03-17T10:21:14.558971Z", "service": "persona-chatbot-worker", "logging_mode": "structured", "message": "Processed"}
```

## Short Note

These screenshots show the full memory loop: avatar selection, fact capture, persisted facts, and recall after chat reset. The final screen demonstrates that `/reset` clears the active conversation context without deleting long-term memory.
