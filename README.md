---
title: CoverPilot
emoji: 📨
colorFrom: blue
colorTo: gray
sdk: gradio
sdk_version: 4.24.0
app_file: "app/app.py"
pinned: false
license: mit
short_description: AI-Powered Cover Letter Generator
---

---

<div align="center">
  <div>&nbsp;</div>

<div>&nbsp;</div>

  <img src="asset/banner.png" width="400"/> 


🎩 **CoverPilot** is an AI-powered cover letter generator. It helps you focus on what matters most - getting the job.

[Watch process in action](#demo) |
[How it can help](#workflow) |
[Deploy your own](#setup)

![sync_to_HF](https://github.com/cxumol/CoverPilot/actions/workflows/hf_sync.yml/badge.svg) |
[![Hugging Face](https://img.shields.io/badge/App-%F0%9F%A4%97%20Hugging%20Face-blue)](https://huggingface.co/spaces/cxumol/CoverPilot)

</div>

## Demo

<video src="asset/CoverPilot_demo_h264_30fps_noaudio.mp4"></video>

https://github.com/cxumol/CoverPilot/assets/8279655/fe66bc9a-8d05-4f69-b3f5-b48f66464993

- Try it on Hugging Face now! [![Hugging Face](https://img.shields.io/badge/App-%F0%9F%A4%97%20Hugging%20Face-blue)](https://huggingface.co/spaces/cxumol/CoverPilot)

## Workflow

With powerful Prompt Engineering, CoverPilot can deeply understand your resume and the job description, and find the best writing style to match your experience with the job. 

In CoverPilot, we hire two AI agents cooperatively writing your cover letter:

- **CheapAI**, an honest format converter and refiner, extracts essential info from job description and résumé.
- **StrongAI**, a thoughtful wordsmith, composes perfect cover letters to make both you and recruiters happy.

> Thanks to **CheapAI**'s work, your spending on **StrongAI** is substaintially saved.


![workflow](asset/CoverPilot_workflow.png)


## Setup

### Prepare API for AI capabilities

> [!IMPORTANT]
> You have to bring your own API keys.  
> If you have no idea about it, try getting one from https://beta.openai.com/account/api-keys

The API base defaults to OpenAI's, and compatible with AI service providers who have the same API structure.

Once you obtained can set API configurations in 2 ways:
- environment variables
- AI Setup panel on the Web UI

Check out the [config.py](app/config.py) for more details.

### Deploy on Hugging Face

[![🤗 Deploy on Hugging Face](https://huggingface.co/datasets/huggingface/badges/resolve/main/deploy-on-spaces-md-dark.svg)](https://huggingface.co/spaces/cxumol/CoverPilot?duplicate=true)

### Run on local

```bash
git clone https://github.com/cxumol/CoverPilot.git && cd CoverPilot
pip install -r requirements.txt
python app/app.py
```

Once the app is running, you can access it at http://localhost:7860.  
And then follow the instructions on the Web UI.  

If you are still confused about how to use it, check out the [demo video](#demo).

## Example

Here is an example of generated file [cover_letter_by_Steve Jobs_to_Microsoft.pdf](https://github.com/cxumol/CoverPilot/blob/main/asset/example_cover_letter_by_Steve%20Jobs_to_Microsoft.pdf)

> [!TIP]
> Yes, it's generated from the video demo.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Motivation

Please consider hiring me if you like this project. 
