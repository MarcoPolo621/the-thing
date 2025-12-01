this is a project analyzing wether or not a messege recieved from a new sender to a android device is a smishing message,
it will check first with the database that it has been tought with ML, if it is unsure, it will use gemini to check over the message,
it will then notify the user of the suspicious message, they will then be able to make the decision on deleting the message, if they do it will report the sender to reportfraud.ftc
or 7726(spam), which will hopefully lower the success rates of these messages being sent

1st run trainmodels.py
2nd run server.py
3rd, point android application to point to the Ip that the server.py gives to you
