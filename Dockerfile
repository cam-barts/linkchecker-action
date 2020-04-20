FROM python:3.7-alpine

LABEL name="linkchecker-action"
LABEL version="1.1.0"
LABEL repository="http://github.com/cam-barts/linkchecker-action"
LABEL homepage="http://github.com/cam-barts/linkchecker-action"

LABEL maintainer="Cam Barts"
LABEL com.github.actions.name="linkchecker-action"
LABEL com.github.actions.description="Checks markdown links for non 200 status codes"
LABEL com.github.actions.icon="link-2"
LABEL com.github.actions.color="purple"

RUN apt-get update && \
    apt-get -y install gcc mono-mcs
RUN pip install markdown requests aiohttp asyncio
COPY "entrypoint.sh" "/entrypoint.sh" 
COPY "check-links.py" "/check-links.py"

RUN chmod +x /entrypoint.sh
RUN chmod +x /check-links.py
ENTRYPOINT ["/entrypoint.sh"]
