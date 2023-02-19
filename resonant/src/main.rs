use std::io::Read;

use alsa::{Direction, ValueOr};
use alsa::pcm::{PCM, HwParams, Format, Access, State, IO};

fn init_speaker(pcm: &PCM) -> IO<i16> {
    // Open default playback device

    // Set hardware parameters: 44100 Hz / Mono / 16 bit
    let hwp = HwParams::any(&pcm).unwrap();
    hwp.set_channels(1).unwrap();
    hwp.set_rate(44100, ValueOr::Nearest).unwrap();
    hwp.set_format(Format::s16()).unwrap();
    hwp.set_access(Access::RWInterleaved).unwrap();
    pcm.hw_params(&hwp).unwrap();

    // Make sure we don't start the stream too early
    let hwp = pcm.hw_params_current().unwrap();
    let swp = pcm.sw_params_current().unwrap();
    swp.set_start_threshold(hwp.get_buffer_size().unwrap()).unwrap();
    pcm.sw_params(&swp).unwrap();

    
    return pcm.io_i16().unwrap();
}

fn init_mic(pcm: &PCM) -> IO<i16> {

    let hwp = HwParams::any(&pcm).unwrap();
    hwp.set_channels(1).unwrap();
    hwp.set_rate(44100, ValueOr::Nearest).unwrap();
    hwp.set_format(Format::s16()).unwrap();
    pcm.hw_params(&hwp).unwrap();

    // Make sure we don't start the stream too early
    let hwp = pcm.hw_params_current().unwrap();
    let swp = pcm.sw_params_current().unwrap();
    swp.set_start_threshold(hwp.get_buffer_size().unwrap()).unwrap();
    pcm.sw_params(&swp).unwrap();

    return pcm.io_i16().unwrap();
}

fn live_playback() {
    let mic_pcm = PCM::new("default", Direction::Capture, false).unwrap();
    let speak_pcm = PCM::new("default", Direction::Playback, false).unwrap();

    let mic_io = init_mic(&mic_pcm);
    let speak_io = init_speaker(&speak_pcm);


    let mut mic_buf = [0i16; 1024];
    for i in 0..5 *44100/1024 {

        assert_eq!(mic_io.readi(&mut mic_buf).unwrap(), 1024);
        assert_eq!(speak_io.writei(&mic_buf).unwrap(), 1024)
    }

    println!("this never ends");
    // In case the buffer was larger than 2 seconds, start the stream manually.
    if mic_pcm.state() != State::Running { mic_pcm.start().unwrap() };
    // Wait for the stream to finish playback.
    mic_pcm.drain().unwrap();// In case the buffer was larger than 2 seconds, start the stream manually.
    
    println!("this never ends");
    if speak_pcm.state() != State::Running { speak_pcm.start().unwrap() };
    // Wait for the stream to finish playback.
    speak_pcm.drain().unwrap();
    println!("this never ends");


}

fn main() {
    println!("Starting live recording and playback for 5 seconds!!");
    live_playback();
}