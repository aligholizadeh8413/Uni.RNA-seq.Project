FROM debian:bookworm-slim@sha256:734a72b3d6142a71993b4bc580ca01d8ca687f77a2c422d96a961d3376b179bc
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      fastqc=0.11.9+dfsg-6 trimmomatic=0.39+dfsg-2 hisat2=2.2.1-4+b2 \
      samtools=1.16.1-1 subread=2.0.3+dfsg-1 \
      default-jre-headless python3 ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*
RUN set -eu; \
    jar_path="$(dpkg -L trimmomatic | awk '/\/trimmomatic-0[.]39[.]jar$/ {print; exit}')"; \
    test -n "$jar_path"; test -f "$jar_path"; \
    mkdir -p /opt/rnaseq; \
    cp -L "$jar_path" /opt/rnaseq/trimmomatic-0.39.jar; \
    test "$(java -jar /opt/rnaseq/trimmomatic-0.39.jar -version)" = "0.39"; \
    dpkg-query -W > /opt/rnaseq/packages.tsv
WORKDIR /work
CMD ["bash"]
