# 3D Audio Localization -  a Hybrid Approach to Sound Positioning, Recognition, and Wearable Presentation
![Resonant Logo](https://user-images.githubusercontent.com/31194806/137144554-4b4ef30d-91d8-40ea-b9a4-d59cc5492606.png)
### Kalin Kochnev, Rohan Menon, Jacob Yanoff

[The rest of the research paper can be found here](https://drive.google.com/file/d/1qwGu7ep9EHtQIG7Da8p2QRF7DOw6s2cd/view?usp=sharing)

## Introduction

In the realm of synthetic sensing, computer vision has been the predominant focus of research over the last several decades. Humans, being a visually dependent species, have been naturally drawn to artificial sight, however, artificial hearing can be an equally important field in terms of the breadth and impact of its applications. For example, human-interface devices, spatially aware robots, and aides for people with disabilities can all see massive improvements through the development of more advanced sound sensing technology.

Three-dimensional sound localization, or the ability to identify the position of an audio source, is among the most important skills for an artificial hearing system. Combining localization with classification would allow such a device to gain complete understanding of the soundscape and navigate the world with new awareness.

![Quad Chart](https://user-images.githubusercontent.com/31194806/137145083-8003562c-6e2e-479a-8e07-8b044fa4ee52.png)

## Goals

Through our research, we aimed to develop algorithms to both localize and classify sounds. They needed to be reasonably accurate while still being fast to compute, to achieve near real-time speeds.

These algorithms would eventually be moved to an embedded platform within a wearable device. This wearable needed to be light-weight, unobtrusive and have a visual interface that is easy to understand.


## Abstract

Recent advancements in machine learning and image processing mean that the ability of computers to see has improved drastically in the last 10 years. While sound is a crucial part of how most people experience their environments, computer hearing has not seen the same advancements. We aimed to develop algorithms to locate audio signals within 3D space as well as classify them into several relevant categories.  Additionally, we wanted to convey this information to a user via a wearable device. The final device uses cross-power spectrum phase analysis to determine the arrival angle of arrival based on two pairs of microphones and displays this information via a heavily modified baseball cap. It uses a small, brim-mounted OLED display to convey positional information to the user. We imagine that potentially, it could be used by a person who is deaf or hard of hearing to better understand their soundscape. The classification algorithm relies on an artificial neural network generated through supervised deep learning. The localization algorithm proved to be highly accurate, with an average error of 2.53% when determining the relative angle of a sound source. The machine learning algorithm is quite successful at identifying test data, exhibiting 84.6% accuracy, however, overfitting is still present and further optimization is required to make the algorithm applicable to less contrived data. While these algorithms perform well independently, combining their functionality poses a new set of challenges that we hope to address in future research.




