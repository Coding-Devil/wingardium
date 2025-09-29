# syntax=docker/dockerfile:1
FROM nfvfp-docker-virtual.artifactory-fpark1.int.net.nokia.com/lfp/rocky8_py310_devops:1.0.0
ARG PORT=5050

ENV PYTHONUNBUFFERED=True
ENV PORT=${PORT}
ENV LOG_LEVEL="INFO"

COPY . ./

RUN pip3 install --no-cache-dir --prefer-binary -r requirements.txt --disable-pip-version-check \
    -i https://artifactory-fpark1.int.net.nokia.com/artifactory/api/pypi/NFVFP-pypi-virtual/simple \
    starship_ai-*.whl \
    && rm *.whl requirements.txt

RUN yum update
    
EXPOSE ${PORT}

ENTRYPOINT ["sh", "-c"]
HEALTHCHECK CMD ["starship_ai", "--version"]
CMD ["starship_ai", "--port", "${PORT}", "--config_file", "/starship.yaml", "--log_level", "${LOG_LEVEL}"]
