# Final Project

## Description

For my final project, I want to build off of what we did in week 5 (W5A Edge Detection – edge image – add blur or show Laplacian (grayscale edges)). I want to combine that with what we did this week with the docker build that runs on localhost, so it would be an image editing service that could be fun to play around with.

## Design

I am using ChatGPT mainly to help me with the final project, but I might also use Claude and Grok. 

I found this website on OpenCV that talks about photoshop: https://learnopencv.com/photoshop-filters-in-opencv/
and I hope to use that documentation with the help of AI to potentially try to make filters as well.

For this project, I am in the early prototyping phase and still figuring out the best way to combine image processing with a simple web interface. My main idea is to build a lightweight Photoshop-like application using OpenCV that runs locally through a Docker container. The user would be able to upload an image and apply different effects such as edge detection, blur, grayscale, and possibly other filters. I plan to start small by reusing code from Week 5 (edge detection and Laplacian filters) and then gradually add more features as I learn how OpenCV works with images in a web environment.

To approach this, I will first focus on getting a basic working version where a user can upload an image and see one transformation applied. After that, I will expand the functionality by adding multiple filter options and possibly buttons or a simple UI to switch between them. I also plan to experiment with combining filters (for example, blur + edge detection) to make the app more interactive and “Photoshop-like.” Running the app through Docker will allow it to be accessed on localhost, which connects this project to what we learned in class about containers and deployment.

I used the following resource to understand how Photoshop-style filters can be implemented in OpenCV:
https://learnopencv.com/photoshop-filters-in-opencv/

These are some other website resources I am looking into: 
https://www.tutorialspoint.com/opencv_python/opencv_python_image_filtering.htm
https://scikit-image.org/skimage-tutorials/lectures/1_image_filters.html
https://www.superdatascience.com/blogs/opencv-face-detection
https://learnopencv.com/create-snapchat-instagram-filters-using-mediapipe/

I like the idea of trying to make face filters similar to what snapchat/tiktok/instagram have, but I will have to look into whether it is realistic for me to accomplish with my skill set and my time. 

I will use AI to help me understand how to structure the project, debug code, and learn how OpenCV functions work. I have asked questions about how to apply image filters, how to connect Python code to a web interface, and how to run applications using Docker. I may also use other AI tools like Claude or Grok for additional explanations or examples if I get stuck. The AI tools are mainly helping me learn step-by-step and break down concepts into simpler parts so I can actually implement them myself.

This design will likely change as I continue developing the project, especially as I discover what is realistic to complete within the time limit.

I use this to run my file:
cd C:\Users\ikecr\OneDrive\Desktop\CIS450\CIS450-demo\finalproject\template
.\.venv\Scripts\Activate.ps1
python app.py
