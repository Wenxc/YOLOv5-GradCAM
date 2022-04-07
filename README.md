# yolov5-grad-cam
A simple implementation of Grad-cam for YOLO-v5. 
To be more simple, You can just copy PlotCAM.py into your project and run it 

Please  give a ⭐ if this functionality benefits your research and projects.



## Installation

```
pip install -r requirements.txt
```



## Infer

```
python main.py --model-path yolov5s.pt --img-path images/cat-dog.jpg --output-dir outputs
```



***NOTE***: If you don't have any weights and just want to test, don't change the model-path argument. The yolov5s model will be automatically downloaded thanks to the download function from yolov5. 



***NOTE***: For more input arguments, check out the main.py or run the following command:

```
python main.py -h
```



**## Note**

Still no explanation for why the truck's heatmap does not show anything. Please inform me or create a pull request if you find the reason.



**## TO Do**

1. Add GradCam++

2. Add ScoreCam



**## References**

1. https://github.com/1Konny/gradcam_plus_plus-pytorch

2. https://github.com/ultralytics/yolov5

3. https://github.com/pooya-mohammadi/yolov5-gradcam

