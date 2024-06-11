import base64
import json
import time

import requests
from PIL import Image
from io import BytesIO


# from doctr.models import ocr_predictor

# ocr = ocr_predictor(
#     pretrained=True,
#     det_arch="db_mobilenet_v3_large",
#     reco_arch="crnn_mobilenet_v3_large",
# )


# def extract_text_from_image(image):
#     result = ocr([image])
#     text = ""
#     for page in result.pages:
#         for block in page.blocks:
#             for line in block.lines:
#                 for word in line.words:
#                     text += word.value + " "
#                 text += "\n"
#             text += "\n"
#     return text

def extract_text_from_image(sc):
    ocr_service_url = "https://ocrs.enoir.org"
    buffered = BytesIO()
    image = Image.fromarray(sc)
    image.save(buffered, format="webp")

    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # post data to https://ocrs.enoir.org
    url = ocr_service_url + "/service/jobs"
    headers = {"Content-Type": "application/json"}
    req_data = {"data": img_str, "fileName": "sc.webp"}
    response = requests.post(url, headers=headers, json=req_data)
    job_id = response.json()['jobId']
    if response.status_code == 200:
        print("success get job id: "+job_id)
    else:
        print("error")
        return ""
    print("Start to fetch data from job id")
    # 10 times each times sleep 1 second
    for i in range(1, 10):
        result_response = requests.get(ocr_service_url + '/service/jobs/' + job_id)
        # if response code not 200 return error
        if result_response.status_code != 200:
            print("error")
            break
        result_response = json.loads(result_response.text)
        if result_response['status'] == 'finished':
            result_objs = result_response['jobRes']['result']
            # for result_obj in result_objs combine result_obj['text'] to a string and return
            rest_text = ""
            for result_obj in result_objs:
                rest_text += result_obj['text'] + '\n'

            print(rest_text)
            return rest_text
        else:
            print("not finished")
        time.sleep(1)
    return ""
