#!/bin/sh
# serve_model.sh

exec mlflow models serve -m models:/${MODEL} --host 0.0.0.0 -p 1234 --no-conda
