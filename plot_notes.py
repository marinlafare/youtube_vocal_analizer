#plot_notes.py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

def plot_pitch_contour(times,
                       freqs,
                       notes,
                       output_filename,
                       hz_threshold:int=250,
                       ):
    """
    Creates a line plot with time on the x-axis and musical notes on the y-axis,
    and saves it as a PNG file.

    Args:
        times (np.ndarray): The array of time points in seconds.
        freqs (np.ndarray): The array of corresponding frequencies in Hz.
        notes (np.ndarray): The array of corresponding musical note names.
        output_filename (str): The name of the file to save the plot as.
        hz_threshold (int): Lowest voice note in Hz
    """
    note_to_midi = {
        'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
        'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
    }

    midi_values = []
    y_tick_labels = []
    filtered_notes = np.array([note if freq > 250 else 'Silence/Noise' for freq, note in zip(freqs, notes)])
    
    for note_str in filtered_notes:
        if note_str == 'Silence/Noise':
            midi_values.append(np.nan)
        else:
            note_name = note_str[:-1]
            octave = int(note_str[-1])
            midi_num = note_to_midi[note_name] + (octave * 12)
            midi_values.append(midi_num)
            
            if note_str not in y_tick_labels:
                y_tick_labels.append(note_str)

    y_tick_labels.sort(key=lambda x: note_to_midi[x[:-1]] + (int(x[-1]) * 12))
    plt.figure(figsize=(15, 6))
    plt.plot(times, midi_values, marker='o', linestyle='-', markersize=2, linewidth=1, label='Detected Pitch')
    y_ticks = [note_to_midi[label[:-1]] + (int(label[-1]) * 12) for label in y_tick_labels]
    
    ax = plt.gca()
    ax.yaxis.set_major_locator(mticker.FixedLocator(y_ticks))
    ax.yaxis.set_major_formatter(mticker.FixedFormatter(y_tick_labels))

    plt.title('Pitch Contour of Vocals')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Note')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    output_dir = 'note_plots'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Plot saved successfully to: {output_path}")