# Resources	

Here you can find different resources which are existing as an HTTP API.

# API


## /face_detection

Detect faces, return bounding boxes and confidence for each.

Input: Image Data

Output:
```json
{
   "detectedFaces":[
      {
         "boundingPoly":{
            "vertices":[
               {
                  "x":0.2236503856041131,
                  "y":0.13727959697732997
               },
               {
                  "x":0.2236503856041131,
                  "y":0.5377833753148614
               },
               {
                  "x":0.5347043701799485,
                  "y":0.13727959697732997
               },
               {
                  "x":0.5347043701799485,
                  "y":0.5347043701799485
               }
            ]
         },
         "confidence":0.9999960660934448
      }
   ]
}
```

Example:
```bash
    curl -H "Content-Type: image/jpg" \
         -H 'customerId: aiconix' \
         --data-binary "@$(pwd)/tests/sample_data/bruce_willis/216.jpg" \
         http://localhost:8000/face_detection
```
