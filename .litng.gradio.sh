#!/bin/bash
pip install -U "gradio>=4,<=5"
GRADIO_SERVER_PORT=7860 gradio app.py --watch-dirs .