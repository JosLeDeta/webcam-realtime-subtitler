import argparse, yaml, requests, os
from tqdm import tqdm
from yaml.loader import SafeLoader

def download_model(lang):
    with open('snakers4_silero-models_master/models.yml', encoding='utf8') as f:
        data = yaml.load(f, Loader=SafeLoader)
        if lang in data['stt_models'].keys():
            url = data['stt_models'][lang]['latest']['jit']
            r  = requests.get(url, allow_redirects=True, stream=True)
            file_path = 'snakers4_silero-models_master/model/' + url.split('/')[-1]
            total_size_in_bytes= int(r.headers.get('content-length', 0))
            block_size = 1024
            print(f'Downloading model for {lang} language..')
            print(f'Saving in {file_path}')
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            with open(file_path, 'wb') as file:
                for data in r.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                print("ERROR, something went wrong")
        else:
            print(f'ERROR No model found for language {lang}')

def model_downloaded(lang):
    with open('snakers4_silero-models_master/models.yml', encoding='utf8') as f:
        data = yaml.load(f, Loader=SafeLoader)
        if lang in data['stt_models'].keys():
            file = data['stt_models'][lang]['latest']['jit'].split('/')[-1]
            return os.path.isfile(f'snakers4_silero-models_master/model/{file}')
        else:
            print(f'ERROR No model found for language {lang}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('lang', type=str, default='en', help='en/es/de/ua')

    args = parser.parse_args()
    if model_downloaded(args.lang) == False:
        download_model(args.lang)
    else:
        print('Model already downloaded!')