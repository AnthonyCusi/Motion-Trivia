from cv2 import VideoCapture
import api_handler
import threading as th
from time import sleep
import sys
import cv2
import html

# initializing window size
WIDTH = 960
HEIGHT = 540

# initializing video capture object
video = cv2.VideoCapture(0)

# initializing cascades
face_cascade = cv2.CascadeClassifier()
eyes_cascade = cv2.CascadeClassifier()

# loading cascades
if not face_cascade.load(cv2.samples.findFile('data/haarcascade_frontalface_alt.xml')):
    print('ERROR: could not load face cascade')
    exit(0)
if not eyes_cascade.load(cv2.samples.findFile('data/haarcascade_eye_tree_eyeglasses.xml')):
    print('ERROR: could not load eyes cascade')
    exit(0)

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


# game function
question_number = 0
curr_question = ''
def run_game():
    global question_number, curr_question, should_start
    # running the game
    for q in question_bank:
        if question_number < len(question_keys) and q['question'] == question_keys[question_number]:
            curr_question = q
            print('QUESTION ' + str(question_number + 1) + ':\n' +  html.unescape(q['question']) + '\n')
    
    sleep(8)

    # getting answer choice
    if face_x_coord > WIDTH / 2:
        choice = 'True'
    else:
        choice = 'False'

    # checking answer
    if choice == curr_question['correct_answer']:
        print("Correct!")
    else:
        print("Incorrect.")
        
    question_number += 1
    should_start = True


# saves timer and status
should_start = True

# handle live video input
while True:
    # get success status and a frame
    success, frame = video.read()

    # checks that frame is not empty
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
        color = (0, 255, 0) if face_x_coord > 480 else (0, 0, 255)
        frame = cv2.ellipse(frame, center, (width // 2, height // 2), 0, 0, 360, color, 4)

        region_of_interest = gray_frame[y: y + height, x: x + width]

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
  
    

    # display the frame
    frame = cv2.putText(frame, html.unescape(curr_question['question']), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,0,255), 2, cv2.LINE_AA) if \
        type(curr_question) == dict else cv2.putText(frame, '', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,0,255), 2, cv2.LINE_AA)
    cv2.imshow('Trivia!', frame)

    # allows quitting program using 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# final cleanup
video.release()
cv2.destroyAllWindows()