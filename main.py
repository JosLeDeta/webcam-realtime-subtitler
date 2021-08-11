import audio_utils
from multiprocessing import Process, Manager
import matplotlib.pyplot as plt
import torch

chunk_size = 1024
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
            clips_dict[signature] = audio_samples[pstart - 128 : pend + 128]
        
        if pend <= chunk_size:
            del clips_dict[signature]
    
    # axs[0].clear()
    # axs[0].plot(audio_samples, c='blue')
    # axs[0].set_ylim([-10000, 10000])
    # axs[1].clear()
    # axs[1].plot(silent_samples, c='blue', fillstyle='none', mfc=None)
    # plt.pause(0.01)

def predict_subtitles(clips_dict, model_tuple):
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
                        print(text)
        
        

if __name__ == '__main__':
    model_tuple = torch.hub.load(
        repo_or_dir='./snakers4_silero-models_master',
        model='silero_stt',
        language='es',
        device='cpu',
        force_reload=True,
        source='local'
    )

    clips_dict = Manager().dict()
    audio_capture_process = Process(target=audio_utils.capture_audio_device, args=(audio_capture_callback, clips_dict))
    audio_capture_process.start()
    subtitler_process = Process(target=predict_subtitles, args=(clips_dict, model_tuple))
    subtitler_process.run()