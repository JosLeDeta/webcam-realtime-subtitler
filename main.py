import audio_utils, video_utils, download_model
from multiprocessing import Process, Manager
import matplotlib.pyplot as plt
import torch, cv2, argparse, pyvirtualcam
import numpy as np

chunk_size = 1600 * 2 
audio_samples = []
silent_samples = []

# fig, axs = plt.subplots(2)

def audio_capture_callback(data, clips_dict):
    global audio_samples, silent_samples

    audio_samples.extend(data)
    silent_samples.extend(audio_utils.generate_silence_samples(data))

    if len(audio_samples) >= 16000 * 10:
        audio_samples = audio_samples[chunk_size:]
        silent_samples = silent_samples[chunk_size:]
    
    silent_points = audio_utils.get_start_end_points(silent_samples)

    for pstart, pend in silent_points:
        signature = audio_utils.get_audio_signature(audio_samples[pstart : pend])
        if signature not in clips_dict.keys():
            clips_dict[signature] = audio_samples[pstart - 512 : pend + 128]
            # audio_utils.save_wave(signature +  '.wav', audio_samples[pstart - 128 : pend + 128])
        
        if pend <= chunk_size:
            del clips_dict[signature]
    
    # axs[0].clear()
    # axs[0].plot(audio_samples, c='blue')
    # axs[0].set_ylim([-10000, 10000])
    # axs[1].clear()
    # axs[1].plot(silent_samples, c='blue', fillstyle='none', mfc=None)
    # plt.pause(0.01)

def predict_subtitles(clips_dict, model_tuple, subtitles_list):
    model, decoder, utils = model_tuple
    (read_batch, split_into_batches, read_audio, prepare_model_input) = utils
    clips_processed = []
    while True:
        for clip in clips_dict.keys():
            if clip not in clips_processed:
                clips_processed.append(clip)
                predicted = model(prepare_model_input(torch.tensor([clips_dict[clip]])))
                for i in predicted:
                    text = decoder(i.cpu())
                    if len(text) > 1:
                        subtitles_list.append(text)
        
def webcam_handler(subtitles_list, video_device=2):
    cap = cv2.VideoCapture(video_device)

    text = ' '
    rect, frame = cap.read()
    with pyvirtualcam.Camera(width=frame.shape[1], height=frame.shape[0], fps=30) as cam:
        while True:
            rect, frame = cap.read()
            if len(subtitles_list) > 0:
                text = subtitles_list[0]
                del subtitles_list[0]
            
            frame = video_utils.PutText(frame, text)

            cv2.imshow('video', frame)
            cv2.waitKey(1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cam.send(frame)
            cam.sleep_until_next_frame()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--lang', type=str, default='en', help='en, es, de')
    parser.add_argument('--video-device', type=int, default=2, help='input video device index')
    parser.add_argument('--audio-device', type=int, default=1, help='input audio device index')

    args = parser.parse_args()

    if download_model.model_downloaded(args.lang) ==  False:
        download_model.download_model(args.lang)
    
    if download_model.model_downloaded(args.lang) == True:
        model_tuple = torch.hub.load(
            repo_or_dir='./snakers4_silero-models_master',
            model='silero_stt',
            language=args.lang,
            device='cpu',
            force_reload=True,
            source='local'
        )
        m = Manager()
        clips_dict = m.dict()
        subtitles_list = m.list()

        audio_capture_process = Process(target=audio_utils.capture_audio_device, args=(audio_capture_callback, clips_dict), kwargs=({'chunk': chunk_size, 'device_index': args.audio_device}))
        audio_capture_process.start()
        subtitler_process = Process(target=predict_subtitles, args=(clips_dict, model_tuple, subtitles_list, ))
        webcam_process = Process(target=webcam_handler, args=(subtitles_list, ), kwargs=({'video_device': args.video_device})).start()
        subtitler_process.run()