# This is a integration test
#       Managing a chat with a character
def test_message_management(char, chat_id, parent_id, message, creator_id, turn_id, text, author):
    message.next(CHAR, CHAT_ID, PARENT_ID)
    message.send(CHAR, CHAT_ID, TEXT, {AUTHOR})
    message.next(CHAR, MESSAGE)
    chat.create(CHAR, CHAT_ID, CREATOR_ID) #may have made a mistake here, it looks like there's a new chat function separate from new message, and I'm not sure if I handled that correctly
    character.get_histories(CHAR) #returns chat IDs?
    chat.get(CHAR)
    chat.get_history(CHAT_ID)
    message.rate(RATE, CHAT_ID, TURN_ID, CANDIDATE_ID)
    message.delete(CHAT_ID, TURN_ID)
    assert True
