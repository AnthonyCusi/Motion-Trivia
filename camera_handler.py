from cv2 import VideoCapture
import threading as th
from time import sleep
import api_handler
import sys
import cv2
import html

# initializing window size
WIDTH = 1152
HEIGHT = 648

# initializing video capture object
video = cv2.VideoCapture(0)

# initializing cascades
face_cascade = cv2.CascadeClassifier()
# eyes_cascade = cv2.CascadeClassifier()

# loading cascades
if not face_cascade.load(cv2.samples.findFile('data/haarcascade_frontalface_alt.xml')):
    print('ERROR: could not load face cascade')
    exit(0)
# if not eyes_cascade.load(cv2.samples.findFile('data/haarcascade_eye_tree_eyeglasses.xml')):
#     print('ERROR: could not load eyes cascade')
#     exit(0)

# game setup
session_data = api_handler.get_session_data()
game_data = api_handler.get_game_data(session_data['token'])

if session_data == "quit" or game_data == "quit":
    sys.exit()
elif game_data['response_code'] == 0:
    question_bank = game_data['results']
    question_keys = [key['question'] for key in question_bank]
    question_number = 0
    choice = ''

# reset session token
else:
    api_handler.reset_token(session_data['token'])


# game functions
should_start = True
question_number = 0
score = 0
curr_question = ''

def run_game():
    global question_number, curr_question, should_start, score

    # running the game
    question_number += 1
    for q in question_bank:
        if question_number < len(question_keys) and q['question'] == question_keys[question_number]:
            curr_question = q
            print('QUESTION ' + str(question_number + 1) + ':\n' +  html.unescape(q['question']) + '\n')
    sleep(8)

    # getting answer choice and checking it
    choice = 'True' if face_x_coord > WIDTH / 2 else 'False'
    curr_question = 'Correct!' if choice == curr_question['correct_answer'] else 'Sorry, Incorrect.'
    score = score + 1 if curr_question == 'Correct!' else score

    should_start = True


# handle live video input
while True:
    # get success status and a frame
    success, frame = video.read()
    if not success:
        break

    # flip and resize frame, and make it grayscale
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    frame = cv2.flip(frame,1)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detect face and bounding box
    face = face_cascade.detectMultiScale(gray_frame)
    for (x, y, width, height) in face:
        center = (x + width // 2, y + height // 2)
        
        # makes outline green if face is on right side of screen; red if on left
        face_x_coord = center[0]
        color = (0, 255, 0) if face_x_coord > WIDTH / 2 else (0, 0, 255)
        frame = cv2.ellipse(frame, center, (width // 2, height // 2), 0, 0, 360, color, 4)

        # region_of_interest = gray_frame[y: y + height, x: x + width]

        # detect eyes and bounding boxes
        # eyes = eyes_cascade.detectMultiScale(region_of_interest)
        # for (x2, y2, height2, width2) in eyes:
        #     eye_center = (x + x2 + width2 // 2, y + y2 + height2 // 2)
        #     radius = int(round((width2 + height2) * 0.25))
        #     frame = cv2.circle(frame, eye_center, radius, color, 4)
    
    # run game
    if should_start:
        timer = th.Timer(2, run_game)
        timer.start()
        should_start = False
  
    # create text and split it if it's too long
    text = 'QUESTION ' + str(question_number) + ': ' + html.unescape(curr_question['question']) if type(curr_question) == dict else curr_question
    text2 = ''
    text_color = (255,0,0) if type(curr_question) == dict else ((0, 255, 0) if text == 'Correct!' else (0, 0, 255))
    font_size = 0.65 if type(curr_question) == dict else 1.2
    should_split = False
    if len(text) > 86:
        should_split = True
        text2 = text[86:]
        text = text[:86]

    # display the frame
    frame = cv2.putText(frame, text, (50,50), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, 2, cv2.LINE_AA)
    if should_split:
        frame = cv2.putText(frame, text2, (50,100), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, 2, cv2.LINE_AA)
    frame = cv2.putText(frame, 'SCORE: ' + str(score), (50,600), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2, cv2.LINE_AA)

    cv2.imshow('Trivia!', frame)

    # allows quitting program using 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# final cleanup
video.release()
cv2.destroyAllWindows()