# palinodes
A website for bands to keep repositories of their songs being worked on

## UI prototype:
https://www.figma.com/proto/TlmfKpF09IonyECzyZjE9D/plainodes.com?page-id=0%3A1&node-id=261-102&starting-point-node-id=261%3A102&scaling=scale-down&show-proto-sidebar=1&mode=design&t=EVN5WzMmM0dI8xwG-1

## Tech stack:
  ### Back-end:
  - Python/Django
    - Django REST framework
  - sqlite (development)
  - postgresql (production)

  ### Front-end:
  - HTML5/CSS3
  - Sass
  - Vanilla Javascript
    - wavesurfer.js (waveform visualisation for audio player) https://wavesurfer.xyz
   
  ### Production:
  
  #### Hosting:
  - AWS Elastic beanstalk
  #### Storage:
  - AWS S3

## How to run:
- Clone repository
- Create virtual environment `python -m venv <my_env>`
- install dependencies `pip install -r requirements.txt`
- run with `python manage.py runserver`
- login with superuser **admin**, password **1234**
  
