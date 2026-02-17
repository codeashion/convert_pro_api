from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError


def convert_mp3_to_wav(input_path: str, output_path: str):
    try:
        audio = AudioSegment.from_mp3(input_path)
        audio.export(output_path, format="wav")

    except CouldntDecodeError:
        raise ValueError("Invalid MP3 file or corrupted audio.")

    except Exception as e:
        raise ValueError(f"Audio conversion failed: {str(e)}")
