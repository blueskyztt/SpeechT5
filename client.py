# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import numpy as np
import requests

import soundfile as sf

url = "http://localhost:8080/predictions/SpeechT5-temp"
data = "Today is Monday. Today is sunny, no wind, and the temperature is mild."

data = json.dumps(data)
res = requests.post(url=url, data=data)
if res.ok:
    res = res.text
    res = json.loads(res)
    rate = res["rate"]
    wav = res["wav"]
    sf.write("output_client.wav", np.array(wav), rate)
    print('Successfully generated output_client.wav')
else:
    print("error....")
