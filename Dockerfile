FROM continuumio/miniconda:4.7.12-alpine

RUN /opt/conda/bin/conda install -c conda-forge nco cdo esmf \
&&  /opt/conda/bin/conda clean -afy

RUN /opt/conda/bin/conda install python=3 pip \
&&  /opt/conda/bin/conda clean -afy

COPY . /gridspec
RUN cd /gridspec && /opt/conda/bin/pip install .
