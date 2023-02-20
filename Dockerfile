FROM python:3.10

LABEL org.opencontainers.image.source https://github.com/binarly-io/fwhunt-scan

RUN apt-get update
RUN apt-get install -y ninja-build parallel
RUN pip install meson==1.0.0

WORKDIR /tmp

# install rizin from source code
RUN wget https://github.com/rizinorg/rizin/releases/download/v0.5.0/rizin-src-v0.5.0.tar.xz
RUN tar -xvf rizin-src-v0.5.0.tar.xz

WORKDIR /tmp/rizin-v0.5.0
RUN meson build
RUN ninja -C build install

# install fwhunt_scan
RUN useradd -u 1001 -m fwhunt_scan
USER fwhunt_scan

COPY fwhunt_scan_analyzer.py /home/fwhunt_scan/app/
COPY requirements.txt /home/fwhunt_scan/app/
COPY fwhunt_scan /home/fwhunt_scan/app/fwhunt_scan

WORKDIR /home/fwhunt_scan/app/

RUN pip install --user -r requirements.txt

ENTRYPOINT ["python3", "fwhunt_scan_analyzer.py"]
