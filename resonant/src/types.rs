use crate::constants::N_CHANNELS;

pub type AudioBuf = [i16; 1024];
pub type ChannelsReading = [AudioBuf; N_CHANNELS];