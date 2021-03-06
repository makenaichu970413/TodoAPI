## 🔥Cognixus Technical Assignment (Cognixus Todo API) <br /> <br />

### 📖Introduction
The assessment API are named as "Cognixus Todo API" and has been deployed into "Heroku" free hosting service with the <br />
URL: (https://cognixus-todo-api.herokuapp.com/). Feel free to use the API whenever you want🚀. <br /> <br />


### 🚀Testing Online Cognixus Todo API
https://cognixus-todo-api.herokuapp.com/ <br /> <br />


### 📖API Dodumentation
https://cognixus-todo-api.herokuapp.com/swagger/ <br /> <br />


### ⚙️Project Setup
***1. Pull Docker Image***
- Pull the Docker Image from Docker Hub by run command: ```docker pull 970413/cognixus_todo_api```<br />

***2. Setup Docker Container***
- After Docker Image have pulled, build up the Docker Container by using given "docker-compose.yml" file and <br /> run command: ```docker-compose up --build -d```<br />

***3. Docker Container Started***
- The started container would run on the server with port "5002", Eg: the ```http://0.0.0.0:5002``` <br /> <br />


### 💻Assessment Features

***1. Authentication***
- User are allow to Signup and Login the account.
- Kept user session and authenticated status whenever user have provided token.
- Restrict the user CRUD todo event whenever token over the expiration time.

***2. Email Verification***
- Sending the email verification link to user email to confirm that a user has provided a correct email and actually wishes to receive important updates from our system.
- The email verification link would be expired after 12 hour of receiving mail. 
- User are required to re-login and perform the sending email verification again.

***3. Password Reset***
- Sending a password reset link to help users securely re-establish access to their accounts.
- The password reset link would be expired after 12 hour of receiving mail. 
- User are required to re-login and perform the sending email verification again.


<br /> <br />That’s the end of the assessment setup and introduction, I hope you have fun!
Wish you hav a nice day 🌻🌻🌻
