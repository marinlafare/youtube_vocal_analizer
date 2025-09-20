# pitch_algorithm.py
import numpy as np
import audioflux as af
import os
import math

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
C0_FREQ = 16.35

def _hz_to_note(freq_hz):
    if freq_hz <= C0_FREQ:
        return 'Silence/Noise'
    n_semitones = 12 * math.log2(freq_hz / C0_FREQ)
    n_semitones_rounded = int(round(n_semitones))
    octave = n_semitones_rounded // 12
    note_index = n_semitones_rounded % 12
    note_name = NOTE_NAMES[note_index]
    return f'{note_name}{octave}'

def _median_filter_on_valid_data(arr, kernel_size):
    if kernel_size % 2 == 0:
        raise ValueError("Kernel size must be an odd number.")
    
    valid_indices = arr > 0
    valid_data = arr[valid_indices]
    
    if len(valid_data) == 0:
        return arr
    
    half_kernel = kernel_size // 2
    padded_data = np.pad(valid_data, (half_kernel, half_kernel), 'edge')
    output_data = np.zeros_like(valid_data)
    
    for i in range(len(valid_data)):
        window = padded_data[i : i + kernel_size]
        output_data[i] = np.median(window)
        
    filtered_arr = np.zeros_like(arr)
    filtered_arr[valid_indices] = output_data
    return filtered_arr

def yin(audio_file_path: str):
    """
    Analyzes audio with the YIN algorithm, returns pitch, notes and times,
    with genius filtering for accuracy (it's still not good enough thou).
    """
    try:
        data, sr, *_ = af.read(audio_file_path)
        
        pitch_analyzer = af.PitchYIN(
            samplate=sr,
            low_fre=30.0,
            high_fre=700.0
        )
        
        freq, pv,*_ = pitch_analyzer.pitch(data)
        
        VOICE_PROB_THRESHOLD = -0.08
        freq[pv < VOICE_PROB_THRESHOLD] = 0.0
        
        smoothed_freq_pass_1 = np.copy(freq)
        last_valid_freq = 0.0
        
        for i in range(len(smoothed_freq_pass_1)):
            current_freq = smoothed_freq_pass_1[i]
            
            if current_freq > 0:
                if last_valid_freq == 0:
                    last_valid_freq = current_freq
                else:
                    # harmonic and sub-harmonic errors
                    candidate_freqs = [
                        last_valid_freq / 3, last_valid_freq / 2, last_valid_freq,
                        last_valid_freq * 2, last_valid_freq * 3
                    ]
                    closest_candidate = min(candidate_freqs, key=lambda x: abs(x - current_freq))
                    if abs(current_freq - closest_candidate) / closest_candidate < 0.05:
                        smoothed_freq_pass_1[i] = closest_candidate
                    else:
                        # Otherwise it's not an error
                        last_valid_freq = current_freq
            else:
                 last_valid_freq = 0.0
        # apply filter to an already headache-inducing fixed note
        smoothed_freq_final = _median_filter_on_valid_data(smoothed_freq_pass_1, kernel_size=11)
        
        times = np.arange(freq.shape[0]) * pitch_analyzer.slide_length / sr
        
        vec_hz_to_note = np.vectorize(_hz_to_note)
        notes = vec_hz_to_note(smoothed_freq_final)
        
        return times, smoothed_freq_final, notes
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return np.array([]), np.array([]), np.array([])