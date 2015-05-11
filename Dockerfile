FROM python:3-onbuild

RUN echo "de_DE.UTF-8 UTF-8" > /etc/locale.gen
RUN apt-get update && apt-get install locales

ENV LANG de_DE.UTF-8
ENV LANGUAGE de_DE.UTF-8
ENV LC_ALL de_DE.UTF-8

RUN pip uninstall -y pyhyphen && pip install --upgrade PyHyphen==2.0.5

CMD ["python", "./wagnerpoems.py"]
