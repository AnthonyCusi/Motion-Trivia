from cv2 import VideoCapture
import threading as th
from time import sleep
import api_handler
import sys
import cv2
import urllib.parse

# -- initializing window size and colors -- #
WIDTH = 1152
HEIGHT = 648
GREEN = (0, 255, 0)
RED = (0, 0, 255)

# -- initializing video capture object -- #
video = cv2.VideoCapture(0)

# initializing cascade
face_cascade = cv2.CascadeClassifier()
if not face_cascade.load(cv2.samples.findFile('data/haarcascade_frontalface_alt.xml')):
    print('ERROR: could not load face cascade')
    exit(0)

# -- game setup -- #
session_data = api_handler.get_session_data()
game_data = api_handler.get_game_data(session_data['token'])

if session_data == "quit" or game_data == "quit":
    sys.exit()
elif game_data['response_code'] == 0:
    question_bank = game_data['results']
    question_keys = [key['question'] for key in question_bank]
    question_number = 0

# reset session token
else:
    api_handler.reset_token(session_data['token'])


# -- game functions -- #
should_start = True
question_number = 0
score = 0
curr_question = ''
choice = ''
total_time = 8
game_over = False

def countdown():
    global total_time
    while (total_time > 0):
        sleep(1)
        total_time -= 1
    total_time = 8

def run_game():
    global question_number, curr_question, should_start, score, choice, game_over

    # running the game
    question_number += 1
    for q in question_bank:
        if question_number < len(question_keys):
            if q['question'] == question_keys[question_number]:
                curr_question = q
        else:
            game_over = True
            return
    countdown()

    # getting answer choice and checking it
    choice = 'True' if face_x_coord > WIDTH / 2 else 'False'
    if type(curr_question) == dict:
        curr_question = 'Correct!' if choice == curr_question['correct_answer'] else 'Sorry, Incorrect.'
    score = score + 1 if curr_question == 'Correct!' else score

    should_start = True


#  --- handle live video input --- #
while not game_over:
    # get success status and a frame
    success, frame = video.read()
    if not success:
        break

    # flip and resize frame, and make it grayscale
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    frame = cv2.flip(frame,1)
    plain_frame = frame
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detect face and bounding box
    face = face_cascade.detectMultiScale(gray_frame)
    for (x, y, width, height) in face:
        center = (x + width // 2, y + height // 2)
        
        # makes outline green if face is on right side of screen; red if on left
        face_x_coord = center[0]
        color = GREEN if face_x_coord > WIDTH / 2 else RED
        choice = 'True' if face_x_coord > WIDTH / 2 else 'False'
        frame = cv2.ellipse(frame, center, (width // 2, height // 2), 0, 0, 360, color, 4)

    
    # run game
    if should_start:
        timer = th.Timer(2, run_game)
        timer.start()
        should_start = False
    
    if not game_over:
        # --- create text and split it if it's too long --- #
        question_text = urllib.parse.unquote(curr_question['question']) if type(curr_question) == dict else curr_question
        while '&quot;' in question_text:
            question_text = question_text.replace('&quot;', '"')
        while '&#039;' in question_text:
            question_text = question_text.replace('&#039;', "'")

        text = 'QUESTION ' + str(question_number) + ': ' + question_text if type(curr_question) == dict else curr_question
        text2 = ''
        text_color = (255,0,0) if type(curr_question) == dict else (GREEN if text == 'Correct!' else RED)
        font_size = 0.85 if type(curr_question) == dict else 1.5
        should_split = False

        if len(text) > 70:
            should_split = True
            text2 = text[70:]
            text = text[:70]
            if text.rfind(" ") != 69:
                text2 = text[text.rfind(" "): ] + text2
                text = text[: text.rfind(" ")]

        # --- display the frame --- #
        # question text
        frame = cv2.putText(frame, text, (50,65), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, 2, cv2.LINE_AA)
        if should_split:
            frame = cv2.putText(frame, text2, (50,115), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, 2, cv2.LINE_AA)
        frame = cv2.putText(frame, 'SCORE: ' + str(score), (50,600), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,0), 5, cv2.LINE_AA)

        # true and false text
        if choice == 'True':
            frame = cv2.putText(frame, 'TRUE', (850,300), cv2.FONT_HERSHEY_SIMPLEX, 3, GREEN, 8, cv2.LINE_AA)
            frame = cv2.putText(frame, 'FALSE', (50,300), cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2, cv2.LINE_AA)
        else:
            frame = cv2.putText(frame, 'TRUE', (1000,300), cv2.FONT_HERSHEY_SIMPLEX, 1, GREEN, 2, cv2.LINE_AA)
            frame = cv2.putText(frame, 'FALSE', (50,300), cv2.FONT_HERSHEY_SIMPLEX, 3, RED, 8, cv2.LINE_AA)

        # timer
        if type(curr_question) == dict:
            frame = cv2.putText(frame, str(total_time), (900,600), cv2.FONT_HERSHEY_SIMPLEX, 6, (255,255,0), 14, cv2.LINE_AA)
            

        cv2.imshow('Trivia!', frame)

    # --- allows quitting program using 'q' --- #
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -- end screen -- #
while True:
    success, frame = video.read()
    if not success:
        break

    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    frame = cv2.flip(frame,1)

    frame = cv2.putText(frame, 'GAME OVER', (40, 300), cv2.FONT_HERSHEY_SIMPLEX, 6, (255,0,0), 17, cv2.LINE_AA)
    frame = cv2.putText(frame, 'Your score: ' + str(score) + '/10', (160, 450), cv2.FONT_HERSHEY_SIMPLEX, 2.75, (255,0,0), 10, cv2.LINE_AA)
    frame = cv2.putText(frame, 'Q: quit', (50,600), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255,255,0), 4, cv2.LINE_AA)

    cv2.imshow('Trivia!', frame)

    # --- allows quitting program using 'q' --- #
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# --- final cleanup --- #
video.release()
cv2.destroyAllWindows()