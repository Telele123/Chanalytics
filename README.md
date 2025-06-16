# Chanalytics
### Video Demo: (https://youtu.be/EcRGxa_hKi8?si=3tpZKXLQGB8O4Wlx)
#### Description:
This is a website that allows users to upload their WhatsApp chat and receive an analysis broken down into:
1.	Messages
2.	Emojis
3.	Words
4.	Links shared
5.	Timeline

The app.py file contains the backend logic. I’ve imported several libraries:
1.	matplotlib – to plot pie charts and bar graphs
2.	Counter – to get the top 10 words, emojis, etc.
3.	tokenize – to divide messages into words
4.	wordcloud – to generate word clouds
5.	datetime 
6.	emoji
/index
The index route and index.html form the homepage. This page contains instructions on how to upload the WhatsApp .txt file. When the user clicks submit, it sets session['visited'] = True, which is passed to layout.html. When visited is True, the navigation bar with the five analysis links is displayed. Each time the user returns to the index page, session['visited'] is reset to False.
Next, I extract both usernames from the text file, making sure not to duplicate names.
index.py also initiates the breakdown of the chat using regular expressions. Since each WhatsApp message starts like this:
[2025/06/13, 21:50:36] Ruan:
I use this pattern to split the text into individual messages for each user. The usernames and message lists are stored in session so they can be accessed across different routes.
 
/messages
This route analyses actual text messages. 
[2025/06/15, 18:17:28] Michelle: ‎Voice call, ‎40 sec  
[2025/06/15, 18:32:05] Michelle: Remember that it’s Father’s Day  
[2025/06/15, 18:37:48] Ruan 🦘: Thanks!  
[2025/06/15, 18:40:10] Ruan 🦘: ‎Missed voice call, ‎Tap to call back  
First voice call, missed voice call etc. are filtered out. If we don’t exclude "Voice call" or "Missed voice call", it would incorrectly inflate the number of texts and words sent. A for loop is created to loop over the list of messages in each user’s text and filter out these phrases as well as count the sum of words in each text message. Later len() is used to count the filtered list of text messages. 
Pie charts are created from the count of words and text messages.
Finally I calculate the duration of the WhatsApp conversation by comparing the timestamps of the first and last message.
 
/emojis
This route uses the emoji library to extract all emojis from the text (via emoji.emoji_list(text_content)). I use Counter.most_common() to find the most used emojis and display this in a pie chart using matplotlib.
I repeat the process to find the top emojis for each user individually. There is also a search option that lets users count how many times a specific emoji was used — both per user and overall.
 
/words
This route is similar to /emojis. I first filter out system messages (missed voice calls, etc.) to avoid skewed results. I then tokenize each user’s messages to extract words, remove punctuation, and discard emojis.
Using isalpha(), I ensure only alphabetic words are kept, and I remove common stopwords like “I”, “you”, “it”, “a”, “the”.
I then use Counter.most_common() to get the most frequent words.
Finally, I generate three word clouds — one for each user and one combined. I also calculate the number of unique words used by converting the word list into a set and finding its length.
 
/links
This route loops through all messages and checks for keywords to count images, voice calls, video calls, audio files, videos, and links.
For voice and video calls, regular expressions are used to extract durations in minutes, hours, and seconds to calculate total call time.
 
/timeline
In this route, I use regex to extract all timestamps. I then extract hours, days, weekdays, and months separately. Each is run through Counter.most_common() to determine frequency.
The most common days, months, and hours are displayed using bar and pie charts.
 
#### HTML Files:
1. index.html
Provides upload instructions and a file submit button.
2. layout.html
Includes Bootstrap links and styles the navigation bar.
3. messages.html
Styled to resemble a WhatsApp scrolling conversation.
4. Words.html
Shows top 10 words and word clouds for both users together and individually. Includes a search option to search for the count of any word.
5. emojis.html
Uses scrollable cards to display the top emojis. Includes a search option to search for the count of any emoji.
6. links.html
Uses scrollable cards to display statistics for different media and links.
7. timeline.html
Displays the three timeline graphs with appropriate headings.
 
Disclaimer:
Most of the HTML styling was done with help from ChatGPT. My original design was much simpler but fully functional. See below
