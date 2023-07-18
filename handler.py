#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import time
import torch
from datasets import load_dataset
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from ts.torch_handler.base_handler import BaseHandler

logger = logging.getLogger(__name__)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

class speecht5Handler(BaseHandler):
    def __init__(self):
        super().__init__()

        self.model_name = "speecht5"
        self.hifigan = 'hifigan'

    def initialize(self, context):
        properties = context.system_properties
        self.map_location = (
            "cuda"
            if torch.cuda.is_available() and properties.get("gpu_id") is not None
            else "cpu"
        )
        self.device = torch.device(
            self.map_location + ":" + str(properties.get("gpu_id"))
            if torch.cuda.is_available() and properties.get("gpu_id") is not None
            else self.map_location
        )
        self.manifest = context.manifest
        logger.info("========properties:" + json.dumps(properties, ensure_ascii=False))
        logger.info("========manifest:" + json.dumps(self.manifest, ensure_ascii=False))
        model_dir = os.path.join(properties.get("model_dir"), self.model_name)
        hifigan_dir = os.path.join(properties.get("model_dir"), self.hifigan)

        logger.info(f"========model_dir:{model_dir}")
        logger.info(f"========hifigan_dir:{hifigan_dir}")

        processor = SpeechT5Processor.from_pretrained(model_dir)
        model = SpeechT5ForTextToSpeech.from_pretrained(model_dir)
        vocoder = SpeechT5HifiGan.from_pretrained(hifigan_dir)
        embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

        self.processor = processor
        self.model = model
        self.speaker_embeddings = speaker_embeddings
        self.vocoder = vocoder
        self.initialized = True

    def preprocess(self, data):
        data = data[0]["body"].decode("utf-8")
        data = json.loads(data)
        logger.info(f"data:{data}")
        return data

    def inference(self, data, *args, **kwargs):
        logger.info(f"====torch.cuda.is_available():{torch.cuda.is_available()}")
        with torch.no_grad():
            result = self.generate(input_data=data)
        return result

    def postprocess(self, data):
        return data

    def handle(self, data, context):
        start_time = time.time()

        self.context = context
        metrics = self.context.metrics

        logger.info('handle(),===============')

        data = self.preprocess(data)
        output = self.inference(data)
        output = self.postprocess(output)

        stop_time = time.time()
        metrics.add_time(
            "HandlerTime", round((stop_time - start_time) * 1000, 2), None, "ms"
        )
        return output

    def generate(self, input_data):
        processor = self.processor
        model = self.model
        speaker_embeddings = self.speaker_embeddings
        vocoder = self.vocoder

        inputs = processor(text=input_data, return_tensors="pt")
        speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)

        speech = speech.numpy().tolist()
        rate = 16000
        ret = {"wav": speech, "rate": rate}
        ret = [ret]
        return ret








