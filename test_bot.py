
import telebot
import time
import os

BOT_TOKEN = '7618558615:AAFO5kgrM5ru_Unp-ESwchCerQFE9eDisQk'
ADMIN_ID = 745211839
TEST_USER_ID = 123456789 # A dummy user ID for testing

bot = telebot.TeleBot(BOT_TOKEN)

def simulate_message(user_id, text):
    # This is a simplified simulation. In a real test, you'd use a testing framework
    # or directly call the bot's message handlers.
    # For this scenario, we'll just print the simulated message.
    print(f"Simulating message from user {user_id}: {text}")
    # In a real test, you would send this message to the bot and check its response.
    # Since we don't have direct access to the bot's message queue, we'll rely on
    # manual verification of the bot's behavior in the Telegram client.


print("\n--- Test Scenario 1: User /start command ---")
# Simulate a new user sending /start
simulate_message(TEST_USER_ID, "/start")
time.sleep(1) # Give the bot some time to process and save user ID

print("\n--- Test Scenario 2: Admin /broadcast command ---")
# Simulate admin sending a broadcast message
simulate_message(ADMIN_ID, "/broadcast Hello everyone, this is a test broadcast!")
time.sleep(1)

print("\n--- Test Scenario 3: Non-admin /broadcast command ---")
# Simulate non-admin sending a broadcast message
simulate_message(TEST_USER_ID, "/broadcast I am not an admin!")
time.sleep(1)

print("\n--- Test Scenario 4: Admin /show_users command ---")
# Simulate admin requesting to show users
simulate_message(ADMIN_ID, "/show_users")
time.sleep(1)

print("\n--- Test Scenario 5: Non-admin /show_users command ---")
# Simulate non-admin requesting to show users
simulate_message(TEST_USER_ID, "/show_users")
time.sleep(1)

print("\n--- Test Scenarios Complete ---")
print("Please manually verify the bot's behavior in Telegram:")
print(f"1. Send /start from a new user (or yourself if you haven't yet) to register them.")
print(f"2. Send /broadcast <your message> from admin ID {ADMIN_ID} and verify other users receive it.")
print(f"3. Send /broadcast <your message> from a non-admin ID and verify it's rejected.")
print(f"4. Send /show_users from admin ID {ADMIN_ID} and verify it lists registered users.")
print(f"5. Send /show_users from a non-admin ID and verify it's rejected.")
print(f"6. Check the `user_ids.txt` file in the bot's directory for saved user IDs.")


