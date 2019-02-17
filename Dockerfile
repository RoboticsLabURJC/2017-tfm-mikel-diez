FROM ubuntu:16.04

RUN apt-get -y update; \
    apt-get -y upgrade; \
    apt-get -y install apt-utils \
    vim \
    htop \
    dstat \
    lsb-release \
    software-properties-common \
    git \
    curl;

RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list';
RUN apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 421C365BD9FF1F717815A3895523BAEEB01FA116;

RUN sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list';
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key 67170598AF249743;

RUN apt-add-repository "deb http://zeroc.com/download/apt/ubuntu$(lsb_release -rs) stable main";
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv 5E6DA83306132997;

RUN sh -c 'touch /etc/apt/sources.list.d/jderobot.list';
RUN sh -c 'echo "deb [arch=amd64] http://jderobot.org/apt xenial main" > /etc/apt/sources.list.d/jderobot.list';

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv 24E521A4;
RUN apt update;

RUN apt -y install jderobot;
RUN apt -y install jderobot-gazebo-assets;

RUN apt -y install jderobot-cameraview jderobot-cameraserver; 

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -

RUN apt -y install nodejs

RUN apt -y install libnss3 libgconf2-4 libcanberra-gtk-module libcanberra-gtk0

CMD ["bash"]
