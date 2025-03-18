FROM python:3.12-slim AS build

# 2 layer, but we can create more for package's we want to cache
RUN apt-get update \
    && apt-get install -y gdal-bin libgdal-dev
RUN apt-get update \
    && apt-get install -y libproj-dev binutils \
    && apt-get install -y libpq-dev
RUN apt-get update \
    && apt-get install -y wget build-essential curl ca-certificates cmake
    && apt-get install -y g++ gcc ninja-build
RUN rm -rf /var/lib/apt/lists/*

RUN wget https://download.osgeo.org/gdal/3.10.2/gdal-3.10.2.tar.gz \
    && tar -xvzf gdal-3.10.2.tar.gz \
    && cd gdal-3.10.2 \
    && cmake . \
        -G Ninja \
        -DCMAKE_INSTALL_PREFIX=/usr \
        -DGDAL_FIND_PACKAGE_PROJ_MODE=MODULE \
        -DGDAL_USE_TIFF_INTERNAL=ON \
        -DGDAL_USE_GEOTIFF_INTERNAL=ON \
        -DBUILD_TESTING=OFF \
    && ninja \
    && ninja install \
    && ldconfig \
    && cd .. && rm -rf gdal-3.10.2 gdal-3.10.2.tar.gz

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
RUN pip install GDAL=="$(gdal-config --version).*"

# bedni multistage
#FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
#ENV PYTHONDONTWRITEBYTECODE=1
#ENV LD_LIBRARY_PATH=/usr/lib # multistage fix cache 1
#COPY --from=build /etc/ /etc/ # .co files | multistage fix cache 2

#WORKDIR /app

#COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
#COPY --from=build /usr/bin/ /usr/bin/
#COPY --from=build /usr/lib/ /usr/lib/
#COPY --from=build /usr/lib64/ /usr/lib64/

COPY ./fgeovisor .
COPY settings.py visor_bend_site/

EXPOSE 8000

CMD python manage.py makemigrations; python manage.py migrate; python manage.py createsuperuser --no-input; python manage.py runserver 0.0.0.0:8000
# ENTRYPOINT ['django-start.sh']

# RUN adduser --system --uid 1000 appuser
# USER appuser