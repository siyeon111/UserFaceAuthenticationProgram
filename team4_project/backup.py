import os
import cv2
import face_recognition
import time
import timeit
import inko
import pygame

myInko = inko.Inko()
name = ''
lines = []
face = []


def check():
    try:
        path = './'
        os.chdir(path)
        files = os.listdir(path)
        for file in files:
            if '.png' in file:
                face.append(file)
    except:
        print('')


def load():
    global name
    name = input('사용자 이름을 입력해주세요 : ')
    if output_name():
        print(f'{name}님 환영합니다.')
        os.system('pause')
    else:
        print('사용자가 존재하지 않습니다.')
        os.system('pause')


########################################################################################################


def output_name():
    global name
    global lines
    try:
        try:
            with open(f'{name}.txt', 'r') as file:
                for line in file:
                    lines.append(line.strip())
            return True
        except:
            with open(f'{myInko.ko2en(name)}.txt', 'r') as file:
                for line in file:
                    lines.append(line.strip())
            return True
    except:
        return False


########################################################################################################
# 이름 등록
def input_name():
    global name
    global lines
    name = input('이름을 입력하세요 : ')
    #  sheet = input('시트값 입력 : ')
    with open(f'{name}.txt', 'w') as file:
        file.write(f'{name}\n')  # line[0]
    #        file.write(f'{sheet}\n')  # line[1]
    output_name()
    file.close()


########################################################################################################
# 사진 인증
def face_certified():
    global name
    cap = cv2.VideoCapture(0)

    face_encodings = []
    for f in face:
        try:
            image = face_recognition.load_image_file(f'{myInko.ko2en(f)}')
            face_encodings.append(face_recognition.face_encodings(image)[0])
        except:
            print(f'Unable to load face image for {f}')
            return False

    frame_cnt = 0
    cap_True_timer = 0
    cap_False_timer = 0

    for i in range(50):
        start_time = timeit.default_timer()

        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break
        #좌우반전
        frame = cv2.flip(frame, 1)

        os.system('cls')
        print('카메라를 바라보세요.\n')
        print('사용자를 확인하는 중입니다...\n')
        print('=====================================\n')

        face_locations = face_recognition.face_locations(frame)
        if face_locations:
            top, right, bottom, left = face_locations[0]
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)

            frame_cnt += 1
            if frame_cnt % 30 == 0:
                encode2 = face_recognition.face_encodings(frame, face_locations)[0]
                results = face_recognition.compare_faces(face_encodings, encode2)
                for i, result in enumerate(results):
                    if result:
                        name = myInko.en2ko(face[i].strip('.png'))
                        print(f'{name}님으로 인증합니다.\n')
                        output_name()
                        cap.release()
                        cv2.destroyAllWindows()
                        return True

            terminate_time = timeit.default_timer()
            elapsed_time = terminate_time - start_time
            if elapsed_time >= 20:
                cap.release()
                cv2.destroyAllWindows()
                return False

        end_time = timeit.default_timer()

        cv2.imshow('Webcam Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()
    cv2.destroyAllWindows()
    return False


########################################################################################################
# 사진 등록
def face_registration():
    el_width = 120
    el_height = 150
    cap_timer = 0
    SUM = 0
    frame_cnt = 0
    end_time = 0

    os.system('cls')
    input_name()
    print('사용자 이름이 등록되었습니다.\n')
    print('사용자 얼굴 등록을 시작합니다...\n')

    # 웹캠 열기
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("카메라 오픈에 실패했습니다.")
        return

    while True:
        start_time = timeit.default_timer()
        frame_cnt += 1

        os.system('cls')
        print('0. 종료\n')
        print('=====================================\n')

        ret, frame = cap.read()
        if not ret:
            print("프레임 캡처에 실패했습니다.")
            break
        #좌우반전
        frame = cv2.flip(frame, 1)

        height, width, _ = frame.shape
        el_left_x = width // 2 - el_width
        el_top_y = height // 2 - el_height
        el_right_x = width // 2 + el_width
        el_bottom_y = height // 2 + el_height

        face_locations = face_recognition.face_locations(frame)
        is_center = False

        if face_locations:
            top, right, bottom, left = face_locations[0]
            face_roi = frame[top:bottom, left:right]

            if left >= el_left_x and right <= el_right_x and top >= el_top_y and bottom <= el_bottom_y:
                is_center = True

        if not is_center:
            SUM = 0
            cv2.putText(frame, 'Align your face with the ellipse', (70, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 255, 255), 2)

        end_time = timeit.default_timer()
        if is_center:
            cap_count = 4 - (int(SUM) % 5)
            SUM += end_time - start_time
            if cap_count == 1:
                img_captured = cv2.imwrite(f'{myInko.ko2en(name)}.png', face_roi)
                cv2.putText(frame, 'complete to capture', (150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            elif cap_count == 0:
                break
            else:
                cv2.putText(frame, 'Dont Move...', (width // 2 - 100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, str(cap_count - 1), (width // 2 - 50, height // 2 + 40), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 5)

        frame = cv2.ellipse(frame, (width // 2, height // 2), (el_height, el_width), 90, 0, 360, (255, 0, 0), 2)
        cv2.imshow('Webcam Face Recognition', frame)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('0'):
            break

    check()
    cap.release()
    cv2.destroyAllWindows()


########################################################################################################
# 배경음악
def play_engine_sound():
    sound_file = 'engine_sound.mp3'  # 자동차 시동음 파일 경로

    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()


########################################################################################################
# 자동차 이모티콘
def print_car():
    car_ascii = '''     
                                   ,__g_gggggggg_,
                             J$$$\f~777^?77$$)77TT%%$$sg,
                            $$)            $)          7$$$y,
                          J$$)             $)            $$$$$y
               ,_gs#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$y,
           s$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$y                    __a^^^^z___,
        g$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$,                M^^^_^^^^^^^_^M
       a$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$,              ,#____^^^^^^^^^^s
      +$$$$$$$$#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$          _ssy^^^^^_^^^^^^^^^^^
      #$$$$$$a$fgssj%$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$[ssg%$$$$$$$$y     gaa$$$$$Mg_^^^^^^^^^^__f
       %%%%%f$$+$$$$ $$%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%T$$)$$$$)#$f%%$$$$ _gs$$$$$$$$$$$$$y_^^^^^~
             %$$g][g$$f                               7$$g]T]a$$    ^T $$$$$$$$$$$$$$$$$$$A^^^
               %%$$\f                                   7%$$$f)          77%$$$$$f%%7^
    '''
    lines = car_ascii.split("\n")
    for line in lines:
        print(line)
        time.sleep(0.1)


########################################################################################################
# main
if __name__ == '__main__':
    check()
    #print(face)
    #os.system('pause')
    while True:
        facecheck = False
        os.system('cls')
        print('1. 얼굴등록   2. 얼굴인증   0. 종료\n')
        print('=====================================\n')
        inline = input()

        if inline == '1':
            face_registration()
        elif inline == '2':
            facecheck = face_certified()
            if facecheck != True:
                print('사용자가 아닙니다.')
                os.system('pause')
        # elif inline == '3':
        # load()
        elif inline == '0':
            break

        if (facecheck == True):
            try:
                for j in range(5):
                    print('.', end='', flush=True)
                    time.sleep(1)
                print('\n시동을 겁니다.')
                time.sleep(1)
                play_engine_sound()
                print_car()
                os.system('pause')
            except:
                print("사용자 정보를 찾을 수 없습니다.")
                os.system('pause')