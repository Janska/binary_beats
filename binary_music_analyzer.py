from aubio import source, tempo
from numpy import median, diff
from scipy.io import wavfile
from scipy.fftpack import fft, fftfreq


def calculate_bpm(song, samplerate):
    win_s, hop_s = 1024, 512
    s = source(song, samplerate, hop_s)
    o = tempo("specdiff", win_s, hop_s, samplerate)
    # List of beats, in samples
    beats = []
    # Total number of frames read
    total_frames = 0

    while True:
        samples, read = s()
        is_beat = o(samples)
        if is_beat:
            this_beat = o.get_last_s()
            beats.append(this_beat)
            # if o.get_confidence() > .2 and len(beats) > 2.:
            #    break
        total_frames += read
        if read < hop_s:
            break

    # Convert to periods and to bpm
    if len(beats) > 1:
        if len(beats) < 4:
            print("few beats found in {:s}".format(song))
        bpms = 60.0 / diff(beats)
        b = median(bpms)
    else:
        b = 0
        print("not enough beats found in {:s}".format(song))
    return b


def get_message(data, bpm, samplerate, frequency):
    """ Find the message in a song given the beats per minute (bpm), song data
        and samplerate.

        :param data: Path to the file.
        :type wif: ``str``
        :param bpm: Beats per minute.
        :type bpm: ``int``
        :param samplerate: The samplerate of the song.
        :type samplerate: ``int``
        :param frequency: The frequency to check beats for.
        :type frequency: ``int``
        :returns: A string of ASCII characters decoded from the beats at given
            bpm and frequency.
        :rtype: ``str``
    """
    # Calculate the number of samples between which the beat can appear.
    samples_between_beats = (60 / bpm) * samplerate

    data = data[:, 0]  # Use left channel. TODO: Better to down-sample to mono?

    binary = []

    # Every ASCII code has 8 bits.
    # Read statically the first 10 characters.
    i = 0
    while True:
        d = data[int(i * samples_between_beats):int((i + 1) * samples_between_beats)]
        i += 1
        samples = d.shape[0]

        # Fourier transformation used for frequency spectrum analysis.
        datafft = fft(d)
        fftabs = abs(datafft)

        # Frequency bins are calculated based on the samples and rate.
        freqs = fftfreq(samples, 1 / samplerate)

        # Suboptimal: Finding the index for `freq` in the frequency-vector.
        idx = 0
        for j, freq in enumerate(freqs):
            if freq >= frequency:
                idx = j
                break

        # Check the gain for `freq`:
        if fftabs[idx] >= 30000000:
            binary.append(1)
        else:
            binary.append(0)

        # Check for every even number of possible ASCII characters and assume
        # at least 3 (6) characters.
        if len(binary) >= 6*8 and len(binary) % 16 == 0:
            # Cut the binary array into pairs of 8 bits used in ASCII
            # characters.
            # Ignore last bits if they cannot pair to 8 bits.
            binary_slice = [
                "".join(str(b) for b in binary[i:i + 8]) for i in range(0, len(binary), 8)
            ]

            # Check that last binary 8-pair is ASCII character.
            if not chr(int(binary_slice[-1], 2)).isalnum():
                raise ValueError("Not all characters are ASCII.")

            # Check if we have repeated a whole cycle of a hidden message.
            if binary_slice[:len(binary_slice)//2] == binary_slice[len(binary_slice)//2:]:
                # Cut off duplicate hidden message.
                binary_slice = binary_slice[:len(binary_slice)//2]
                break

    return "".join([chr(int(b, 2)) for b in binary_slice])


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        help = """Binary Music Analyzer

Finds hidden messages embedded inside the beat of a song.

Usage:
    binary_music_analyzer.py <song>
Options:
    <song>  Path to song in wav format.
"""
        print(help)
        sys.exit(1)

    f = sys.argv[1]
    samplerate, data = wavfile.read(f)
    print(f"Trying to find the hidden message in song '{f}'...")
    bpm = calculate_bpm(f, samplerate)
    i = 0
    while i < 10:  # Bruteforcing is bad.
        try:
            m = get_message(data, bpm, samplerate, frequency=50)
            break
        except ValueError:
            # Not all characters are ASCII in hidden message.
            # Adjust BPM parameter.
            bpm -= 1  # TODO: Adjust BPM in both ways?
            i += 1
    else:
        print("Sorry! Hidden message couldn't be found.")
        sys.exit(1)

    print(f"Hidden message: '{m}'")
