#!/bin/bash
# Make sure to run     chmod a+x install.sh     before running
# To execute  ./install.sh
# Make sure this is run at the root directory
echo "----------------------------- Checking for updates first... -----------------------------"
sudo apt-get update

REQUIRED_PACKAGES=( 
    python3 python3-pip python3-venv git python3-dev
    libssl-dev libatlas-base-dev # Numpy
    i2c-tools # imu
    libopenjp2-7 libtiff5 # Pillow
    portaudio19-dev python3-pyaudio # libportaudio0 libportaudio2 libportaudiocpp0 libasound2-dev #Pyaudio
)

# IF YOU ARE RUNNING THIS ON A PI
# git clone https://github.com/respeaker/seeed-voicecard
# cd seeed-voicecard
# sudo ./install.sh
# sudo reboot

# ALSO
# Change the i2c speed so the display/gyro refreshes faster
# See https://www.raspberrypi-spy.co.uk/2018/02/change-raspberry-pi-i2c-bus-speed/

function checkOrInstall() {
    REQUIRED_PKG=$1
    PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok")
    echo Checking for $REQUIRED_PKG: $PKG_OK
    if [ "" = "$PKG_OK" ]; then
    echo "$REQUIRED_PKG not found. Setting up $REQUIRED_PKG..."
    sudo apt-get --yes install $REQUIRED_PKG 
    fi
}

for PACKAGE in ${REQUIRED_PACKAGES[@]}
do
    checkOrInstall $PACKAGE
done

echo "----------------------------- Linux packages installed -----------------------------"
if [ ! -d "env/" ]; then
    echo "Creating virtual env..."
    python3 -m venv env/
fi

. ./env/bin/activate
echo "----------------------------- Installing pip packages -----------------------------"
pip3 install -r requirements.txt

echo "----------------------------- All done! -----------------------------"