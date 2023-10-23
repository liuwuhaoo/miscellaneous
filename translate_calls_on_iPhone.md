# Translate Calls on iPhone

iOS does not provide a feature to handle the voice of the call, such as recording. However, there is a way around this - Facetime on the Mac. In short, using Facetime on MacOS allows you to handle the voice.

By default, when you make calls on a Mac, the default voice input/output would be, of course, the default speaker and microphone. It's already enough for the voice handling. By [whisper.cpp](https://github.com/ggerganov/whisper.cpp), you can handle the voice of the call __streamly__, like recording or translating. However, this is not different from making calls on the iPhone, and translate (like google translate) the voice on you Mac.

There is a better way: use [Black Hole](https://github.com/ExistentialAudio/BlackHole) as the voice output. When using whisper.cpp, select the blackhole as the voice source. In this case, it would like there is a tunnel between `you iPhone --(Facetime)--> you Mac --(black hole)--> whisper.cpp --> voice handling`. 

*Note*: Make Phone calls on Mac could resulting in voice failing output to a MIDI multi-output device. Solution: Set the ouptut device to black hole, and redirect the audio from black hole to a speaker manually.