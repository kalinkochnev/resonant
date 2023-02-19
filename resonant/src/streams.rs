use crate::{types::{AudioBuf, ChannelsReading}, constants::N_CHANNELS};


trait AudioStream {
    /// Fills a buffer with the number of bytes specified
    fn read(buf: &AudioBuf) -> ChannelsReading;
}

struct UDPStream {}
impl UDPStream {
    fn acquire(ip: &'static str) {
        
    }

}
struct ALSAStream {}
impl ALSAStream {

}


struct FileStream{}
impl FileStream {
    fn from(file: &'static str);
}

/// This struct 
struct Accumulator {
    packets: Vec<ChannelsReading>
}

impl Accumulator {
    /// Returns an iterator for the last n samples
    fn last_n(samples: usize);

}